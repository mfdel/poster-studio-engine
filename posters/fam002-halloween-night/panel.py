#!/usr/bin/env python3
"""
The panel sheet (FAM-002) — a framed map with the trick-or-treat log beneath it.

This is the original Halloween layout. The map keeps a border and a title band,
and everything the child writes on sits in one bordered panel under the map (or
beside it, in landscape). ``layouts.py`` holds the four full-bleed alternatives
that push the writing off the map entirely.

What the child fills in after the walk: costume, who they walked with, a treat
tally, a drawing box, and the house they liked best.

The rule that must never break
------------------------------
Nothing here names a house, and nothing claims which houses give treats or which
houses are safe. That data does not exist before the evening — a porch light
goes on when a neighbour decides it does. The sheet records the child's night; it
does not promise one. Keep every string on this side of that line.
"""
from __future__ import annotations

import math
from html import escape

from posterlab.map import home_glyph
from posterlab.svg.primitives import num as _num

from sheet_text import (
    DRAW_LABEL,
    FIELDS,
    HINT,
    MEMORY,
    TALLY_CELL_MM,
    TALLY_COUNT,
    TALLY_LABEL,
)


def _note_line(x1: float, x2: float, y: float, color: str) -> str:
    return (f'<line x1="{_num(x1)}" y1="{_num(y)}" x2="{_num(x2)}" y2="{_num(y)}" '
            f'stroke="{color}" stroke-width="0.3"/>')



def _field_line(x: float, y: float, w: float, label: str, size: float,
                theme: dict) -> str:
    """``Costume ____________`` — a caption with a rule to write on."""
    pal = theme["palette"]
    t = theme["type"]
    txt = label.upper() if t.get("subtitle_uppercase") else label
    lab_w = len(txt) * size * 0.62 + size * 0.8
    return (f'<text x="{_num(x)}" y="{_num(y)}" '
            f'font-family="{escape(t["label_font"])}" font-size="{_num(size)}" '
            f'letter-spacing="{_num(size * 0.08)}" fill="{pal["muted"]}">'
            f'{escape(txt)}</text>'
            + _note_line(x + lab_w, x + w, y + size * 0.28, pal["annotation_line"]))


def _tick_grid(x: float, y: float, w: float, count: int, color: str,
               cell_max: float) -> tuple[str, float]:
    """``count`` empty rounded boxes to colour in, packed into ``w``.

    The column count is derived from ``cell_max`` rather than fixed, so the same
    tally fits a wide panel under the map and a narrow one beside it without the
    boxes growing to swallow the page. Columns are snapped to a divisor of
    ``count`` so the last row is never ragged. Returns ``(svg, height)``.
    """
    gap_ratio = 0.34
    divisors = [d for d in range(1, count + 1) if count % d == 0]
    # Ascending, so the first fit is the fewest columns — the largest boxes that
    # still sit inside ``w``. Falls back to the most columns when none fit.
    cols = next((d for d in divisors
                 if w / (d + gap_ratio * (d - 1)) <= cell_max), divisors[-1])
    rows = math.ceil(count / cols)
    cell = w / (cols + gap_ratio * (cols - 1))
    gap = cell * gap_ratio
    out = []
    for i in range(count):
        r, c = divmod(i, cols)
        bx = x + c * (cell + gap)
        by = y + r * (cell + gap)
        out.append(f'<rect x="{_num(bx)}" y="{_num(by)}" width="{_num(cell)}" '
                   f'height="{_num(cell)}" rx="{_num(cell * 0.18)}" fill="none" '
                   f'stroke="{color}" stroke-width="{_num(max(0.18, cell * 0.06))}"/>')
    return "".join(out), rows * cell + (rows - 1) * gap


