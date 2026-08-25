#!/usr/bin/env python3
"""
Map body renderer — the styled street map every map-shaped poster draws.

Turns basemap geometry + a **theme** (style-as-data) into the SVG for one map
rectangle: land -> sea -> green -> water -> coastline -> buildings -> roads.
Visual style lives entirely in ``studio/themes/*.json``; this module is
style-agnostic, so swapping the theme swaps the whole aesthetic.

What a product marks *on top* of the map is the product's own business. Pass it
in as ``overlay`` — an SVG fragment already projected into the same frame. The
playground map passes numbered park markers; the Halloween sheet passes one home
glyph. Neither product owns the streets underneath.

Also here: the two home glyphs every product shares, the basemap loaders, and
the auto-orientation rule, because they are all decisions about the map itself
rather than about one poster.

Data © OpenStreetMap contributors (ODbL) — attribution is rendered on every
poster by ``posterlab.chrome.furniture.attribution``.
"""
from __future__ import annotations

import json
from pathlib import Path

from posterlab.geo import Projector, merc
from posterlab.geo.sea_fill import build_sea_rings
from posterlab.svg import chunk_path_ds, heart_path, path_d, star_path, wavy_path_d
from posterlab.svg.primitives import num as _num

# Draw roads minor-first so arterials sit on top.
ROAD_ORDER = ["path", "service", "residential", "secondary", "primary", "motorway"]

# Auto-orientation: portrait is the default; flip to landscape only when the
# content spread is *significantly* wider than tall. A roughly-square (or tall)
# spread stays portrait, so this threshold is comfortably above 1:1.
LANDSCAPE_ASPECT_RATIO = 1.20


# --------------------------------------------------------------------------- #
# Orientation
# --------------------------------------------------------------------------- #

def content_aspect(bbox: tuple[float, float, float, float]) -> float:
    """Web-Mercator width/height of the framed area.

    Measured in the *same* projected space the map is drawn in — not raw lon/lat
    degrees — so it reflects the true on-page shape of the spread. Longitude
    degrees shrink toward the poles; Mercator already accounts for that, so a
    wide-looking cluster far north isn't mistaken for landscape. >1 = wider than
    tall.
    """
    min_lon, min_lat, max_lon, max_lat = bbox
    x_min, y_min = merc(min_lon, min_lat)
    x_max, y_max = merc(max_lon, max_lat)
    bw, bh = x_max - x_min, y_max - y_min
    return bw / bh if bh else 1.0


def resolve_orientation(orientation: str,
                        bbox: tuple[float, float, float, float]) -> tuple[bool, str]:
    """Decide page orientation. Returns ``(landscape, reason)``.

    ``portrait`` / ``landscape`` force it; ``auto`` picks landscape only when the
    content is at least ``LANDSCAPE_ASPECT_RATIO`` times wider than tall.
    """
    if orientation == "landscape":
        return True, "forced landscape"
    if orientation == "portrait":
        return False, "forced portrait"
    asp = content_aspect(bbox)
    if asp >= LANDSCAPE_ASPECT_RATIO:
        return True, f"auto — spread is {asp:.2f}:1 (≥ {LANDSCAPE_ASPECT_RATIO:.2f}:1 → landscape)"
    return False, f"auto — spread is {asp:.2f}:1 (portrait default)"


# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #

def run_id_for_path(geometry_path: Path) -> str | None:
    """If a geometry file lives in a run dir (``data/runs/<kind>/<id>/...``, or the
    legacy flat ``data/runs/<id>/...``), return that run id so the output folder can
    be named after the run. Returns None for arbitrary paths, so ad-hoc renders fall
    back to the title slug."""
    parent = geometry_path.parent
    ancestors = {p.name for p in list(parent.parents)[:2]}
    return parent.name if "runs" in ancestors else None


def load_basemap(path: Path) -> tuple[list[dict], dict]:
    if not path.exists():
        return [], {}
    d = json.loads(path.read_text(encoding="utf-8"))
    return d["features"], d.get("metadata", {})


def with_sea(basemap: list[dict], meta: dict) -> list[dict]:
    """Append reconstructed filled-sea polygon features (``layer="sea"``).

    OSM ships the ocean only as coastline *lines*; ``sea_fill.build_sea_rings``
    turns them into filled polygons (islands as holes) so coastal water reads as
    water, not land. No-op for inland maps or when the bbox is unknown.
    """
    bbox = meta.get("bbox")
    if not bbox:
        return basemap
    coast = [f for f in basemap if f["properties"]["layer"] == "coastline"]
    rings = build_sea_rings(
        coast, (bbox["min_lon"], bbox["min_lat"], bbox["max_lon"], bbox["max_lat"])
    )
    for poly in rings:
        basemap.append({
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": poly},
            "properties": {"layer": "sea"},
        })
    return basemap


# --------------------------------------------------------------------------- #
# Home glyph — shared, because every product built on this map marks one address
# --------------------------------------------------------------------------- #

