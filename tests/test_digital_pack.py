"""The digital download must hold every sheet the render loop produced.

FAM-002 sells one ZIP of eight PDFs: two themes x two layouts x two paper sizes.
The seller used to render it with a shell loop of eight `render.py` calls, each
with `--zip`. Every call rebuilt the archive from its own single PDF, and the
name was keyed on the theme alone, so the loop left two ZIPs of one sheet each
and a buyer received a quarter of the product.

These tests hold the two rules that make that impossible: one call renders the
whole selection into one archive, and no two selections share an archive name.
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "posters" / "fam002-halloween-night"))

import render  # noqa: E402

from posterlab.chrome import resolve_sizes  # noqa: E402
from posterlab.export import build_zip  # noqa: E402
from posterlab.themes import resolve_themes  # noqa: E402

# The pack the listing sells, as the one command a seller now runs.
PACK = {"theme": "lantern,ink", "layout": "band,bonus", "size": "Letter,A4"}


def _file(dir_: Path, name: str) -> Path:
    p = dir_ / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(name, encoding="utf-8")
    return p


# --------------------------------------------------------------------------- #
# The archive
# --------------------------------------------------------------------------- #

def test_build_zip_reports_what_it_packed(tmp_path):
    files = [_file(tmp_path, "a.pdf"), _file(tmp_path, "b.pdf"),
             _file(tmp_path, "HOW-TO-PRINT.txt")]
    zip_path = tmp_path / "pack.zip"
    packed = build_zip(zip_path, files)
    assert packed == ["a.pdf", "b.pdf", "HOW-TO-PRINT.txt"]
    with zipfile.ZipFile(zip_path) as zf:
        assert zf.namelist() == packed


def test_build_zip_refuses_to_swallow_a_file(tmp_path):
    """A flat archive keeps only the last member of a repeated name. Refuse it —
    a silently short download is worse than a failed render."""
    files = [_file(tmp_path / "Letter", "sheet.pdf"),
             _file(tmp_path / "A4", "sheet.pdf")]
    zip_path = tmp_path / "pack.zip"
    build_zip(zip_path, [_file(tmp_path, "kept.pdf")])

    with pytest.raises(SystemExit):
        build_zip(zip_path, files)

    # The guard runs before the archive is opened for writing, so the pack that
    # was already there is still whole.
    with zipfile.ZipFile(zip_path) as zf:
        assert zf.namelist() == ["kept.pdf"]


# --------------------------------------------------------------------------- #
# The selection
# --------------------------------------------------------------------------- #

def test_every_axis_takes_a_list():
    assert resolve_themes(PACK["theme"]) == ["lantern", "ink"]
    assert render.resolve_layouts(PACK["layout"]) == ["band", "bonus"]
    assert resolve_sizes(PACK["size"]) == ["Letter", "A4"]


def test_the_old_single_and_all_forms_still_mean_what_they_meant():
    assert render.resolve_layouts("panel") == ["panel"]
    assert render.resolve_layouts("all") == list(render.LAYOUTS)
    assert resolve_sizes("A4") == ["A4"]
    assert resolve_themes("lantern") == ["lantern"]


def test_a_name_asked_for_twice_is_rendered_once():
    assert render.resolve_layouts("band,band,bonus") == ["band", "bonus"]
    assert resolve_sizes("A4,all") == list(resolve_sizes("all"))


def test_an_unknown_layout_stops_the_render():
    with pytest.raises(SystemExit):
        render.resolve_layouts("panl")


# --------------------------------------------------------------------------- #
# The archive name
# --------------------------------------------------------------------------- #

def test_two_packs_cannot_share_a_name():
    """One out_dir holds every pack rendered for a run. The sold pack, one sheet
    out of it, and the same selection in landscape are three different products."""
    names = {
        render.zip_name("sofia", ["lantern", "ink"], ["Letter", "A4"],
                        ["band", "bonus"], "portrait"),
        render.zip_name("sofia", ["lantern"], ["Letter"], ["band"], "portrait"),
        render.zip_name("sofia", ["ink"], ["Letter"], ["band"], "portrait"),
        render.zip_name("sofia", ["lantern", "ink"], ["Letter", "A4"],
                        ["band", "bonus"], "landscape"),
    }
    assert len(names) == 4


def test_the_zip_name_reads_like_the_sheets_inside():
    """Same axes, same order as ``<slug>_<theme>_<size>_<layout>_<orientation>``."""
    assert render.zip_name("sofia", ["lantern", "ink"], ["Letter", "A4"],
                           ["band", "bonus"], "portrait") == \
        "sofia_lantern-ink_Letter-A4_band-bonus_digital.zip"


# --------------------------------------------------------------------------- #
# End to end
# --------------------------------------------------------------------------- #

def _latest_basemap() -> Path | None:
    """The newest saved run, or None. Runs are regenerable and gitignored, so
    this test is skipped wherever ``data/runs/halloween/`` is empty."""
    from posterlab.runstore import resolve_run
    try:
        path = resolve_run("latest", render.KIND) / "basemap.geojson"
    except SystemExit:
        return None
    return path if path.exists() else None


def test_the_zip_holds_every_pdf_the_call_rendered(tmp_path):
    basemap = _latest_basemap()
    if basemap is None:
        pytest.skip("no saved halloween run — run make.py once to fetch one")

    # Two themes, one layout, one size: the smallest selection that spans the
    # axis the old code split its archives on.
    written = render.render_run(basemap, theme="lantern,ink", layout="band",
                                size="Letter", title="Pack Test",
                                out_dir=tmp_path, make_zip=True)
    assert len(written) == 2

    zips = list(tmp_path.glob("*.zip"))
    assert len(zips) == 1, "one call must leave one pack, not one pack per theme"
    with zipfile.ZipFile(zips[0]) as zf:
        packed = zf.namelist()
    assert sorted(n for n in packed if n.endswith(".pdf")) == sorted(p.name for p in written)
    assert "HOW-TO-PRINT.txt" in packed and "LICENSE-ATTRIBUTION.txt" in packed
