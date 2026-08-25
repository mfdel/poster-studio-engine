#!/usr/bin/env python3
"""
Hand-drawn line wobble (FAM-001) — Andy Woodruff-style wave perturbation
(andywoodruff.com/posts/2024/qgis-hand-drawn-maps), ported from his QGIS
geometry-generator recipe to this SVG pipeline.

Opt-in per theme via ``theme["map"]["hand_drawn"]`` (absent/false = the exact
old behaviour — plain straight-line paths). Wired into roads + coastline only
(see INTEGRATION notes in posters/fam001-playground-map/render.py); land-cover polygon *fills* are
left alone because a wobbled ring with holes (fill-rule="evenodd") risks
self-intersecting at high amplitude.

Determinism, not randomness, is the point: the same run must wobble the same
way on every re-render (a reprint that redraws itself differently would read
as a bug, not a style), so the wave's phase/amplitude/wavelength are seeded
per *feature* (via ``seed``, caller-supplied and stable across renders), never
off wall-clock or process state.
"""
from __future__ import annotations

import math
from random import Random

from posterlab.svg.primitives import num as _num


def _resample(pts: list[tuple[float, float]], step_mm: float, max_points: int = 400
             ) -> list[tuple[float, float]]:
    """Densify a polyline to ~step_mm spacing.

    OSM way vertices can be sparse (a straight motorway segment may be just 2
    nodes); a sine wobble sampled only at those 2 points isn't a wave, it's a
    kink. Resampling gives the wave enough points to read as smooth. Capped at
    ``max_points`` per feature so one very long way can't blow up path size.
    """
    if len(pts) < 2:
        return pts
    out = [pts[0]]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if len(out) >= max_points:
            break
        seg_len = math.hypot(x1 - x0, y1 - y0)
        n = min(max(1, int(seg_len // step_mm)), max_points - len(out))
        for i in range(1, n + 1):
            t = i / (n + 1)
            out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
        out.append((x1, y1))
    return out[:max_points]


def wavy_path_d(coords: list[list[float]], proj, seed: int,
                amplitude_mm: float = 0.35, wavelength_mm: float = 16.0,
                close: bool = False) -> str:
    """Same contract as ``posterlab.svg.primitives.path_d`` (coords in [lon,lat], a
    Projector, optional close), plus a deterministic sine wobble applied
    perpendicular to the line's local direction, in projected mm-space (so
    amplitude means the same physical thing regardless of map scale/zoom).

    ``seed`` must be stable per feature — callers should derive it from the
    feature's own coordinates/id, not from render order or wall-clock time.
    """
    pts = [proj(lon, lat) for lon, lat in coords]
    if len(pts) < 2:
        return ""
    pts = _resample(pts, wavelength_mm / 6)
    n = len(pts)

    rng = Random(seed)
    phase = rng.uniform(0, 2 * math.pi)
    # Jitter amplitude/wavelength too (not just phase) so parallel streets
    # don't all wobble in visible lockstep with each other.
    amp = amplitude_mm * rng.uniform(0.75, 1.25)
    wl = wavelength_mm * rng.uniform(0.85, 1.15)

    out: list[tuple[float, float]] = []
    dist = 0.0
    for i, (x, y) in enumerate(pts):
        if i > 0:
            dist += math.hypot(x - pts[i - 1][0], y - pts[i - 1][1])
        if i == 0:
            tx, ty = pts[1][0] - x, pts[1][1] - y
        elif i == n - 1:
            tx, ty = x - pts[i - 1][0], y - pts[i - 1][1]
        else:
            tx, ty = pts[i + 1][0] - pts[i - 1][0], pts[i + 1][1] - pts[i - 1][1]
        tlen = math.hypot(tx, ty) or 1.0
        nx, ny = -ty / tlen, tx / tlen  # perpendicular unit vector
        offset = amp * math.sin(2 * math.pi * dist / wl + phase)
        out.append((x + nx * offset, y + ny * offset))

    d = "M" + "L".join(f"{_num(px)} {_num(py)}" for px, py in out)
    if close:
        d += "Z"
    return d
