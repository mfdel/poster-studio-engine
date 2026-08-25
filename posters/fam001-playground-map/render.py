#!/usr/bin/env python3
"""
Poster renderer (FAM-001 Playground Map — milestones M1 / M2).

Turns playground points + basemap geometry + a **theme** (style-as-data) into a
composed, print-ready poster. Visual style lives entirely in
``studio/themes/*.json``; this module is style-agnostic — swapping the theme swaps
the whole aesthetic. Page furniture (border, title band, coordinates line,
attribution), print sizes and export come from ``posterlab``, shared with every
other poster product.

Approach (PRD §5.2, SVG-first, vector = resolution-independent):
    geometry -> Web Mercator projection into the poster frame
             -> styled SVG layers (land/water/green/coastline/roads/markers)
             -> full poster composition (title, markers, furniture, attribution)
             -> export to PDF (and optional PNG preview) at exact print size.

Two variants (PRD §5.3):
    clean     — gallery-clean framable poster.
    annotate  — adds the "adventure log": numbered park list, rating legend,
                blank note lines, and photo-corner spots.

Usage (M1 — one clean poster):
    python posters/fam001-playground-map/render.py --theme whimsy --size A2 \
        --variant clean --title "Sofia's Playground Map" --preview

Usage (M2 — both variants, full size bundle, zipped digital deliverable):
    python posters/fam001-playground-map/render.py --theme whimsy --size all \
        --variant both --title "Sofia's Playground Map" --zip

Orientation (PRD §5.5): portrait by default; ``--orientation auto`` flips to
landscape when the playgrounds+home spread is significantly wider than tall.
``--orientation portrait|landscape`` forces it.

Data © OpenStreetMap contributors (ODbL) — attribution is rendered on every poster.
"""
from __future__ import annotations

import argparse
import json
import math
from html import escape
from pathlib import Path

