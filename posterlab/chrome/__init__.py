"""Brand chrome: the page furniture every poster in the shop shares.

A poster product supplies only its *body*; the page size, border, title band,
coordinates line and attribution come from here, so two different products read
as the same studio.
"""
from __future__ import annotations

from posterlab.chrome.furniture import (
    ATTRIBUTION_OSM,
    attribution,
    coords_label,
    render_border,
    title_block,
)
from posterlab.chrome.page import (
    DIGITAL_BUNDLE,
    POD_DPI,
    POD_SIZES,
    PRODIGI_SIZE_CODE,
    SIZES,
    page_size,
    prodigi_sku,
    resolve_sizes,
)

__all__ = [
    "ATTRIBUTION_OSM",
    "DIGITAL_BUNDLE",
    "POD_DPI",
    "POD_SIZES",
    "PRODIGI_SIZE_CODE",
    "SIZES",
    "attribution",
    "coords_label",
    "page_size",
    "prodigi_sku",
    "render_border",
    "resolve_sizes",
    "title_block",
]
