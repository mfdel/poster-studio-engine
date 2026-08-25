#!/usr/bin/env python3
"""
Local web dashboard for the poster CLIs (every product in ``posters/``).

A tiny, dependency-free control panel: pick a poster product, fill its parameters
(address, radius, theme, size, variant, …), hit **Generate**, and the dashboard
runs that product's ``make.py`` — streaming its log live and showing the PNG
previews / PDF files it produced.

Design notes
------------
* **Stdlib only** (``http.server``). No Flask/FastAPI — this is a side-hustle
  helper, not a service. Runs locally, binds to 127.0.0.1.
* **Registry-driven**: products are discovered from ``posters/*/poster.toml``
  (:mod:`posterlab.product`), and each product ships its own form description in
  ``posters/<slug>/dashboard.json``. Adding a poster needs no change here.
* Theme + size options are expanded from ``studio/themes/*.json`` and
  ``posterlab.chrome.SIZES`` (the ``@themes`` / ``@sizes`` placeholders) so the UI
  stays in sync with the code.
* The product CLI is invoked with an **argv list** (never a shell string), so form
  input can't inject shell commands.
* Output files under ``output/`` are served read-only with a path-traversal guard.

Usage
-----
    # from the repo root, with the venv active (so cairosvg etc. are importable)
    source .venv/bin/activate
    python studio/dashboard/dashboard.py            # -> http://127.0.0.1:8000
    python studio/dashboard/dashboard.py --port 8010 --open

Data © OpenStreetMap contributors (ODbL).
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import subprocess
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from posterlab.chrome import SIZES
from posterlab.paths import OUTPUT, ROOT
from posterlab.product import Poster, discover_posters
from posterlab.runstore import index_entries
from posterlab.themes import THEMES

HERE = Path(__file__).resolve().parent
HTML_FILE = HERE / "dashboard.html"

# Serialize runs — the product CLIs hit public OSM endpoints; one at a time is
# polite and keeps the streamed log unambiguous.
_RUN_LOCK = threading.Lock()


# --------------------------------------------------------------------------- #
# Discover products + options from the code so the form never drifts from the CLI
# --------------------------------------------------------------------------- #

POSTERS: dict[str, Poster] = {p.kind: p for p in discover_posters()}
if not POSTERS:
    raise SystemExit(f"No poster products found under {ROOT / 'posters'}")


def discover_themes() -> list[dict[str, str]]:
    themes: list[dict[str, str]] = []
    for p in sorted(THEMES.glob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            themes.append({"value": d.get("name", p.stem), "label": d.get("label", p.stem)})
        except Exception:
            themes.append({"value": p.stem, "label": p.stem})
    return themes or [{"value": "minimal", "label": "Minimal"}]


def _expand_options(options):
    """Resolve the ``@themes`` / ``@sizes`` placeholders a product may use."""
    if options == "@themes":
        return discover_themes() + [{"value": "all", "label": "★ All themes"}]
    if options == "@sizes":
        return list(SIZES) + ["bundle", "pod", "all"]
    return options


def build_meta(kind: str) -> dict:
    """Everything the frontend needs to render one product's form."""
    poster = POSTERS[kind]
    form = poster.form_schema() or {"schema": [], "groups": [], "recall": {}}
    schema = []
    for item in form.get("schema", []):
        item = dict(item)
        if "options" in item:
            item["options"] = _expand_options(item["options"])
        schema.append(item)
    entry = poster.entry.relative_to(ROOT) if poster.entry else None
    return {
        "poster": kind,
        "name": poster.name,
        "id": poster.id,
        "buildable": poster.buildable,
        "command_prefix": f"python {entry}" if entry else "",
        "attribution": poster.data.get("license", ""),
        "posters": [
            {"value": p.kind, "label": p.name, "id": p.id,
             "buildable": p.buildable, "status": p.status}
            for p in POSTERS.values()
        ],
        "schema": schema,
        "groups": form.get("groups", []),
        "recall": form.get("recall", {}),
    }


META: dict[str, dict] = {kind: build_meta(kind) for kind in POSTERS}
DEFAULT_KIND = next((k for k, m in META.items() if m["buildable"]), next(iter(META)))


def _meta_for(kind: str | None) -> dict:
    return META.get(kind or DEFAULT_KIND, META[DEFAULT_KIND])


