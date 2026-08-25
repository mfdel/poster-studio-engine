"""Print sizes shared by every poster product.

Two families live here and they must not be confused:

* **Metric cm sizes** (``30x40`` / ``40x50`` / ``50x70``) are the ones we actually
  sell as printed and framed posters. Each is backed by a Prodigi SKU whose real
  product dimensions are metric — see ``PRODIGI_SIZE_CODE``. Prodigi's SKU codes
  read imperial (``-16X20``) for historical reasons, but the product behind
  ``GLOBAL-BLP-16X20`` measures 40.0 x 50.0 cm, not 16 x 20 inches. Verified
  against ``GET /v4.0/products/<sku>`` on 2026-08-22.
* **A-series and true imperial sizes** are digital-download only, for home
  printers and US frame shops. Nothing is fulfilled at those sizes.

Prodigi does not resize a PDF asset — it prints it at the size it receives — so a
page rendered here at the wrong size prints with a white edge. Keep the metric
entries exactly equal to the Prodigi product dimensions.
"""
from __future__ import annotations

from posterlab.select import expand_selection

# Standard print sizes (mm), portrait. A-series is 1:√2; posters are 5:7 / 3:4;
# imperial covers home printers + US shops. (FAM-001 PRD §5.5)
SIZES: dict[str, tuple[float, float]] = {
    "A4": (210.0, 297.0),
    "A3": (297.0, 420.0),
    "A2": (420.0, 594.0),
    "Letter": (215.9, 279.4),
    "16x20": (406.4, 508.0),      # true 16x20 inches — digital only, NOT the Prodigi 16X20 SKU
    "18x24": (457.2, 609.6),      # true 18x24 inches — digital only
    "30x40": (300.0, 400.0),      # Prodigi GLOBAL-*-12X16
    "40x50": (400.0, 500.0),      # Prodigi GLOBAL-*-16X20
    "50x70": (500.0, 700.0),      # Prodigi GLOBAL-*-20X28
}

# Print-on-demand: our size name -> the Prodigi SKU size code. The full SKU is
# "<tier>-<code>", e.g. GLOBAL-BLP-20X28 (Budget poster, Silk 170gsm) or
# GLOBAL-BFP-20X28 (Budget Framed Poster). These three are the only sizes we
# fulfil; every other entry in SIZES is a digital download.
PRODIGI_SIZE_CODE: dict[str, str] = {
    "30x40": "12X16",
    "40x50": "16X20",
    "50x70": "20X28",
}
# The sizes a print-on-demand order can ask for, in the order they are listed.
POD_SIZES = list(PRODIGI_SIZE_CODE)

# The bundle shipped in the digital-download ZIP (a spread of ratios + sizes).
DIGITAL_BUNDLE = ["A4", "A3", "A2", "Letter", "18x24", "50x70"]

# Prodigi recommends 300 dpi for raster assets. Our print asset is the vector PDF,
# so this only applies when a raster has to be sent instead.
POD_DPI = 300


def page_size(size: str, landscape: bool = False) -> tuple[float, float]:
    """(width_mm, height_mm) for a size name, swapped when ``landscape``."""
    w, h = SIZES[size]
    return (h, w) if landscape else (w, h)


def prodigi_sku(size: str, tier: str = "GLOBAL-BLP") -> str:
    """The Prodigi SKU that prints ``size``. Raises if the size is digital-only.

    ``tier`` is the product prefix: ``GLOBAL-BLP`` (Budget poster, Silk 170gsm),
    ``GLOBAL-PAP`` (Photographic Art Print 240gsm) or ``GLOBAL-BFP``
    (Budget Framed Poster).
    """
    if size not in PRODIGI_SIZE_CODE:
        raise SystemExit(
            f"Size {size!r} is digital-only; Prodigi fulfils {POD_SIZES} only"
        )
    return f"{tier}-{PRODIGI_SIZE_CODE[size]}"


def resolve_sizes(size: str) -> list[str]:
    """Expand a ``--size`` value: a name, ``'bundle'``, ``'pod'``, ``'all'``, or a
    comma-separated list of any of those (``'Letter,A4'``).

    A pack sold as one download is often two paper sizes, so one render call has
    to be able to name both. See ``posterlab.select`` for the shared syntax.
    """
    return expand_selection(
        size, SIZES,
        groups={"all": list(SIZES), "bundle": list(DIGITAL_BUNDLE), "pod": list(POD_SIZES)},
        what="size")
