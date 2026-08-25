#!/usr/bin/env python3
"""
Basemap fetcher — OpenStreetMap geometry for a poster bounding box.

Shared by every map-shaped poster product. A gift-worthy poster needs more than
dots: it needs land, water, green and roads under whatever the product marks on
top. This pulls that geometry for a bounding box around a centre point and
returns GeoJSON-shaped features that ``posterlab.map.body`` styles per theme.

One combined Overpass query (mirror fail-over + retry via ``posterlab.geo``), so
we stay a good API citizen. Layers produced:

  * roads      — bucketed by class (motorway / primary / secondary / residential
                 / service / path) so the theme can weight them differently
  * water      — `natural=water` areas + `waterway` lines
  * coastline  — `natural=coastline` (matters for Malmö)
  * green      — parks, grass, recreation_ground, wood, scrub, meadow, ...
  * buildings  — **opt-in**, for the print-at-home neighbourhood sheet
                 (FAM-002). See `BUILDINGS_MAX_RADIUS_M`.

A product's ``make.py`` calls ``build_query`` + ``elements_to_features`` and
writes the result into its own run directory. The CLI below is a low-level debug
tool: it writes a flat ``data/basemap.geojson`` and creates no cached run.

    python -m posterlab.map.overpass --address "Tygelsjö, Malmö, Sweden" --radius 2600
    python -m posterlab.map.overpass --lat 55.5147 --lon 13.0017 --radius 2600
    python -m posterlab.map.overpass --address "Elm St, Decatur, Georgia" --radius 600 --buildings

Data © OpenStreetMap contributors (ODbL).
"""
from __future__ import annotations

import argparse
import json

from posterlab.geo import bbox_around, geocode, overpass
from posterlab.paths import DATA

# Highway tag -> theme road class. Anything unmatched falls back to "residential".
ROAD_CLASS = {
    "motorway": "motorway", "motorway_link": "motorway",
    "trunk": "motorway", "trunk_link": "motorway",
    "primary": "primary", "primary_link": "primary",
    "secondary": "secondary", "secondary_link": "secondary",
    "tertiary": "secondary", "tertiary_link": "secondary",
    "unclassified": "residential", "residential": "residential",
    "living_street": "residential", "road": "residential",
    "service": "service",
    "pedestrian": "path", "footway": "path", "path": "path",
    "cycleway": "path", "track": "path", "steps": "path",
}

# landuse / natural values we treat as "green".
GREEN_LANDUSE = {
    "grass", "recreation_ground", "forest", "meadow", "village_green",
    "cemetery", "farmland", "allotments", "orchard", "greenfield",
}
GREEN_NATURAL = {"wood", "scrub", "grassland", "heath", "wetland"}

HIGHWAY_RE = (
    "^(motorway|trunk|primary|secondary|tertiary|unclassified|residential|"
    "living_street|service|pedestrian|footway|path|cycleway|track|steps)"
)

# Buildings are opt-in because the layer is *heavy*: a suburban 600 m box returns
# a few thousand footprints with full geometry, and the count grows with the area
# — a 3 km box is tens of thousands, which is a rude thing to ask a public
# endpoint for (Guardrail: don't hammer Nominatim/Overpass). Only the
# print-at-home neighbourhood sheet needs houses, and that sheet only works at a
# small radius anyway (a 10 m house prints at 0.45 mm on an A4 2 km map — grey
# mush), so the cap costs the product nothing.
BUILDINGS_MAX_RADIUS_M = 1000


def build_query(bbox: tuple[float, float, float, float],
                buildings: bool = False) -> str:
    """Overpass QL for every basemap layer inside the bbox, with geometry.

    ``buildings`` adds the house-footprint layer. Cap the box with
    ``check_buildings_radius`` before you pass it.
    """
    min_lon, min_lat, max_lon, max_lat = bbox
    b = f"{min_lat},{min_lon},{max_lat},{max_lon}"  # south,west,north,east
    building_q = (f'way["building"]({b});relation["building"]({b});'
                  if buildings else "")
    return (
        "[out:json][timeout:180];"
        "("
        f'way["highway"~"{HIGHWAY_RE}"]({b});'
        f'way["natural"="water"]({b});'
        f'relation["natural"="water"]({b});'
        f'way["waterway"~"river|stream|canal|riverbank"]({b});'
        f'way["natural"="coastline"]({b});'
        f'way["leisure"="park"]({b});'
        f'relation["leisure"="park"]({b});'
        f'way["landuse"]({b});'
        f'way["natural"~"wood|scrub|grassland|heath|wetland"]({b});'
        f"{building_q}"
        ");"
        "out geom;"
    )