def previous_runs(kind: str) -> list[dict]:
    """Runs the user has generated before for this product, newest first.

    Powers the "recall a previous run" search box. The product's
    ``dashboard.json`` ``recall`` block decides which index field is the label and
    which fields refill which flags, so this stays product-agnostic. Returns an
    empty list when the index is missing or the product has no recall block.
    """
    recall = _meta_for(kind).get("recall") or {}
    label_field = recall.get("label")
    if not label_field:
        return []
    fill_map: dict[str, str] = recall.get("fill", {})
    # Each "meta" entry is a field name, or {"field": …, "suffix": " m"}.
    meta_fields = [m if isinstance(m, dict) else {"field": m}
                   for m in recall.get("meta", [])]
    rows: list[dict] = []
    try:
        entries = index_entries(kind)
    except Exception:
        return []
    for e in entries:
        label = e.get(label_field)
        if not label:
            continue
        rows.append({
            "label": str(label),
            "meta": " · ".join(f"{e[m['field']]}{m.get('suffix', '')}"
                               for m in meta_fields if e.get(m["field"]) is not None),
            "latest": e.get("latest", ""),
            "fill": {flag: e.get(field) for field, flag in fill_map.items()
                     if e.get(field) is not None},
        })
    return rows


# --------------------------------------------------------------------------- #
# argv construction (whitelist only — no shell)
# --------------------------------------------------------------------------- #

def build_argv(kind: str, params: dict) -> list[str]:
    meta = _meta_for(kind)
    checkboxes = {i["flag"] for i in meta["schema"] if i["type"] == "checkbox"}
    argv: list[str] = []
    for item in meta["schema"]:            # deterministic, schema-defined order
        flag = item["flag"]
        if flag not in params:
            continue
        val = params[flag]
        if flag in checkboxes:
            if bool(val):
                argv.append(flag)
            continue
        if val is None:
            continue
        s = str(val).strip()
        if s == "":
            continue
        argv.extend([flag, s])
    return argv


def display_command(kind: str, argv: list[str]) -> str:
    def q(s: str) -> str:
        return f'"{s}"' if any(c in s for c in ' "\'$`\\') else s
    prefix = _meta_for(kind)["command_prefix"] or "python"
    return " ".join([prefix, *(q(a) for a in argv)])


# --------------------------------------------------------------------------- #
# Output snapshotting (to report exactly what a run produced)
# --------------------------------------------------------------------------- #

_TRACKED_SUFFIXES = {".png", ".pdf", ".zip"}


def snapshot() -> dict[str, float]:
    snap: dict[str, float] = {}
    if not OUTPUT.exists():
        return snap
    for p in OUTPUT.rglob("*"):
        if p.is_file() and p.suffix.lower() in _TRACKED_SUFFIXES:
            try:
                snap[str(p.relative_to(OUTPUT))] = p.stat().st_mtime
            except OSError:
                pass
    return snap


def new_files(before: dict[str, float]) -> list[dict]:
    after = snapshot()
    changed = [rel for rel, mt in after.items()
               if rel not in before or mt > before[rel] + 1e-6]
    files: list[dict] = []
    for rel in changed:
        p = OUTPUT / rel
        try:
            size = p.stat().st_size
            mt = p.stat().st_mtime
        except OSError:
            continue
        files.append({"rel": rel, "name": p.name, "size": size, "mtime": mt})
    files.sort(key=lambda f: f["mtime"], reverse=True)
    return files


# --------------------------------------------------------------------------- #
# HTTP handler
# --------------------------------------------------------------------------- #