from posterlab.chrome import (
    POD_SIZES,
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
from posterlab.geo import Projector, bbox_around, bounds_around
from posterlab.map import (
    home_glyph as _home_glyph,
)
from posterlab.map import (
    home_marker_svg,
    load_basemap,
    render_map_body,
    resolve_orientation,
    run_id_for_path,
    with_sea,
)
from posterlab.paths import OUTPUT
from posterlab.svg import star_path
from posterlab.svg.primitives import num as _num
from posterlab.text import format_locality, slugify
from posterlab.themes import load_theme

from icons import HOME_EXTRA, render_icon_markers


def home_glyph(x: float, y: float, r: float, theme: dict) -> str:
    """The theme's home marker, with this product's icon home styles wired in."""
    return _home_glyph(x, y, r, theme, HOME_EXTRA)

# Poster kind — partitions this product's runs (``data/runs/map/``) and output
# (``output/map/``) from every other poster's. Mirrors ``poster.toml``.
KIND = "map"

HERE = Path(__file__).resolve().parent

# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #

def _rel(p: Path) -> str:
    """Repo-relative path for logging, or the path itself when it lives elsewhere
    (``--out /tmp/...`` is legal and must not crash a finished render)."""
    try:
        return str(p.resolve().relative_to(OUTPUT.parent))
    except ValueError:
        return str(p)


def load_playgrounds(path: Path) -> tuple[dict, list[dict], dict]:
    d = json.loads(path.read_text(encoding="utf-8"))
    meta = d.get("metadata", {})
    home = meta["home"]
    pts = [f["properties"] for f in d["features"]]
    return home, pts, meta


# --------------------------------------------------------------------------- #
# Playground-specific markers
# --------------------------------------------------------------------------- #

# --------------------------------------------------------------------------- #
# Map body
# --------------------------------------------------------------------------- #

def render_secondary_markers(secondary: list[dict], proj: Projector, theme: dict) -> str:
    """Small, unnumbered dots for playgrounds that are in-frame but beyond the
    numbering radius. They fill the poster's outer bands (so it no longer reads
    as a circle of numbered pins in an empty rectangle) while staying visually
    subordinate to the numbered, curated list. Clipped to the map frame by the
    caller's clip group. Theme override: ``markers.secondary_scale``.
    """
    if not secondary:
        return ""
    mk = theme["markers"]
    pal = theme["palette"]
    r = mk.get("playground_radius", 4.0) * mk.get("secondary_scale", 0.42)
    fill = pal["playground_marker"]
    stroke = pal.get("page", "#ffffff")
    out = []
    for p in secondary:
        x, y = proj(p["lon"], p["lat"])
        out.append(f'<circle cx="{_num(x)}" cy="{_num(y)}" r="{_num(r)}" '
                   f'fill="{fill}" fill-opacity="0.9" stroke="{stroke}" '
                   f'stroke-width="{_num(max(0.2, r * 0.28))}"/>')
    return "".join(out)


def render_markers(numbered: list[dict], secondary: list[dict], home: dict,
                   proj: Projector, theme: dict) -> str:
    """Everything this product marks on the map: beyond-radius dots, then the
    numbered playgrounds, then home. Handed to ``posterlab.map.render_map_body``
    as its overlay, so the streets underneath stay product-agnostic."""
    pal = theme["palette"]
    mk = theme["markers"]
    out: list[str] = []

    # Beyond-radius playgrounds first, as small dots, so the numbered, curated
    # markers always draw on top of them.
    out.append(render_secondary_markers(secondary, proj, theme))

    if mk.get("style") == "icon":
        out.append(render_icon_markers(numbered, home, proj, theme, home_marker_svg))
        return "".join(out)

    r = mk["playground_radius"]
    for i, p in enumerate(numbered, 1):
        x, y = proj(p["lon"], p["lat"])
        out.append(f'<circle cx="{_num(x)}" cy="{_num(y)}" r="{_num(r)}" '
                   f'fill="{pal["playground_marker"]}" stroke="{mk["playground_stroke"]}" '
                   f'stroke-width="{_num(mk["playground_stroke_w"])}"/>')
        out.append(f'<text x="{_num(x)}" y="{_num(y + r * 0.35)}" text-anchor="middle" '
                   f'font-family="{escape(theme["type"]["label_font"])}" '
                   f'font-size="{_num(r * 1.05)}" font-weight="700" '
                   f'fill="{pal["playground_marker_text"]}">{i}</text>')
    hx, hy = proj(home["lon"], home["lat"])
    out.append(home_marker_svg(hx, hy, mk.get("home_style", "pin"),
                               pal["home_marker"], pal["page"], r * mk.get("home_scale", 1.0)))
    return "".join(out)


def select_playgrounds(pts: list[dict], count: int) -> list[dict]:
    """Nearest `count` playgrounds to home, by distance.

    The display bbox is derived from this selection (via `bounds_around`), not
    the other way around — so the frame fits what's actually shown instead of
    centering on home and hoping a fixed span happens to cover it.
    """
    return sorted(pts, key=lambda p: p.get("distance_m", 0))[:count]


def compose_svg(
    size: str,
    variant: str,
    theme: dict,
    home: dict,
    numbered: list[dict],
    secondary: list[dict],
    basemap: list[dict],
    bbox: tuple[float, float, float, float],
    title: str,
    subtitle: str,
    *,
    landscape: bool = False,
) -> str:
    """Full poster SVG for one size + variant, portrait or landscape.

    ``landscape`` swaps the page's width/height; everything downstream is sized
    proportionally, so the layout follows. The annotate variant stacks the map
    over the adventure log in portrait, and sets them side-by-side in landscape.
    """
    W, H = page_size(size, landscape)
    pal = theme["palette"]
    inset = theme.get("border", {}).get("inset", 7.0)
    cx = W / 2

    # Margins are set per-orientation. Landscape's sides/bottom were already right,
    # so only its top grows. Portrait gets roomier sides (restored to the earlier,
    # airier value), a larger bottom (though still tighter than the original), and
    # more breathing room above the title.
    if landscape:
        side_margin = max(inset + 3.0, W * 0.04)
        bottom_margin = max(inset + 3.0, W * 0.04)
        top = max(inset + 2.0, W * 0.022) + H * 0.024
    else:
        side_margin = max(inset + 6.0, W * 0.06)
        bottom_margin = max(inset + 7.0, W * 0.072)
        top = max(inset + 4.0, W * 0.05) + H * 0.012
    # Title/subtitle band, sized off the page *width*. Its height scales with H —
    # the short side in landscape, which would leave no room and let the subtitle
    # collide with the map — so floor it to a width-derived height when landscape
    # (portrait, where H > W, is unaffected). Kept compact so the title doesn't
    # eat the page, especially in landscape.
    title_h = max(H * 0.085, W * 0.11) if landscape else H * 0.09

    # Drawable content area sits between the title band and the bottom margin.
    content_x = side_margin
    content_y = top + title_h
    content_w = W - 2 * side_margin
    content_h = H - content_y - bottom_margin

    # Map frame — clean fills the whole content area; annotate leaves room for the
    # adventure log (below in portrait, beside in landscape).
    map_x, map_y = content_x, content_y
    log_x = log_y = log_w = log_h = 0.0
    if variant == "annotate":
        map_share = 0.60
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
    else:
        map_w = content_w
        map_h = content_h

    proj = Projector.cover(*bbox, map_x, map_y, map_w, map_h)

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{_num(W)}mm" height="{_num(H)}mm" '
        f'viewBox="0 0 {_num(W)} {_num(H)}">',
        f'<rect x="0" y="0" width="{_num(W)}" height="{_num(H)}" fill="{pal["page"]}"/>',
        title_block(W, top + title_h * 0.42, title, subtitle, coords_label(home),
                    theme, cx, map_w),
        render_map_body(basemap, proj, (map_x, map_y, map_w, map_h), theme,
                        overlay=render_markers(numbered, secondary, home, proj, theme)),
        f'<rect x="{_num(map_x)}" y="{_num(map_y)}" width="{_num(map_w)}" height="{_num(map_h)}" '
        f'fill="none" stroke="{pal["border"]}" stroke-width="0.4"/>',
    ]

    if variant == "annotate":
        parts.append(render_annotation_log(
            log_x, log_y, log_w, log_h, numbered, theme))

    # OSM/ODbL credit lives inside the map's bottom-right corner — small and faint.
    parts.append(attribution((map_x, map_y, map_w, map_h), theme))
    parts.append(render_border(W, H, theme))
    parts.append("</svg>")
    return "".join(parts)


