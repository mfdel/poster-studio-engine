#!/usr/bin/env python3
"""FAM-003 Shelf Room — entry point.

Builds a print-at-home pack that turns one cube shelf into a room: a calibration
page, an assembly map, and the tiled sheets. No network and no data run; the
artwork is generated, so this is a pure render.

    uv run python posters/fam003-shelf-room/make.py --theme whimsy
    uv run python posters/fam003-shelf-room/make.py --cube 380x380x400 --size Letter
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import cairosvg
from pypdf import PdfWriter

import room
from posterlab.chrome.tiling import (
    OVERLAP_MM, cube_surfaces, naive_sheet_count, plan_cube, printable_sheet,
    render_calibration_svg, render_net_svg, render_sheet_svg, seam_lines,
)
from posterlab.export import build_zip, write_deliverable_notes
from posterlab.paths import OUTPUT
from posterlab.runstore import make_run_id
from posterlab.themes import load_theme, room_tokens

KIND = "room"
PRODUCT = "Shelf Room"
LICENSE_TEXT = """LICENSE
=======

Design
------
The artwork, layout and typography in this pack are original work.

Your purchase
-------------
You may print this design for your own personal, non-commercial use as many
times as you like. Please do not resell or redistribute the files themselves.

Compatibility
-------------
This pack fits cube shelves with an inside opening of 33 x 33 cm (13 x 13 in).
It is not affiliated with, endorsed by, or sponsored by Inter IKEA Systems B.V.
IKEA and KALLAX are trademarks of Inter IKEA Systems B.V.
"""


def howto(plans: dict, cube: tuple[float, float, float], easy: bool) -> str:
    """The printed instructions. ``plans`` is one plan per paper size in the pack.

    The bundle carries a single HOW-TO-PRINT.txt, so with ``--size both`` every
    paper-dependent line has to name both papers. Naming only one sends half the
    buyers to the wrong PDF.
    """
    mode = "Easy" if easy else "Eco"
    sizes = list(plans)
    if len(sizes) == 1:
        paper = f"Use {sizes[0]} paper."
        pdf_line = ""
    else:
        paper = f"Use {' or '.join(sizes)} paper."
        pdf_line = ("\n   This pack holds one PDF per paper size. The paper size is in the\n"
                    "   file name. Print the PDF that matches the paper in your printer.")
    sheets = ", ".join(f"{s} {plans[s].sheet_count}" for s in sizes)
    covered = ", ".join(f"{s} {plans[s].efficiency:.0%}" for s in sizes)
    return f"""HOW TO PRINT
============

1. Print every page at 100 percent. Turn off "Fit to page" and "Shrink to fit".
2. Measure the square on page 1. It must be 50 mm across. If it is not, print again.
3. {paper} Thicker paper holds its shape better. 160 gsm is ideal.{pdf_line}
4. Cut each panel on the dashed line.
5. Page 2 shows where each panel goes. The panel name is printed in the margin.
6. Glue the grey strips. A grey strip always goes UNDER the next panel.
7. Fit the floor first. Then the back. Then the two side walls.

Pack
----
Cube inside size: {cube[0]:.0f} x {cube[1]:.0f} x {cube[2]:.0f} mm
Print mode: {mode}
Sheets of artwork: {sheets}
Overlap on every join: {OVERLAP_MM:.0f} mm
Paper covered by artwork: {covered}
"""


def main() -> None:
    ap = argparse.ArgumentParser(description="FAM-003 Shelf Room — printable cube room")
    ap.add_argument("--cube", default="330x330x390",
                    help="inside size of the cube in mm, WxHxD (default IKEA Kallax)")
    ap.add_argument("--cover-depth", type=float, default=360.0,
                    help="mm of depth to cover; the rest hides behind the shelf lip")
    ap.add_argument("--size", default="A4", choices=("A4", "Letter", "both"))
    ap.add_argument("--theme", default="whimsy")
    ap.add_argument("--ceiling", action="store_true", help="also print the ceiling")
    ap.add_argument("--easy", action="store_true",
                    help="one panel per sheet — more paper, less cutting")
    ap.add_argument("--preview", action="store_true", help="also write a preview PNG")
    args = ap.parse_args()

    try:
        cube = tuple(float(v) for v in args.cube.lower().split("x"))
        if len(cube) != 3:
            raise ValueError
    except ValueError as err:
        raise SystemExit(
            f"--cube wants WxHxD in mm, for example 330x330x390 (got {args.cube!r})") from err

    theme = load_theme(args.theme)
    tok = room_tokens(theme)
    sizes = ["A4", "Letter"] if args.size == "both" else [args.size]
    run_id = make_run_id(f"{args.theme}-cube", "local", [f"{int(cube[0])}mm"])
    out_dir = OUTPUT / KIND / run_id
    written: list[Path] = []
    plans: dict[str, object] = {}

    for size in sizes:
        sheet = printable_sheet(size)
        surfaces = cube_surfaces(*cube, cover_depth=args.cover_depth, ceiling=args.ceiling)
        plan = plan_cube(surfaces, sheet)
        plans[size] = plan
        if args.easy:
            # One piece per sheet: the pack costs more paper but never asks the
            # buyer to find two panels on one page.
            plan.sheet_count = len(plan.placements)
            for i, pl in enumerate(plan.placements):
                pl.sheet_index, pl.at_x, pl.at_y = i, 0.0, 0.0
        art = room.build_art(surfaces, tok, seam_lines(plan))

        total = plan.sheet_count + 2
        pages = [
            render_calibration_svg(plan, theme, size=size, title=f"{PRODUCT} — {args.theme}",
                                   lines=("Print at 100 percent. Do not fit to page.",
                                          f"{plan.sheet_count} sheets of artwork follow.")),
            render_net_svg(plan, art, theme, size=size, title="Where each panel goes",
                           note="Dashed lines are cut lines. Grey strips glue underneath."),
        ]
        pages += [render_sheet_svg(plan, i, art, theme, size=size, page_number=i + 3,
                                   total_pages=total, footer=PRODUCT)
                  for i in range(plan.sheet_count)]

        out_dir.mkdir(parents=True, exist_ok=True)
        merger = PdfWriter()
        for n, svg in enumerate(pages):
            page_pdf = out_dir / f".page{n:02d}.pdf"
            cairosvg.svg2pdf(bytestring=svg.encode("utf-8"), write_to=str(page_pdf))
            merger.append(str(page_pdf))
            page_pdf.unlink()
        mode = "easy" if args.easy else "eco"
        pdf = out_dir / f"shelf-room-{args.theme}-{size}-{mode}.pdf"
        merger.write(str(pdf))
        merger.close()
        written.append(pdf)
        if args.preview:
            png = out_dir / f"shelf-room-{args.theme}-{size}-map.png"
            cairosvg.svg2png(bytestring=pages[1].encode("utf-8"), write_to=str(png), dpi=150)
            written.append(png)
        print(f"{size}: {plan.sheet_count} art sheets (+2 front matter), "
              f"naive {naive_sheet_count(surfaces, sheet)}, "
              f"paper used {plan.efficiency:.0%} -> {pdf}")

    written += write_deliverable_notes(out_dir, howto(plans, cube, args.easy), LICENSE_TEXT)
    zip_path = out_dir / f"shelf-room-{args.theme}.zip"
    build_zip(zip_path, written)
    print(f"bundle: {zip_path}")


if __name__ == "__main__":
    main()
