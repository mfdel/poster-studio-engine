"""Text helpers shared by every poster product: slugs, locality and font stacks."""
from __future__ import annotations

import re

from typing import Iterable

# CSS generic families a renderer can always fall back to.
_GENERIC_FAMILIES = {"serif", "sans-serif", "monospace", "cursive", "fantasy"}


def font_families(stack: str) -> list[str]:
    """Split a CSS ``font-family`` stack into bare family names, quotes removed."""
    return [f.strip().strip('"\'') for f in stack.split(",") if f.strip()]


def pick_font(stack: str, available: Iterable[str], fallback: str = "serif") -> str:
    """First family in a CSS stack that ``available`` actually has.

    Themes carry CSS stacks because the map renders through SVG, where the browser
    or cairosvg walks the stack itself. Renderers that pick one concrete face
    (matplotlib) must resolve the stack the same way, or a theme silently loses its
    typography to the toolkit default. Falls back to the stack's generic family,
    then to ``fallback``.
    """
    have = set(available)
    names = font_families(stack)
    for name in names:
        if name in have:
            return name
    for name in names:
        if name.lower() in _GENERIC_FAMILIES:
            return name.lower()
    return fallback


def slugify(s: str) -> str:
    """Filesystem-safe slug: lowercase alnum, single underscores, trimmed."""
    keep = "".join(c if c.isalnum() else "_" for c in s.lower())
    while "__" in keep:
        keep = keep.replace("__", "_")
    return keep.strip("_") or "map"


# Nominatim orders a display_name coarsely from most- to least-specific:
#   [house_number,] road, [neighbourhoods…], city, municipality, region,
#   [postcode,] country
# For a human "Street Number, City" line we keep the street (prefixing a leading
# house number when present) and walk in from the tail — dropping country, an
# optional postcode, then the two admin levels (municipality + region) — to land
# on the city/locality.
_HOUSE_NUM = re.compile(r"^\d+\s*[A-Za-z]?$")
_ADMIN_SUFFIX = re.compile(
    r"\s+(kommun|kommune|län|county|gemeinde|comune|município|municipality)$",
    re.IGNORECASE)


def _has_digit(s: str) -> bool:
    return any(ch.isdigit() for ch in s)


def format_locality(display_name: str) -> str:
    """Best-effort 'Street Number, City' from a Nominatim display_name."""
    parts = [p.strip() for p in display_name.split(",") if p.strip()]
    if not parts:
        return ""
    number = ""
    if _HOUSE_NUM.match(parts[0]) and len(parts) > 1:
        number, parts = parts[0], parts[1:]
    street = parts[0]
    tail = parts[1:]
    if tail:  # drop country
        tail = tail[:-1]
    if tail and _has_digit(tail[-1]):  # drop postcode
        tail = tail[:-1]
    for _ in range(2):  # drop region + municipality, but keep the city itself
        if len(tail) > 1:
            tail = tail[:-1]
    city = _ADMIN_SUFFIX.sub("", tail[-1]).strip() if tail else ""
    street_full = f"{street} {number}".strip()
    if city and city.lower() not in street_full.lower():
        return f"{street_full}, {city}"
    return street_full
