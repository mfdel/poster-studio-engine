"""Invariants of posterlab.chrome.tiling.

The tiler is what makes FAM-003 printable at home: it cuts each cube face into
sheet-sized pieces, packs them, and reports where the cuts land. Every assertion
here is something a buyer feels if it breaks -- a panel that does not reach its
neighbour, a piece that runs off the paper, or a seam with no drawing on it.
"""
from __future__ import annotations

import itertools

import pytest

from posterlab.chrome.tiling import (
    OVERLAP_MM,
    cube_surfaces,
    naive_sheet_count,
    plan_cube,
    printable_sheet,
    seam_lines,
    split_axis,
)

SIZES = ("A4", "Letter")
CUBES = [
    (330.0, 330.0, 390.0),   # IKEA Kallax, the default
    (300.0, 300.0, 300.0),   # smaller cube, fewer splits
    (600.0, 500.0, 500.0),   # big cube, three pieces on an axis
]


def _plans():
    """Every (cube, paper, ceiling) case, with a label to name a failure by."""
    for cube, size in itertools.product(CUBES, SIZES):
        for ceiling in (False, True):
            surfaces = cube_surfaces(*cube, cover_depth=cube[2] - 30.0, ceiling=ceiling)
            label = f"{cube[0]:.0f}x{cube[1]:.0f}x{cube[2]:.0f} {size} ceiling={ceiling}"
            yield label, surfaces, plan_cube(surfaces, printable_sheet(size))


# --------------------------------------------------------------------------- #
# split_axis
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("length", [50.0, 189.0, 190.0, 330.0, 371.0, 600.0, 2000.0])
@pytest.mark.parametrize("max_len", [190.0, 272.0, 60.0])
def test_split_pays_one_overlap_per_cut(length, max_len):
    """k pieces of a length-L axis print L + (k-1) * overlap."""
    pieces = split_axis(length, max_len, OVERLAP_MM)
    assert sum(pieces) == pytest.approx(length + (len(pieces) - 1) * OVERLAP_MM)


@pytest.mark.parametrize("length", [50.0, 330.0, 600.0, 2000.0])
def test_split_never_exceeds_the_sheet(length):
    for piece in split_axis(length, 190.0, OVERLAP_MM):
        assert piece <= 190.0 + 1e-9
        assert piece > 0.0


def test_split_leaves_a_short_surface_whole():
    assert split_axis(180.0, 190.0, OVERLAP_MM) == [180.0]


def test_split_refuses_a_sheet_smaller_than_the_overlap():
    with pytest.raises(ValueError):
        split_axis(500.0, OVERLAP_MM, OVERLAP_MM)


# --------------------------------------------------------------------------- #
# plan_cube
# --------------------------------------------------------------------------- #

def test_pieces_stay_on_the_paper():
    for label, _surfaces, plan in _plans():
        for pl in plan.placements:
            pw, ph = pl.piece.sheet_size
            where = f"{label} {pl.piece.id}"
            assert pl.at_x + pw <= plan.sheet.width_mm + 1e-6, where
            assert pl.at_y + ph <= plan.sheet.height_mm + 1e-6, where
            assert pl.at_x >= -1e-6 and pl.at_y >= -1e-6, where


def test_pieces_never_overlap_on_a_sheet():
    for label, _surfaces, plan in _plans():
        for sheet_index, placements in enumerate(plan.sheets()):
            for a, b in itertools.combinations(placements, 2):
                aw, ah = a.piece.sheet_size
                bw, bh = b.piece.sheet_size
                apart = (a.at_x + aw <= b.at_x + 1e-6 or b.at_x + bw <= a.at_x + 1e-6
                         or a.at_y + ah <= b.at_y + 1e-6 or b.at_y + bh <= a.at_y + 1e-6)
                assert apart, f"{label} sheet {sheet_index}: {a.piece.id} hits {b.piece.id}"


def test_every_sheet_index_is_used():
    for label, _surfaces, plan in _plans():
        used = {pl.sheet_index for pl in plan.placements}
        assert used == set(range(plan.sheet_count)), label