def check_buildings_radius(radius_m: float, allow_wide: bool = False) -> None:
    """Refuse a building query over a box wider than ``BUILDINGS_MAX_RADIUS_M``.

    ``allow_wide`` is the deliberate escape hatch for a one-off comparison render.
    """
    if radius_m <= BUILDINGS_MAX_RADIUS_M or allow_wide:
        return
    raise SystemExit(
        f"Building box half-width {radius_m:.0f} m exceeds the "
        f"{BUILDINGS_MAX_RADIUS_M} m cap. A building query over that area is "
        f"heavy for a public Overpass endpoint, and houses print as grey mush "
        f"above ~1 km anyway. Lower --radius, or pass --allow-wide-buildings "
        f"for a one-off comparison."
    )


def classify(tags: dict) -> tuple[str, str, bool] | None:
    """Map OSM tags to (layer, kind, is_area). Returns None to drop the element."""
    if tags.get("natural") == "coastline":
        return ("coastline", "coastline", False)
    if tags.get("natural") == "water":
        return ("water", "water", True)
    if tags.get("waterway"):
        return ("water", "river", False)
    if "highway" in tags:
        return ("roads", ROAD_CLASS.get(tags["highway"], "residential"), False)
    if "building" in tags:
        # Every building value (house, apartments, garage, yes, ...) draws the
        # same. The sheet says a house is *there*; it never says who is home.
        return ("buildings", "building", True)
    if tags.get("leisure") == "park":
        return ("green", "park", True)
    lu = tags.get("landuse")
    if lu in GREEN_LANDUSE:
        return ("green", lu, True)
    nat = tags.get("natural")
    if nat in GREEN_NATURAL:
        return ("green", nat, True)
    return None  # a landuse we don't render (industrial, residential, ...)


def _ring(geometry: list[dict]) -> list[list[float]]:
    """[{lat,lon}, ...] -> [[lon, lat], ...]."""
    return [[round(pt["lon"], 6), round(pt["lat"], 6)] for pt in geometry]


def _feature(coords: list[list[float]], layer: str, kind: str, is_area: bool) -> dict | None:
    if len(coords) < 2:
        return None
    closed = coords[0] == coords[-1]
    if is_area and closed and len(coords) >= 4:
        geom = {"type": "Polygon", "coordinates": [coords]}
    else:
        geom = {"type": "LineString", "coordinates": coords}
    return {
        "type": "Feature",
        "geometry": geom,
        "properties": {"layer": layer, "kind": kind},
    }


def _stitch_rings(fragments: list[list[list[float]]]) -> list[list[list[float]]]:
    """Chain open member ways into closed rings.

    An OSM multipolygon ring is often split across several member ways (the Seine's
    outer ring is 8 of them), and the fragments are neither ordered nor consistently
    wound. Repeatedly join whichever fragment shares an endpoint, flipping it when
    needed, until the ring closes. Fragments that never close are dropped.
    """
    pending = [list(f) for f in fragments if len(f) >= 2]
    rings: list[list[list[float]]] = []
    while pending:
        ring = pending.pop(0)
        joined = True
        while ring[0] != ring[-1] and joined:
            joined = False
            for i, frag in enumerate(pending):
                if frag[0] == ring[-1]:
                    ring.extend(frag[1:])
                elif frag[-1] == ring[-1]:
                    ring.extend(frag[-2::-1])
                elif frag[-1] == ring[0]:
                    ring[:0] = frag[:-1]
                elif frag[0] == ring[0]:
                    ring[:0] = frag[:0:-1]
                else:
                    continue
                pending.pop(i)
                joined = True
                break
        if len(ring) >= 4 and ring[0] == ring[-1]:
            rings.append(ring)
    return rings


def _point_in_ring(pt: list[float], ring: list[list[float]]) -> bool:
    """Ray-casting point-in-polygon (keeps this module free of a geometry dep)."""
    x, y = pt
    inside = False
    for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            inside = not inside
    return inside