def home_marker_svg(x: float, y: float, style: str, color: str, stroke: str, r: float) -> str:
    """A distinct 'home' glyph. Falls back to a ringed dot for unknown styles."""
    if style == "star":
        return (f'<path d="{star_path(x, y, r * 1.4)}" fill="{color}" '
                f'stroke="{stroke}" stroke-width="{_num(r * 0.18)}"/>')
    if style == "heart":
        return (f'<path d="{heart_path(x, y, r * 1.25)}" fill="{color}" '
                f'stroke="{stroke}" stroke-width="{_num(r * 0.18)}"/>')
    if style == "house":
        s = r * 1.3
        body = (f'<rect x="{_num(x - s * 0.7)}" y="{_num(y - s * 0.2)}" '
                f'width="{_num(s * 1.4)}" height="{_num(s * 1.1)}" fill="{color}"/>')
        roof = (f'<path d="M{_num(x - s)} {_num(y - s * 0.2)} L{_num(x)} {_num(y - s * 1.1)} '
                f'L{_num(x + s)} {_num(y - s * 0.2)} Z" fill="{color}"/>')
        return f'<g stroke="{stroke}" stroke-width="{_num(r * 0.16)}" stroke-linejoin="round">{roof}{body}</g>'
    # default: pin — a ringed dot
    return (f'<circle cx="{_num(x)}" cy="{_num(y)}" r="{_num(r * 1.15)}" fill="{color}" '
            f'stroke="{stroke}" stroke-width="{_num(r * 0.35)}"/>')


def home_glyph(x: float, y: float, r: float, theme: dict, extra: dict | None = None) -> str:
    """The theme's home marker, drawn anywhere — map or legend.

    Same dispatch the map body uses, so a legend key can never disagree with the
    glyph actually printed on the map. ``extra`` lets a product add its own home
    styles (the playground map's icon set adds ``compass`` and ``sun``); the four
    built-in styles are available to every product without one.
    """
    mk = theme["markers"]
    pal = theme["palette"]
    style = mk.get("home_style", "pin")
    if extra and mk.get("style") == "icon" and style in extra:
        return extra[style](x, y, r, pal["home_marker"], pal["page"])
    return home_marker_svg(x, y, style, pal["home_marker"], pal["page"], r)


# --------------------------------------------------------------------------- #
# Map body
# --------------------------------------------------------------------------- #

