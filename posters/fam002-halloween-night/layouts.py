"""Full-bleed sheet layouts (FAM-002): map to the paper edge, writing off it.

The panel sheet (``panel.render_log``) frames the map and parks a bordered panel
under it. These layouts invert that: the map runs to the paper edge with no
frame, and every line you write on is pushed into a solid band or a margin
column, so the middle of the map stays clear to draw a route on.

    band    — solid title band across the top, all fields in a footer band.
    sheet   — map to all four edges, title and fields dropped onto scrims.
    ledger  — map full bleed, every field in a right-hand column.
    bonus   — no map at all: the spotting game, the tally and the drawing box.

``bonus`` is deliberately independent. It carries no sheet numbering, so it pairs
with any of the three map layouts (or sells on its own) rather than being page 2
of one specific bundle.

Decoration is raster art from ``studio/themes/<dir>/*_cut.png``, embedded as
base64 so a rendered PDF is a single portable file. Placement is declared in
``DECOR`` as page fractions, so the same layout decorates A4 and US Letter
without the art drifting into the trim.

This module never imports from ``render``. ``render`` asks it where the map goes
(``map_box``/``clip_box``), draws the map itself, and hands the fragment back to
``compose`` — so there is no cycle and no duplicated map code.

Every printed string comes from ``sheet_text``, shared with the panel sheet.
Nothing here names a house, or claims which houses take part.
"""
from __future__ import annotations

import base64
import math
import struct
from html import escape
from pathlib import Path

from posterlab.chrome import page_size
from posterlab.svg.primitives import num as _num

from sheet_text import (
    BONUS_EYEBROW,
    BONUS_HINT,
    BONUS_ITEMS,
    BONUS_TITLE,
    DRAW_LABEL,
    FIELDS,
    HEADING,
    MEMORY,
    ROUTE_CALL,
    SHEET_HEADING,
    TALLY_COUNT,
    TALLY_LABEL,
    TALLY_SHORT,
)

LAYOUTS = ("band", "sheet", "ledger", "bonus")

# --------------------------------------------------------------------------- #
# Decor placement
# --------------------------------------------------------------------------- #

# (art, anchor, x, y, width) — x/y/width are page fractions; anchor names which
# corner x/y measure from, so the same row works on any sheet size. Height comes
# from the PNG's own aspect ratio, never from a second guess here.
#
# Two art pieces were tried and dropped, both for the same reason — they were
# painted over by content that has to be there:
#   drip-banner  at page width its drips fall a third of the header and bury the title.
#   witch-hat    on the bonus sheet the spotting grid starts on top of it.
DECOR: dict[str, tuple[tuple[str, str, float, float, float], ...]] = {
    "band": (
        ("crescent-moon",  "top-right",    0.032, 0.143, 0.159),
        ("spider-drop",    "top-left",     0.145, 0.112, 0.059),
        ("cat-on-fence",   "bottom-left",  0.035, 0.259, 0.199),
        ("candy-scatter",  "bottom-right", 0.030, 0.274, 0.255),
    ),
    "sheet": (
        ("bat-hanging",    "top-left",     0.653, 0.000, 0.102),
        ("cobweb-corner",  "top-right",    0.000, 0.000, 0.228),
        ("jack-o-lantern", "bottom-right", 0.035, 0.025, 0.204),
    ),
    "ledger": (
        ("owl-on-branch",  "top-left",     0.030, 0.017, 0.129),
        ("bats-corner-trio", "top-left",   0.202, 0.753, 0.226),
    ),
    # The foot art was sized before the memory field moved under the tally, and
    # the three bottom pieces grew tall enough to sit under "The house we liked
    # best". They are smaller here so the writing line has clear paper.
    "bonus": (
        ("ghost-trio-peek", "top-right",   0.040, 0.021, 0.282),
        ("gravestones",    "bottom-left",  0.027, 0.008, 0.200),
        ("skeleton-wave",  "bottom-left",  0.262, 0.004, 0.090),
        ("pumpkin-row",    "bottom-right", 0.032, 0.013, 0.300),
    ),
}

# The ledger column reserves its own art slots, measured inside the column.
LEDGER_TOP_ART = "lantern-glow"
LEDGER_FOOT_ART = "black-cat-arched"


def _png_size(path: Path) -> tuple[int, int]:
    """(width, height) from a PNG's IHDR — stdlib only, no image library.

    The renderer already depends on cairosvg for export; adding Pillow just to
    read two integers off the front of a file would be a heavier dependency than
    the job deserves.
    """
    with path.open("rb") as fh:
        head = fh.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"not a PNG: {path}")
    return struct.unpack(">II", head[16:24])