# --------------------------------------------------------------------------- #
# Annotate-me furniture (M2): the "adventure log"
# --------------------------------------------------------------------------- #

def _outline_star(cx: float, cy: float, r: float, color: str, w: float = 0.3) -> str:
    return (f'<path d="{star_path(cx, cy, r)}" fill="none" stroke="{color}" '
            f'stroke-width="{_num(w)}" stroke-linejoin="round"/>')


def _star_row(x: float, y: float, r: float, gap: float, n: int, color: str) -> str:
    return "".join(_outline_star(x + i * (2 * r + gap) + r, y, r, color, w=r * 0.14)
                   for i in range(n))


def _note_line(x1: float, x2: float, y: float, color: str) -> str:
    return (f'<line x1="{_num(x1)}" y1="{_num(y)}" x2="{_num(x2)}" y2="{_num(y)}" '
            f'stroke="{color}" stroke-width="0.3"/>')


def _truncate(s: str, n: int) -> str:
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def _photo_corners(x: float, y: float, s: float, color: str) -> str:
    L = s * 0.24
    seg = (
        f"M{_num(x)} {_num(y + L)} L{_num(x)} {_num(y)} L{_num(x + L)} {_num(y)}"
        f"M{_num(x + s - L)} {_num(y)} L{_num(x + s)} {_num(y)} L{_num(x + s)} {_num(y + L)}"
        f"M{_num(x)} {_num(y + s - L)} L{_num(x)} {_num(y + s)} L{_num(x + L)} {_num(y + s)}"
        f"M{_num(x + s - L)} {_num(y + s)} L{_num(x + s)} {_num(y + s)} "
        f"L{_num(x + s)} {_num(y + s - L)}"
    )
    return (f'<path d="{seg}" fill="none" stroke="{color}" stroke-width="0.5" '
            f'stroke-linecap="round"/>')


