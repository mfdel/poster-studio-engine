"""The cosy room artwork for FAM-003, drawn per cube face.

Each function returns SVG for one whole surface in that surface's own coordinate
space (millimetres, origin top left). ``posterlab.chrome.tiling`` clips the pieces
out of it, so nothing here knows about paper.

Every surface is drawn *seam-aware*: **every** cut line that :func:`seam_lines`
reports gets a real feature on it — a wallpaper stripe edge, a picture rail, the
top of the skirting board, a floorboard end joint, a ceiling moulding — so a glued
join reads as part of the room. This holds for any cube size, not only the default
one that splits into two pieces per axis.
"""
from __future__ import annotations

from posterlab.svg.primitives import num

# Height of the skirting board is set by the horizontal seam, not chosen: the
# board's top edge *is* the cut line. This is the fallback when a surface has no
# horizontal seam (a very small cube printed on one sheet).
SKIRTING_FALLBACK_MM = 55.0
EPS_MM = 0.5          # a seam this close to an edge is the edge, not a cut
STRIPE_TARGET_MM = 31.0
PLANK_TARGET_MM = 46.0


def _band_edges(seams: list[float], extent: float, target: float) -> list[float]:
    """Band boundaries across ``0..extent`` that land exactly on every seam.

    A single repeat width can only hit one seam. Each gap between consecutive
    seams therefore gets its own repeat, chosen as the whole number of bands
    closest to ``target``. Band widths vary by a few millimetres between gaps,
    which reads as hand-drawn wallpaper, and every cut line is a band edge.
    """
    anchors = [0.0] + [s for s in sorted(seams) if EPS_MM < s < extent - EPS_MM] + [extent]
    edges = [0.0]
    for a, b in zip(anchors, anchors[1:]):
        n = max(1, round((b - a) / target))
        step = (b - a) / n
        edges += [a + step * i for i in range(1, n + 1)]
    return edges


def _seam_list(seams: dict, axis: str, extent: float) -> list[float]:
    """The interior seams on one axis, sorted and clear of the surface edges."""
    return [s for s in sorted(seams.get(axis) or []) if EPS_MM < s < extent - EPS_MM]


def _rect(x, y, w, h, fill, stroke=None, sw=0.4, rx=0.0) -> str:
    s = (f'<rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}" '
         f'fill="{fill}"')
    if rx:
        s += f' rx="{num(rx)}"'
    if stroke:
        s += f' stroke="{stroke}" stroke-width="{num(sw)}"'
    return s + "/>"


def _line(x1, y1, x2, y2, color, sw=0.4, opacity=1.0) -> str:
    return (f'<path d="M{num(x1)} {num(y1)}L{num(x2)} {num(y2)}" stroke="{color}" '
            f'stroke-width="{num(sw)}" opacity="{num(opacity)}" fill="none"/>')


# --------------------------------------------------------------------------- #
# Walls
# --------------------------------------------------------------------------- #