def _relation_polygons(el: dict) -> list[list[list[list[float]]]]:
    """Assemble a multipolygon relation into ``[[exterior, *holes], ...]``.

    Members carry an ``outer``/``inner`` role; inner rings are the islands, which
    must become *holes* in their containing outer ring rather than shapes of their
    own — otherwise the Seine's islands render as solid water.
    """
    by_role: dict[str, list[list[list[float]]]] = {"outer": [], "inner": []}
    for m in el.get("members", []):
        if m.get("type") != "way" or not m.get("geometry"):
            continue
        # An empty role means "outer" in practice for water/park relations.
        role = "inner" if m.get("role") == "inner" else "outer"
        by_role[role].append(_ring(m["geometry"]))

    outers = _stitch_rings(by_role["outer"])
    inners = _stitch_rings(by_role["inner"])
    if not outers:
        return []

    polygons = [[o] for o in outers]
    for hole in inners:
        # Attach each hole to the outer ring that contains it (usually the only one).
        target = 0 if len(outers) == 1 else next(
            (i for i, o in enumerate(outers) if _point_in_ring(hole[0], o)), None)
        if target is not None:
            polygons[target].append(hole)
    return polygons


def elements_to_features(elements: list[dict]) -> list[dict]:
    features: list[dict] = []
    for el in elements:
        tags = el.get("tags", {})
        cls = classify(tags)
        if cls is None:
            continue
        layer, kind, is_area = cls
        if el["type"] in ("way",) and el.get("geometry"):
            feat = _feature(_ring(el["geometry"]), layer, kind, is_area)
            if feat:
                features.append(feat)
        elif el["type"] == "relation":
            # `out geom` inlines member geometry. Area relations are multipolygons:
            # stitch the members into rings so holes stay holes. Non-area relations
            # keep the old per-member treatment (they are just lines).
            if is_area:
                for rings in _relation_polygons(el):
                    features.append({
                        "type": "Feature",
                        "geometry": {"type": "Polygon", "coordinates": rings},
                        "properties": {"layer": layer, "kind": kind},
                    })
            else:
                for m in el.get("members", []):
                    if m.get("type") == "way" and m.get("geometry"):
                        feat = _feature(_ring(m["geometry"]), layer, kind, is_area)
                        if feat:
                            features.append(feat)
    return features


def main() -> None:
    ap = argparse.ArgumentParser(description="Fetch OSM basemap geometry for a poster bbox.")
    ap.add_argument("--address", help="geocode this to find the centre")
    ap.add_argument("--lat", type=float, help="centre latitude (skips geocoding)")
    ap.add_argument("--lon", type=float, help="centre longitude (skips geocoding)")
    ap.add_argument("--radius", type=int, default=2600,
                    help="half-width of the fetched box in metres (default 2600)")
    ap.add_argument("--buildings", action="store_true",
                    help=f"also fetch house footprints (max radius "
                         f"{BUILDINGS_MAX_RADIUS_M} m)")
    ap.add_argument("--allow-wide-buildings", action="store_true",
                    help="lift the building radius cap for one comparison render")
    ap.add_argument("--out", default=str(DATA / "basemap.geojson"))
    args = ap.parse_args()

    if args.buildings:
        check_buildings_radius(args.radius, args.allow_wide_buildings)

    if args.lat is not None and args.lon is not None:
        lat, lon, display = args.lat, args.lon, f"{args.lat:.5f}, {args.lon:.5f}"
    elif args.address:
        print(f"Geocoding: {args.address}")
        lat, lon, display = geocode(args.address)
    else:
        ap.error("provide --address or both --lat and --lon")

    bbox = bbox_around(lat, lon, args.radius)
    print(f"  centre @ {lat:.5f}, {lon:.5f}")
    print(f"  bbox    {bbox[1]:.4f},{bbox[0]:.4f} .. {bbox[3]:.4f},{bbox[2]:.4f}")
    print(f"Querying Overpass for basemap geometry ({args.radius} m box) ...")

    elements = overpass(build_query(bbox, buildings=args.buildings))
    features = elements_to_features(elements)

    counts: dict[str, int] = {}
    for f in features:
        counts[f["properties"]["layer"]] = counts.get(f["properties"]["layer"], 0) + 1

    fc = {
        "type": "FeatureCollection",
        "metadata": {
            "home": {"lat": lat, "lon": lon, "display_name": display},
            "bbox": {"min_lon": bbox[0], "min_lat": bbox[1],
                     "max_lon": bbox[2], "max_lat": bbox[3]},
            "radius_m": args.radius,
            "layer_counts": counts,
            "source": "OpenStreetMap via Overpass API",
            "license": "ODbL - © OpenStreetMap contributors",
        },
        "features": features,
    }

    DATA.mkdir(exist_ok=True)
    out = args.out
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(fc, fh, ensure_ascii=False)

    print(f"\nSaved {len(features)} basemap features -> {out}")
    for layer in ("coastline", "water", "green", "roads", "buildings"):
        print(f"  {layer:10s} {counts.get(layer, 0)}")


if __name__ == "__main__":
    main()