def render_annotation_log(x: float, y: float, w: float, h: float,
                          numbered: list[dict], theme: dict) -> str:
    """The co-creation panel: heading + rating key + numbered list (name, stars,
    note line) + a strip of photo-corner spots. Numbers match the map markers."""
    if not numbered:
        return ""
    pal = theme["palette"]
    t = theme["type"]
    out: list[str] = []

    out.append(f'<rect x="{_num(x)}" y="{_num(y)}" width="{_num(w)}" height="{_num(h)}" '
               f'fill="{pal["annotation_box"]}" stroke="{pal["annotation_line"]}" '
               f'stroke-width="0.4"/>')

    pad = w * 0.028
    ix, iw = x + pad, w - 2 * pad
    photo_h = h * 0.26
    star_r = w * 0.011

    # --- Heading + rating key (content-driven height, no overlap) -------------
    head_size = w * 0.026
    heading_y = y + pad + head_size
    heading = "Our Playground Adventures"
    if t.get("subtitle_uppercase"):
        heading = heading.upper()
    out.append(f'<text x="{_num(ix)}" y="{_num(heading_y)}" '
               f'font-family="{escape(t["title_font"])}" font-size="{_num(head_size)}" '
               f'font-weight="{t.get("title_weight", "700")}" fill="{pal["text"]}">'
               f'{escape(heading)}</text>')
    key_size = w * 0.015
    key_y = heading_y + key_size * 1.7
    out.append(f'<text x="{_num(ix)}" y="{_num(key_y)}" '
               f'font-family="{escape(t["body_font"])}" font-size="{_num(key_size)}" '
               f'fill="{pal["muted"]}">Colour a star for every visit — how much did we love it?</text>')
    out.append(_note_line(ix, ix + iw, key_y + pad * 0.5, pal["annotation_line"]))
    list_top = key_y + pad * 1.1
    list_h = (y + h - photo_h) - list_top - pad

    # --- Numbered list --------------------------------------------------------
    # Two columns when the panel is wide (portrait, log under the map); a single
    # column when it's a tall side-panel (landscape) so rows stay readable.
    n = len(numbered)
    tall = h > w * 1.3
    cols = 1 if (tall or n <= 6) else 2
    rows = math.ceil(n / cols)
    col_w = iw / cols
    row_h = list_h / rows
    name_size = min(row_h * 0.30, w * 0.022)
    badge_r = min(row_h * 0.16, w * 0.017)

    for j, p in enumerate(numbered):
        col, row = divmod(j, rows)
        cx0 = ix + col * col_w
        cy0 = list_top + row * row_h
        mid = cy0 + row_h * 0.38
        # number badge
        bx = cx0 + badge_r + 1
        out.append(f'<circle cx="{_num(bx)}" cy="{_num(mid)}" r="{_num(badge_r)}" '
                   f'fill="{pal["playground_marker"]}"/>')
        out.append(f'<text x="{_num(bx)}" y="{_num(mid + badge_r * 0.36)}" '
                   f'text-anchor="middle" font-family="{escape(t["label_font"])}" '
                   f'font-size="{_num(badge_r * 1.05)}" font-weight="700" '
                   f'fill="{pal["playground_marker_text"]}">{j + 1}</text>')
        # name + distance
        tx = bx + badge_r + 2
        name = p.get("name") or f"Playground {j + 1}"
        dist = p.get("distance_m")
        dist_txt = f"{dist/1000:.1f} km" if dist and dist >= 1000 else (f"{dist} m" if dist else "")
        max_chars = int((col_w - (tx - cx0) - col_w * 0.16) / (name_size * 0.55))
        out.append(f'<text x="{_num(tx)}" y="{_num(mid + name_size * 0.35)}" '
                   f'font-family="{escape(t["label_font"])}" font-size="{_num(name_size)}" '
                   f'fill="{pal["text"]}">{escape(_truncate(name, max(6, max_chars)))}</text>')
        if dist_txt:
            out.append(f'<text x="{_num(cx0 + col_w - col_w * 0.03)}" '
                       f'y="{_num(mid + name_size * 0.35)}" text-anchor="end" '
                       f'font-family="{escape(t["body_font"])}" '
                       f'font-size="{_num(name_size * 0.8)}" fill="{pal["muted"]}">'
                       f'{escape(dist_txt)}</text>')
        # star rating + note line on the second line of the cell
        sy = cy0 + row_h * 0.74
        out.append(_star_row(tx, sy, star_r, star_r * 0.7, 5, pal["muted"]))
        stars_w = 5 * (2 * star_r + star_r * 0.7)
        out.append(_note_line(tx + stars_w + 2, cx0 + col_w - col_w * 0.03, sy + star_r,
                              pal["annotation_line"]))

    # --- Photo-corner strip ---------------------------------------------------
    strip_y = y + h - photo_h
    out.append(_note_line(ix, ix + iw, strip_y, pal["annotation_line"]))
    label_size = w * 0.016
    out.append(f'<text x="{_num(ix)}" y="{_num(strip_y + label_size * 1.6)}" '
               f'font-family="{escape(t["label_font"])}" font-size="{_num(label_size)}" '
               f'font-weight="700" fill="{pal["text"]}">Stick your favourite photos here</text>')
    n_photos = 4
    box_top = strip_y + label_size * 2.4
    box_s = min((photo_h - label_size * 3.2), (iw - (n_photos - 1) * pad) / n_photos)
    gap = (iw - n_photos * box_s) / (n_photos - 1)
    for k in range(n_photos):
        px = ix + k * (box_s + gap)
        out.append(_photo_corners(px, box_top, box_s, pal["muted"]))

    return "".join(out)


