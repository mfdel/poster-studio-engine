"""Theme loading — style-as-data, shared across every poster product.

A theme JSON lives in ``studio/themes/`` and carries the *brand* blocks
(``palette``, ``type``, ``border``) plus optional *product* blocks:

    map    — road weights, marker sizes, hand-drawn wobble  (FAM-001)
    chart  — day/night/curve/grid/axis/marker colours        (PRT-006 and later)

Product blocks are optional. ``chart_tokens`` derives a usable chart palette from
the brand palette when a theme has no ``chart`` block, so a new poster type
renders in all existing themes on day one instead of needing 14 file edits.
"""
from __future__ import annotations

import json
from pathlib import Path

from posterlab.paths import THEMES
from posterlab.select import expand_selection

__all__ = ["THEMES", "load_theme", "available_themes", "resolve_themes",
           "chart_tokens", "room_tokens"]


def load_theme(name_or_path: str) -> dict:
    p = Path(name_or_path)
    if not p.exists():
        p = THEMES / f"{name_or_path}.json"
    if not p.exists():
        raise SystemExit(f"Theme not found: {name_or_path!r} (looked in {THEMES})")
    return json.loads(p.read_text(encoding="utf-8"))


def available_themes() -> list[str]:
    """Theme names shipped in ``studio/themes/`` (sorted) — used by ``--theme all``."""
    return sorted(p.stem for p in THEMES.glob("*.json"))


def resolve_themes(theme: str) -> list[str]:
    """Expand a ``--theme`` value: a name or path, ``'all'``, or a comma-separated
    list of either (``'lantern,ink'``).

    A pack sold as one download often ships both colourways, so one render call
    has to be able to name both. The names are not checked here, because
    ``load_theme`` also accepts a path to a theme file and is the authority on
    what resolves.
    """
    return expand_selection(theme, groups={"all": available_themes()}, what="theme")


def chart_tokens(theme: dict) -> dict[str, str]:
    """Chart colours for a theme: its ``chart`` block, else derived from the palette.

    The derivation deliberately reuses brand tokens (not a fresh chart palette) so
    an unedited theme still reads as the same studio. Hand-tune the ``chart`` block
    only on the themes that actually go into listings.
    """
    pal = theme["palette"]
    derived = {
        "day": pal.get("home_marker", pal.get("playground_marker", "#e8b64c")),
        "night": pal.get("text", "#1a1a1a"),
        "curve": pal.get("coastline", pal.get("text", "#1a1a1a")),
        "grid": pal.get("annotation_line", pal.get("border", "#cccccc")),
        "axis": pal.get("border", pal.get("muted", "#888888")),
        "marker": pal.get("playground_marker", pal.get("home_marker", "#d1495b")),
    }
    derived.update(theme.get("chart") or {})
    return derived


def room_tokens(theme: dict) -> dict[str, str]:
    """Room-interior colours for a theme: its ``room`` block, else derived.

    Same contract as :func:`chart_tokens` — FAM-003 prints a room, not a map, but
    it must still read as this studio, so the fallback reuses brand tokens rather
    than inventing an interior palette. Hand-tune a ``room`` block only on the
    themes that go into listings.
    """
    pal = theme["palette"]
    roads = pal.get("roads", {})
    derived = {
        "wall": pal.get("annotation_box", pal["land"]),
        "wall_stripe": pal.get("green", pal["land"]),
        "wall_line": pal.get("annotation_line", pal["muted"]),
        "skirting": pal["page"],
        "trim": pal["text"],
        "floor": roads.get("residential", pal["land"]),
        "floor_joint": roads.get("path", pal["muted"]),
        "rug": pal.get("playground_marker", pal["border"]),
        "rug_alt": pal.get("annotation_box", pal["page"]),
        "sky": pal["water"],
        "accent": pal["border"],
        "muted": pal["muted"],
    }
    derived.update(theme.get("room", {}))
    return derived
