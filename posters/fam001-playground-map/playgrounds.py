#!/usr/bin/env python3
"""
Playground finder (FAM-001 Playground Map generator prototype).

Geocodes an address, pulls every OpenStreetMap `leisure=playground` within a
radius via the Overpass API, saves them (GeoJSON + CSV) with coordinates, and
renders an interactive Leaflet/folium map.

Usage:
    python playgrounds.py --address "Vindögatan, Tygelsjö, Malmö, Sweden" --radius 10000

Low-level / debug tool: this writes the flat ``data/playgrounds.geojson`` +
``.csv`` and does *not* create a cached run. For the normal cached workflow
(playgrounds + basemap saved as a timestamped run) use ``make.py``, which
reuses this module's ``fetch_playgrounds``.

Data © OpenStreetMap contributors (ODbL).
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import folium

from posterlab.geo import geocode, haversine_m, merge_nearby, overpass
from posterlab.paths import DATA, OUTPUT


def fetch_playgrounds(lat: float, lon: float, radius_m: int,
                       merge_threshold_m: float = 60,
                       bbox: tuple[float, float, float, float] | None = None) -> list[dict]:
    """Pull ``leisure=playground`` around ``(lat, lon)``.

    By default queries a circle of ``radius_m``. Pass ``bbox``
    (min_lon, min_lat, max_lon, max_lat) to query a rectangle instead — the
    poster frame is rectangular, so a rectangular fetch is what fills its
    corners (a circular fetch leaves the top/bottom bands empty). ``distance_m``
    is always measured from ``(lat, lon)`` regardless of the fetch shape.
    """
    if bbox is not None:
        min_lon, min_lat, max_lon, max_lat = bbox
        selector = (f'nwr["leisure"="playground"]'
                    f'({min_lat},{min_lon},{max_lat},{max_lon});')
    else:
        selector = f'nwr["leisure"="playground"](around:{radius_m},{lat},{lon});'
    query = f"[out:json][timeout:120];({selector});out center tags;"
    elements = overpass(query)

    playgrounds = []
    for el in elements:
        if el["type"] == "node":
            plat, plon = el.get("lat"), el.get("lon")
        else:  # way / relation -> use computed center
            c = el.get("center", {})
            plat, plon = c.get("lat"), c.get("lon")
        if plat is None or plon is None:
            continue
        tags = el.get("tags", {})
        # Collect any playground equipment tags for the "note the equipment" feature.
        equipment = sorted(
            v if k == "playground" else k.split(":", 1)[1]
            for k, v in tags.items()
            if k == "playground" or k.startswith("playground:")
        )
        playgrounds.append(
            {
                "osm_type": el["type"],
                "osm_id": el["id"],
                "name": tags.get("name", ""),
                "lat": round(plat, 6),
                "lon": round(plon, 6),
                "distance_m": round(haversine_m(lat, lon, plat, plon)),
                "surface": tags.get("surface", ""),
                "access": tags.get("access", ""),
                "min_age": tags.get("min_age", ""),
                "max_age": tags.get("max_age", ""),
                "wheelchair": tags.get("wheelchair", ""),
                "equipment": ";".join(equipment),
                "osm_url": f"https://www.openstreetmap.org/{el['type']}/{el['id']}",
            }
        )
    playgrounds.sort(key=lambda p: p["distance_m"])
    if merge_threshold_m > 0:
        before = len(playgrounds)
        playgrounds = merge_nearby(playgrounds, merge_threshold_m)
        if len(playgrounds) < before:
            print(f"  merged {before - len(playgrounds)} playground(s) within "
                  f"{merge_threshold_m:.0f}m of another")
    return playgrounds


def save_outputs(playgrounds: list[dict], home: dict) -> tuple[Path, Path]:
    DATA.mkdir(exist_ok=True)
    geojson_path = DATA / "playgrounds.geojson"
    csv_path = DATA / "playgrounds.csv"

    features = [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [p["lon"], p["lat"]]},
            "properties": p,
        }
        for p in playgrounds
    ]
    fc = {
        "type": "FeatureCollection",
        "metadata": {
            "home": home,
            "count": len(playgrounds),
            "source": "OpenStreetMap via Overpass API",
            "license": "ODbL - © OpenStreetMap contributors",
        },
        "features": features,
    }
    geojson_path.write_text(json.dumps(fc, ensure_ascii=False, indent=2), encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(playgrounds[0].keys()))
        writer.writeheader()
        writer.writerows(playgrounds)

    return geojson_path, csv_path


def build_map(playgrounds: list[dict], home: dict, radius_m: int) -> Path:
    hlat, hlon = home["lat"], home["lon"]
    fmap = folium.Map(location=[hlat, hlon], zoom_start=12, tiles="CartoDB positron")

    # 10 km search radius.
    folium.Circle(
        location=[hlat, hlon],
        radius=radius_m,
        color="#3186cc",
        weight=1,
        fill=True,
        fill_opacity=0.05,
        popup=f"{radius_m/1000:.0f} km radius",
    ).add_to(fmap)

    # Home marker.
    folium.Marker(
        location=[hlat, hlon],
        tooltip="Home",
        popup=folium.Popup(f"<b>Home</b><br>{home['display_name']}", max_width=280),
        icon=folium.Icon(color="red", icon="home", prefix="fa"),
    ).add_to(fmap)

    # Colour playgrounds by distance ring.
    def color_for(d: float) -> str:
        if d <= 2000:
            return "#1a9850"  # green - walkable
        if d <= 5000:
            return "#fdae61"  # amber - short drive
        return "#d73027"      # red - edge of radius

    for i, p in enumerate(playgrounds, 1):
        label = p["name"] or f"Playground #{i}"
        rows = [f"<b>{label}</b>", f"{p['distance_m']} m from home"]
        if p["equipment"]:
            rows.append(f"Equipment: {p['equipment'].replace(';', ', ')}")
        if p["surface"]:
            rows.append(f"Surface: {p['surface']}")
        if p["wheelchair"]:
            rows.append(f"Wheelchair: {p['wheelchair']}")
        rows.append(f"<a href='{p['osm_url']}' target='_blank'>View on OSM</a>")
        folium.CircleMarker(
            location=[p["lat"], p["lon"]],
            radius=6,
            color=color_for(p["distance_m"]),
            fill=True,
            fill_opacity=0.9,
            tooltip=f"{i}. {label} — {p['distance_m']} m",
            popup=folium.Popup("<br>".join(rows), max_width=280),
        ).add_to(fmap)

    legend = f"""
    <div style="position: fixed; bottom: 24px; left: 24px; z-index: 9999;
         background: white; padding: 10px 14px; border-radius: 8px;
         box-shadow: 0 1px 6px rgba(0,0,0,.3); font: 13px/1.4 sans-serif;">
      <b>{len(playgrounds)} playgrounds</b> within {radius_m/1000:.0f} km<br>
      <span style="color:#1a9850;">●</span> ≤ 2 km (walkable)<br>
      <span style="color:#fdae61;">●</span> 2–5 km<br>
      <span style="color:#d73027;">●</span> 5–{radius_m/1000:.0f} km<br>
      <span style="color:#c00;">⌂</span> Home<br>
      <span style="font-size:11px;color:#666;">© OpenStreetMap contributors</span>
    </div>"""
    fmap.get_root().html.add_child(folium.Element(legend))

    OUTPUT.mkdir(exist_ok=True)
    out = OUTPUT / "playgrounds_map.html"
    fmap.save(str(out))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--address", default="Vindögats väg 18C, Tygelsjö, Malmö, Sweden")
    ap.add_argument("--radius", type=int, default=2000, help="metres")
    ap.add_argument("--merge-threshold", type=float, default=60,
                     help="merge playgrounds within this many metres of each other, "
                          "keeping whichever is closer to home (0 disables)")
    args = ap.parse_args()

    print(f"Geocoding: {args.address}")
    lat, lon, display = geocode(args.address)
    home = {"lat": lat, "lon": lon, "display_name": display}
    print(f"  home @ {lat:.5f}, {lon:.5f}")

    print(f"Querying Overpass for playgrounds within {args.radius/1000:.0f} km ...")
    playgrounds = fetch_playgrounds(lat, lon, args.radius, args.merge_threshold)
    print(f"  found {len(playgrounds)} playgrounds")
    if not playgrounds:
        raise SystemExit("No playgrounds returned.")

    geojson_path, csv_path = save_outputs(playgrounds, home)
    map_path = build_map(playgrounds, home, args.radius)

    nearest = playgrounds[0]
    print("\nSaved:")
    print(f"  {geojson_path}")
    print(f"  {csv_path}")
    print(f"  {map_path}")
    print(f"\nNearest: {nearest['name'] or '(unnamed)'} — {nearest['distance_m']} m")
    print(f"Farthest: {playgrounds[-1]['distance_m']} m")


if __name__ == "__main__":
    main()
