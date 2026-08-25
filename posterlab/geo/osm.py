"""OpenStreetMap network access: Nominatim geocoding + Overpass querying.

One source of truth for being a good API citizen: a real User-Agent, polite
spacing, mirror fail-over and retry/back-off.

Data © OpenStreetMap contributors (ODbL). Attribution is mandatory on every
rendered/printed/sold artifact.
"""
from __future__ import annotations

import time

import requests

NOMINATIM = "https://nominatim.openstreetmap.org/search"

# The main Overpass instance frequently returns 504/429 under load, so we fail
# over between mirrors and retry the whole set with back-off.
OVERPASS_MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]

UA = "posterlab/1.0 (personal project; contact via github.com/mfdel)"


def geocode(address: str) -> tuple[float, float, str]:
    """Return (lat, lon, display_name).

    Falls back to progressively coarser locality queries if the full street
    query returns nothing. Polite (1s) spacing between attempts.
    """
    candidates = [address]
    parts = [p.strip() for p in address.split(",")]
    if len(parts) > 1:
        candidates.append(", ".join(parts[1:]))
        candidates.append(", ".join(parts[-2:]))
    for q in candidates:
        resp = requests.get(
            NOMINATIM,
            params={"q": q, "format": "jsonv2", "limit": 1},
            headers={"User-Agent": UA},
            timeout=30,
        )
        resp.raise_for_status()
        hits = resp.json()
        if hits:
            h = hits[0]
            print(f"  geocoded via '{q}' -> {h['display_name']}")
            return float(h["lat"]), float(h["lon"]), h["display_name"]
        time.sleep(1)
    raise SystemExit(f"Could not geocode any variant of: {address!r}")


def overpass(query: str, *, attempts: int = 3, timeout: int = 180) -> list[dict]:
    """Run an Overpass QL query with mirror fail-over + retry/back-off.

    Returns the `elements` list. Raises SystemExit if every mirror fails on
    every attempt.
    """
    last_err: Exception | None = None
    for attempt in range(1, attempts + 1):
        for mirror in OVERPASS_MIRRORS:
            try:
                resp = requests.post(
                    mirror,
                    data={"data": query},
                    headers={"User-Agent": UA},
                    timeout=timeout,
                )
                resp.raise_for_status()
                elements = resp.json().get("elements", [])
                print(f"  fetched from {mirror.split('/')[2]} (attempt {attempt})")
                return elements
            except (requests.RequestException, ValueError) as exc:
                last_err = exc
                print(f"  {mirror.split('/')[2]} failed: {exc}")
        time.sleep(5)  # back off before retrying the whole mirror set
    raise SystemExit(f"All Overpass mirrors failed: {last_err}")