# --------------------------------------------------------------------------- #
# Digital deliverable: how-to + license + ZIP (M2)
# --------------------------------------------------------------------------- #

HOWTO_TEXT = """HOW TO PRINT YOUR PLAYGROUND MAP
================================

Thank you! This is a DIGITAL download — no physical item was shipped. You print
it yourself (home printer) or send a file to a local print shop.

What's in this ZIP
------------------
- Print-ready PDFs in several standard sizes and shapes.
- Two versions of each:
    *_clean.pdf     — a clean poster, ready to frame.
    *_annotate.pdf  — the same map with a numbered list, star ratings, note
                      lines and photo-corner spots to fill in together.

Printing tips
-------------
1. Pick the size that matches your frame or paper (A4/A3/A2 metric, US Letter,
   18x24 in, or 50x70 cm).
2. Print at 100% / "Actual size" — do NOT let the printer "fit" or "scale to
   page", or the margins and framing will shift.
3. Matte or lightly textured paper around 200 gsm looks best; heavier paper
   holds up to markers on the annotate version.
4. Colours vary between screens, printers and papers — the printed result will
   look a little different from your screen. That's normal.

Enjoy the ritual — choose a park, go, rate it, draw, and stick in a photo.

Map data (c) OpenStreetMap contributors (ODbL). See LICENSE-ATTRIBUTION.txt.
"""




# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def render_run(
    playgrounds_path: Path,
    basemap_path: Path,
    *,
    theme: str = "minimal",
    title: str = "Our Playground Map",
    subtitle: str = "",
    count: int = 12,
    number_radius_m: float | None = None,
    pad: float = 0.12,
    size: str = "A2",
    variant: str = "clean",
    orientation: str = "auto",
    frame_radius_m: float | None = None,
    out_dir: Path | None = None,
    preview: bool = False,
    make_zip: bool = False,
) -> list[Path]:
    """Render poster PDF(s) — and optional PNG previews / digital ZIP — from a
    run's geometry files. Pure rendering: reads two GeoJSON files, hits no network.

    `theme` is a theme name or path (loaded here). `out_dir` defaults to
    ``output/map/<run_id>`` when the geometry comes from a saved run, else
    ``output/map/<title-slug>``. Returns the PDF paths written.
    """
    theme_data = load_theme(theme)
    home, pts, pg_meta = load_playgrounds(playgrounds_path)
    basemap, basemap_meta = load_basemap(basemap_path)
    basemap = with_sea(basemap, basemap_meta)

    subtitle = subtitle or format_locality(home.get("display_name", ""))

    # Numbering gate: only playgrounds within `number_radius_m` of home are
    # numbered (nearest `count` of them). Everything else that falls inside the
    # frame is drawn as a small unnumbered dot. Falls back to the search radius
    # recorded at fetch time; if neither is known, number the nearest `count`
    # anywhere (legacy behaviour) with no secondary dots.
    if number_radius_m is None:
        number_radius_m = pg_meta.get("search_radius_m")
    if number_radius_m is not None:
        within = [p for p in pts if p.get("distance_m", 0) <= number_radius_m]
    else:
        within = pts
    numbered = select_playgrounds(within, count)
    numbered_keys = {(p.get("osm_type"), p.get("osm_id")) for p in numbered}
    secondary = [p for p in pts if (p.get("osm_type"), p.get("osm_id")) not in numbered_keys]

    # Frame the radius neighbourhood (home + everything within the numbering
    # radius), not just the numbered few — so a tight `count` in a dense city
    # doesn't zoom past the surrounding parks. The secondary dots then populate
    # the bands that `Projector.cover` adds to reach the page aspect.
    frame_src = within or numbered or pts
    points = [(home["lat"], home["lon"])] + [(p["lat"], p["lon"]) for p in frame_src]
    bbox = bounds_around(points, pad_ratio=pad)

    if frame_radius_m:
        bbox = bbox_around(home["lat"], home["lon"], frame_radius_m)

    landscape, reason = resolve_orientation(orientation, bbox)
    orient_tag = "landscape" if landscape else "portrait"

    out_dir = out_dir or (OUTPUT / KIND / (run_id_for_path(playgrounds_path) or slugify(title)))
    slug = slugify(title)

    sizes = resolve_sizes(size)
    variants = ["clean", "annotate"] if variant == "both" else [variant]

    written: list[Path] = []
    for s in sizes:
        for v in variants:
            svg = compose_svg(s, v, theme_data, home, numbered, secondary, basemap, bbox,
                              title, subtitle, landscape=landscape)
            name = f"{slug}_{theme_data['name']}_{s}_{v}_{orient_tag}"
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
    print(f"Theme: {theme_data['label']} · numbered {len(numbered)} playgrounds"
          f"{f' within {number_radius_m:.0f} m' if number_radius_m is not None else ''}"
          f" · {len(secondary)} shown as small dots"
          + (f" · {n_buildings} buildings" if n_buildings else ""))
    print(f"Orientation: {orient_tag} ({reason})")

    if make_zip:
        notes = write_deliverable_notes(out_dir, HOWTO_TEXT, OSM_LICENSE_TEXT)
        zip_path = out_dir / f"{slug}_{theme_data['name']}_digital.zip"
        build_zip(zip_path, written + notes)
        print(f"Digital ZIP: {_rel(zip_path)} "
              f"({len(written)} PDFs + {len(notes)} notes)")

    return written


