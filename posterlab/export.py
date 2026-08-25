"""Export: SVG -> print-ready PDF / preview PNG, plus the digital-download ZIP.

Product-specific copy (how-to-print text, licence wording) is passed in, not
hardcoded here, so every poster ships the same file mechanics with its own words.
"""
from __future__ import annotations

import zipfile
from pathlib import Path

import cairosvg


def export_pdf(svg: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cairosvg.svg2pdf(bytestring=svg.encode("utf-8"), write_to=str(out_path))


def export_png(svg: str, out_path: Path, dpi: int = 150) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(out_path), dpi=dpi)


# The ODbL note that ships inside every digital download. It is the same for
# every map poster in the shop, so it lives here rather than in one product.
OSM_LICENSE_TEXT = """LICENSE & ATTRIBUTION
=====================

Map data
--------
This map is derived from OpenStreetMap data.
(c) OpenStreetMap contributors. Licensed under the Open Database License (ODbL).
https://www.openstreetmap.org/copyright  |  https://opendatacommons.org/licenses/odbl/

The ODbL attribution "(c) OpenStreetMap contributors" is printed on every map.

Design
------
The visual style, layout, typography and illustrations are original work created
for this product and are not part of the OpenStreetMap data.

Your purchase
-------------
You may print this design for your own personal, non-commercial use as many
times as you like. Please don't resell or redistribute the files themselves.
"""


def write_deliverable_notes(out_dir: Path, howto_text: str,
                            license_text: str) -> list[Path]:
    """Write the two plain-text notes that ship inside the digital ZIP."""
    out_dir.mkdir(parents=True, exist_ok=True)
    howto = out_dir / "HOW-TO-PRINT.txt"
    lic = out_dir / "LICENSE-ATTRIBUTION.txt"
    howto.write_text(howto_text, encoding="utf-8")
    lic.write_text(license_text, encoding="utf-8")
    return [howto, lic]


def build_zip(zip_path: Path, files: list[Path]) -> list[str]:
    """Bundle ``files`` into the download ZIP, flat. Returns the names inside it.

    The archive is flat — the arcname is the file name — so two files with the
    same name in different directories would collapse into one member and the
    buyer would silently receive a short pack. That is the one thing a paid
    download must never do, so it is an error, checked before the archive is
    opened (opening it for writing truncates whatever was there).

    The returned names are what the archive actually holds, so a caller can
    report a true count rather than the count it hoped for.
    """
    names = [f.name for f in files]
    clashes = sorted({n for n in names if names.count(n) > 1})
    if clashes:
        raise SystemExit(
            f"Refusing to write {zip_path.name}: {', '.join(clashes)} would be "
            f"packed more than once, and a flat ZIP keeps only the last copy. "
            f"Give the files distinct names, or pack them separately."
        )
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            zf.write(f, arcname=f.name)
    return names
