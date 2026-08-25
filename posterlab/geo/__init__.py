"""Geodesy + OpenStreetMap plumbing.

``geodesy`` is pure maths (no network); ``osm`` talks to Nominatim/Overpass;
``sea_fill`` reconstructs filled water from OSM coastline lines.

Data © OpenStreetMap contributors (ODbL). Attribution is mandatory on every
rendered/printed/sold artifact.
"""
from __future__ import annotations

from posterlab.geo.geodesy import (
    EARTH_R,
    Projector,
    bbox_around,
    bounds_around,
    haversine_m,
    merc,
    merge_nearby,
)
from posterlab.geo.osm import NOMINATIM, OVERPASS_MIRRORS, UA, geocode, overpass

__all__ = [
    "EARTH_R",
    "NOMINATIM",
    "OVERPASS_MIRRORS",
    "Projector",
    "UA",
    "bbox_around",
    "bounds_around",
    "geocode",
    "haversine_m",
    "merc",
    "merge_nearby",
    "overpass",
]