class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):  # quieter console
        sys.stderr.write("· " + (fmt % args) + "\n")

    # -- small helpers -------------------------------------------------------
    def _send(self, code: int, body: bytes, ctype: str, extra: dict | None = None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, obj) -> None:
        self._send(code, json.dumps(obj).encode("utf-8"), "application/json; charset=utf-8")

    # -- routing -------------------------------------------------------------
    def _poster_param(self) -> str:
        """The ``?poster=<kind>`` query value, falling back to the default."""
        qs = parse_qs(urlparse(self.path).query)
        kind = (qs.get("poster") or [None])[0]
        return kind if kind in META else DEFAULT_KIND

    def do_GET(self):
        path = unquote(urlparse(self.path).path)
        if path in ("/", "/index.html"):
            return self._serve_html()
        if path == "/api/meta":
            return self._json(200, _meta_for(self._poster_param()))
        if path == "/api/addresses":
            kind = self._poster_param()
            return self._json(200, {"addresses": previous_runs(kind)})
        if path.startswith("/output/"):
            return self._serve_output(path[len("/output/"):])
        self._send(404, b"not found", "text/plain; charset=utf-8")

    def do_POST(self):
        path = unquote(urlparse(self.path).path)
        if path == "/api/run":
            return self._run()
        self._send(404, b"not found", "text/plain; charset=utf-8")

    # -- handlers ------------------------------------------------------------
    def _serve_html(self):
        try:
            body = HTML_FILE.read_bytes()
        except OSError:
            return self._send(500, b"dashboard.html missing", "text/plain; charset=utf-8")
        self._send(200, body, "text/html; charset=utf-8")

    def _serve_output(self, rel: str):
        rel = rel.split("?", 1)[0]
        target = (OUTPUT / rel).resolve()
        base = OUTPUT.resolve()
        if base != target and base not in target.parents:
            return self._send(403, b"forbidden", "text/plain; charset=utf-8")
        if not target.is_file():
            return self._send(404, b"not found", "text/plain; charset=utf-8")
        ctype = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        data = target.read_bytes()
        self._send(200, data, ctype, extra={"Cache-Control": "no-store"})

    def _run(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            params = json.loads(raw.decode("utf-8"))
            if not isinstance(params, dict):
                raise ValueError("expected an object")
        except Exception as e:
            return self._json(400, {"error": f"bad request: {e}"})

        kind = params.pop("_poster", None)
        if kind not in META:
            kind = DEFAULT_KIND
        poster = POSTERS[kind]

        # keep only flags this product declares
        known = {i["flag"] for i in _meta_for(kind)["schema"]}
        params = {k: v for k, v in params.items() if k in known}
        argv = build_argv(kind, params)

        # Stream NDJSON: one JSON object per line.
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "close")
        self.end_headers()

        def emit(obj) -> bool:
            try:
                self.wfile.write((json.dumps(obj) + "\n").encode("utf-8"))
                self.wfile.flush()
                return True
            except (BrokenPipeError, ConnectionResetError):
                return False

        emit({"type": "command", "argv": argv, "display": display_command(kind, argv)})

        if not poster.buildable:
            emit({"type": "error",
                  "message": f"{poster.name} ({poster.id}) has no CLI yet — it is still "
                             f"a {poster.status} product."})
            emit({"type": "result", "code": 1, "files": []})
            return

        if not _RUN_LOCK.acquire(blocking=False):
            emit({"type": "error", "message": "another run is already in progress"})
            emit({"type": "result", "code": 1, "files": []})
            return

        before = snapshot()
        try:
            env = dict(os.environ, PYTHONUNBUFFERED="1")
            proc = subprocess.Popen(
                [sys.executable, str(poster.entry), *argv],
                # Run inside the product dir so its sibling modules import.
                cwd=str(poster.dir), env=env,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1,
            )
            assert proc.stdout is not None
            for line in proc.stdout:
                if not emit({"type": "log", "line": line.rstrip("\n")}):
                    proc.kill()
                    return
            code = proc.wait()
        except Exception as e:
            emit({"type": "error", "message": str(e)})
            emit({"type": "result", "code": 1, "files": []})
            return
        finally:
            _RUN_LOCK.release()

        emit({"type": "result", "code": code, "files": new_files(before)})


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #

def main() -> None:
    ap = argparse.ArgumentParser(description="Local dashboard for the poster CLIs.")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--open", action="store_true", help="open the dashboard in a browser")
    args = ap.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    url = f"http://{args.host}:{args.port}"
    print(f"Poster studio dashboard → {url}")
    for p in POSTERS.values():
        state = "ready" if p.buildable else f"{p.status}, no CLI yet"
        print(f"  {p.id}  {p.name} ({p.kind}) — {state}")
    print(f"  serving previews from {OUTPUT}")
    print("  Ctrl-C to stop.")
    if args.open:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping.")
        server.shutdown()


if __name__ == "__main__":
    main()
