#!/usr/bin/env python3
"""
Playground Map orchestrator (FAM-001) — the recommended entry point.

Couples the two data fetchers (playgrounds + basemap) behind one **address cache**
and owns the three run modes. One address+radius = one saved, timestamped *run*
under ``data/runs/map/<run_id>/`` holding both layers; nothing is overwritten.

Modes
-----
  standard : check the cache; fetch only on a miss; **no render**.
             (Re-running a known address is a no-op — no network at all.)
  poster   : check the cache; fetch only on a miss; then **always (re)render** the
             poster from the run's cached data. (default)
  fresh    : ignore the cache; refetch everything as a **new run** (newer id/date);
             then render.

Rendering is fully decoupled from fetching — see ``render.py --run latest``
to (re)render a saved run's data with zero network.

Usage
-----
    python posters/fam001-playground-map/make.py --address "Tygelsjö, Malmö, Sweden" --radius 2000 \
        --mode poster --theme whimsy --size A2 --variant clean \
        --title "Sofia's Playground Map" --preview

Data © OpenStreetMap contributors (ODbL).
"""
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path

from posterlab.geo import bbox_around, geocode, overpass
from posterlab.runstore import (
    cache_key,
    latest_run_id,
    make_run_id,
    normalise_text,
    record_run,
    run_dir,
)
from posterlab.themes import available_themes

from posterlab.map import (
    BUILDINGS_MAX_RADIUS_M,
    build_query,
    check_buildings_radius,
    elements_to_features,
)

from playgrounds import fetch_playgrounds
from render import KIND, render_run

SOURCE = "OpenStreetMap via Overpass API"
LICENSE = "ODbL - © OpenStreetMap contributors"

# The basemap box is deliberately larger than the playground search radius so the
# rendered frame has margin around the outermost marker (see PRD framing notes).
# It must also fully contain the cover-expanded poster frame: a square content
# spread projected into a portrait/landscape page stretches the short axis by up
# to ~1.41x (A2 / 50x70), so the factor stays above that to keep the poster's
# outer bands filled with real geometry — and real playgrounds — rather than
# empty margin. Playgrounds are fetched over this same box (see `acquire`).
BASEMAP_RADIUS_FACTOR = 1.5


# --------------------------------------------------------------------------- #
# Run serialization (mirrors playgrounds.save_outputs + basemap.main,
# but writes into a run directory instead of the flat data/ files)
# --------------------------------------------------------------------------- #

