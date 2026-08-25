# CLAUDE.md — Poster Studio Engine

This file provides guidance to Claude Code (claude.ai/code) and AI agents when working in this repository.

---

## Project Overview

**Poster Studio Engine** is a deterministic data-to-art Python pipeline that converts OpenStreetMap (OSM) and astronomical data into print-ready, high-DPI poster products sold on Etsy, Shopify, and print-on-demand fulfillment networks (Prodigi).

### Product Suite (`posters/`)

1. **FAM-001 — Playground Map (`posters/fam001-playground-map/`):**
   - Geocoded address + radius $\rightarrow$ Overpass OSM query $\rightarrow$ SVG map body + hand-drawn vector elements $\rightarrow$ high-DPI PDF (≥300 DPI) & PNG preview.
   - Includes Bromma keepsake map sample (`"Rättviksvägen 18, 167 75 Bromma"`).
2. **FAM-002 — Halloween Night Sheet (`posters/fam002-halloween-night/`):**
   - Print-at-home trick-or-treat keepsake map and spotting log within 300–400m of an address.
   - Includes Salem, Massachusetts sample (`"Chestnut Street, Salem, Massachusetts, USA"`).
3. **FAM-003 — Shelf Room Playscape (`posters/fam003-shelf-room/`):**
   - Print-at-home multi-sheet room inserts for standard cube shelves (e.g. IKEA Kallax 330x330mm).
   - Powered by `posterlab/chrome/tiling.py` (overlap-aware multi-sheet packing, seam reporting).
4. **PRT-006 — Sun-Year Poster (`posters/prt006-sun-year/`):**
   - 365-day solar daylight ring poster computed deterministically for any latitude.

---

## Architecture & Codebase Map

| Component | Path | Description |
|---|---|---|
| **Core Engine** | `posterlab/` | Shared rendering engine (`paths.py`, `text.py`, `themes.py`, `export.py`, `product.py`, `runstore.py`) |
| **Geodesy & OSM** | `posterlab/geo/` | Geocoding (Nominatim), bounding box, geodesy, and sea fill |
| **Map Renderer** | `posterlab/map/` | Overpass query builder (`overpass.py`) and styled map canvas (`body.py`) |
| **SVG Primitives** | `posterlab/svg/` | Mathematical curves, star/heart shapes, and hand-drawn wobble (`hand_drawn.py`) |
| **Page & Chrome** | `posterlab/chrome/` | Multi-size poster frames (`page.py`), furniture, and multi-sheet tiling (`tiling.py`) |
| **Products** | `posters/` | Product-specific orchestrators (`make.py`, `render.py`, `poster.toml`) |
| **Studio & Ops** | `studio/` | Interactive dashboard, 14 theme definitions, mockups, POD calculators, and shop automation |
| **Sample Data** | `data/` | Hash-addressed query cache (`index.json`), pre-rendered runs, and offline Bromma GeoJSON |
| **Output Prints** | `output/` | High-DPI PDF and PNG preview samples across all 4 products |
| **Tests** | `tests/` | 70-test pytest suite covering digital packs, POD sizing, seam calculations, and tiling logic |

---

## Technical Environment & Commands

- **Environment:** Python 3.12 managed via `uv`.
- **Install in editable mode:**
  ```bash
  uv venv --python 3.12 && source .venv/bin/activate
  uv pip install -e ".[dev]"
  ```

### Common CLI Workflows

```bash
# 1. Run FAM-001 Playground Map for an address (online fetch or cached hit)
uv run python posters/fam001-playground-map/make.py \
    --address "Rättviksvägen 18, 167 75 Bromma" \
    --radius 2000 \
    --theme whimsy \
    --size A2 \
    --title "Our Playground Map" \
    --preview

# 2. Re-render cached run without network calls
uv run python posters/fam001-playground-map/render.py --run latest --theme whimsy --size A2

# 3. Generate FAM-002 Halloween Sheet
uv run python posters/fam002-halloween-night/make.py \
    --address "Chestnut Street, Salem, Massachusetts, USA" \
    --radius 300 \
    --layout panel

# 4. Generate FAM-003 Shelf Room Tiled Pack
uv run python posters/fam003-shelf-room/make.py --cube 330 --pack A4

# 5. Render PRT-006 Sun Year Astronomical Poster
uv run python posters/prt006-sun-year/render_1b.py --lat 59.327 --city "Stockholm" --year 2026

# 6. Launch interactive Studio Dashboard
uv run python studio/dashboard/dashboard.py --open

# 7. Run Test Suite
uv run pytest
```

---

## Operating Principles & Guidelines

1. **Deterministic Art:** Poster layouts, coordinate projections, and solar calculations are mathematically reproducible from input parameters and cached datasets.
2. **Offline Resilience:** Every product supports local caching (`data/runs/`) and offline datasets so rendering can proceed without network dependencies or rate limits.
3. **Print-on-Demand Ready:** Output PDFs are rendered at high resolution (≥300 DPI) matching standard European (A4, A3, A2, 50x70) and US (Letter, 12x16, 18x24) print dimensions.
4. **Attribution Compliance:** All OpenStreetMap data adheres strictly to the Open Database License (ODbL) with explicit attribution on generated maps.
