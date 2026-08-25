"""The printed sizes must equal the Prodigi product they are fulfilled by.

Prodigi prints a PDF asset at exactly the size it receives — it does not resize.
So a page rendered a few millimetres off the SKU's real dimensions prints with a
white edge. The numbers below are the live catalogue, read on 2026-08-22 from
``GET https://api.prodigi.com/v4.0/products/<sku>`` (field ``productDimensions``).

Note the trap this test exists to catch: Prodigi's SKU codes read imperial, but
the products behind them are metric. ``GLOBAL-BLP-16X20`` is 40.0 x 50.0 cm, not
16 x 20 inches. Refresh with ``studio/commerce/prodigi_quotes.py`` credentials if
Prodigi ever changes the catalogue.
"""
from __future__ import annotations

import pytest

from posterlab.chrome import (
    POD_SIZES,
    PRODIGI_SIZE_CODE,
    SIZES,
    page_size,
    prodigi_sku,
    resolve_sizes,
)

# Prodigi productDimensions, in mm, per SKU size code (verified 2026-08-22).
PRODIGI_PRODUCT_MM = {
    "12X16": (300.0, 400.0),
    "16X20": (400.0, 500.0),
    "20X28": (500.0, 700.0),
}

# Tiers we quote and order from: Budget poster, Photographic Art Print, Budget frame.
TIERS = ("GLOBAL-BLP", "GLOBAL-PAP", "GLOBAL-BFP")


@pytest.mark.parametrize("size", POD_SIZES)
def test_pod_size_matches_prodigi_product(size):
    code = PRODIGI_SIZE_CODE[size]
    assert page_size(size) == PRODIGI_PRODUCT_MM[code], (
        f"{size} renders at {page_size(size)} mm but Prodigi {code} prints "
        f"{PRODIGI_PRODUCT_MM[code]} mm — the PDF would not fill the sheet"
    )


def test_every_pod_size_has_a_sku_code():
    assert set(POD_SIZES) == set(PRODIGI_SIZE_CODE)
    assert set(PRODIGI_SIZE_CODE.values()) == set(PRODIGI_PRODUCT_MM)


@pytest.mark.parametrize("tier", TIERS)
def test_prodigi_sku_builds_the_codes_we_order(tier):
    assert [prodigi_sku(s, tier) for s in POD_SIZES] == [
        f"{tier}-12X16", f"{tier}-16X20", f"{tier}-20X28"
    ]


def test_prodigi_sku_refuses_a_digital_only_size():
    with pytest.raises(SystemExit):
        prodigi_sku("A2")


def test_imperial_16x20_is_not_the_prodigi_16x20():
    """Keep the two apart: 16x20 inches is a home-print size, not a SKU size."""
    assert SIZES["16x20"] == (406.4, 508.0)
    assert SIZES["40x50"] == (400.0, 500.0)


def test_resolve_sizes_pod():
    assert resolve_sizes("pod") == list(POD_SIZES)
    assert "40x50" in resolve_sizes("all")
