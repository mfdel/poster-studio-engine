#!/usr/bin/env python3
"""Fetch live Prodigi costs for exactly the sizes we offer (poster + framed).

Prodigi's base prices are gated behind an account, so this pulls real quotes
(item + shipping) for the poster and framed SKUs that back our Etsy listing, then
prints comparison tables: per-size cost to Sweden, plus a multi-country snapshot.

Poster tier : GLOBAL-BLP (Budget poster, Silk 170gsm — cheapest) as default, with
              GLOBAL-PAP (Photographic Art Print 240gsm) shown as the premium-paper upgrade.
Framed tier : GLOBAL-BFP (Budget Framed Poster, no mount) in wood(natural)/white —
              far better margin than the Classic frame, and offers 30×40/40×50/50×70.

Auth: requires a Prodigi API key in a .env file at the repo root (gitignored):
    PRODIGI_API_KEY=your-key-here
    PRODIGI_ENV=live        # or: sandbox
Run:  uv run python studio/commerce/prodigi_quotes.py

Docs: https://www.prodigi.com/print-api/docs/reference/#create-quote
Data / products © Prodigi. OSM playground data is separate (ODbL).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib import error, request

# --- sizes we offer (size code -> human dimensions) ---
POSTER_SIZES = [
    ("12X16", "30×40 cm"), ("16X20", "40×50 cm"), ("20X28", "50×70 cm"),
]
# framed sizes we offer: (human dims, Prodigi size code)
FRAMED_SIZES = [("30×40 cm", "12X16"), ("40×50 cm", "16X20"), ("50×70 cm", "20X28")]

# required attribute set for a Budget Framed Poster (no-mount) quote
BFP_ATTRS = {
    "frame": "Budget", "glaze": "Acrylic / Perspex",
    "mount": "No mount / Mat", "paperType": "Silk", "substrateWeight": "150gsm",
}
FRAME_COLORS = ("natural", "white")  # natural = wood (no black on rectangular budget frames)

HOME = "SE"                       # home market for the per-size tables
SNAPSHOT_COUNTRIES = ["SE", "GB", "US", "DE"]
SHIPPING_METHOD = "Budget"       # budget | standard | standardplus | express | overnight

BASE_URLS = {"sandbox": "https://api.sandbox.prodigi.com", "live": "https://api.prodigi.com"}


def load_dotenv(path: Path) -> None:
    """Minimal .env loader so we don't add a dependency."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def create_quote(base_url: str, api_key: str, sku: str, country: str, attributes: dict) -> dict:
    payload = {
        "shippingMethod": SHIPPING_METHOD,
        "destinationCountryCode": country,
        "items": [{"sku": sku, "copies": 1, "attributes": attributes,
                   "assets": [{"printArea": "default"}]}],
    }
    req = request.Request(
        f"{base_url}/v4.0/quotes",
        data=json.dumps(payload).encode(),
        headers={"X-API-Key": api_key, "Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=40) as resp:
        return json.loads(resp.read().decode())


def total(base_url: str, api_key: str, sku: str, country: str, attributes: dict):
    """Return (total_cost, currency) or ('ERR<code>', '')."""
    try:
        resp = create_quote(base_url, api_key, sku, country, attributes)
        q = (resp.get("quotes") or [{}])[0]
        cs = q.get("costSummary", {})
        items, ship = cs.get("items", {}) or {}, cs.get("shipping", {}) or {}
        cur = items.get("currency") or ship.get("currency") or ""
        return float(items.get("amount", 0) or 0) + float(ship.get("amount", 0) or 0), cur
    except error.HTTPError as e:
        return f"ERR{e.code}", ""
    except Exception as e:  # noqa: BLE001
        return f"ERR:{str(e)[:30]}", ""


def fmt(val, cur=""):
    return f"{val:.2f}{cur[:3]}" if isinstance(val, (int, float)) else str(val)


def main() -> int:
    load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")
    api_key = os.environ.get("PRODIGI_API_KEY")
    env = os.environ.get("PRODIGI_ENV", "sandbox").lower()
    if not api_key:
        print("ERROR: PRODIGI_API_KEY not set (add it to .env).", file=sys.stderr)
        return 1
    if env not in BASE_URLS:
        print(f"ERROR: PRODIGI_ENV must be one of {list(BASE_URLS)} (got {env!r})", file=sys.stderr)
        return 1
    base_url = BASE_URLS[env]

    print(f"Prodigi quotes  [{env}]  shipping={SHIPPING_METHOD}  (item + shipping, ex-tax)\n")

    # ---- posters, per size, to home market ----
    print(f"PRINTED POSTER — total cost to {HOME}  (BLP = budget Silk 170gsm; PAP = premium 240gsm)")
    print(f"{'Size':<15}{'BLP total':>11}{'PAP total':>11}   SKU (BLP)")
    print("-" * 62)
    for code, dims in POSTER_SIZES:
        blp, cur = total(base_url, api_key, f"GLOBAL-BLP-{code}", HOME, {})
        pap, _ = total(base_url, api_key, f"GLOBAL-PAP-{code}", HOME, {})
        print(f"{code+' '+dims:<15}{fmt(blp):>11}{fmt(pap):>11}   GLOBAL-BLP-{code}")

    # ---- framed, per size + colour, to home market ----
    print(f"\nFRAMED POSTER (Budget frame, no mount) — total cost to {HOME}")
    print(f"{'Size':<15}{'wood/natural':>13}{'white':>10}   SKU")
    print("-" * 55)
    for dims, code in FRAMED_SIZES:
        cells = []
        for col in FRAME_COLORS:
            t, _ = total(base_url, api_key, f"GLOBAL-BFP-{code}", HOME, {**BFP_ATTRS, "color": col})
            cells.append(fmt(t))
        print(f"{dims:<15}{cells[0]:>13}{cells[1]:>10}   GLOBAL-BFP-{code}")

    # ---- multi-country snapshot for the price-cap sizes ----
    print(f"\nMULTI-COUNTRY snapshot — total cost by ship-to ({SHIPPING_METHOD} shipping)")
    hdr = f"{'Product':<30}" + "".join(f"{c:>10}" for c in SNAPSHOT_COUNTRIES)
    print(hdr)
    print("-" * len(hdr))
    snap = [
        ("Poster 30×40 (BLP-12X16)", "GLOBAL-BLP-12X16", {}),
        ("Poster 50×70 (BLP-20X28)", "GLOBAL-BLP-20X28", {}),
        ("Framed 50×70 wood (BFP-20X28)", "GLOBAL-BFP-20X28", {**BFP_ATTRS, "color": "natural"}),
    ]
    for label, sku, attrs in snap:
        cells = []
        for c in SNAPSHOT_COUNTRIES:
            t, cur = total(base_url, api_key, sku, c, attrs)
            cells.append(fmt(t, cur))
        print(f"{label:<30}" + "".join(f"{x:>10}" for x in cells))

    print("\nNote: amounts exclude tax. Prodigi has every size we offer — no substitutions needed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
