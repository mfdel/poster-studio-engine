"""FAM-003 promises a drawn feature on every seam. This test holds it to that.

docs/product.md tells the buyer that each glued join lands on a stripe edge, a
rail, the top of the skirting board, a floorboard joint or a ceiling moulding.
The artwork used to read only the first seam on each axis, so the claim was true
for the default Kallax cube and false for anything bigger. These cases cover both.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "posters" / "fam003-shelf-room"))

import room  # noqa: E402

from posterlab.chrome.tiling import (  # noqa: E402
    cube_surfaces, plan_cube, printable_sheet, seam_lines,
)
from posterlab.themes import load_theme, room_tokens  # noqa: E402

TOL_MM = 0.02          # two-decimal SVG coordinates, so this is the rounding only
SEGMENT = re.compile(r"M(-?[\d.]+) (-?[\d.]+)L(-?[\d.]+) (-?[\d.]+)")

CASES = [
    ((330.0, 330.0, 390.0), "A4"),      # the default: two pieces per axis
    ((330.0, 330.0, 390.0), "Letter"),
    ((600.0, 500.0, 500.0), "A4"),      # three pieces on an axis
    ((900.0, 700.0, 700.0), "A4"),      # four or more
    ((120.0, 120.0, 120.0), "A4"),      # small enough to have no seam at all
]


def _drawn_lines(svg: str) -> tuple[list[float], list[float]]:
    """The x of every vertical segment and the y of every horizontal one."""
    verticals, horizontals = [], []
    for x1, y1, x2, y2 in SEGMENT.findall(svg):
        x1, y1, x2, y2 = float(x1), float(y1), float(x2), float(y2)
        if abs(x1 - x2) <= TOL_MM and abs(y1 - y2) > TOL_MM:
            verticals.append(x1)
        elif abs(y1 - y2) <= TOL_MM and abs(x1 - x2) > TOL_MM:
            horizontals.append(y1)
    return verticals, horizontals


def _art(cube, size, ceiling=True):
    surfaces = cube_surfaces(*cube, cover_depth=cube[2] - 30.0, ceiling=ceiling)
    plan = plan_cube(surfaces, printable_sheet(size))
    tok = room_tokens(load_theme("whimsy"))
    return surfaces, seam_lines(plan), room.build_art(surfaces, tok, seam_lines(plan))


@pytest.mark.parametrize("cube,size", CASES)
def test_every_seam_carries_a_drawn_line(cube, size):
    surfaces, seams, art = _art(cube, size)
    for surface in surfaces:
        svg = art[surface.name]
        verticals, horizontals = _drawn_lines(svg)
        axes = seams.get(surface.name, {"x": [], "y": []})
        for seam in axes["x"]:
            assert any(abs(v - seam) <= TOL_MM for v in verticals), (
                f"{cube} {size} {surface.name}: no vertical line on x seam {seam}")
        for seam in axes["y"]:
            assert any(abs(hz - seam) <= TOL_MM for hz in horizontals), (
                f"{cube} {size} {surface.name}: no horizontal line on y seam {seam}")


@pytest.mark.parametrize("cube,size", CASES)
def test_artwork_stays_inside_its_surface(cube, size):
    """Nothing is drawn off the face; the tiler would clip it into a blank strip."""
    surfaces, _seams, art = _art(cube, size)
    for surface in surfaces:
        verticals, horizontals = _drawn_lines(art[surface.name])
        for v in verticals:
            assert -TOL_MM <= v <= surface.width_mm + TOL_MM, f"{surface.name} x={v}"
        for hz in horizontals:
            assert -TOL_MM <= hz <= surface.height_mm + TOL_MM, f"{surface.name} y={hz}"


def test_band_edges_land_on_every_seam():
    seams = [185.0, 365.0, 545.0]
    edges = room._band_edges(seams, 600.0, room.STRIPE_TARGET_MM)
    for seam in seams:
        assert any(abs(e - seam) <= 1e-9 for e in edges)
    assert edges[0] == pytest.approx(0.0)
    assert edges[-1] == pytest.approx(600.0)
    assert edges == sorted(edges)
    for a, b in zip(edges, edges[1:]):
        assert 0.5 * room.STRIPE_TARGET_MM < b - a < 2.0 * room.STRIPE_TARGET_MM


def test_band_edges_without_seams_are_the_plain_repeat():
    edges = room._band_edges([], 300.0, 30.0)
    assert edges == pytest.approx([30.0 * i for i in range(11)])


def test_every_face_is_drawn():
    for cube, size in CASES:
        surfaces, _seams, art = _art(cube, size)
        assert set(art) == {s.name for s in surfaces}
        for name, svg in art.items():
            assert svg.strip(), f"{name} rendered empty"