def render_map_body(
    basemap: list[dict],
    proj: Projector,
    frame: tuple[float, float, float, float],
    theme: dict,
    *,
    overlay: str = "",
) -> str:
    """SVG for the map rectangle: land -> green -> water -> roads -> ``overlay``.

    ``overlay`` is the product's own marker layer, already projected with ``proj``.
    It is drawn last and inside the frame's clip group, so a marker near the edge
    is trimmed with the streets instead of escaping the map.
    """
    fx, fy, fw, fh = frame
    pal = theme["palette"]
    weights = theme["road_weights"]
    map_cfg = theme.get("map", {})
    cap = map_cfg.get("linecap", "round")
    # Optional bold outline on land-cover shapes (green/water), theme opt-in via
    # `map.outline` — the "black-outline + pastel fill" illustrated-map look.
    # Absent (the default for all existing themes) reproduces the old bare fill.
    outline = map_cfg.get("outline")
    shape_stroke = (f'stroke="{outline}" stroke-width="{_num(map_cfg.get("outline_weight", 0.8))}" '
                    f'stroke-linejoin="round"') if outline else 'stroke="none"'

    # Optional Woodruff-style hand-drawn wobble on roads + coastline, theme
    # opt-in via `map.hand_drawn` (absent/false = old straight-line behaviour).
    hd_cfg = map_cfg.get("hand_drawn")
    hd_amp = hd_cfg.get("amplitude_mm", 0.35) if isinstance(hd_cfg, dict) else 0.35
    hd_wl = hd_cfg.get("wavelength_mm", 16.0) if isinstance(hd_cfg, dict) else 16.0

    def _feature_coords(f: dict) -> list[list[float]]:
        g = f["geometry"]
        return g["coordinates"] if g["type"] == "LineString" else g["coordinates"][0]

    def _seed_key(coords: list[list[float]]):
        # Stable per feature (endpoints + point count), independent of render
        # order, so the same run wobbles identically on every re-render.
        return (coords[0][0], coords[0][1], coords[-1][0], coords[-1][1], len(coords))

    def _line_d(coords: list[list[float]]) -> str:
        if not hd_cfg:
            return path_d(coords, proj)
        return wavy_path_d(coords, proj, hash(_seed_key(coords)),
                           amplitude_mm=hd_amp, wavelength_mm=hd_wl)

    out: list[str] = []
    clip_id = "mapclip"
    out.append(f'<clipPath id="{clip_id}"><rect x="{_num(fx)}" y="{_num(fy)}" '
               f'width="{_num(fw)}" height="{_num(fh)}"/></clipPath>')
    # Land background.
    out.append(f'<rect x="{_num(fx)}" y="{_num(fy)}" width="{_num(fw)}" height="{_num(fh)}" '
               f'fill="{pal["land"]}"/>')
    out.append(f'<g clip-path="url(#{clip_id})">')

    # Sort basemap by layer for correct stacking.
    seas = [f for f in basemap if f["properties"]["layer"] == "sea"]
    greens = [f for f in basemap if f["properties"]["layer"] == "green"]
    waters = [f for f in basemap if f["properties"]["layer"] == "water"]
    coast = [f for f in basemap if f["properties"]["layer"] == "coastline"]
    roads = [f for f in basemap if f["properties"]["layer"] == "roads"]
    buildings = [f for f in basemap if f["properties"]["layer"] == "buildings"]

    # Sea fill (reconstructed from coastline). Drawn under land detail; islands are
    # holes in the polygon, so fill-rule="evenodd" carves them back out to land.
    for f in seas:
        rings = f["geometry"]["coordinates"]
        d = "".join(path_d(ring, proj, close=True) for ring in rings)
        out.append(f'<path d="{d}" fill="{pal["water"]}" fill-rule="evenodd" '
                   f'{shape_stroke}/>')

    # Green areas (fills). Rings after the first are holes -> evenodd carves them out.
    for f in greens:
        g = f["geometry"]
        if g["type"] == "Polygon":
            d = "".join(path_d(ring, proj, close=True) for ring in g["coordinates"])
            out.append(f'<path d="{d}" fill="{pal["green"]}" fill-rule="evenodd" '
                       f'{shape_stroke}/>')

    # Water: area fills + river lines. Islands are holes in the river polygon.
    for f in waters:
        g = f["geometry"]
        if g["type"] == "Polygon":
            d = "".join(path_d(ring, proj, close=True) for ring in g["coordinates"])
            out.append(f'<path d="{d}" fill="{pal["water"]}" fill-rule="evenodd" '
                       f'{shape_stroke}/>')
        else:  # river/stream line
            out.append(f'<path d="{path_d(g["coordinates"], proj)}" fill="none" '
                       f'stroke="{pal["water"]}" stroke-width="0.6" '
                       f'stroke-linecap="{cap}" stroke-linejoin="round"/>')

    # Coastline.
    cw = map_cfg.get("coastline_weight", 0.6)
    for f in coast:
        coords = _feature_coords(f)
        out.append(f'<path d="{_line_d(coords)}" fill="none" '
                   f'stroke="{pal["coastline"]}" stroke-width="{_num(cw)}" '
                   f'stroke-linecap="{cap}" stroke-linejoin="round"/>')

    # Buildings (opt-in fetch — the Halloween sheet, FAM-002). Drawn over the land
    # cover and *under* the roads, so the street grid still reads as the walking
    # route. A theme with no `buildings` token falls back to the annotation line
    # colour, which is always a quiet mid-tone between land and text.
    if buildings:
        b_fill = pal.get("buildings", pal.get("annotation_line", pal["coastline"]))
        b_edge = pal.get("buildings_edge")
        # A hairline edge is what separates two semi-detached houses at 2 mm.
        edge = (f'stroke="{b_edge}" stroke-width="{_num(map_cfg.get("building_edge_weight", 0.12))}" '
                f'stroke-linejoin="round"') if b_edge else 'stroke="none"'
        out.append(f'<g fill="{b_fill}" fill-rule="evenodd" {edge}>')
        for f in buildings:
            g = f["geometry"]
            if g["type"] != "Polygon":
                continue
            d = "".join(path_d(ring, proj, close=True) for ring in g["coordinates"])
            out.append(f'<path d="{d}"/>')
        out.append("</g>")

    # Roads, minor-first.
    by_class: dict[str, list[dict]] = {}
    for f in roads:
        by_class.setdefault(f["properties"]["kind"], []).append(f)
    for kind in ROAD_ORDER:
        w = weights.get(kind, 0.4)
        color = pal["roads"].get(kind, pal["roads"].get("residential", "#cccccc"))
        segs = by_class.get(kind, [])
        if not segs:
            continue
        ds = [_line_d(_feature_coords(f)) for f in segs]
        out.append(f'<g fill="none" stroke="{color}" stroke-width="{_num(w)}" '
                   f'stroke-linecap="{cap}" stroke-linejoin="round">')
        out.extend(f'<path d="{d}"/>' for d in chunk_path_ds(ds))
        out.append("</g>")

    # Whatever this product marks on the map.
    out.append(overlay)
    out.append("</g>")
    return "".join(out)


def home_only_overlay(home: dict, proj: Projector, theme: dict,
                      extra: dict | None = None) -> str:
    """The overlay for a poster whose only marker is the address itself."""
    mk = theme["markers"]
    x, y = proj(home["lon"], home["lat"])
    r = mk.get("playground_radius", 4.0) * mk.get("home_scale", 1.0)
    return home_glyph(x, y, r, theme, extra)
