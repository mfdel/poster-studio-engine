# Copilot Instructions — Poster Studio Engine

You are the build-and-ship partner for **Poster Studio Engine**, a multi-poster deterministic rendering pipeline and automated print-on-demand studio.

## Core Directives

1. **Architecture Decoupling:** Keep `posterlab/` generic and decoupled from specific poster products in `posters/`.
2. **Deterministic Outputs:** Coordinate transformations (Mercator `Projector`), solar calculations, and geometric clipping (`sea_fill.py`) must remain pure and reproducible.
3. **Data Licensing:** Always preserve OpenStreetMap ODbL attribution on rendered maps.
4. **Testing Integrity:** All engine modifications must pass the 70-test test suite (`uv run pytest`).

## Key Entry Points

- **FAM-001 (Playground Map):** `posters/fam001-playground-map/make.py`
- **FAM-002 (Halloween Night):** `posters/fam002-halloween-night/make.py`
- **FAM-003 (Shelf Room):** `posters/fam003-shelf-room/make.py`
- **PRT-006 (Sun Year):** `posters/prt006-sun-year/render_1b.py`
- **Interactive Dashboard:** `studio/dashboard/dashboard.py`
- **E-Commerce Ops:** `.github/skills/shop-run/SKILL.md` & `studio/ops/shop_run.sh`
