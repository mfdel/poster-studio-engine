#!/usr/bin/env python3
"""
Halloween night sheet renderer (FAM-002).

Turns one run's basemap geometry + a **theme** (style-as-data) into a
print-at-home A4 / US Letter trick-or-treat sheet. The map shows the streets and
the house footprints around one address, with that address marked. Everything
else on the page is space for a child to write in after the walk.

Five sheets, one engine:

    panel   the framed map with the log in a bordered panel under it (default)
    band    solid title band top, all writing in a footer band
    sheet   map to all four edges, title and fields on scrims
    ledger  map full bleed, writing in a right-hand column
    bonus   no map — the spotting game, the tally and the drawing box

``panel`` is composed here, because it uses the shop's shared page furniture
(border, title band, attribution). The other four bleed the map to the paper edge
and own their whole page, so they are composed by ``layouts.py``; this module
still draws the map body for them.

The rule that must never break
------------------------------
The sheet never says which houses give treats, which houses take part, or which
houses are safe. Nobody can know that before the evening. See ``docs/product.md``.

Usage
-----
    python posters/fam002-halloween-night/render.py --run latest \\
        --theme lantern --size A4 --layout ledger \\
        --night "31 October 2026" --title "Hillcrest Halloween" --preview

``--theme``, ``--size`` and ``--layout`` each take a comma-separated list, so the
whole sold pack comes out of one call — and out of **one** ZIP:

    python posters/fam002-halloween-night/render.py --run latest \\
        --theme lantern,ink --size Letter,A4 --layout band,bonus \\
        --night "31 October 2026" --title "Hillcrest Halloween" --zip

Data © OpenStreetMap contributors (ODbL) — attribution is rendered on every sheet.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from posterlab.chrome import (
    SIZES,
    attribution,
    coords_label,
    page_size,
    render_border,
    resolve_sizes,
    title_block,
)
from posterlab.export import (
    OSM_LICENSE_TEXT,
    build_zip,
    export_pdf,
    export_png,
    write_deliverable_notes,
)
from posterlab.geo import Projector, bbox_around
from posterlab.map import (
    home_only_overlay,
    load_basemap,
    render_map_body,
    resolve_orientation,
    run_id_for_path,
    with_sea,
)
from posterlab.paths import OUTPUT, THEMES
from posterlab.select import expand_selection
from posterlab.svg.primitives import num as _num
from posterlab.text import format_locality, slugify
from posterlab.themes import load_theme, resolve_themes

import panel
from layouts import LAYOUTS as BLEED_LAYOUTS
from layouts import art_dir_for
from layouts import compose as compose_bleed
from layouts import map_box as bleed_map_box


# --------------------------------------------------------------------------- #
# Home glyph
# --------------------------------------------------------------------------- #

def _plain_disc(x: float, y: float, r: float, color: str, page: str) -> str:
    """A dot with no ring.

    Some themes ask for a ``compass`` or ``sun`` home glyph. Those belong to the
    playground map's icon set, which this product does not carry, so the engine
    falls back to a dot ringed in the page colour. Over a street map that ring
    prints as a pale halo. The sheet marks exactly one address, so the dot on its
    own is already unambiguous.
    """
    return (f'<circle cx="{_num(x)}" cy="{_num(y)}" r="{_num(r * 1.15)}" '
            f'fill="{color}"/>')


# The home styles this product has no artwork for. Anything not listed here —
# house, star, heart, pin — is drawn by the engine as usual.
HOME_GLYPHS = {"compass": _plain_disc, "sun": _plain_disc}

# Poster kind — partitions this product's runs (``data/runs/halloween/``) and
# output (``output/halloween/``) from every other poster's. Mirrors poster.toml.
KIND = "halloween"

# Every layout this product can render. ``panel`` is the framed default.
LAYOUTS = ("panel", *BLEED_LAYOUTS)

# The sheet is walked with, not framed, so it prints at home. Anything larger is
# a poster, and this product is not a poster.
DEFAULT_SIZES = "A4"

# How far around home the sheet frames, when the run does not say. A child walks
# a few streets, not a district; at 400 m a house still prints wide enough to see.
DEFAULT_FRAME_RADIUS_M = 400


def _rel(p: Path) -> str:
    """Repo-relative path for logging, or the path itself when it lives elsewhere
    (``--out /tmp/...`` is legal and must not crash a finished render)."""
    try:
        return str(p.resolve().relative_to(OUTPUT.parent))
    except ValueError:
        return str(p)


def resolve_layouts(layout: str) -> list[str]:
    """Expand a ``--layout`` value: a name, ``'all'``, or a comma-separated list.

    ``band,bonus`` is the pair the listing sells, so one call can render the pack.
    """
    return expand_selection(layout, LAYOUTS, groups={"all": list(LAYOUTS)},
                            what="layout")


def zip_name(slug: str, themes: list[str], sizes: list[str], layouts: list[str],
             orient_tag: str) -> str:
    """The digital ZIP's file name, spelling out everything the pack holds.

    The sheets inside are named ``<slug>_<theme>_<size>_<layout>_<orientation>``,
    so the archive names the same axes in the same order and joins the values of
    one axis with ``-``. Naming the whole selection matters more than a short
    name: one ``out_dir`` collects every pack rendered for a run, and a name keyed
    on less than the selection lets a two-sheet pack quietly overwrite an
    eight-sheet one — which is how a buyer ends up with a quarter of the product.
    Portrait is left off, because every sheet this product sells is portrait.
    """
    parts = ["-".join(themes), "-".join(sizes), "-".join(layouts)]
    if orient_tag != "portrait":
        parts.append(orient_tag)
    return f"{slug}_{'_'.join(parts)}_digital.zip"


# --------------------------------------------------------------------------- #
# Composition
# --------------------------------------------------------------------------- #

def compose_panel(size: str, theme: dict, home: dict, basemap: list[dict],
                  bbox: tuple[float, float, float, float], title: str,
                  subtitle: str, *, landscape: bool = False,
                  night: str = "") -> str:
    """The framed sheet: title band, bordered map, log panel, page border.

    Portrait stacks the map over the panel; landscape sets them side by side. The
    panel takes a slightly larger share than a display poster's log would, because
    this page is filled in with a marker rather than read.
    """
    W, H = page_size(size, landscape)
    pal = theme["palette"]
    inset = theme.get("border", {}).get("inset", 7.0)
    cx = W / 2

    if landscape:
        side_margin = max(inset + 3.0, W * 0.04)
        bottom_margin = max(inset + 3.0, W * 0.04)
        top = max(inset + 2.0, W * 0.022) + H * 0.024
    else:
        side_margin = max(inset + 6.0, W * 0.06)
        bottom_margin = max(inset + 7.0, W * 0.072)
        top = max(inset + 4.0, W * 0.05) + H * 0.012
    title_h = max(H * 0.085, W * 0.11) if landscape else H * 0.09

    content_x = side_margin
    content_y = top + title_h
    content_w = W - 2 * side_margin
    content_h = H - content_y - bottom_margin

    map_x, map_y = content_x, content_y
    map_share = 0.56
    if landscape:
        gutter = W * 0.02
        map_w = content_w * map_share - gutter / 2
        map_h = content_h
        log_x = map_x + map_w + gutter
        log_y = content_y
        log_w = content_w - map_w - gutter
        log_h = content_h
    else:
        map_w = content_w
        map_h = content_h * map_share
        log_x = map_x
        log_y = map_y + map_h + H * 0.02
        log_w = content_w
        log_h = (content_y + content_h) - log_y

    proj = Projector.cover(*bbox, map_x, map_y, map_w, map_h)
    frame = (map_x, map_y, map_w, map_h)

    return "".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{_num(W)}mm" height="{_num(H)}mm" '
        f'viewBox="0 0 {_num(W)} {_num(H)}">',
        f'<rect x="0" y="0" width="{_num(W)}" height="{_num(H)}" fill="{pal["page"]}"/>',
        title_block(W, top + title_h * 0.42, title, subtitle, coords_label(home),
                    theme, cx, map_w),
        render_map_body(basemap, proj, frame, theme,
                        overlay=home_only_overlay(home, proj, theme, HOME_GLYPHS)),
        f'<rect x="{_num(map_x)}" y="{_num(map_y)}" width="{_num(map_w)}" height="{_num(map_h)}" '
        f'fill="none" stroke="{pal["border"]}" stroke-width="0.4"/>',
        panel.render_log(log_x, log_y, log_w, log_h, theme, night),
        attribution(frame, theme),
        render_border(W, H, theme),
        "</svg>",
    ])


def compose_svg(size: str, layout: str, theme: dict, home: dict,
                basemap: list[dict], bbox: tuple[float, float, float, float],
                title: str, subtitle: str, *, landscape: bool = False,
                night: str = "") -> str:
    """One sheet, in whichever layout was asked for."""
    if layout == "panel":
        return compose_panel(size, theme, home, basemap, bbox, title, subtitle,
                             landscape=landscape, night=night)

    W, H = page_size(size, landscape)
    art_dir = art_dir_for(theme, THEMES)
    if layout == "bonus":
        return compose_bleed(size, "bonus", theme=theme, map_svg="", title=title,
                             subtitle=subtitle, coords=coords_label(home),
                             night=night, art_dir=art_dir, landscape=landscape)

    mx, my, mw, mh = bleed_map_box(layout, W, H)
    proj = Projector.cover(*bbox, mx, my, mw, mh)
    frame = (mx, my, mw, mh)
    return compose_bleed(
        size, layout, theme=theme,
        map_svg=render_map_body(basemap, proj, frame, theme,
                                overlay=home_only_overlay(home, proj, theme, HOME_GLYPHS)),
        title=title, subtitle=subtitle, coords=coords_label(home), night=night,
        art_dir=art_dir, attribution_svg=attribution(frame, theme),
        landscape=landscape)


# --------------------------------------------------------------------------- #
# Rendering a run
# --------------------------------------------------------------------------- #

def render_run(
    basemap_path: Path,
    *,
    theme: str = "lantern",
    title: str = "Our Halloween Night",
    subtitle: str = "",
    size: str = DEFAULT_SIZES,
    layout: str = "panel",
    orientation: str = "portrait",
    frame_radius_m: float | None = None,
    night: str = "",
    out_dir: Path | None = None,
    preview: bool = False,
    make_zip: bool = False,
) -> list[Path]:
    """Render sheet PDF(s) — and optional PNG previews / digital ZIP — from a
    run's basemap. Pure rendering: reads one GeoJSON file, hits no network.

    ``theme``, ``size`` and ``layout`` each take one name, ``"all"``, or a
    comma-separated list (``"lantern,ink"``, ``"Letter,A4"``, ``"band,bonus"``).
    Every combination is rendered, and ``make_zip`` packs all of them into **one**
    archive — the pack sold as a download is 2 themes x 2 layouts x 2 sizes, and
    it has to come out of a single call to be complete. ``out_dir`` defaults to
    ``output/halloween/<run_id>``. Returns the PDF paths written.
    """
    theme_datas = [load_theme(t) for t in resolve_themes(theme)]
    basemap, meta = load_basemap(basemap_path)
    if not basemap:
        raise SystemExit(f"No basemap geometry in {basemap_path}")
    home = meta["home"]
    basemap = with_sea(basemap, meta)

    subtitle = subtitle or format_locality(home.get("display_name", ""))

    # The sheet's subject is the walk from the front door, so it frames a fixed
    # box around home. The radius is what decides whether a house prints at 2 mm
    # or at 0.5 mm, so it is never derived from what happens to be in the data.
    frame_radius_m = frame_radius_m or meta.get("frame_radius_m") or DEFAULT_FRAME_RADIUS_M
    bbox = bbox_around(home["lat"], home["lon"], frame_radius_m)

    landscape, reason = resolve_orientation(orientation, bbox)
    orient_tag = "landscape" if landscape else "portrait"

    out_dir = out_dir or (OUTPUT / KIND / (run_id_for_path(basemap_path) or slugify(title)))
    slug = slugify(title)

    sizes = resolve_sizes(size)
    layouts = resolve_layouts(layout)

    written: list[Path] = []
    for theme_data in theme_datas:
        for s in sizes:
            for lay in layouts:
                svg = compose_svg(s, lay, theme_data, home, basemap, bbox, title,
                                  subtitle, landscape=landscape, night=night)
                name = f"{slug}_{theme_data['name']}_{s}_{lay}_{orient_tag}"
                pdf = out_dir / f"{name}.pdf"
                export_pdf(svg, pdf)
                written.append(pdf)
                print(f"  wrote {_rel(pdf)}")
                if preview:
                    png = out_dir / f"{name}.png"
                    export_png(svg, png)
                    print(f"  wrote {_rel(png)}")

    n_buildings = sum(1 for f in basemap if f["properties"]["layer"] == "buildings")
    print(f"\nDone — {len(written)} PDF(s) in {out_dir}")
    print(f"Theme: {', '.join(t['label'] for t in theme_datas)} · "
          f"{n_buildings} buildings drawn · frame radius {frame_radius_m:.0f} m")
    if not n_buildings:
        print("  NOTE: no buildings in this box — refetch, or pick an address "
              "with better OpenStreetMap coverage.")
    print(f"Orientation: {orient_tag} ({reason})")

    if make_zip:
        notes = write_deliverable_notes(out_dir, panel.HOWTO_TEXT, OSM_LICENSE_TEXT)
        zip_path = out_dir / zip_name(slug, [t["name"] for t in theme_datas],
                                      sizes, layouts, orient_tag)
        packed = build_zip(zip_path, written + notes)
        # Counted from the archive rather than from the render loop, so the line
        # states what the buyer will actually unzip.
        n_pdf = sum(1 for n in packed if n.lower().endswith(".pdf"))
        print(f"Digital ZIP: {_rel(zip_path)} "
              f"({n_pdf} PDF{'s' if n_pdf != 1 else ''} + {len(packed) - n_pdf} notes)")

    return written


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Render a Halloween night sheet from a saved run + a theme.")
    ap.add_argument("--run", default=None,
                    help="render from a saved run: a run id or 'latest'. Defaults to "
                         "the latest run when no explicit path is given. No network.")
    ap.add_argument("--basemap", default=None,
                    help="explicit basemap path (escape hatch; not for use with --run)")
    ap.add_argument("--theme", default="lantern",
                    help="a theme name, 'all', or a comma-separated list "
                         "('lantern,ink')")
    ap.add_argument("--title", default="Our Halloween Night")
    ap.add_argument("--subtitle", default="", help="defaults to the geocoded locality")
    ap.add_argument("--size", default=DEFAULT_SIZES,
                    help=f"one of {list(SIZES)}, or a comma-separated list "
                         f"('Letter,A4'). The sheet is printed at home, so A4 and "
                         f"Letter are the sizes that matter.")
    ap.add_argument("--layout", default="panel",
                    help="'panel' is the framed map + bordered log; band/sheet/ledger "
                         "bleed the map to the paper edge and push the writing off it; "
                         "'bonus' is the standalone spotting game (no map); 'all' "
                         "renders every one. Takes a comma-separated list too "
                         "('band,bonus' is the pack the listing sells).")
    ap.add_argument("--orientation", default="portrait",
                    choices=["auto", "portrait", "landscape"],
                    help="portrait by default — the bleed layouts' band and column "
                         "fractions are tuned for it")
    ap.add_argument("--frame-radius", type=int, default=None,
                    help=f"half-width (m) of the box framed around home "
                         f"(default: the run's own, else {DEFAULT_FRAME_RADIUS_M})")
    ap.add_argument("--night", default="",
                    help="the date printed on the sheet, e.g. '31 October 2026'")
    ap.add_argument("--out", default=None,
                    help="output dir (default output/halloween/<run-id>)")
    ap.add_argument("--preview", action="store_true", help="also write a PNG preview")
    ap.add_argument("--zip", action="store_true",
                    help="assemble the digital-download ZIP (PDFs + how-to + license)")
    args = ap.parse_args()

    if args.basemap:
        if args.run:
            ap.error("pass either --run or --basemap, not both")
        basemap_path = Path(args.basemap)
    else:
        from posterlab.runstore import resolve_run
        d = resolve_run(args.run or "latest", KIND)
        basemap_path = d / "basemap.geojson"
        print(f"Rendering from run: {d.name}")

    render_run(
        basemap_path,
        theme=args.theme, title=args.title, subtitle=args.subtitle,
        size=args.size, layout=args.layout, orientation=args.orientation,
        frame_radius_m=args.frame_radius, night=args.night,
        out_dir=Path(args.out) if args.out else None,
        preview=args.preview, make_zip=args.zip,
    )


if __name__ == "__main__":
    main()