def main() -> None:
    ap = argparse.ArgumentParser(description="Render a playground poster from geometry + a theme.")
    ap.add_argument("--run", default=None,
                    help="render from a saved run: a run id or 'latest'. Defaults to "
                         "the latest run when no explicit paths are given. No network.")
    ap.add_argument("--playgrounds", default=None,
                    help="explicit geometry path (escape hatch; not for use with --run)")
    ap.add_argument("--basemap", default=None,
                    help="explicit basemap path (escape hatch; not for use with --run)")
    ap.add_argument("--theme", default="minimal")
    ap.add_argument("--title", default="Our Playground Map")
    ap.add_argument("--subtitle", default="", help="defaults to the geocoded locality")
    ap.add_argument("--count", type=int, default=12, help="how many nearest playgrounds to number")
    ap.add_argument("--number-radius", type=int, default=None,
                    help="only number playgrounds within this many metres of home; farther "
                         "ones in-frame become small unnumbered dots (default: the run's search radius)")
    ap.add_argument("--pad", type=float, default=0.12,
                    help="fractional padding around home+playgrounds when framing (0.12 = 12%%)")
    ap.add_argument("--size", default="A2",
                    help=f"one of {list(SIZES)}, 'bundle' (digital set), "
                         f"'pod' ({POD_SIZES} — the Prodigi-fulfilled sizes), or 'all'")
    ap.add_argument("--variant", default="clean",
                    choices=["clean", "annotate", "both"])
    ap.add_argument("--orientation", default="auto", choices=["auto", "portrait", "landscape"],
                    help="page orientation; 'auto' picks landscape when the playgrounds "
                         "span significantly wider than tall, else portrait (the default)")
    ap.add_argument("--frame-radius", type=int, default=None,
                    help="frame a fixed box of this half-width (m) around home instead "
                         "of the playground spread")
    ap.add_argument("--out", default=None, help="output dir (default output/map/<run-id>)")
    ap.add_argument("--preview", action="store_true", help="also write a PNG preview")
    ap.add_argument("--zip", action="store_true",
                    help="assemble the digital-download ZIP (PDFs + how-to + license)")
    args = ap.parse_args()

    if args.playgrounds or args.basemap:
        if args.run:
            ap.error("pass either --run or --playgrounds/--basemap, not both")
        playgrounds_path = (Path(args.playgrounds) if args.playgrounds
                            else Path(args.basemap).parent / "playgrounds.geojson")
        basemap_path = (Path(args.basemap) if args.basemap
                        else playgrounds_path.parent / "basemap.geojson")
    else:
        from posterlab.runstore import resolve_run
        d = resolve_run(args.run or "latest", KIND)
        playgrounds_path = d / "playgrounds.geojson"
        basemap_path = d / "basemap.geojson"
        print(f"Rendering from run: {d.name}")

    render_run(
        playgrounds_path, basemap_path,
        theme=args.theme, title=args.title, subtitle=args.subtitle,
        count=args.count, number_radius_m=args.number_radius,
        pad=args.pad, size=args.size, variant=args.variant,
        orientation=args.orientation, frame_radius_m=args.frame_radius,
        out_dir=Path(args.out) if args.out else None,
        preview=args.preview, make_zip=args.zip,
    )


if __name__ == "__main__":
    main()