def wall_base(w: float, h: float, tok: dict, seams: dict) -> tuple[list[str], float]:
    """Wallpaper, skirting board and picture rail. Returns the skirting top."""
    seams_x = _seam_list(seams, "x", w)
    seams_y = _seam_list(seams, "y", h)
    # The skirting takes the lowest seam that sits in the bottom of the wall. Any
    # other horizontal seam becomes a rail, so no cut line is ever left blank.
    low = [s for s in seams_y if s > h * 0.6]
    skirt_top = min(low) if low else h - SKIRTING_FALLBACK_MM
    edges = _band_edges(seams_x, w, STRIPE_TARGET_MM)

    out = [_rect(0, 0, w, h, tok["wall"])]
    for i, (x0, x1) in enumerate(zip(edges, edges[1:])):
        if i % 2:
            out.append(_rect(x0, 0, x1 - x0, skirt_top, tok["wall_stripe"]))
    # Hairline between every stripe pair keeps the paper reading as paper.
    for x in edges[1:-1]:
        out.append(_line(x, 0, x, skirt_top, tok["wall_line"], 0.25, 0.7))

    rails = [s for s in seams_y if s < skirt_top - EPS_MM]
    if not rails:
        rails = [min(h * 0.16, 52.0)]
    for rail in rails:
        out.append(_line(0, rail, w, rail, tok["trim"], 0.8, 0.55))
        out.append(_line(0, rail + 2.2, w, rail + 2.2, tok["wall_line"], 0.4, 0.7))

    out.append(_rect(0, skirt_top, w, h - skirt_top, tok["skirting"]))
    out.append(_line(0, skirt_top, w, skirt_top, tok["trim"], 0.9, 0.8))
    out.append(_line(0, skirt_top + 3.5, w, skirt_top + 3.5, tok["trim"], 0.35, 0.45))
    # A seam inside the skirting board gets a moulding line of its own.
    for s in seams_y:
        if s > skirt_top + EPS_MM:
            out.append(_line(0, s, w, s, tok["trim"], 0.6, 0.5))
    return out, skirt_top


def _window(x: float, y: float, w: float, h: float, tok: dict) -> list[str]:
    out = [_rect(x - 4, y - 4, w + 8, h + 8, tok["trim"], rx=1.5),
           _rect(x, y, w, h, tok["sky"])]
    # A hill and a sun, so the view is part of the room's story.
    out.append(f'<path d="M{num(x)} {num(y + h)}L{num(x)} {num(y + h * 0.72)}'
               f'Q{num(x + w * 0.3)} {num(y + h * 0.46)} {num(x + w * 0.58)} {num(y + h * 0.68)}'
               f'Q{num(x + w * 0.8)} {num(y + h * 0.82)} {num(x + w)} {num(y + h * 0.6)}'
               f'L{num(x + w)} {num(y + h)}Z" fill="{tok["wall_stripe"]}"/>')
    out.append(f'<circle cx="{num(x + w * 0.74)}" cy="{num(y + h * 0.26)}" '
               f'r="{num(min(w, h) * 0.12)}" fill="{tok["accent"]}" opacity="0.85"/>')
    out.append(_line(x + w / 2, y, x + w / 2, y + h, tok["trim"], 1.6))
    out.append(_line(x, y + h / 2, x + w, y + h / 2, tok["trim"], 1.6))
    out.append(_rect(x - 4, y, w + 8, h + 8, "none", tok["trim"], 1.4))
    out.append(_rect(x - 9, y + h + 4, w + 18, 6, tok["skirting"], tok["trim"], 0.6, rx=1.0))
    for side in (0, 1):
        cx = x - 9 + side * (w + 18)
        d = 1 if side == 0 else -1
        out.append(f'<path d="M{num(cx)} {num(y - 8)}'
                   f'Q{num(cx + d * 16)} {num(y + h * 0.35)} {num(cx + d * 8)} {num(y + h + 2)}'
                   f'L{num(cx + d * 22)} {num(y + h + 2)}'
                   f'Q{num(cx + d * 26)} {num(y + h * 0.3)} {num(cx + d * 20)} {num(y - 8)}Z" '
                   f'fill="{tok["rug"]}" opacity="0.9"/>')
    out.append(_rect(x - 26, y - 12, w + 52, 6, tok["trim"], rx=2.0))
    return out


def back_wall(w: float, h: float, tok: dict, seams: dict) -> str:
    out, skirt_top = wall_base(w, h, tok, seams)
    ww, wh = w * 0.42, h * 0.40
    out += _window((w - ww) / 2, h * 0.27, ww, wh, tok)
    # Two small framed pictures, one each side of the window.
    for cx in (w * 0.16, w * 0.84):
        out.append(_rect(cx - 13, h * 0.33, 26, 20, tok["rug_alt"], tok["trim"], 1.2, rx=1.0))
        out.append(f'<path d="M{num(cx - 9)} {num(h * 0.33 + 16)}'
                   f'L{num(cx - 2)} {num(h * 0.33 + 7)}L{num(cx + 4)} {num(h * 0.33 + 14)}'
                   f'L{num(cx + 9)} {num(h * 0.33 + 9)}L{num(cx + 9)} {num(h * 0.33 + 16)}Z" '
                   f'fill="{tok["wall_stripe"]}"/>')
    return "".join(out)


