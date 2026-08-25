#!/usr/bin/env python3
"""
Halloween night sheet orchestrator (FAM-002) — the recommended entry point.

Geocodes one address, fetches the streets and the house footprints around it, and
saves both behind an **address cache**. One address + radius = one saved,
timestamped *run* under ``data/runs/halloween/<run_id>/``; nothing is overwritten.

Modes
-----
  standard : check the cache; fetch only on a miss; **no render**.
             (Re-running a known address is a no-op — no network at all.)
  poster   : check the cache; fetch only on a miss; then **always (re)render** the
             sheet from the run's cached data. (default)
  fresh    : ignore the cache; refetch as a **new run** (newer id/date); then render.

Rendering is fully decoupled from fetching — see ``render.py --run latest`` to
(re)render a saved run with zero network.

This product fetches no playgrounds. Its subject is the walk from the front door,
so the only marked point is the address itself.

Usage
-----
    python posters/fam002-halloween-night/make.py --address "Elm St, Decatur, Georgia" \\
        --radius 400 --theme lantern --size A4 --layout ledger \\
        --night "31 October 2026" --title "Elm Street Halloween" --preview

Data © OpenStreetMap contributors (ODbL).
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from posterlab.geo import bbox_around, geocode, overpass
from posterlab.map import (
    BUILDINGS_MAX_RADIUS_M,
    build_query,
    check_buildings_radius,
    elements_to_features,
)
from posterlab.runstore import (
    cache_key,
    latest_run_id,
    make_run_id,
    normalise_text,
    record_run,
    run_dir,
)
from posterlab.themes import resolve_themes

from render import KIND, render_run

SOURCE = "OpenStreetMap via Overpass API"
LICENSE = "ODbL - © OpenStreetMap contributors"

# The fetched box is larger than the framed radius so the sheet's outer bands hold
# real geometry. A square frame projected into a portrait page stretches the short
# axis by up to ~1.41x, so the factor stays above that.
FETCH_RADIUS_FACTOR = 1.5


# --------------------------------------------------------------------------- #
# Run serialization
# --------------------------------------------------------------------------- #

def _write_basemap(dest: Path, features: list[dict], home: dict,
                   bbox: tuple[float, float, float, float], radius_m: int,
                   frame_radius_m: int, layer_counts: dict[str, int]) -> None:
    """The run's single geometry file. It carries ``home`` in its metadata, so the
    renderer needs no second file to know which address the sheet is about."""
    fc = {
        "type": "FeatureCollection",
        "metadata": {
            "home": home,
            "bbox": {"min_lon": bbox[0], "min_lat": bbox[1],
                     "max_lon": bbox[2], "max_lat": bbox[3]},
            "radius_m": radius_m,
            # The circle the sheet actually frames, as asked for. The fetched box
            # is deliberately wider (see FETCH_RADIUS_FACTOR).
            "frame_radius_m": frame_radius_m,
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
# Acquire
# --------------------------------------------------------------------------- #

def acquire(address: str, radius_m: int, *, fetch_radius_m: int | None = None,
            force: bool = False, allow_wide: bool = False) -> tuple[str, bool]:
    """Ensure a run exists for (address, radius).

    Returns ``(run_id, cached)``. On a cache hit (and ``not force``) returns the
    latest run for the query with **no network calls**. Otherwise geocodes once,
    fetches the basemap with house footprints, writes a new timestamped run,
    updates the index, and returns the new id.
    """
    key = cache_key(KIND, [normalise_text(address), int(radius_m)])
    if not force:
        rid = latest_run_id(key)
        if rid and run_dir(rid, KIND).is_dir():
            return rid, True

    if fetch_radius_m is None:
        fetch_radius_m = round(radius_m * FETCH_RADIUS_FACTOR)
    check_buildings_radius(fetch_radius_m, allow_wide)

    print(f"Geocoding: {address}")
    lat, lon, display = geocode(address)
    home = {"lat": lat, "lon": lon, "display_name": display}
    print(f"  home @ {lat:.5f}, {lon:.5f}")

    bbox = bbox_around(lat, lon, fetch_radius_m)
    print(f"Querying Overpass for streets and buildings ({fetch_radius_m} m box, "
          f"framing {radius_m} m) ...")
    features = elements_to_features(overpass(build_query(bbox, buildings=True)))
    layer_counts: dict[str, int] = {}
    for f in features:
        layer = f["properties"]["layer"]
        layer_counts[layer] = layer_counts.get(layer, 0) + 1
    print(f"  {len(features)} features "
          f"({', '.join(f'{k}:{v}' for k, v in sorted(layer_counts.items()))})")
    if not layer_counts.get("buildings"):
        print("  NOTE: no building footprints here. The sheet still renders, but "
              "the streets will be bare — OpenStreetMap coverage varies by town.")

    run_id = make_run_id(address, key, tags=[f"r{int(radius_m)}"])
    dest = run_dir(run_id, KIND)
    dest.mkdir(parents=True, exist_ok=True)
    _write_basemap(dest, features, home, bbox, fetch_radius_m, radius_m, layer_counts)
    _write_manifest(
        dest,
        run_id=run_id,
        kind=KIND,
        created=datetime.now().isoformat(timespec="seconds"),
        cache_key=key,
        address=address,
        home=home,
        frame_radius_m=radius_m,
        fetch_radius_m=fetch_radius_m,
        counts={"basemap_layers": layer_counts},
        source=SOURCE,
        license=LICENSE,
    )
    record_run(key, run_id, kind=KIND, address=address, radius_m=int(radius_m))
    return run_id, False


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Acquire (cached) OSM data for an address and render a "
                    "Halloween night sheet.")
    ap.add_argument("--address", default="Vindögats väg 18C, Tygelsjö, Malmö, Sweden")
    ap.add_argument("--radius", type=int, default=400,
                    help="half-width (m) of the neighbourhood the sheet frames. A "
                         "child walks a few streets; at 400 m a house still prints "
                         "wide enough to see.")
    ap.add_argument("--fetch-radius", type=int, default=None,
                    help=f"half-width (m) of the box actually fetched. Blank = "
                         f"radius x {FETCH_RADIUS_FACTOR}. Capped at "
                         f"{BUILDINGS_MAX_RADIUS_M} m, because building footprints "
                         f"over a wide box are a heavy Overpass query.")
    ap.add_argument("--allow-wide", action="store_true",
                    help="lift the building radius cap for one comparison render")
    ap.add_argument("--mode", default="poster", choices=["standard", "poster", "fresh"],
                    help="standard = data only · poster = data + render · "
                         "fresh = refetch + render")
    # Design
    ap.add_argument("--theme", default="lantern",
                    help="a theme name, 'all', or a comma-separated list "
                         "('lantern,ink')")
    ap.add_argument("--title", default="Our Halloween Night")
    ap.add_argument("--subtitle", default="", help="defaults to the geocoded locality")
    ap.add_argument("--size", default="A4",
                    help="A4 or Letter — this sheet prints at home. Takes a "
                         "comma-separated list ('Letter,A4').")
    ap.add_argument("--layout", default="panel",
                    help="'panel' is the framed map + bordered log; band/sheet/ledger "
                         "bleed the map to the paper edge and push the writing off it; "
                         "'bonus' is the standalone spotting game (no map); 'all' "
                         "renders every one. Takes a comma-separated list too "
                         "('band,bonus' is the pack the listing sells).")
    ap.add_argument("--orientation", default="portrait",
                    choices=["auto", "portrait", "landscape"])
    ap.add_argument("--night", default="",
                    help="the date printed on the sheet, e.g. '31 October 2026'")
    # Output
    ap.add_argument("--out", default=None,
                    help="output dir (default output/halloween/<run-id>)")
    ap.add_argument("--preview", action="store_true", help="also write a PNG preview")
    ap.add_argument("--zip", action="store_true",
                    help="assemble the digital-download ZIP (PDFs + how-to + license)")
    args = ap.parse_args()

    run_id, cached = acquire(
        args.address, args.radius,
        fetch_radius_m=args.fetch_radius,
        force=args.mode == "fresh",
        allow_wide=args.allow_wide,
    )
    dest = run_dir(run_id, KIND)
    print(f"{'Cache hit — using' if cached else 'Saved'} run {run_id}")

    if args.mode == "standard":
        print(f"Data ready in {dest} (mode=standard, no render).")
        return

    themes = resolve_themes(args.theme)
    if len(themes) > 1:
        print(f"Rendering {len(themes)} themes: {', '.join(themes)}")
    print(f"Rendering sheet from run {run_id} ...")
    # The whole selection goes into one render_run call on purpose. Looping the
    # themes here would write one ZIP per theme, each holding a fraction of the
    # pack the buyer paid for.
    render_run(
        dest / "basemap.geojson",
        theme=args.theme, title=args.title, subtitle=args.subtitle,
        size=args.size, layout=args.layout, orientation=args.orientation,
        frame_radius_m=args.radius, night=args.night,
        out_dir=Path(args.out) if args.out else None,
        preview=args.preview, make_zip=args.zip,
    )


if __name__ == "__main__":
    main()
