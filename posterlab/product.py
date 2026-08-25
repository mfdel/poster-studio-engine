"""Poster product registry — reads ``posters/<slug>/poster.toml``.

Adding a poster to the shop means adding a directory with a ``poster.toml``; the
dashboard and any tooling discover it from here instead of hardcoding a list.

    from posterlab.product import discover_posters, load_poster
    for p in discover_posters():
        print(p.id, p.kind, p.entry)
"""
from __future__ import annotations

import json
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from posterlab.paths import POSTERS

MANIFEST = "poster.toml"
FORM_SCHEMA = "dashboard.json"


@dataclass
class Poster:
    slug: str                 # directory name, e.g. "fam001-playground-map"
    id: str                   # idea code, e.g. "FAM-001"
    kind: str                 # short run/output partition key, e.g. "map"
    name: str                 # human label, e.g. "Playground Map"
    status: str               # "live" | "draft"
    dir: Path
    entry: Path | None        # the CLI to run, if the product has one yet
    data: dict = field(default_factory=dict)     # source/licence metadata
    commerce: dict = field(default_factory=dict)  # sku prefix, sizes …

    @property
    def buildable(self) -> bool:
        return self.entry is not None and self.entry.is_file()

    def form_schema(self) -> dict | None:
        """The dashboard form description shipped by this product, if any."""
        p = self.dir / FORM_SCHEMA
        if not p.is_file():
            return None
        return json.loads(p.read_text(encoding="utf-8"))


def load_poster(directory: Path) -> Poster:
    manifest = directory / MANIFEST
    if not manifest.is_file():
        raise SystemExit(f"No {MANIFEST} in {directory}")
    raw = tomllib.loads(manifest.read_text(encoding="utf-8"))
    p = raw.get("poster", {})
    entry_name = p.get("entry")
    entry = directory / entry_name if entry_name else None
    return Poster(
        slug=p.get("slug", directory.name),
        id=p.get("id", directory.name),
        kind=p.get("kind", directory.name),
        name=p.get("name", directory.name),
        status=p.get("status", "draft"),
        dir=directory,
        entry=entry,
        data=raw.get("data", {}),
        commerce=raw.get("commerce", {}),
    )


def discover_posters(*, buildable_only: bool = False) -> list[Poster]:
    """Every poster product with a manifest, ordered by idea code."""
    posters = [load_poster(m.parent) for m in sorted(POSTERS.glob(f"*/{MANIFEST}"))]
    if buildable_only:
        posters = [p for p in posters if p.buildable]
    return sorted(posters, key=lambda p: p.id)


def poster_by_kind(kind: str) -> Poster | None:
    for p in discover_posters():
        if p.kind == kind:
            return p
    return None