def test_pieces_cover_every_surface_exactly():
    """Pieces span the whole face in surface space, lapping by the overlap.

    Piece rectangles are in surface coordinates, so neighbours share the flap and
    the outer extent is the true face size. The paper cost of the cuts shows up in
    the summed widths instead, one overlap per cut.
    """
    for label, surfaces, plan in _plans():
        for surface in surfaces:
            pieces = [pl.piece for pl in plan.placements if pl.piece.surface == surface.name]
            assert pieces, f"{surface.name} has no pieces"
            cols = sorted({p.x for p in pieces})
            rows = sorted({p.y for p in pieces})
            where = f"{label} {surface.name}"
            assert cols[0] == pytest.approx(0.0), where
            assert rows[0] == pytest.approx(0.0), where
            assert max(p.x + p.width_mm for p in pieces) == pytest.approx(surface.width_mm), where
            assert max(p.y + p.height_mm for p in pieces) == pytest.approx(surface.height_mm), where

            # One row of pieces pays exactly one overlap per internal cut.
            top = [p for p in pieces if p.y == rows[0]]
            printed = sum(p.width_mm for p in sorted(top, key=lambda p: p.x))
            assert printed == pytest.approx(surface.width_mm + (len(cols) - 1) * OVERLAP_MM), where
            left = [p for p in pieces if p.x == cols[0]]
            printed = sum(p.height_mm for p in sorted(left, key=lambda p: p.y))
            assert printed == pytest.approx(surface.height_mm + (len(rows) - 1) * OVERLAP_MM), where


def test_neighbouring_pieces_lap_by_the_overlap():
    for label, surfaces, plan in _plans():
        for surface in surfaces:
            pieces = [pl.piece for pl in plan.placements if pl.piece.surface == surface.name]
            rows = sorted({p.y for p in pieces})
            top = sorted((p for p in pieces if p.y == rows[0]), key=lambda p: p.x)
            for a, b in zip(top, top[1:]):
                where = f"{label} {surface.name}"
                assert (a.x + a.width_mm) - b.x == pytest.approx(OVERLAP_MM), where
                assert a.flap_right, where


def test_packing_never_loses_to_one_piece_per_sheet():
    for label, surfaces, plan in _plans():
        assert plan.sheet_count <= naive_sheet_count(surfaces, plan.sheet), label
        assert plan.sheet_count <= len(plan.placements), label


def test_kallax_a4_eco_is_eleven_sheets():
    """The number quoted in docs/product.md and in the listing copy."""
    surfaces = cube_surfaces(330.0, 330.0, 390.0, cover_depth=360.0)
    plan = plan_cube(surfaces, printable_sheet("A4"))
    assert plan.sheet_count == 11
    assert naive_sheet_count(surfaces, printable_sheet("A4")) == 16


def test_the_ceiling_costs_two_more_a4_sheets():
    """The claim in dashboard.json."""
    def count(ceiling):
        surfaces = cube_surfaces(330.0, 330.0, 390.0, cover_depth=360.0, ceiling=ceiling)
        return plan_cube(surfaces, printable_sheet("A4")).sheet_count
    assert count(True) - count(False) == 2


# --------------------------------------------------------------------------- #
# seam_lines
# --------------------------------------------------------------------------- #

def test_every_seam_falls_on_a_piece_boundary():
    """A seam is the middle of an overlap, so it is a cut edge minus half a flap."""
    for label, _surfaces, plan in _plans():
        seams = seam_lines(plan)
        for name, axes in seams.items():
            pieces = [pl.piece for pl in plan.placements if pl.piece.surface == name]
            right = {round(p.x + p.width_mm - OVERLAP_MM / 2, 3) for p in pieces if p.flap_right}
            bottom = {round(p.y + p.height_mm - OVERLAP_MM / 2, 3) for p in pieces if p.flap_bottom}
            assert set(axes["x"]) == right, f"{label} {name}"
            assert set(axes["y"]) == bottom, f"{label} {name}"


def test_seams_are_sorted_unique_and_inside_the_surface():
    for label, surfaces, plan in _plans():
        by_name = {s.name: s for s in surfaces}
        for name, axes in seam_lines(plan).items():
            surface = by_name[name]
            for axis, extent in (("x", surface.width_mm), ("y", surface.height_mm)):
                values = axes[axis]
                assert values == sorted(set(values)), f"{label} {name}.{axis}"
                for v in values:
                    assert 0.0 < v < extent + OVERLAP_MM * len(values), f"{label} {name}.{axis}"


def test_a_single_sheet_surface_has_no_seams():
    surfaces = cube_surfaces(120.0, 120.0, 120.0, cover_depth=120.0)
    plan = plan_cube(surfaces, printable_sheet("A4"))
    for axes in seam_lines(plan).values():
        assert axes == {"x": [], "y": []}