def _data_uri(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def art_path(art_dir: Path, name: str) -> Path:
    """Resolve an art name to its cut-out file.

    ``_cut`` files are the ones with the background removed; the unsuffixed
    siblings still carry their own plate and would print as a grey box over the
    map, so they are never used here.
    """
    return art_dir / f"{name}_cut.png"


def place(art_dir: Path, name: str, anchor: str, x: float, y: float,
          w_frac: float, W: float, H: float, *, opacity: float = 1.0) -> str:
    """One decor image, positioned from the named corner in page fractions."""
    p = art_path(art_dir, name)
    if not p.exists():
        return ""  # a missing cut-out must not take the whole render down
    pw, ph = _png_size(p)
    w = W * w_frac
    h = w * ph / pw
    px = W * x if "left" in anchor else W - W * x - w
    py = H * y if "top" in anchor else H - H * y - h
    op = f' opacity="{_num(opacity)}"' if opacity < 1 else ""
    return (f'<image x="{_num(px)}" y="{_num(py)}" width="{_num(w)}" '
            f'height="{_num(h)}" preserveAspectRatio="xMidYMid meet"{op} '
            f'xlink:href="{_data_uri(p)}"/>')


def decor_for(layout: str, art_dir: Path, W: float, H: float,
              y_at: dict[str, float] | None = None) -> str:
    """Every decor piece for one layout.

    ``y_at`` replaces the stored y for a named piece. The band footer is sized by
    what it holds, so it is not the same fraction of A4 and of Letter, and the
    art that sits on its top edge cannot use one stored page fraction.
    """
    out = []
    for name, anchor, x, y, w in DECOR.get(layout, ()):
        out.append(place(art_dir, name, anchor, x,
                         y_at[name] if y_at and name in y_at else y, w, W, H))
    return "".join(out)


def art_dir_for(theme: dict, themes_root: Path) -> Path:
    """Where this theme's cut-outs live.

    ``ink`` has no art of its own — the cut-outs are dark-bodied silhouettes, so
    they read correctly on cream paper as well as on plum, and both themes point
    at the same folder rather than shipping two copies.
    """
    return themes_root / theme.get("decor", {}).get("dir", theme["name"])


# --------------------------------------------------------------------------- #
# Small drawing helpers
# --------------------------------------------------------------------------- #

def _text(x: float, y: float, s: str, *, font: str, size: float, fill: str,
          weight: str = "", tracking: float = 0.0, anchor: str = "",
          italic: bool = False) -> str:
    bits = [f'x="{_num(x)}"', f'y="{_num(y)}"',
            f'font-family="{escape(font)}"', f'font-size="{_num(size)}"',
            f'fill="{fill}"']
    if weight:
        bits.append(f'font-weight="{weight}"')
    if tracking:
        bits.append(f'letter-spacing="{_num(tracking)}"')
    if anchor:
        bits.append(f'text-anchor="{anchor}"')
    if italic:
        bits.append('font-style="italic"')
    return f'<text {" ".join(bits)}>{escape(s)}</text>'


# Average glyph advance as a fraction of the font size. cairosvg exposes no text
# metrics, so a display line is sized against this estimate the same way
# ``posterlab.chrome.title_block`` does. The numbers are measured off this
# renderer at the theme's own font stack, rounded up so the estimate never
# under-reports a width.
_UPPER_RATIO = 0.66
_LOWER_RATIO = 0.53


def _fit(text: str, max_size: float, width: float, *, tracking: float = 0.0,
         tracking_ratio: float = 0.0, safety: float = 0.96) -> float:
    """Largest font size at or below ``max_size`` that keeps ``text`` in ``width``.

    Every heading in this module was transcribed from a comp as a fixed fraction
    of the page, which holds only for the string the comp happened to show. A
    real title is any length, so each line is shrunk to its own box instead.

    ``tracking`` is letter-spacing in mm; ``tracking_ratio`` is letter-spacing as
    a multiple of the font size. Pass whichever form the call site uses.
    """
    n = max(len(text), 1)
    ratio = _UPPER_RATIO if text == text.upper() else _LOWER_RATIO
    per_size = ratio * n + tracking_ratio * (n - 1)
    room = width * safety - tracking * (n - 1)
    return max(2.5, min(max_size, room / per_size)) if per_size else max_size


def _fit_all(lines, max_size: float, width: float, **kw) -> float:
    """One size that fits every line — headings must not change size mid-block."""
    return min((_fit(ln, max_size, width, **kw) for ln in lines if ln),
               default=max_size)


def _rule(x1: float, x2: float, y: float, color: str, w: float = 0.3) -> str:
    return (f'<line x1="{_num(x1)}" y1="{_num(y)}" x2="{_num(x2)}" y2="{_num(y)}" '
            f'stroke="{color}" stroke-width="{_num(w)}"/>')


def _band(x: float, y: float, w: float, h: float, fill: str, *,
          edge: str = "", edge_side: str = "") -> str:
    """A solid strip of page colour, optionally with one hairline edge.

    Solid, not a gradient: on the ink sheet this is the cheapest ink on the page,
    and a band with a hard edge is also the only way a title stays legible over
    whatever the map happens to be doing underneath it.
    """
    out = [f'<rect x="{_num(x)}" y="{_num(y)}" width="{_num(w)}" height="{_num(h)}" '
           f'fill="{fill}"/>']
    if edge:
        ey = y + h if edge_side == "bottom" else y
        out.append(_rule(x, x + w, ey, edge, 0.4))
    return "".join(out)


def _scrim(x: float, y: float, w: float, h: float, page: str, gid: str,
           *, from_top: bool) -> str:
    """A fade from the page colour into the map, for the full-bleed layout.

    The map has to reach all four edges, so the type can't sit on a hard band
    without cutting the sheet in half. A fade keeps the bleed and still gives the
    text a ground.
    """
    y1, y2 = ("0%", "100%") if from_top else ("100%", "0%")
    return (f'<defs><linearGradient id="{gid}" x1="0%" y1="{y1}" x2="0%" y2="{y2}">'
            f'<stop offset="0%" stop-color="{page}" stop-opacity="1"/>'
            f'<stop offset="46%" stop-color="{page}" stop-opacity="1"/>'
            f'<stop offset="100%" stop-color="{page}" stop-opacity="0"/>'
            f'</linearGradient></defs>'
            f'<rect x="{_num(x)}" y="{_num(y)}" width="{_num(w)}" height="{_num(h)}" '
            f'fill="url(#{gid})"/>')


def stacked_field(x: float, y: float, w: float, label: str, theme: dict,
                  size: float, *, gap: float | None = None) -> str:
    """Caption above the rule, not beside it.

    The panel sheet writes ``Costume ______``; these layouts stack the caption so
    the writing line can run the full width of a band or a narrow column. In a
    72 mm ledger an inline caption leaves about 30 mm to write a name in.

    ``gap`` is the clear height in mm between the caption and its rule — the
    space a child actually writes in. It defaults to the caption's own size,
    which is enough for a printed answer but not for a marker.
    """
    pal, t = theme["palette"], theme["type"]
    size = _fit(label.upper(), size, w, tracking_ratio=0.18)
    rule_y = y + (size * 0.95 if gap is None else gap)
    return (_text(x, y, label.upper(), font=t["label_font"], size=size,
                  fill=pal["muted"], tracking=size * 0.18)
            + _rule(x, x + w, rule_y, pal["annotation_line"], 0.35))


def tick_grid(x: float, y: float, w: float, count: int, cols: int,
              color: str, *, gap_ratio: float = 0.34) -> tuple[str, float]:
    """``count`` boxes to colour in, at a *fixed* column count.

    ``render._tick_grid`` derives its columns from a max cell size, which is
    right for a panel that must swallow the grid whatever shape it is. Here the
    column count is part of the layout — 20 across to make the footer band a
    footer, 5 across to fill a ledger's height — so it is an argument, not a
    consequence. Returns ``(svg, height)``.
    """
    rows = math.ceil(count / cols)
    cell = w / (cols + gap_ratio * (cols - 1))
    gap = cell * gap_ratio
    out = []
    for i in range(count):
        r, c = divmod(i, cols)
        out.append(f'<rect x="{_num(x + c * (cell + gap))}" '
                   f'y="{_num(y + r * (cell + gap))}" width="{_num(cell)}" '
                   f'height="{_num(cell)}" rx="{_num(cell * 0.18)}" fill="none" '
                   f'stroke="{color}" stroke-width="{_num(max(0.18, cell * 0.06))}"/>')
    return "".join(out), rows * cell + (rows - 1) * gap


# --------------------------------------------------------------------------- #
# Geometry: where the map goes, per layout
# --------------------------------------------------------------------------- #

# Band heights as fractions of page height, from the approved comps.
BAND_HEADER_H = 0.116
BAND_TALLY_COLS = 20

# The band footer's gaps, as fractions of page *width*. Height fractions do not
# transfer between A4 and the shorter, wider Letter page, and the writing rules
# were the first thing to be squeezed when they were tried.
BAND_HEAD_GAP = 0.052       # heading baseline -> the first field label
BAND_WRITE_GAP = 0.044      # a field label -> the rule you write on
BAND_TALLY_GAP = 0.028      # a field rule -> the tally label
BAND_MEMORY_GAP = 0.052     # the tally grid -> the memory label
BAND_BOTTOM_MARGIN = 0.038  # the last rule -> the paper edge

# How far the two bottom decor pieces overlap the footer's top edge, in page
# widths. They sit on that edge, so they are placed from the measured footer.
BAND_ART_SINK = {"cat-on-fence": 0.0368, "candy-scatter": 0.0156}


def band_footer_h(W: float, H: float) -> float:
    """The band footer's height, summed from what it has to hold.

    A fixed page fraction fitted one paper size and crowded the other. Measuring
    the same gaps the layout draws with keeps the writing lines the same size on
    A4 and on Letter, and the map takes whatever height is left.
    """
    pad = W * 0.054
    field_size = W * 0.0295
    _, grid_h = tick_grid(0, 0, W - 2 * pad, TALLY_COUNT, BAND_TALLY_COLS, "none")
    return (pad * 0.62 + W * 0.056                     # top pad + the heading
            + W * BAND_HEAD_GAP + W * BAND_WRITE_GAP   # the two fields
            + W * BAND_TALLY_GAP                       # the tally label
            + field_size * 0.7 + grid_h                # the tally grid
            + W * BAND_MEMORY_GAP + W * BAND_WRITE_GAP # the memory field
            + W * BAND_BOTTOM_MARGIN)
LEDGER_W = 0.347          # right-hand column, as a fraction of page width
SHEET_TOP_SCRIM = 0.143
SHEET_FOOT_SCRIM = 0.304


def map_box(layout: str, W: float, H: float) -> tuple[float, float, float, float]:
    """The box the map is *projected* into — i.e. what gets framed.

    For ``ledger`` this is only the clear half of the page, not the whole sheet.
    The map still bleeds under the column (see ``clip_box``), but home is framed
    against the part of the page you can actually see, so the amber house glyph
    can't end up hidden behind the writing lines.
    """
    if layout == "band":
        top = H * BAND_HEADER_H
        return 0.0, top, W, H - top - band_footer_h(W, H)
    if layout == "ledger":
        return 0.0, 0.0, W - W * LEDGER_W, H
    return 0.0, 0.0, W, H          # sheet


def clip_box(layout: str, W: float, H: float) -> tuple[float, float, float, float]:
    """The region the map is allowed to paint. Equals the page except for
    ``band``, where the bands own the top and bottom of the sheet."""
    if layout == "band":
        return map_box(layout, W, H)
    return 0.0, 0.0, W, H


# --------------------------------------------------------------------------- #
# Layouts
# --------------------------------------------------------------------------- #

def _band_layout(W: float, H: float, theme: dict, title: str, subtitle: str,
                 coords: str, night: str, art_dir: Path) -> str:
    pal, t = theme["palette"], theme["type"]
    pad = W * 0.054
    header_h, footer_h = H * BAND_HEADER_H, band_footer_h(W, H)
    write_gap = W * BAND_WRITE_GAP
    sink = {k: (footer_h - W * v) / H for k, v in BAND_ART_SINK.items()}
    out = [decor_for("band", art_dir, W, H, sink)]

    # --- Header band: title in a solid strip, never floating over the streets --
    out.append(_band(0, 0, W, header_h, pal["page"], edge=pal["border"],
                     edge_side="bottom"))
    iw_head = W - 2 * pad
    head = title.upper() if t.get("title_uppercase") else title
    track = t.get("title_tracking", 3.6) * 0.45
    title_size = _fit(head, W * 0.088, iw_head, tracking=track)
    out.append(_text(pad, header_h * 0.56, head, font=t["title_font"],
                     size=title_size, fill=pal["text"],
                     weight=t.get("title_weight", "500"),
                     tracking=track))
    line = " · ".join(s for s in (subtitle, night) if s)
    sub_size = _fit(line, W * 0.0335, iw_head, tracking_ratio=0.16)
    out.append(_text(pad, header_h * 0.84, line, font=t["body_font"],
                     size=sub_size, fill=pal["muted"], tracking=sub_size * 0.16))

    # --- Footer band: heading, route call, two fields, the tally, one memory ---
    fy = H - footer_h
    out.append(_band(0, fy, W, footer_h, pal["page"], edge=pal["border"],
                     edge_side="top"))
    iw = W - 2 * pad
    cur = fy + pad * 0.62 + W * 0.056
    # Heading left, route call right, on one baseline — so each is fitted to its
    # own half of the band and they cannot meet in the middle.
    out.append(_text(pad, cur, HEADING, font=t["title_font"],
                     size=_fit(HEADING, W * 0.056, iw * 0.54),
                     fill=pal["text"], weight=t.get("title_weight", "500")))
    out.append(_text(W - pad, cur, ROUTE_CALL, font=t["body_font"],
                     size=_fit(ROUTE_CALL, W * 0.040, iw * 0.42),
                     fill=pal["playground_marker"], anchor="end", italic=True))

    field_size = W * 0.0295
    cur += W * BAND_HEAD_GAP
    half = (iw - pad) / 2
    for k, label in enumerate(FIELDS):
        out.append(stacked_field(pad + k * (half + pad), cur, half, label,
                                 theme, field_size, gap=write_gap))

    # Past the rule the fields are written on, not past the label above it.
    cur += write_gap + W * BAND_TALLY_GAP
    tally_size = _fit(TALLY_LABEL.upper(), field_size, iw, tracking_ratio=0.18)
    out.append(_text(pad, cur, TALLY_LABEL.upper(), font=t["label_font"],
                     size=tally_size, fill=pal["muted"],
                     tracking=tally_size * 0.18))
    grid, grid_h = tick_grid(pad, cur + field_size * 0.7, iw, TALLY_COUNT,
                             BAND_TALLY_COLS, pal["annotation_line"])
    out.append(grid)

    # The memory field follows the grid instead of hanging off the paper edge,
    # so its own writing gap cannot be eaten by the bottom margin.
    cur += field_size * 0.7 + grid_h + W * BAND_MEMORY_GAP
    out.append(stacked_field(pad, cur, iw, MEMORY, theme, field_size,
                             gap=write_gap))
    return "".join(out)


def _sheet_layout(W: float, H: float, theme: dict, title: str, subtitle: str,
                  coords: str, night: str, art_dir: Path) -> str:
    pal, t = theme["palette"], theme["type"]
    pad = W * 0.059
    out = [
        _scrim(0, 0, W, H * SHEET_TOP_SCRIM, pal["page"], "hw-top", from_top=True),
        _scrim(0, H - H * SHEET_FOOT_SCRIM, W, H * SHEET_FOOT_SCRIM, pal["page"],
               "hw-foot", from_top=False),
        decor_for("sheet", art_dir, W, H),
    ]

    # Title top-left, on the fade. Two short lines: at this size one line would
    # run into the cobweb in the opposite corner.
    words = SHEET_HEADING.split()
    l1, l2 = " ".join(words[:2]), " ".join(words[2:])
    # The cobweb owns the top-right corner, so the heading only has the left of
    # the page to run in.
    size = _fit_all((l1, l2), W * 0.102, W * 0.72 - pad)
    out.append(_text(pad, H * 0.062, l1, font=t["title_font"], size=size,
                     fill=pal["text"], weight=t.get("title_weight", "500")))
    out.append(_text(pad, H * 0.062 + size * 1.05, l2, font=t["title_font"],
                     size=size, fill=pal["text"],
                     weight=t.get("title_weight", "500")))

    # Fields stack up from the foot, so the map's whole middle stays clear.
    field_size = W * 0.0295
    col_w = W * 0.645
    cur = H - pad * 0.9
    # The jack-o-lantern sits in the bottom-right corner; the meta line stops
    # short of it rather than running underneath.
    meta = " · ".join(s for s in (subtitle, night) if s)
    meta_size = _fit(meta, W * 0.0322, W * 0.74 - pad, tracking_ratio=0.14)
    out.append(_text(pad, cur, meta, font=t["body_font"], size=meta_size,
                     fill=pal["muted"], tracking=meta_size * 0.14))
    cur -= H * 0.038
    out.append(stacked_field(pad, cur, col_w, TALLY_SHORT, theme, field_size))
    cur -= H * 0.038
    out.append(stacked_field(pad, cur, col_w, FIELDS[1], theme, field_size))
    cur -= H * 0.038
    out.append(stacked_field(pad, cur, col_w, FIELDS[0], theme, field_size))
    cur -= H * 0.034
    out.append(_text(pad, cur, ROUTE_CALL, font=t["body_font"],
                     size=_fit(ROUTE_CALL, W * 0.043, col_w),
                     fill=pal["playground_marker"], italic=True))
    return "".join(out)


def _ledger_layout(W: float, H: float, theme: dict, title: str, subtitle: str,
                   coords: str, night: str, art_dir: Path) -> str:
    pal, t = theme["palette"], theme["type"]
    out = [decor_for("ledger", art_dir, W, H)]

    col_w = W * LEDGER_W
    col_x = W - col_w
    out.append(f'<rect x="{_num(col_x)}" y="0" width="{_num(col_w)}" '
               f'height="{_num(H)}" fill="{pal["page"]}"/>')
    out.append(f'<line x1="{_num(col_x)}" y1="0" x2="{_num(col_x)}" '
               f'y2="{_num(H)}" stroke="{pal["border"]}" stroke-width="0.4"/>')

    pad = W * 0.035
    ix, iw = col_x + pad, col_w - 2 * pad
    cur = H * 0.030

    # A lantern at the head of the column, centred — the column is narrow enough
    # that a centred object reads as a masthead rather than as clutter.
    lamp = art_path(art_dir, LEDGER_TOP_ART)
    if lamp.exists():
        lw = col_w * 0.30
        pw, ph = _png_size(lamp)
        out.append(f'<image x="{_num(col_x + (col_w - lw) / 2)}" y="{_num(cur)}" '
                   f'width="{_num(lw)}" height="{_num(lw * ph / pw)}" '
                   f'preserveAspectRatio="xMidYMid meet" '
                   f'xlink:href="{_data_uri(lamp)}"/>')
        cur += lw * ph / pw + H * 0.022

    # Heading wraps to two lines by hand: "Our Trick-" / "or-Treat Night" is the
    # break the comp uses, and an automatic break would put "Night" alone.
    size = _fit_all(("Our Trick-", "or-Treat Night"), col_w * 0.208, iw)
    cur += size
    out.append(_text(ix, cur, "Our Trick-", font=t["title_font"], size=size,
                     fill=pal["text"], weight=t.get("title_weight", "500")))
    cur += size * 1.06
    out.append(_text(ix, cur, "or-Treat Night", font=t["title_font"], size=size,
                     fill=pal["text"], weight=t.get("title_weight", "500")))

    # A locality can be one word or five, so the meta block takes one size that
    # holds all of its lines rather than a size per line.
    meta_parts = [q.upper() for q in (subtitle, night, coords) if q]
    meta_size = _fit_all(meta_parts, col_w * 0.085, iw, tracking_ratio=0.16)
    for part in meta_parts:
        cur += meta_size * 1.62
        out.append(_text(ix, cur, part, font=t["label_font"],
                         size=meta_size, fill=pal["muted"],
                         tracking=meta_size * 0.16))

    cur += H * 0.026
    out.append(_rule(ix, ix + iw, cur, pal["annotation_line"], 0.35))
    cur += H * 0.030
    out.append(_text(ix, cur, ROUTE_CALL, font=t["body_font"],
                     size=_fit(ROUTE_CALL, col_w * 0.108, iw),
                     fill=pal["playground_marker"], italic=True))

    field_size = col_w * 0.081
    for label in FIELDS:
        cur += H * 0.042
        out.append(stacked_field(ix, cur, iw, label, theme, field_size))

    cur += H * 0.044
    tally_size = _fit(TALLY_LABEL.upper(), field_size, iw, tracking_ratio=0.18)
    out.append(_text(ix, cur, TALLY_LABEL.upper(), font=t["label_font"],
                     size=tally_size, fill=pal["muted"],
                     tracking=tally_size * 0.18))
    # 5 across × 8 down: the column's height is the resource here, not its width.
    grid, grid_h = tick_grid(ix, cur + field_size * 0.8, iw, TALLY_COUNT, 5,
                             pal["annotation_line"])
    out.append(grid)
    # The cat is measured before the memory field is placed, so the field can be
    # lifted clear of it. On the shorter Letter page the two collided.
    cat = art_path(art_dir, LEDGER_FOOT_ART)
    cat_top = H
    if cat.exists():
        cw = col_w * 0.43
        pw, ph = _png_size(cat)
        ch = cw * ph / pw
        cat_top = H - H * 0.052 - ch

    cur += field_size * 0.8 + grid_h + H * 0.036
    cur = min(cur, cat_top - H * 0.014 - field_size * 0.95)
    out.append(stacked_field(ix, cur, iw, MEMORY, theme, field_size))

    if cat.exists():
        out.append(f'<image x="{_num(ix)}" y="{_num(cat_top)}" '
                   f'width="{_num(cw)}" height="{_num(ch)}" '
                   f'preserveAspectRatio="xMidYMid meet" '
                   f'xlink:href="{_data_uri(cat)}"/>')
    return "".join(out)


def _wrap_item(item: str) -> list[str]:
    """One spotting-grid caption, wrapped to two lines when it is long.

    Shared by the drawing loop and by the size calculation, so the size that is
    measured is the size that is drawn.
    """
    words = item.split()
    if len(item) > 16 and len(words) > 2:
        mid = len(words) // 2 + len(words) % 2
        return [" ".join(words[:mid]), " ".join(words[mid:])]
    return [item]


def _wrap_items(items: list[str]) -> list[str]:
    return [ln for item in items for ln in _wrap_item(item)]


def _bonus_layout(W: float, H: float, theme: dict, night: str,
                  art_dir: Path) -> str:
    """The spotting game — no map, no sheet numbering, no dependency on a layout."""
    pal, t = theme["palette"], theme["type"]
    out = [
        f'<rect x="0" y="0" width="{_num(W)}" height="{_num(H)}" '
        f'fill="{pal["annotation_box"]}"/>',
        decor_for("bonus", art_dir, W, H),
    ]
    pad = W * 0.059
    iw = W - 2 * pad

    eyebrow = W * 0.0322
    if BONUS_EYEBROW:
        out.append(_text(pad, H * 0.052, BONUS_EYEBROW.upper(), font=t["label_font"],
                         size=eyebrow, fill=pal["playground_marker"],
                         tracking=eyebrow * 0.3))
    words = BONUS_TITLE.split()
    heads = (" ".join(words[:3]), " ".join(words[3:]))
    # The ghosts peek in from the top-right, so the title runs in the left 70%.
    size = _fit_all(heads, W * 0.102, W * 0.70 - pad)
    for i, line in enumerate(heads):
        out.append(_text(pad, H * 0.052 + size * (1.05 + i * 1.05), line,
                         font=t["title_font"], size=size, fill=pal["text"],
                         weight=t.get("title_weight", "500")))
    # --- 4 × 4 spotting grid. Empty boxes with a caption at the foot of each:
    # the child crosses the box, so the box has to stay open.
    grid_top = H * 0.255

    # The hint sits a fixed gap above the grid. Hanging it off the title's height
    # put it inside the first row of boxes, because the title's size now depends
    # on how wide the title happens to be.
    hint = _fit(BONUS_HINT, W * 0.0363, iw)
    out.append(_text(pad, grid_top - H * 0.020, BONUS_HINT,
                     font=t["body_font"], size=hint, fill=pal["muted"]))
    gap = W * 0.0121
    cell_w = (iw - 3 * gap) / 4
    cell_h = H * 0.0874
    label_size = W * 0.0322
    item_size = _fit_all(_wrap_items(BONUS_ITEMS), label_size, cell_w * 0.82)
    for i, item in enumerate(BONUS_ITEMS):
        r, c = divmod(i, 4)
        bx, by = pad + c * (cell_w + gap), grid_top + r * (cell_h + gap)
        out.append(f'<rect x="{_num(bx)}" y="{_num(by)}" width="{_num(cell_w)}" '
                   f'height="{_num(cell_h)}" fill="{pal["page"]}" '
                   f'stroke="{pal["annotation_line"]}" stroke-width="0.35"/>')
        lines = _wrap_item(item)
        # Every caption in the grid shares one size, set by the widest line, so
        # sixteen boxes do not print in sixteen different type sizes.
        for j, ln in enumerate(reversed(lines)):
            out.append(_text(bx + cell_w * 0.10,
                             by + cell_h - cell_h * 0.13 - j * item_size * 1.28,
                             ln, font=t["body_font"], size=item_size,
                             fill=pal["text"]))

    # --- Tally beside the drawing box ----------------------------------------
    body_top = grid_top + 4 * cell_h + 3 * gap + H * 0.036
    tally_w = W * 0.355
    tally_size = _fit(TALLY_LABEL.upper(), label_size, tally_w, tracking_ratio=0.18)
    out.append(_text(pad, body_top, TALLY_LABEL.upper(), font=t["label_font"],
                     size=tally_size, fill=pal["muted"],
                     tracking=tally_size * 0.18))
    # 10 per row divides 40 exactly, so the block is 4 clean rows instead of 4
    # rows plus 4 orphan boxes, and it is one row shorter — which is what keeps
    # the memory field off the grid.
    grid, grid_h = tick_grid(pad, body_top + label_size * 0.8, tally_w,
                             TALLY_COUNT, 10, pal["annotation_line"])
    out.append(grid)

    draw_x = pad + tally_w + W * 0.038
    draw_w = W - draw_x - pad
    draw_size = _fit(DRAW_LABEL.upper(), label_size, draw_w, tracking_ratio=0.18)
    out.append(_text(draw_x, body_top, DRAW_LABEL.upper(), font=t["label_font"],
                     size=draw_size, fill=pal["muted"],
                     tracking=draw_size * 0.18))
    box_y = body_top + label_size * 0.8
    box_h = grid_h
    out.append(f'<rect x="{_num(draw_x)}" y="{_num(box_y)}" width="{_num(draw_w)}" '
               f'height="{_num(box_h)}" fill="none" stroke="{pal["annotation_line"]}" '
               f'stroke-width="0.3" stroke-dasharray="1.4 1.4" '
               f'rx="{_num(label_size * 0.5)}"/>')

    # Clamped clear of the foot art. Without the clamp the caption and its rule
    # land on the gravestones, and a child cannot write on printed artwork.
    memory_y = min(box_y + box_h + H * 0.048, H * 0.828)
    out.append(stacked_field(pad, memory_y, iw, MEMORY, theme, label_size))
    if night:
        # Right-anchored at the ghosts' left edge, not at the page margin: the
        # ghost trio owns the top-right corner and the date is not readable
        # through it.
        night_right = W * 0.66
        night_size = _fit(night, eyebrow, night_right - pad - W * 0.40,
                          tracking_ratio=0.14)
        out.append(_text(night_right, H * 0.052, night, font=t["body_font"],
                         size=night_size, fill=pal["muted"], anchor="end",
                         tracking=night_size * 0.14))
    return "".join(out)


# --------------------------------------------------------------------------- #
# Composition
# --------------------------------------------------------------------------- #

def compose(size: str, layout: str, *, theme: dict, map_svg: str,
            title: str, subtitle: str, coords: str, night: str,
            art_dir: Path, attribution_svg: str = "",
            landscape: bool = False) -> str:
    """A full halloween sheet.

    ``map_svg`` is the map body already projected into ``map_box(layout, W, H)``
    by the caller; it is clipped to ``clip_box`` here so a full-bleed map can
    overflow its projection box without painting over the bands. ``bonus`` takes
    no map and ignores it.

    No ``render_border`` call: all three map layouts bleed, and an inset frame
    around a bleeding map is the one thing that makes it look like a mistake.
    """
    if layout not in LAYOUTS:
        raise ValueError(f"unknown halloween layout: {layout!r} (want {LAYOUTS})")
    W, H = page_size(size, landscape)
    pal = theme["palette"]

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{_num(W)}mm" height="{_num(H)}mm" '
        f'viewBox="0 0 {_num(W)} {_num(H)}">',
        f'<rect x="0" y="0" width="{_num(W)}" height="{_num(H)}" fill="{pal["page"]}"/>',
    ]

    if layout == "bonus":
        parts.append(_bonus_layout(W, H, theme, night, art_dir))
    else:
        cx, cy, cw, ch = clip_box(layout, W, H)
        parts.append(
            f'<defs><clipPath id="hw-map"><rect x="{_num(cx)}" y="{_num(cy)}" '
            f'width="{_num(cw)}" height="{_num(ch)}"/></clipPath></defs>'
            f'<g clip-path="url(#hw-map)">{map_svg}</g>'
        )
        if layout == "band":
            parts.append(_band_layout(W, H, theme, title, subtitle, coords, night, art_dir))
        elif layout == "sheet":
            parts.append(_sheet_layout(W, H, theme, title, subtitle, coords, night, art_dir))
        else:
            parts.append(_ledger_layout(W, H, theme, title, subtitle, coords, night, art_dir))
        parts.append(attribution_svg)

    parts.append("</svg>")
    return "".join(parts)
