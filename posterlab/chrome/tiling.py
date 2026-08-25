"""Tiled printing: one large surface -> many home-printer sheets.

A cube diorama (FAM-003) needs panels far bigger than A4, so each surface is cut
into pieces, every internal cut gets an overlap flap, and the pieces are packed
onto as few sheets as possible.

Two rules keep the output assemblable by a child's parent at a kitchen table:

* Pieces are packed by stacking them down the sheet, never side by side. Every
  cut line therefore runs straight across the page -- no L-shaped cutting.
* Seam positions come from the split, not from the packer, so the artwork can be
  drawn seam-aware (a wallpaper stripe or a floorboard joint on every seam).

All dimensions are millimetres, matching ``posterlab.chrome.page``.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from html import escape

from posterlab.chrome.page import page_size
from posterlab.svg.primitives import num

# Overlap flap on every internal cut. One glued edge, 10 mm, as costed in the
# sheet plan: a surface of length L in k pieces prints L + (k-1)*OVERLAP.
OVERLAP_MM = 10.0
# Unprintable border assumed on a consumer inkjet/laser, all four edges.
PRINT_MARGIN_MM = 10.0


@dataclass(frozen=True)
class Sheet:
    """The printable area of one sheet of paper."""
    name: str
    width_mm: float
    height_mm: float

    @property
    def area_mm2(self) -> float:
        return self.width_mm * self.height_mm


def printable_sheet(size: str = "A4", margin_mm: float = PRINT_MARGIN_MM) -> Sheet:
    w, h = page_size(size)
    return Sheet(size, w - 2 * margin_mm, h - 2 * margin_mm)


@dataclass(frozen=True)
class Surface:
    """One flat face of the finished object, in its own coordinate space.

    ``width_mm`` x ``height_mm`` is the *printed* extent, so it already includes
    any join flap that laps onto a neighbouring surface.
    """
    name: str
    width_mm: float
    height_mm: float


@dataclass(frozen=True)
class Piece:
    """A rectangle of one surface, cut out and printed on a single sheet.

    ``x``/``y``/``width_mm``/``height_mm`` are in surface space. ``rotated`` means
    the piece is turned a quarter turn to fit the sheet, so it takes up
    ``height_mm`` x ``width_mm`` of paper. Sides marked as flaps carry the overlap
    that glues under the neighbouring piece.
    """
    id: str
    surface: str
    x: float
    y: float
    width_mm: float
    height_mm: float
    flap_right: bool = False
    flap_bottom: bool = False
    rotated: bool = False

    @property
    def area_mm2(self) -> float:
        return self.width_mm * self.height_mm

    @property
    def sheet_size(self) -> tuple[float, float]:
        """Paper the piece occupies, (width_mm, height_mm)."""
        return (self.height_mm, self.width_mm) if self.rotated else (self.width_mm, self.height_mm)


@dataclass
class Placement:
    piece: Piece
    sheet_index: int
    at_x: float
    at_y: float


@dataclass
class Plan:
    sheet: Sheet
    surfaces: list[Surface]
    placements: list[Placement]
    sheet_count: int
    art_area_mm2: float = 0.0

    @property
    def efficiency(self) -> float:
        """Fraction of printable paper covered by artwork."""
        return self.art_area_mm2 / (self.sheet_count * self.sheet.area_mm2)

    def sheets(self) -> list[list[Placement]]:
        out: list[list[Placement]] = [[] for _ in range(self.sheet_count)]
        for p in self.placements:
            out[p.sheet_index].append(p)
        return out


def split_axis(length: float, max_len: float, overlap: float = OVERLAP_MM) -> list[float]:
    """Cut ``length`` into pieces of at most ``max_len``, each cut costing ``overlap``.

    Returns the printed length of each piece; the sum is
    ``length + (k - 1) * overlap``. Pieces are taken at full size first so most
    sheets are filled edge to edge and the offcuts collect at the end, where they
    stack together.
    """
    if length <= max_len:
        return [length]
    if max_len <= overlap:
        raise ValueError("Sheet is not bigger than the overlap; cannot tile.")
    k = math.ceil((length - overlap) / (max_len - overlap))
    total = length + (k - 1) * overlap
    pieces = [max_len] * (k - 1)
    pieces.append(round(total - max_len * (k - 1), 3))
    return pieces


def _grid_for(surface: Surface, sheet: Sheet, overlap: float,
              swap: bool) -> tuple[list[float], list[float], float, bool]:
    """Column and row splits for one axis assignment, plus printed area."""
    wmax, hmax = (sheet.height_mm, sheet.width_mm) if swap else (sheet.width_mm, sheet.height_mm)
    cols = split_axis(surface.width_mm, wmax, overlap)
    rows = split_axis(surface.height_mm, hmax, overlap)
    return cols, rows, sum(cols) * sum(rows), swap


def make_pieces(surface: Surface, sheet: Sheet, overlap: float = OVERLAP_MM) -> list[Piece]:
    """Cut one surface into pieces, choosing the cheaper of the two orientations."""
    candidates = [_grid_for(surface, sheet, overlap, swap) for swap in (False, True)]
    cols, rows, _, rotated = min(candidates, key=lambda c: (len(c[0]) * len(c[1]), c[2]))

    pieces: list[Piece] = []
    y = 0.0
    for r, row_h in enumerate(rows):
        x = 0.0
        for c, col_w in enumerate(cols):
            pieces.append(Piece(
                id=f"{surface.name}-{chr(ord('A') + r)}{c + 1}",
                surface=surface.name,
                x=x, y=y, width_mm=col_w, height_mm=row_h,
                flap_right=c < len(cols) - 1,
                flap_bottom=r < len(rows) - 1,
                rotated=rotated,
            ))
            x += col_w - overlap
        y += row_h - overlap
    return pieces


def pack(pieces: list[Piece], sheet: Sheet) -> tuple[list[Placement], int]:
    """Stack pieces down sheets, tallest first (first-fit-decreasing on height).

    Pieces are never placed side by side: two offcuts of a 330 mm surface are
    150 mm wide each and would need 300 mm of sheet width, which no home printer
    has. Stacking keeps every cut line straight across the page.
    """
    ordered = sorted(pieces, key=lambda p: (-p.sheet_size[1], -p.sheet_size[0]))
    used: list[float] = []           # height consumed on each open sheet
    placements: list[Placement] = []

    for piece in ordered:
        pw, ph = piece.sheet_size
        if pw > sheet.width_mm + 1e-6:
            raise ValueError(f"{piece.id} needs {pw} mm of width; sheet has {sheet.width_mm} mm")
        for i, top in enumerate(used):
            if top + ph <= sheet.height_mm + 1e-6:
                placements.append(Placement(piece, i, 0.0, top))
                used[i] = top + ph
                break
        else:
            placements.append(Placement(piece, len(used), 0.0, 0.0))
            used.append(ph)

    placements.sort(key=lambda p: (p.sheet_index, p.at_y))
    return placements, len(used)


def cube_surfaces(inner_w: float, inner_h: float, inner_d: float, *,
                  cover_depth: float | None = None,
                  ceiling: bool = False,
                  join_flap: float = OVERLAP_MM) -> list[Surface]:
    """The printed faces of an open cube (IKEA Kallax: 330 x 330 x 390).

    ``cover_depth`` stops the floor and walls short of the cube mouth; the last
    few millimetres sit behind the shelf lip and are never seen. Trimming a
    Kallax from 390 to 360 mm is what lets the offcut row pair up on US Letter.

    The floor carries the join flaps for all of its neighbours, so the wall and
    back pieces butt straight onto it.
    """
    depth = inner_d if cover_depth is None else min(cover_depth, inner_d)
    faces = [
        Surface("BACK", inner_w, inner_h),
        Surface("FLOOR", inner_w + 2 * join_flap, depth + join_flap),
        Surface("WALL-L", depth, inner_h),
        Surface("WALL-R", depth, inner_h),
    ]
    if ceiling:
        faces.append(Surface("ROOF", inner_w, depth))
    return faces


def plan_cube(surfaces: list[Surface], sheet: Sheet,
              overlap: float = OVERLAP_MM) -> Plan:
    pieces: list[Piece] = []
    for s in surfaces:
        pieces.extend(make_pieces(s, sheet, overlap))
    placements, count = pack(pieces, sheet)
    return Plan(
        sheet=sheet,
        surfaces=surfaces,
        placements=placements,
        sheet_count=count,
        art_area_mm2=sum(p.area_mm2 for p in pieces),
    )


def naive_sheet_count(surfaces: list[Surface], sheet: Sheet,
                      overlap: float = OVERLAP_MM) -> int:
    """Sheets used if each surface is tiled on its own, one piece per sheet."""
    return sum(len(make_pieces(s, sheet, overlap)) for s in surfaces)


# --------------------------------------------------------------------------- #
# Sheet pages
# --------------------------------------------------------------------------- #

_FLAP_FILL = "#000000"
_FLAP_OPACITY = 0.07


def _svg_open(w: float, h: float, page_fill: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{num(w)}mm" height="{num(h)}mm" '
        f'viewBox="0 0 {num(w)} {num(h)}">',
        f'<rect x="0" y="0" width="{num(w)}" height="{num(h)}" fill="{page_fill}"/>',
    ]


def _corner_marks(x: float, y: float, w: float, h: float, color: str,
                  arm: float = 4.0) -> str:
    """Crosshair arms at the four corners of a cut rectangle."""
    d = []
    for cx, cy in ((x, y), (x + w, y), (x, y + h), (x + w, y + h)):
        d.append(f"M{num(cx - arm)} {num(cy)}H{num(cx + arm)}")
        d.append(f"M{num(cx)} {num(cy - arm)}V{num(cy + arm)}")
    return (f'<path d="{"".join(d)}" fill="none" stroke="{color}" '
            f'stroke-width="0.25" opacity="0.75"/>')


def _flap_marks(piece: Piece, flap: float) -> str:
    """Grey the overlap strips, drawn in surface space so rotation is free."""
    out = []
    if piece.flap_right:
        out.append(f'<rect x="{num(piece.x + piece.width_mm - flap)}" y="{num(piece.y)}" '
                   f'width="{num(flap)}" height="{num(piece.height_mm)}" '
                   f'fill="{_FLAP_FILL}" opacity="{_FLAP_OPACITY}"/>')
    if piece.flap_bottom:
        out.append(f'<rect x="{num(piece.x)}" y="{num(piece.y + piece.height_mm - flap)}" '
                   f'width="{num(piece.width_mm)}" height="{num(flap)}" '
                   f'fill="{_FLAP_FILL}" opacity="{_FLAP_OPACITY}"/>')
    return "".join(out)


def render_sheet_svg(plan: Plan, sheet_index: int, art: dict[str, str], theme: dict,
                     *, size: str = "A4", margin_mm: float = PRINT_MARGIN_MM,
                     total_pages: int = 0, page_number: int = 0,
                     footer: str = "") -> str:
    """One printable sheet: its pieces stacked, cut lines, flap tints, IDs.

    ``art`` maps a surface name to the SVG for that whole surface, drawn in the
    surface's own coordinate space. Each piece clips its window out of that SVG,
    so the artwork stays continuous across a cut without the caller slicing it.
    """
    pal = theme["palette"]
    label_font = theme["type"]["label_font"]
    ink, muted = pal["text"], pal["muted"]
    W, H = page_size(size)
    flap = OVERLAP_MM

    out = _svg_open(W, H, pal["page"])
    for n, pl in enumerate(plan.sheets()[sheet_index]):
        piece = pl.piece
        pw, ph = piece.sheet_size
        px, py = margin_mm + pl.at_x, margin_mm + pl.at_y
        clip = f"clip{sheet_index}-{n}"

        if piece.rotated:
            # rotate(90) sends (u,v) -> (-v,u); shifting by the piece height puts
            # the w x h surface rectangle back inside the h x w paper rectangle.
            xform = (f"translate({num(px + piece.height_mm)} {num(py)}) rotate(90) "
                     f"translate({num(-piece.x)} {num(-piece.y)})")
        else:
            xform = f"translate({num(px - piece.x)} {num(py - piece.y)})"

        out.append(f'<clipPath id="{clip}"><rect x="{num(px)}" y="{num(py)}" '
                   f'width="{num(pw)}" height="{num(ph)}"/></clipPath>')
        out.append(f'<g clip-path="url(#{clip})"><g transform="{xform}">')
        out.append(art.get(piece.surface, ""))
        out.append(_flap_marks(piece, flap))
        out.append("</g></g>")
        out.append(f'<rect x="{num(px)}" y="{num(py)}" width="{num(pw)}" height="{num(ph)}" '
                   f'fill="none" stroke="{ink}" stroke-width="0.3" '
                   f'stroke-dasharray="2 1.5" opacity="0.55"/>')
        out.append(_corner_marks(px, py, pw, ph, ink))
        # The piece id rides in the left margin, never on the artwork.
        out.append(f'<text x="{num(margin_mm * 0.55)}" y="{num(py + ph / 2)}" '
                   f'transform="rotate(-90 {num(margin_mm * 0.55)} {num(py + ph / 2)})" '
                   f'text-anchor="middle" font-family="{escape(label_font)}" font-size="3.2" '
                   f'fill="{muted}">{piece.id}</text>')

    if page_number:
        out.append(f'<text x="{num(W / 2)}" y="{num(H - margin_mm * 0.35)}" '
                   f'text-anchor="middle" font-family="{escape(label_font)}" font-size="3.2" '
                   f'fill="{muted}">Sheet {page_number} of {total_pages}'
                   f'{"  |  " + escape(footer) if footer else ""}</text>')
    out.append("</svg>")
    return "\n".join(out)


def render_calibration_svg(plan: Plan, theme: dict, *, size: str = "A4",
                           margin_mm: float = PRINT_MARGIN_MM,
                           title: str = "", lines: tuple[str, ...] = ()) -> str:
    """Page one: the 50 mm test square that proves the printer scaled nothing."""
    pal = theme["palette"]
    ink, muted, accent = pal["text"], pal["muted"], pal["border"]
    title_font, label_font = theme["type"]["title_font"], theme["type"]["label_font"]
    W, H = page_size(size)
    box = 50.0
    bx, by = (W - box) / 2, margin_mm + 62.0

    out = _svg_open(W, H, pal["page"])
    out.append(f'<text x="{num(W / 2)}" y="{num(margin_mm + 18)}" text-anchor="middle" '
               f'font-family="{escape(title_font)}" font-size="9" fill="{ink}">{escape(title)}</text>')
    y = margin_mm + 30
    for line in lines:
        out.append(f'<text x="{num(W / 2)}" y="{num(y)}" text-anchor="middle" '
                   f'font-family="{escape(label_font)}" font-size="4" fill="{muted}">{escape(line)}</text>')
        y += 6.5
    out.append(f'<rect x="{num(bx)}" y="{num(by)}" width="{num(box)}" height="{num(box)}" '
               f'fill="none" stroke="{accent}" stroke-width="0.6"/>')
    out.append(f'<text x="{num(W / 2)}" y="{num(by + box / 2 + 1.5)}" text-anchor="middle" '
               f'font-family="{escape(label_font)}" font-size="4.5" fill="{ink}">'
               f'50 mm / 1.97 in</text>')
    out.append(f'<text x="{num(W / 2)}" y="{num(by + box + 9)}" text-anchor="middle" '
               f'font-family="{escape(label_font)}" font-size="4" fill="{muted}">'
               f'Measure this square. If it is not 50 mm, print again at Actual Size.</text>')

    y = by + box + 24
    out.append(f'<text x="{num(margin_mm + 6)}" y="{num(y)}" font-family="{escape(label_font)}" '
               f'font-size="4.4" fill="{ink}">Sheets in this pack</text>')
    y += 7
    for s in plan.surfaces:
        ids = sorted({p.piece.id for p in plan.placements if p.piece.surface == s.name})
        out.append(f'<text x="{num(margin_mm + 6)}" y="{num(y)}" font-family="{escape(label_font)}" '
                   f'font-size="3.8" fill="{muted}">{escape(s.name)}: {", ".join(ids)}</text>')
        y += 5.5
    out.append("</svg>")
    return "\n".join(out)


def seam_lines(plan: Plan, overlap: float = OVERLAP_MM) -> dict[str, dict[str, list[float]]]:
    """Where each surface is cut, in surface coordinates.

    Artwork uses this to put a real line on every seam — a dado rail, a floorboard
    joint, a wallpaper stripe edge — so a glued join reads as part of the drawing.
    """
    out: dict[str, dict[str, list[float]]] = {}
    for pl in plan.placements:
        p = pl.piece
        s = out.setdefault(p.surface, {"x": [], "y": []})
        if p.flap_right:
            s["x"].append(round(p.x + p.width_mm - overlap / 2, 3))
        if p.flap_bottom:
            s["y"].append(round(p.y + p.height_mm - overlap / 2, 3))
    for s in out.values():
        s["x"] = sorted(set(s["x"]))
        s["y"] = sorted(set(s["y"]))
    return out


# Where each face sits when the cube is unfolded flat, as multiples of the
# neighbouring face's size. Used for the assembly map only.
_NET_ORDER = ("ROOF", "WALL-L", "BACK", "WALL-R", "FLOOR")


def _net_layout(surfaces: list[Surface]) -> tuple[dict[str, tuple[float, float, bool]], float, float]:
    by = {s.name: s for s in surfaces}
    back = by["BACK"]
    dep = by["WALL-L"].width_mm if "WALL-L" in by else 0.0
    roof_h = by["ROOF"].height_mm if "ROOF" in by else 0.0
    ox, oy = dep, roof_h
    pos: dict[str, tuple[float, float, bool]] = {"BACK": (ox, oy, False)}
    if "WALL-L" in by:
        pos["WALL-L"] = (0.0, oy, True)       # mirrored: its front edge faces out
    if "WALL-R" in by:
        pos["WALL-R"] = (ox + back.width_mm, oy, False)
    if "FLOOR" in by:
        f = by["FLOOR"]
        pos["FLOOR"] = (ox - (f.width_mm - back.width_mm) / 2, oy + back.height_mm, False)
    if "ROOF" in by:
        pos["ROOF"] = (ox, 0.0, False)
    w = dep * 2 + back.width_mm
    h = roof_h + back.height_mm + (by["FLOOR"].height_mm if "FLOOR" in by else 0.0)
    return pos, w, h


def render_net_svg(plan: Plan, art: dict[str, str], theme: dict, *,
                   size: str = "A4", margin_mm: float = PRINT_MARGIN_MM,
                   title: str = "", note: str = "") -> str:
    """The assembly map: the cube unfolded flat, every piece outlined and named."""
    pal = theme["palette"]
    ink, muted = pal["text"], pal["muted"]
    label_font = theme["type"]["label_font"]
    W, H = page_size(size)
    pos, nw, nh = _net_layout(plan.surfaces)

    top = margin_mm + 22
    avail_w, avail_h = W - 2 * margin_mm, H - top - margin_mm - 10
    k = min(avail_w / nw, avail_h / nh)
    ox = (W - nw * k) / 2
    oy = top + (avail_h - nh * k) / 2

    out = _svg_open(W, H, pal["page"])
    out.append(f'<text x="{num(W / 2)}" y="{num(margin_mm + 12)}" text-anchor="middle" '
               f'font-family="{escape(theme["type"]["title_font"])}" font-size="8" fill="{ink}">'
               f'{title}</text>')
    out.append(f'<g transform="translate({num(ox)} {num(oy)}) scale({num(k)})">')
    for s in plan.surfaces:
        if s.name not in pos:
            continue
        x, y, mirror = pos[s.name]
        flip = (f"translate({num(x + s.width_mm)} {num(y)}) scale(-1 1)" if mirror
                else f"translate({num(x)} {num(y)})")
        clip = f"net-{s.name}"
        out.append(f'<clipPath id="{clip}"><rect x="0" y="0" '
                   f'width="{num(s.width_mm)}" height="{num(s.height_mm)}"/></clipPath>')
        out.append(f'<g transform="{flip}"><g clip-path="url(#{clip})">')
        out.append(art.get(s.name, ""))
        out.append("</g>")
        out.append(f'<rect x="0" y="0" width="{num(s.width_mm)}" height="{num(s.height_mm)}" '
                   f'fill="none" stroke="{ink}" stroke-width="{num(1.2 / k)}"/>')
        for pl in plan.placements:
            p = pl.piece
            if p.surface != s.name:
                continue
            out.append(f'<rect x="{num(p.x)}" y="{num(p.y)}" width="{num(p.width_mm)}" '
                       f'height="{num(p.height_mm)}" fill="none" stroke="{ink}" '
                       f'stroke-width="{num(0.7 / k)}" stroke-dasharray="{num(6 / k)} {num(4 / k)}" '
                       f'opacity="0.8"/>')
        out.append("</g>")
        # Ids sit outside the mirrored group so the text never reads backwards.
        for pl in plan.placements:
            p = pl.piece
            if p.surface != s.name:
                continue
            cx = (x + s.width_mm - p.x - p.width_mm / 2) if mirror else (x + p.x + p.width_mm / 2)
            ty = y + p.y + p.height_mm / 2
            out.append(f'<rect x="{num(cx - 13 / k)}" y="{num(ty - 3.4 / k)}" '
                       f'width="{num(26 / k)}" height="{num(5 / k)}" rx="{num(1.2 / k)}" '
                       f'fill="{pal["page"]}" opacity="0.85"/>')
            out.append(f'<text x="{num(cx)}" y="{num(ty + 1.4 / k)}" '
                       f'text-anchor="middle" font-family="{escape(label_font)}" '
                       f'font-size="{num(4.2 / k)}" fill="{ink}" opacity="0.95">{p.id}</text>')
    out.append("</g>")
    if note:
        out.append(f'<text x="{num(W / 2)}" y="{num(H - margin_mm)}" text-anchor="middle" '
                   f'font-family="{escape(label_font)}" font-size="3.6" fill="{muted}">{escape(note)}</text>')
    out.append("</svg>")
    return "\n".join(out)
