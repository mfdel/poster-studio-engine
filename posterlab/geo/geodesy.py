"""Geodesy: distances, bounding boxes, point merging, Web Mercator projection.

Pure maths — no network, no OSM knowledge, no poster knowledge.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

EARTH_R = 6_371_000  # metres
_M_PER_DEG_LAT = 111_320.0  # good enough for framing at city scale


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in metres."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * EARTH_R * math.asin(math.sqrt(a))


def bbox_around(lat: float, lon: float, radius_m: float) -> tuple[float, float, float, float]:
    """A square lon/lat bounding box `radius_m` around a point.

    Returns (min_lon, min_lat, max_lon, max_lat).
    """
    dlat = radius_m / _M_PER_DEG_LAT
    dlon = radius_m / (_M_PER_DEG_LAT * math.cos(math.radians(lat)))
    return (lon - dlon, lat - dlat, lon + dlon, lat + dlat)


def bounds_around(points: list[tuple[float, float]], pad_ratio: float = 0.12,
                  min_pad_m: float = 250) -> tuple[float, float, float, float]:
    """Tight lon/lat bounding box around `points` ((lat, lon) pairs), e.g. home
    + the playgrounds actually being shown — not centred on any single one of
    them. Padded proportionally to their spread so the farthest marker doesn't
    sit flush on the frame edge; `min_pad_m` floors that pad so a tight cluster
    doesn't collapse to a hairline box.

    Returns (min_lon, min_lat, max_lon, max_lat).
    """
    lats = [lat for lat, lon in points]
    lons = [lon for lat, lon in points]
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)
    lat0 = (min_lat + max_lat) / 2
    floor_dlat = min_pad_m / _M_PER_DEG_LAT
    floor_dlon = min_pad_m / (_M_PER_DEG_LAT * math.cos(math.radians(lat0)))
    pad_lat = max((max_lat - min_lat) * pad_ratio, floor_dlat)
    pad_lon = max((max_lon - min_lon) * pad_ratio, floor_dlon)
    return (min_lon - pad_lon, min_lat - pad_lat, max_lon + pad_lon, max_lat + pad_lat)


def merge_nearby(points: list[dict], threshold_m: float = 60) -> list[dict]:
    """Collapse points within `threshold_m` of each other into one.

    OSM often has duplicate/adjacent nodes for the same physical feature (e.g. a
    mapped play area plus a separate equipment node a few metres away). Pairs
    closer than `threshold_m` are unioned into clusters (so a chain of near
    neighbours merges transitively, not just pairwise), and each cluster keeps
    only its point with the smallest `distance_m` (closest to home).

    `points` items must have "lat", "lon", and "distance_m" keys. Order of the
    input is preserved among survivors.
    """
    n = len(points)
    parent = list(range(n))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i: int, j: int) -> None:
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj

    for i in range(n):
        for j in range(i + 1, n):
            if haversine_m(points[i]["lat"], points[i]["lon"],
                           points[j]["lat"], points[j]["lon"]) < threshold_m:
                union(i, j)

    clusters: dict[int, list[int]] = {}
    for i in range(n):
        clusters.setdefault(find(i), []).append(i)

    keep = sorted(min(idxs, key=lambda i: points[i]["distance_m"]) for idxs in clusters.values())
    return [points[i] for i in keep]


# --------------------------------------------------------------------------- #
# Web Mercator projection: lon/lat -> poster points
# --------------------------------------------------------------------------- #

def merc(lon: float, lat: float) -> tuple[float, float]:
    """Web Mercator on the unit sphere (conformal; scale is applied later)."""
    x = math.radians(lon)
    y = math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
    return x, y


@dataclass
class Projector:
    """Maps lon/lat to points inside a poster frame rectangle.

    Built via :meth:`cover`, which expands the shorter axis of the geographic
    box so the map fills the whole frame edge-to-edge *without distortion*
    (Mercator is conformal, so shapes stay true).
    """

    x_min: float
    y_min: float
    x_max: float
    y_max: float
    fx: float  # frame origin x (points)
    fy: float  # frame origin y (points)
    fw: float  # frame width (points)
    fh: float  # frame height (points)

    @classmethod
    def cover(
        cls,
        min_lon: float,
        min_lat: float,
        max_lon: float,
        max_lat: float,
        fx: float,
        fy: float,
        fw: float,
        fh: float,
    ) -> "Projector":
        x_min, y_min = merc(min_lon, min_lat)
        x_max, y_max = merc(max_lon, max_lat)
        bw, bh = x_max - x_min, y_max - y_min
        target = fw / fh
        cur = bw / bh
        if cur < target:  # box too tall -> widen it
            new_bw = bh * target
            cx = (x_min + x_max) / 2
            x_min, x_max = cx - new_bw / 2, cx + new_bw / 2
        else:  # box too wide -> heighten it
            new_bh = bw / target
            cy = (y_min + y_max) / 2
            y_min, y_max = cy - new_bh / 2, cy + new_bh / 2
        return cls(x_min, y_min, x_max, y_max, fx, fy, fw, fh)

    def __call__(self, lon: float, lat: float) -> tuple[float, float]:
        x, y = merc(lon, lat)
        px = self.fx + (x - self.x_min) / (self.x_max - self.x_min) * self.fw
        # SVG y grows downwards; Mercator y grows up -> flip.
        py = self.fy + self.fh - (y - self.y_min) / (self.y_max - self.y_min) * self.fh
        return px, py