def _write_playgrounds(dest: Path, playgrounds: list[dict], home: dict,
                       search_radius_m: int) -> None:
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
            # The circle the user asked for: playgrounds within this many metres
            # of home get numbered; farther ones (fetched to fill the frame) are
            # drawn as small unnumbered dots. The renderer reads this as the
            # default numbering gate.
            "search_radius_m": search_radius_m,
            "source": SOURCE,
            "license": LICENSE,
        },
        "features": features,
    }
    (dest / "playgrounds.geojson").write_text(
        json.dumps(fc, ensure_ascii=False, indent=2), encoding="utf-8")

    # A small box can legitimately hold no playground, and there are no field
    # names to write a header from.
    if not playgrounds:
        return
    with (dest / "playgrounds.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(playgrounds[0].keys()))
        writer.writeheader()
        writer.writerows(playgrounds)


def _write_basemap(dest: Path, features: list[dict], home: dict,
                   bbox: tuple[float, float, float, float], radius_m: int,
                   layer_counts: dict[str, int]) -> None:
    fc = {
        "type": "FeatureCollection",
        "metadata": {
            "home": home,
            "bbox": {"min_lon": bbox[0], "min_lat": bbox[1],
                     "max_lon": bbox[2], "max_lat": bbox[3]},
            "radius_m": radius_m,
            "layer_counts": layer_counts,
            "source": SOURCE,
            "license": LICENSE,
        },
        "features": features,
    }
    (dest / "basemap.geojson").write_text(
        json.dumps(fc, ensure_ascii=False), encoding="utf-8")


def _write_manifest(dest: Path, **fields) -> None:
    (dest / "run.json").write_text(
        json.dumps(fields, ensure_ascii=False, indent=2), encoding="utf-8")


# --------------------------------------------------------------------------- #
# Acquire: cache-aware fetch of both layers into a run
# --------------------------------------------------------------------------- #

def acquire(address: str, radius_m: int, merge_threshold_m: float, *,
            basemap_radius_m: int | None = None, force: bool = False,
            buildings: bool = False, allow_wide: bool = False) -> tuple[str, bool]:
    """Ensure a run exists for (address, radius, merge_threshold, buildings).

    Returns ``(run_id, cached)``. On a cache hit (and ``not force``) returns the
    latest run for the query with **no network calls**. Otherwise geocodes once,
    fetches playgrounds + basemap, writes a new timestamped run, updates the index,
    and returns the new id.

    ``buildings`` adds the house-footprint layer and takes its own cache key, so a
    run fetched without houses is never mistaken for one fetched with them. The
    marker is appended only when it is on, which leaves every existing key
    untouched.
    """
    parts: list[object] = [normalise_text(address), int(radius_m),
                           f"{float(merge_threshold_m):g}"]
    if buildings:
        parts.append("buildings")
    key = cache_key(KIND, parts)
    if not force:
        rid = latest_run_id(key)
        if rid and run_dir(rid, KIND).is_dir():
            return rid, True

    if basemap_radius_m is None:
        basemap_radius_m = round(radius_m * BASEMAP_RADIUS_FACTOR)
    if buildings:
        check_buildings_radius(basemap_radius_m, allow_wide)

    print(f"Geocoding: {address}")
    lat, lon, display = geocode(address)
    home = {"lat": lat, "lon": lon, "display_name": display}
    print(f"  home @ {lat:.5f}, {lon:.5f}")

    bbox = bbox_around(lat, lon, basemap_radius_m)
    print(f"Querying Overpass for playgrounds in the {basemap_radius_m} m box "
          f"(numbering the ones within {radius_m / 1000:.1f} km) ...")
    playgrounds = fetch_playgrounds(lat, lon, radius_m, merge_threshold_m, bbox=bbox)
    print(f"  found {len(playgrounds)} playgrounds "
          f"({sum(p['distance_m'] <= radius_m for p in playgrounds)} within "
          f"{radius_m / 1000:.1f} km)")
    if not playgrounds and not buildings:
        raise SystemExit("No playgrounds returned.")
    if not playgrounds:
        print("  none — fine for a buildings run; the sheet does not need one")

    print(f"Querying Overpass for basemap geometry ({basemap_radius_m} m box"
          f"{', with buildings' if buildings else ''}) ...")
    features = elements_to_features(overpass(build_query(bbox, buildings=buildings)))
    layer_counts: dict[str, int] = {}
    for f in features:
        layer = f["properties"]["layer"]
        layer_counts[layer] = layer_counts.get(layer, 0) + 1
    print(f"  {len(features)} basemap features "
          f"({', '.join(f'{k}:{v}' for k, v in sorted(layer_counts.items()))})")

    run_id = make_run_id(address, key, tags=[f"r{int(radius_m)}"])
    dest = run_dir(run_id, KIND)
    dest.mkdir(parents=True, exist_ok=True)
    _write_playgrounds(dest, playgrounds, home, radius_m)
    _write_basemap(dest, features, home, bbox, basemap_radius_m, layer_counts)
    _write_manifest(
        dest,
        run_id=run_id,
        kind=KIND,
        created=datetime.now().isoformat(timespec="seconds"),
        cache_key=key,
        address=address,
        home=home,
        radius_m=radius_m,
        merge_threshold_m=merge_threshold_m,
        basemap_radius_m=basemap_radius_m,
        buildings=buildings,
        counts={"playgrounds": len(playgrounds), "basemap_layers": layer_counts},
        source=SOURCE,
        license=LICENSE,
    )
    record_run(key, run_id, kind=KIND, address=address, radius_m=int(radius_m),
               merge_threshold_m=float(merge_threshold_m))
    return run_id, False


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Acquire (cached) OSM data for an address and render a poster.")
    # Acquisition
    ap.add_argument("--address", default="Vindögats väg 18C, Tygelsjö, Malmö, Sweden")
    ap.add_argument("--radius", type=int, default=2000, help="playground search radius (m)")
    ap.add_argument("--merge-threshold", type=float, default=60,
                    help="merge playgrounds within this many metres (0 disables)")
    ap.add_argument("--basemap-radius", type=int, default=None,
                    help=f"basemap box half-width (m); default radius*{BASEMAP_RADIUS_FACTOR}")
    ap.add_argument("--buildings", action="store_true",
                    help=f"also fetch house footprints (box half-width capped at "
                         f"{BUILDINGS_MAX_RADIUS_M} m)")
    ap.add_argument("--allow-wide-buildings", action="store_true",
                    help="lift the building radius cap for one comparison render")
    ap.add_argument("--mode", choices=["standard", "poster", "fresh"], default="poster",
                    help="standard=data only (cache); poster=data+render; fresh=refetch+render")
    # Render pass-through (ignored in 'standard' mode)
    ap.add_argument("--theme", default="minimal",
                    help="a theme name, or 'all' to render every theme in studio/themes/")
    ap.add_argument("--title", default="Our Playground Map")
    ap.add_argument("--subtitle", default="", help="defaults to the geocoded locality")
    ap.add_argument("--count", type=int, default=15, help="how many nearest playgrounds to number")
    ap.add_argument("--number-radius", type=int, default=None,
                    help="only number playgrounds within this many metres of home; farther "
                         "ones in-frame become small unnumbered dots (default: the search radius)")
    ap.add_argument("--pad", type=float, default=0.12,
                    help="fractional framing padding around home+playgrounds")
    ap.add_argument("--size", default="A2",
                    help="a size, 'bundle' (digital set), 'pod' (the three "
                         "Prodigi-fulfilled cm sizes), or 'all'")
    ap.add_argument("--variant", default="clean",
                    choices=["clean", "annotate", "both"])
    ap.add_argument("--orientation", default="auto", choices=["auto", "portrait", "landscape"],
                    help="page orientation; 'auto' picks landscape when the playgrounds "
                         "span significantly wider than tall, else portrait (the default)")
    ap.add_argument("--frame-radius", type=int, default=None,
                    help="frame a fixed box of this half-width (m) around home instead of "
                         "the playground spread")
    ap.add_argument("--out", default=None, help="poster output dir (default output/map/<run-id>)")
    ap.add_argument("--preview", action="store_true", help="also write a PNG preview")
    ap.add_argument("--zip", action="store_true", help="assemble the digital-download ZIP")
    args = ap.parse_args()

    buildings = args.buildings

    run_id, cached = acquire(
        args.address, args.radius, args.merge_threshold,
        basemap_radius_m=args.basemap_radius, force=(args.mode == "fresh"),
        buildings=buildings, allow_wide=args.allow_wide_buildings,
    )
    dest = run_dir(run_id, KIND)
    print(f"{'Cache hit — using' if cached else 'Saved'} run {run_id}")

    if args.mode == "standard":
        print(f"Data ready in {dest} (mode=standard, no render).")
        return

    themes = available_themes() if args.theme.strip().lower() == "all" else [args.theme]
    if len(themes) > 1:
        print(f"Rendering {len(themes)} themes: {', '.join(themes)}")
    for th in themes:
        print(f"Rendering poster from run {run_id} (theme={th}) ...")
        render_run(
            dest / "playgrounds.geojson", dest / "basemap.geojson",
            theme=th, title=args.title, subtitle=args.subtitle,
            count=args.count, number_radius_m=args.number_radius,
            pad=args.pad, size=args.size, variant=args.variant,
            orientation=args.orientation,
            frame_radius_m=args.frame_radius,
            out_dir=Path(args.out) if args.out else None,
            preview=args.preview, make_zip=args.zip,
        )


if __name__ == "__main__":
    main()
