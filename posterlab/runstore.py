#!/usr/bin/env python3
"""
Run store + query cache, shared by every poster product.

Every data acquisition (whatever a product needs for one set of inputs) is saved
as an immutable, timestamped **run** under ``data/runs/<kind>/<run_id>/`` —
nothing is ever overwritten. A small JSON index (``data/index.json``) maps a
*cache key* (derived from the product's own inputs) to its runs, so re-running the
same inputs reads the saved run instead of re-hitting the network.

``kind`` is the poster product's short slug (``map`` for FAM-001, ``sun`` for
PRT-006 — see each product's ``poster.toml``). It partitions both the run
directories and the index, which is what keeps ``--run latest`` from resolving a
playground-map run for a sun poster.

Deliberately a plain-filesystem store, not a database: the heavy artifacts are
GeoJSON files the renderers read straight off disk, there is a single user and no
concurrency, and a directory of runs + a JSON index stays git-diffable, greppable
and dependency-free.

This module is pure plumbing: filesystem + JSON only, no network and no product
knowledge. Acquisition logic lives in each product's ``make.py``.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Iterable, Sequence

from posterlab.paths import DATA
from posterlab.text import slugify

# --------------------------------------------------------------------------- #
# Paths / layout
# --------------------------------------------------------------------------- #

RUNS = DATA / "runs"
INDEX = DATA / "index.json"

# v1 was single-product (playground maps only): runs sat flat in ``data/runs/``
# and index entries had no ``kind``. v2 partitions by kind; v1 entries and any
# leftover flat run directories are read as ``kind="map"``.
INDEX_VERSION = 2
DEFAULT_KIND = "map"


# --------------------------------------------------------------------------- #
# Cache key / run id
# --------------------------------------------------------------------------- #

def normalise_text(s: str) -> str:
    """Lowercase, trim, collapse internal whitespace — so trivially different
    spellings of the same typed input share a cache key."""
    return re.sub(r"\s+", " ", s.strip().lower())


def cache_key(kind: str, parts: Sequence[object]) -> str:
    """Stable 8-hex-char key for one product query. Same parts -> same key.

    ``parts`` are the product's cache-defining inputs, already normalised by the
    caller (e.g. ``[normalise_text(address), 2000, "60"]``). The basis is prefixed
    with ``kind`` for every product except the original ``map`` kind, whose keys
    are left unprefixed so the existing ``data/index.json`` keeps hitting its
    cached runs instead of refetching the whole history from Overpass.
    """
    basis = "|".join(str(p) for p in parts)
    if kind != DEFAULT_KIND:
        basis = f"{kind}|{basis}"
    return hashlib.sha1(basis.encode("utf-8")).hexdigest()[:8]


def make_run_id(label: str, key: str, tags: Iterable[str] = ()) -> str:
    """Human-readable, unique, chronologically sortable id:
    ``{YYYYMMDD-HHMMSS}__{slug}__{tags…}__{key}``.

    ``tags`` are short product-specific discriminators (``r2000`` for a map's
    radius, ``y2026`` for a sun poster's year) so a directory listing is readable.
    """
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    slug = slugify(label)[:40]
    middle = "".join(f"{t}__" for t in tags)
    return f"{ts}__{slug}__{middle}{key}"


def kind_dir(kind: str) -> Path:
    return RUNS / kind


def run_dir(run_id: str, kind: str = DEFAULT_KIND) -> Path:
    """Where a run lives. Falls back to the legacy flat ``data/runs/<run_id>``
    path when that directory exists (pre-v2 local data)."""
    legacy = RUNS / run_id
    if legacy.is_dir():
        return legacy
    return kind_dir(kind) / run_id


# --------------------------------------------------------------------------- #
# Index
# --------------------------------------------------------------------------- #

def load_index() -> dict:
    """The index, migrated forward in memory (written back on the next save)."""
    idx = {"version": INDEX_VERSION, "queries": {}}
    if INDEX.exists():
        try:
            idx = json.loads(INDEX.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            return idx
    if idx.get("version", 1) < INDEX_VERSION:
        for entry in (idx.get("queries") or {}).values():
            entry.setdefault("kind", DEFAULT_KIND)
        idx["version"] = INDEX_VERSION
    return idx


def save_index(idx: dict) -> None:
    DATA.mkdir(exist_ok=True)
    INDEX.write_text(json.dumps(idx, ensure_ascii=False, indent=2), encoding="utf-8")


def latest_run_id(key: str) -> str | None:
    """The most recent run id for a cache key, or None if never run."""
    entry = load_index().get("queries", {}).get(key)
    return entry.get("latest") if entry else None


def record_run(key: str, run_id: str, *, kind: str = DEFAULT_KIND, **fields) -> None:
    """Append `run_id` to the key's history and mark it the latest.

    ``fields`` are the product's descriptive fields (``address``, ``radius_m``,
    ``place``, ``year`` …) — kept fresh on every run so the index stays a readable
    list of what has been generated.
    """
    idx = load_index()
    queries = idx.setdefault("queries", {})
    entry = queries.setdefault(key, {"kind": kind, "runs": []})
    entry["kind"] = kind
    entry.update(fields)
    entry.setdefault("runs", [])
    if run_id not in entry["runs"]:
        entry["runs"].append(run_id)
    entry["latest"] = run_id
    save_index(idx)


def index_entries(kind: str | None = None) -> list[dict]:
    """Index entries, newest first, optionally filtered to one poster kind.

    Run ids start with a ``YYYYMMDD-HHMMSS`` stamp, so a lexical sort on
    ``latest`` is chronological.
    """
    rows = []
    for entry in (load_index().get("queries") or {}).values():
        if kind and entry.get("kind", DEFAULT_KIND) != kind:
            continue
        rows.append(entry)
    rows.sort(key=lambda e: e.get("latest", ""), reverse=True)
    return rows


# --------------------------------------------------------------------------- #
# Resolving which run to read
# --------------------------------------------------------------------------- #

def newest_run_id(kind: str | None = None) -> str | None:
    """Newest run id, restricted to ``kind`` when given.

    Without a ``kind`` this spans every product — which is almost never what a
    renderer wants, so products should always pass their own kind.
    """
    if not RUNS.exists():
        return None
    ids: list[str] = []
    if kind is None:
        for p in RUNS.rglob("run.json"):
            ids.append(p.parent.name)
    else:
        for base in (kind_dir(kind), RUNS):  # RUNS covers legacy flat layout
            if not base.exists():
                continue
            ids.extend(p.parent.name for p in base.glob("*/run.json"))
    return max(ids) if ids else None


def resolve_run(selector: str, kind: str = DEFAULT_KIND) -> Path:
    """Resolve a `--run` selector to a run directory.

    `selector` may be the literal ``"latest"`` (newest run *of this kind*) or an
    explicit run id. Raises SystemExit with a helpful message if it can't be
    resolved.
    """
    if selector == "latest":
        rid = newest_run_id(kind)
        if rid is None:
            raise SystemExit(
                f"No {kind!r} runs found under {kind_dir(kind)} — run the product's "
                f"make.py first.")
        return run_dir(rid, kind)
    d = run_dir(selector, kind)
    if not d.is_dir():
        raise SystemExit(f"Run not found: {selector!r} (looked in {kind_dir(kind)})")
    return d