def render_log(x: float, y: float, w: float, h: float, theme: dict,
                         night: str = "") -> str:
    """The trick-or-treat panel: costume + crew fields, a treat tally, a drawing
    box, and one memory line. Everything here is written *after* the walk."""
    pal = theme["palette"]
    t = theme["type"]
    out: list[str] = [
        f'<rect x="{_num(x)}" y="{_num(y)}" width="{_num(w)}" height="{_num(h)}" '
        f'fill="{pal["annotation_box"]}" stroke="{pal["annotation_line"]}" '
        f'stroke-width="0.4"/>'
    ]

    pad = w * 0.028
    ix, iw = x + pad, w - 2 * pad
    head_size = w * 0.026
    body_size = w * 0.015
    tall = h > w  # the landscape side-panel: stack every block full width

    # --- Heading row: title left, the night's date right ----------------------
    cur = y + pad + head_size
    heading = "Our Trick-or-Treat Night"
    if t.get("subtitle_uppercase"):
        heading = heading.upper()
    out.append(f'<text x="{_num(ix)}" y="{_num(cur)}" '
               f'font-family="{escape(t["title_font"])}" font-size="{_num(head_size)}" '
               f'font-weight="{t.get("title_weight", "700")}" fill="{pal["text"]}">'
               f'{escape(heading)}</text>')
    if night and not tall:
        out.append(f'<text x="{_num(ix + iw)}" y="{_num(cur)}" text-anchor="end" '
                   f'font-family="{escape(t["body_font"])}" font-size="{_num(body_size)}" '
                   f'letter-spacing="{_num(body_size * 0.12)}" fill="{pal["muted"]}">'
                   f'{escape(night)}</text>')

    # --- Legend + hint. The glyph is the same one the map draws. --------------
    cur += body_size * 1.9
    gx, gy = ix + body_size * 0.6, cur - body_size * 0.32
    out.append(home_glyph(gx, gy, body_size * 0.62, theme))
    hint = f"{night}.  {HINT}" if (night and tall) else HINT
    out.append(f'<text x="{_num(gx + body_size * 1.5)}" y="{_num(cur)}" '
               f'font-family="{escape(t["body_font"])}" font-size="{_num(body_size)}" '
               f'fill="{pal["muted"]}">{escape(hint)}</text>')
    cur += pad * 0.55
    out.append(_note_line(ix, ix + iw, cur, pal["annotation_line"]))
    cur += pad * 1.1

    # --- Fields: side by side when the panel is wide, stacked when it is tall --
    field_size = body_size * 1.05
    if tall:
        for label in FIELDS:
            cur += field_size * 1.1
            out.append(_field_line(ix, cur, iw, label, field_size, theme))
            cur += field_size * 1.1
    else:
        cur += field_size * 1.2
        half = (iw - pad) / 2
        for k, label in enumerate(FIELDS):
            out.append(_field_line(ix + k * (half + pad), cur, half, label,
                                   field_size, theme))
        cur += field_size * 1.4

    # --- Reserve the memory line at the foot, then split what is left ---------
    memory_y = y + h - pad - field_size * 0.4
    body_bottom = memory_y - field_size * 1.8
    body_h = body_bottom - cur
    label_size = w * 0.016

    def _block_label(bx: float, by: float, text: str) -> str:
        return (f'<text x="{_num(bx)}" y="{_num(by)}" '
                f'font-family="{escape(t["label_font"])}" font-size="{_num(label_size)}" '
                f'font-weight="700" fill="{pal["text"]}">{escape(text)}</text>')

    lo, hi = TALLY_CELL_MM
    cell_max = min(hi, max(lo, body_size * 2.9))
    if tall:
        # Stack: tally over the drawing box, and never let the tally take more
        # than half the remaining panel.
        out.append(_block_label(ix, cur + label_size, TALLY_LABEL))
        grid, grid_h = _tick_grid(ix, cur + label_size * 1.7, iw, TALLY_COUNT,
                                  pal["annotation_line"], min(cell_max, body_h * 0.11))
        out.append(grid)
        draw_top = cur + label_size * 1.7 + grid_h + pad
        draw_x, draw_w = ix, iw
        draw_h = body_bottom - draw_top
    else:
        tally_w = iw * 0.56
        out.append(_block_label(ix, cur + label_size, TALLY_LABEL))
        grid, _ = _tick_grid(ix, cur + label_size * 1.7, tally_w, TALLY_COUNT,
                             pal["annotation_line"], cell_max)
        out.append(grid)
        draw_x = ix + tally_w + pad
        draw_w = iw - tally_w - pad
        draw_top = cur
        draw_h = body_h

    # --- The drawing box: open space, one caption, nothing printed inside -----
    if draw_h > label_size * 3:
        out.append(_block_label(draw_x, draw_top + label_size, DRAW_LABEL))
        box_y = draw_top + label_size * 1.7
        out.append(f'<rect x="{_num(draw_x)}" y="{_num(box_y)}" width="{_num(draw_w)}" '
                   f'height="{_num(draw_top + draw_h - box_y)}" fill="none" '
                   f'stroke="{pal["annotation_line"]}" stroke-width="0.3" '
                   f'stroke-dasharray="1.4 1.4" rx="{_num(label_size * 0.5)}"/>')

    out.append(_field_line(ix, memory_y, iw, MEMORY, field_size, theme))
    return "".join(out)


# --------------------------------------------------------------------------- #
# Digital deliverable: the how-to note that ships inside the ZIP
# --------------------------------------------------------------------------- #

HOWTO_TEXT = """HOW TO PRINT YOUR TRICK-OR-TREAT MAP
=====================================

Thank you! This is a DIGITAL download — no physical item was shipped. You print
it at home on plain A4 or US Letter paper, the same day if you like.

What's in this ZIP
------------------
- Print-ready PDFs, A4 and US Letter.
- Your street, your neighbours' houses, and your own home marked with a glyph.
- Space to fill in after the walk: costume, who came along, a treat tally, a
  drawing box, and the house you liked best.

Printing tips
-------------
1. Print at 100% / "Actual size" — do NOT let the printer "fit" or "scale to
   page", or the streets and the writing lines will shift.
2. Plain paper is fine. Slightly heavier paper (120 gsm+) holds up better to a
   marker without bleeding through.
3. Colours vary between screens, printers and papers. That's normal.
4. Print two — one for the walk, one to keep clean.

What this map does and does not show
------------------------------------
This map shows the streets and the buildings around your address, drawn from
OpenStreetMap. It does NOT show which houses hand out treats, and it does not
show which houses are taking part. Nobody can know that in advance — a porch
light goes on when a neighbour decides it does, on the night. Use the map to
plan a route and to keep the memory, and always follow your own local rules.

Map data (c) OpenStreetMap contributors (ODbL). See LICENSE-ATTRIBUTION.txt.
"""
