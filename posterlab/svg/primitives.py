"""Poster-agnostic SVG primitives.

Every poster product composes its body from these, so coordinate rounding (and
therefore file size and vector precision) is identical across the shop.
"""
from __future__ import annotations

import math
from typing import Callable, Sequence

# cairosvg's path parser re-slices the remaining `d` string on every token, so a
# single `d` costs O(tokens x length). Merging a whole class of geometry into one
# element makes dense drawings (central Paris: 35k footways, 2.6 MB of `d`)
# effectively hang. Capping each element keeps the cost linear.
MAX_PATH_D_CHARS = 8000


def num(v: float) -> str:
    """Two-decimal coordinate formatting — the shop-wide SVG precision."""
    return f"{v:.2f}"


def path_d(coords: Sequence[Sequence[float]],
           proj: Callable[[float, float], tuple[float, float]],
           close: bool = False) -> str:
    """[[lon,lat],...] -> an SVG path `d` string, projected into the frame."""
    parts = []
    for i, (lon, lat) in enumerate(coords):
        x, y = proj(lon, lat)
        parts.append(f"{'M' if i == 0 else 'L'}{num(x)} {num(y)}")
    if close:
        parts.append("Z")
    return "".join(parts)


def chunk_path_ds(ds: list[str], limit: int = MAX_PATH_D_CHARS) -> list[str]:
    """Group per-feature `d` strings into merged `d`s of at most ``limit`` chars."""
    out: list[str] = []
    buf: list[str] = []
    size = 0
    for d in ds:
        if buf and size + len(d) > limit:
            out.append("".join(buf))
            buf, size = [], 0
        buf.append(d)
        size += len(d)
    if buf:
        out.append("".join(buf))
    return out


def star_path(cx: float, cy: float, r: float, points: int = 5) -> str:
    inner = r * 0.42
    pts = []
    for i in range(points * 2):
        ang = math.pi / points * i - math.pi / 2
        rad = r if i % 2 == 0 else inner
        pts.append(f"{num(cx + rad * math.cos(ang))},{num(cy + rad * math.sin(ang))}")
    return "M" + "L".join(pts) + "Z"


def heart_path(cx: float, cy: float, r: float) -> str:
    # A simple two-lobe heart centred roughly on (cx, cy).
    return (
        f"M{num(cx)} {num(cy + r * 0.9)} "
        f"C{num(cx - r * 1.3)} {num(cy - r * 0.2)} "
        f"{num(cx - r * 0.55)} {num(cy - r * 1.05)} {num(cx)} {num(cy - r * 0.35)} "
        f"C{num(cx + r * 0.55)} {num(cy - r * 1.05)} "
        f"{num(cx + r * 1.3)} {num(cy - r * 0.2)} {num(cx)} {num(cy + r * 0.9)} Z"
    )