def left_wall(w: float, h: float, tok: dict, seams: dict) -> str:
    """x = 0 at the back of the cube, x = w at the open front. Carries the door."""
    out, skirt_top = wall_base(w, h, tok, seams)
    dw, dx = w * 0.30, w * 0.58
    dy = h * 0.13
    out.append(_rect(dx - 4, dy - 4, dw + 8, skirt_top - dy + 4, tok["trim"], rx=1.5))
    out.append(_rect(dx, dy, dw, skirt_top - dy, tok["rug_alt"]))
    for py, ph in ((0.06, 0.34), (0.46, 0.44)):
        out.append(_rect(dx + dw * 0.16, dy + (skirt_top - dy) * py,
                         dw * 0.68, (skirt_top - dy) * ph,
                         "none", tok["trim"], 0.7, rx=1.0))
    out.append(f'<circle cx="{num(dx + dw * 0.86)}" cy="{num(dy + (skirt_top - dy) * 0.5)}" '
               f'r="3.2" fill="{tok["accent"]}"/>')
    # A coat hook rail on the wall behind the door.
    rail_y = h * 0.30
    out.append(_rect(w * 0.08, rail_y, w * 0.34, 4, tok["trim"], rx=1.0))
    for i in range(4):
        hx = w * 0.11 + i * w * 0.09
        out.append(_line(hx, rail_y + 4, hx, rail_y + 11, tok["trim"], 1.4))
    return "".join(out)


def right_wall(w: float, h: float, tok: dict, seams: dict) -> str:
    """Bookcase and a plant. Mirrors the left wall so the cube reads as a room."""
    out, skirt_top = wall_base(w, h, tok, seams)
    bx, bw = w * 0.14, w * 0.42
    by = h * 0.34
    out.append(_rect(bx, by, bw, skirt_top - by, tok["floor"], tok["trim"], 1.2, rx=1.0))
    shelves = 3
    step = (skirt_top - by) / shelves
    for i in range(1, shelves):
        out.append(_line(bx, by + step * i, bx + bw, by + step * i, tok["trim"], 1.0))
    colours = [tok["rug"], tok["wall_stripe"], tok["sky"], tok["accent"], tok["rug_alt"]]
    for row in range(shelves):
        x = bx + 3
        i = row
        while x < bx + bw - 6:
            bwid = 3.4 + (i % 3) * 1.6
            bhei = step * (0.52 + 0.12 * (i % 3))
            out.append(_rect(x, by + step * (row + 1) - bhei - 1.2, bwid, bhei,
                             colours[i % len(colours)], tok["trim"], 0.3, rx=0.8))
            x += bwid + 1.4
            i += 1
    px = w * 0.76
    out.append(_rect(px - 9, skirt_top - 16, 18, 16, tok["accent"], tok["trim"], 0.7, rx=1.5))
    for d, lean in ((-1, 0.7), (0, 1.0), (1, 0.7)):
        out.append(f'<path d="M{num(px)} {num(skirt_top - 16)}'
                   f'Q{num(px + d * 14)} {num(skirt_top - 30 * lean - 10)} '
                   f'{num(px + d * 8)} {num(skirt_top - 34 * lean - 12)}" '
                   f'stroke="{tok["wall_stripe"]}" stroke-width="2.4" fill="none" '
                   f'stroke-linecap="round"/>')
    return "".join(out)


# --------------------------------------------------------------------------- #
# Floor
# --------------------------------------------------------------------------- #

