# Architecture — a multi-poster studio in one repo

This repo builds **several personalised poster products** from one shared engine. It started as a
single product (FAM-001 Playground Map) and was generalised on 2026-08-09; the layout below is the
result.

## Layout

```
pyproject.toml            posterlab is an installable package: uv pip install -e .

posterlab/                SHARED ENGINE — poster-type agnostic, no product knows another
  paths.py                canonical repo paths (ROOT, DATA, OUTPUT, THEMES …)
  text.py                 slugify, Nominatim display_name -> "Street, City"
  themes.py               theme loading + chart-token derivation
  export.py               SVG -> PDF / PNG, deliverable notes, digital ZIP
  product.py              poster registry: reads posters/*/poster.toml
  runstore.py             immutable runs + query cache, partitioned by poster kind
  geo/                    geodesy.py (maths) · osm.py (Nominatim/Overpass) · sea_fill.py
  map/                    overpass.py (basemap fetch) · body.py (the styled street map,
                          home glyph, basemap loaders, auto-orientation)
  svg/                    primitives.py (num, path_d, star/heart) · hand_drawn.py
  chrome/                 page.py (print SIZES) · furniture.py (border, title band,
                          coordinates line, attribution)

posters/                  ONE DIRECTORY PER PRODUCT
  fam001-playground-map/  poster.toml · dashboard.json · make.py · render.py ·
                          playgrounds.py · icons.py · docs/ · brand/
  fam002-halloween-night/ poster.toml · dashboard.json · make.py · render.py ·
                          panel.py · layouts.py · sheet_text.py · docs/
  prt006-sun-year/        poster.toml · docs/ · drafts/     (draft: no CLI yet)

studio/                   SHOP LEVEL, product-agnostic
  themes/                 the 14 theme JSONs + figure assets (shared on purpose)
  brand/                  logo, shop name, shop description, Pinterest guide
  commerce/               Prodigi quotes, Etsy orders, SKU workbook
  print_on_demand/        vendor pricing CSVs + SKU workbooks
  research/               Etsy traffic / seasonal / roadmap research
  dashboard/              local control panel (drives every product's CLI)
  assets/                 listing mockups, cutouts, image-generation helpers
  scratch/                throwaway notebooks

data/index.json           query cache index (version 2, "kind" per entry) — tracked
data/runs/<kind>/<run>/   immutable per-run data — gitignored, regenerable
output/<kind>/<run>/       rendered posters — gitignored, regenerable
docs/                     cross-product docs (this file, prior-art scans, strategy)
```

## The rules that keep it honest

1. **A poster product owns nothing generic.** If two products need it, it moves into `posterlab/`.
   Product directories import `posterlab`; they never import each other.
2. **Themes are shared.** One hand-illustrated art style across every product is the moat, so a new
   poster inherits `studio/themes/*.json` instead of inventing a look. Brand blocks (`palette`,
   `type`, `border`) are common; product blocks (`map`, `chart`) are optional, and
   `posterlab.themes.chart_tokens()` derives chart colours from the brand palette when a theme has no
   `chart` block — so a new poster type renders in all 14 themes on day one.
3. **`kind` partitions everything stateful.** Each product's `poster.toml` declares a short `kind`
   (`map`, `halloween`, `sun`). It names the run directory (`data/runs/<kind>/`), the output directory
   (`output/<kind>/`), the `kind` field in `run.json` and in each `data/index.json` entry, and the
   filter on `resolve_run("latest")` — which is what stops a sun poster from rendering a map run.
4. **Adding a poster is adding a directory.** `posters/<slug>/poster.toml` makes it visible to
   `posterlab.product.discover_posters()` and therefore to the dashboard; `dashboard.json` describes
   its form. No registry edits anywhere else.
5. **A map is not a product.** Every map-shaped poster draws the same streets from `posterlab.map`
   and passes its own marker layer in as `render_map_body(..., overlay=...)`. FAM-001 passes numbered
   playgrounds; FAM-002 passes one home glyph. Neither owns the roads underneath.
6. **Attribution survives to print.** Anything derived from OpenStreetMap keeps the ODbL credit
   (`posterlab.chrome.attribution`), including products that only use Nominatim to geocode.

## Running things

```bash
source .venv/bin/activate
uv pip install -e .                       # once: makes posterlab importable

# FAM-001 — data (cached) + render
python posters/fam001-playground-map/make.py --address "Tygelsjö, Malmö, Sweden" --radius 2000 \
    --theme whimsy --size A2 --variant clean --preview

# re-render a saved run, no network
python posters/fam001-playground-map/render.py --run latest --theme ink --size A2

# FAM-002 — the Halloween night sheet, print at home
python posters/fam002-halloween-night/make.py --address "Elm St, Decatur, Georgia" \
    --radius 400 --theme lantern --size A4 --layout ledger --night "31 October 2026" --preview

# the control panel for every product
python studio/dashboard/dashboard.py --open
```

Poster products are run **as scripts**, not imported: their directory names are deliberately not
valid module names, and sibling modules (`render`, `panel`, `icons`) resolve because the script's
own directory is on `sys.path`. The dashboard runs them with `cwd` set to the product directory for
the same reason.

## Cache-key compatibility

`posterlab.runstore.cache_key(kind, parts)` prefixes the hash basis with `kind` for every product
**except** `map`. That exception is deliberate: the 41 existing `data/index.json` entries were hashed
without a prefix, and prefixing them would silently miss the cache and refetch the whole history from
Overpass. New products get prefixed keys and cannot collide with map keys.

## The 2026-08-19 map-engine split

FAM-002 (Halloween night sheet) started as a `--variant halloween` inside FAM-001. It became its own
product on 2026-08-19, which forced the shared street map out of the product and into
`posterlab/map/`:

| moved from | moved to |
| --- | --- |
| `posters/fam001-playground-map/basemap.py` | `posterlab/map/overpass.py` |
| `render.render_map_body` (minus its markers) | `posterlab.map.body.render_map_body(..., overlay=)` |
| `render.home_marker_svg` / `home_glyph` | `posterlab.map.body` |
| `render.load_basemap` / `with_sea` / `run_id_for_path` | `posterlab.map.body` |
| `render.content_aspect` / `resolve_orientation` | `posterlab.map.body` |
| `render.LICENSE_TEXT` | `posterlab.export.OSM_LICENSE_TEXT` |
| `render.render_halloween_log` + its copy | `posters/fam002-halloween-night/panel.py` |
| `render.halloween_layouts` | `posters/fam002-halloween-night/layouts.py` |

FAM-001 kept only what is unique to it: playground fetching, numbered markers, the icon set and the
adventure log. FAM-002 fetches no playgrounds at all — its run holds one `basemap.geojson`, and that
file's metadata carries `home`.

## The 2026-08-09 restructure

Verified behaviour-neutral for the live product: 144 composed SVGs (3 runs × 3 orientations × 4
themes × 2 sizes × 2 variants) hash identically before and after the extraction, and all 41 cached
query keys still resolve. Existing `data/runs/*` and `output/*` were moved into their `map/`
partitions, so the cache stayed warm.
