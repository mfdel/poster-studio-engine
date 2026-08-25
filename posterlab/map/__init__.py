"""Map engine shared by every map-shaped poster product.

``overpass`` fetches OpenStreetMap basemap geometry for a bounding box.
``body`` renders that geometry into one styled map rectangle, plus the home
glyph, the basemap loaders and the auto-orientation rule.

A product supplies the address, the framing and whatever it marks on top; it
does not re-implement the streets. See ``docs/architecture.md``.
"""
from __future__ import annotations

from posterlab.map.body import (
    LANDSCAPE_ASPECT_RATIO,
    ROAD_ORDER,
    content_aspect,
    home_glyph,
    home_marker_svg,
    home_only_overlay,
    load_basemap,
    render_map_body,
    resolve_orientation,
    run_id_for_path,
    with_sea,
)
from posterlab.map.overpass import (
    BUILDINGS_MAX_RADIUS_M,
    build_query,
    check_buildings_radius,
    classify,
    elements_to_features,
)

__all__ = [
    "BUILDINGS_MAX_RADIUS_M",
    "LANDSCAPE_ASPECT_RATIO",
    "ROAD_ORDER",
    "build_query",
    "check_buildings_radius",
    "classify",
    "content_aspect",
    "elements_to_features",
    "home_glyph",
    "home_marker_svg",
    "home_only_overlay",
    "load_basemap",
    "render_map_body",
    "resolve_orientation",
    "run_id_for_path",
    "with_sea",
]