def floor(w: float, h: float, tok: dict, seams: dict, flap: float = 10.0) -> str:
    """Floorboards run back to front. y = 0 is the back of the cube."""
    seams_x = _seam_list(seams, "x", w)
    seams_y = _seam_list(seams, "y", h)
    edges = _band_edges(seams_x, w, PLANK_TARGET_MM)

    out = [_rect(0, 0, w, h, tok["floor"])]
    for x in edges[1:-1]:
        out.append(_line(x, 0, x, h, tok["floor_joint"], 0.5, 0.85))
    # End joints, staggered per plank. Every horizontal seam gets its own row,
    # and a seam row never staggers, because that row is the cut line.
    joint_rows = [(y, True) for y in seams_y] + [(h * 0.30, False), (h * 0.68, False)]
    for col, (x0, x1) in enumerate(zip(edges, edges[1:])):
        for j, (jy, on_seam) in enumerate(joint_rows):
            y = jy if on_seam else jy + ((col + j) % 3 - 1) * 18.0
            if flap < y < h - flap:
                out.append(_line(x0, y, x1, y, tok["floor_joint"], 0.5, 0.8))

    rw, rh = w * 0.56, h * 0.42
    rx, ry = (w - rw) / 2, h * 0.36
    out.append(_rect(rx, ry, rw, rh, tok["rug"], rx=4.0))
    out.append(_rect(rx + 6, ry + 6, rw - 12, rh - 12, "none", tok["rug_alt"], 1.6, rx=3.0))
    out.append(_rect(rx + 12, ry + 12, rw - 24, rh - 24, tok["rug_alt"], rx=2.5))
    out.append(_rect(rx + 20, ry + 20, rw - 40, rh - 40, tok["rug"], rx=2.0))
    for side in (0, 1):
        y = ry + side * rh
        d = -1 if side == 0 else 1
        fx = rx + 4
        while fx < rx + rw - 3:
            out.append(_line(fx, y, fx, y + d * -4, tok["rug"], 0.8, 0.9))
            fx += 5.0
    return "".join(out)


def roof(w: float, h: float, tok: dict, seams: dict) -> str:
    """Plain ceiling with a light rose — only printed when --ceiling is passed.

    The ceiling is one flat colour, so a seam would show as a bare step. Every cut
    line therefore carries a moulding line and reads as a panelled ceiling.
    """
    out = [_rect(0, 0, w, h, tok["rug_alt"])]
    for x in _seam_list(seams, "x", w):
        out.append(_line(x, 0, x, h, tok["trim"], 0.8, 0.45))
        out.append(_line(x + 2.2, 0, x + 2.2, h, tok["wall_line"], 0.4, 0.5))
    for y in _seam_list(seams, "y", h):
        out.append(_line(0, y, w, y, tok["trim"], 0.8, 0.45))
        out.append(_line(0, y + 2.2, w, y + 2.2, tok["wall_line"], 0.4, 0.5))
    out.append(f'<circle cx="{num(w / 2)}" cy="{num(h * 0.42)}" r="{num(min(w, h) * 0.11)}" '
               f'fill="none" stroke="{tok["trim"]}" stroke-width="1.2" opacity="0.7"/>')
    out.append(f'<circle cx="{num(w / 2)}" cy="{num(h * 0.42)}" r="{num(min(w, h) * 0.05)}" '
               f'fill="{tok["accent"]}" opacity="0.8"/>')
    return "".join(out)


BUILDERS = {
    "BACK": back_wall,
    "WALL-L": left_wall,
    "WALL-R": right_wall,
    "FLOOR": floor,
    "ROOF": roof,
}


def build_art(surfaces, tok: dict, seams: dict) -> dict[str, str]:
    """SVG for every surface, keyed by surface name."""
    empty = {"x": [], "y": []}
    return {s.name: BUILDERS[s.name](s.width_mm, s.height_mm, tok, seams.get(s.name, empty))
            for s in surfaces if s.name in BUILDERS}
