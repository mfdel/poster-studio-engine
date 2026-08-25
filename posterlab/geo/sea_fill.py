#!/usr/bin/env python3
"""
Sea fill (FAM-001 Playground Map).

OpenStreetMap stores the ocean only as ``natural=coastline`` *lines* — there is
no polygon for "the sea", so a naive render leaves coastal water the same colour
as land. This module reconstructs a filled **sea polygon** from the coastline
lines we already fetch, robustly enough for archipelagos (islands become holes).

Method (all in lon/lat degrees):
  1. Clip every coastline line to the basemap bbox so open chains terminate on
     the frame edge.
  2. Node the coastline + bbox boundary together and ``polygonize`` -> a set of
     faces that tile the bbox.
  3. Classify each face land/sea via OSM's rule — *water is on the RIGHT of the
     directed coastline*: drop a probe point a hair left/right of every coastline
     segment, find the containing face, and vote. Majority per face wins.
  4. Union the sea faces; islands drop out as holes automatically.

Returns GeoJSON-style polygon coordinate arrays so the renderer needs no
geometry library. Degrades gracefully (returns ``[]``) if Shapely is missing,
there is no coastline, or anything goes wrong — the map simply renders without a
sea fill, exactly as before.
"""
from __future__ import annotations

import math
import sys

try:  # Shapely is optional; without it we simply skip the sea fill.
    from shapely import STRtree
    from shapely.geometry import LineString, MultiLineString, Point, box
    from shapely.ops import polygonize, unary_union
    _HAVE_SHAPELY = True
except ImportError:  # pragma: no cover - environment without shapely
    _HAVE_SHAPELY = False

# Probe offset in degrees (~1 m). Coastline coords are rounded to 6 dp (~0.11 m)
# and real canals are several metres wide, so 1 m reliably lands inside a face.
_PROBE_EPS = 1e-5

Ring = list[list[float]]
Polygon = list[Ring]  # [exterior, *holes]


def _coast_lines(coast_features: list[dict]):
    for f in coast_features:
        g = f["geometry"]
        if g["type"] == "LineString":
            yield g["coordinates"]
        elif g["type"] == "Polygon":  # defensive: a closed coastline ring
            yield g["coordinates"][0]


def build_sea_rings(
    coast_features: list[dict],
    bbox: tuple[float, float, float, float],
) -> list[Polygon]:
    """Reconstruct filled-sea polygons from coastline lines within ``bbox``.

    ``bbox`` is ``(min_lon, min_lat, max_lon, max_lat)``. Returns a list of
    GeoJSON ``Polygon`` coordinate arrays (each ``[exterior, *holes]``), or an
    empty list when there is no sea to draw.
    """
    if not _HAVE_SHAPELY or not coast_features:
        return []
    try:
        return _build(coast_features, bbox)
    except Exception as exc:  # never let sea-fill break a render
        print(f"[sea_fill] skipped (unexpected error: {exc})", file=sys.stderr)
        return []


def _build(coast_features: list[dict], bbox) -> list[Polygon]:
    B = box(*bbox)

    # 1. Clip coastline to the bbox so open chains end on the frame edge.
    clipped: list[LineString] = []
    for coords in _coast_lines(coast_features):
        if len(coords) < 2:
            continue
        inter = LineString(coords).intersection(B)
        if inter.is_empty:
            continue
        if isinstance(inter, LineString):
            clipped.append(inter)
        elif isinstance(inter, MultiLineString):
            clipped.extend(g for g in inter.geoms if isinstance(g, LineString))
    if not clipped:
        return []

    # 2. Node everything and split the box into faces.
    faces = list(polygonize(unary_union(clipped + [B.boundary])))
    if not faces:
        return []

    # 3. Vote each face sea/land from the coastline's right-hand-water rule.
    tree = STRtree(faces)
    votes = [[0, 0] for _ in faces]  # [sea, land]

    def face_of(x: float, y: float):
        p = Point(x, y)
        for i in tree.query(p):  # bbox candidates only; test containment explicitly
            if faces[int(i)].contains(p):
                return int(i)
        return None

    for line in clipped:
        cs = list(line.coords)
        for (ax, ay), (bx, by) in zip(cs, cs[1:]):
            dx, dy = bx - ax, by - ay
            length = math.hypot(dx, dy)
            if length == 0:
                continue
            mx, my = (ax + bx) / 2, (ay + by) / 2
            rx, ry = dy / length, -dx / length  # right-hand normal of a->b (= sea)
            for sign, col in ((1, 0), (-1, 1)):
                i = face_of(mx + rx * _PROBE_EPS * sign, my + ry * _PROBE_EPS * sign)
                if i is not None:
                    votes[i][col] += 1

    sea_faces = [f for f, (s, l) in zip(faces, votes) if s > l]
    if not sea_faces:
        return []

    # 4. Union sea faces (islands remain holes) and emit coordinate arrays.
    sea = unary_union(sea_faces)
    return _to_rings(sea)


def _to_rings(geom) -> list[Polygon]:
    from shapely.geometry import MultiPolygon
    from shapely.geometry import Polygon as ShpPolygon

    polys = geom.geoms if isinstance(geom, MultiPolygon) else [geom]
    out: list[Polygon] = []
    for p in polys:
        if not isinstance(p, ShpPolygon) or p.is_empty:
            continue
        rings = [list(p.exterior.coords)] + [list(r.coords) for r in p.interiors]
        out.append([[[round(x, 6), round(y, 6)] for x, y in ring] for ring in rings])
    return out
