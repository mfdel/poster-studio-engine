# Plan — Multi-Poster Etsy Strategy + Daylight ("Sunmap") Poster

## Context

The playground map shop (`HopscotchMaps`) is live on Etsy with listings and sales. The founder wants
to expand into more poster products, starting with a **daylight-hours poster**: for a given location,
plot sunrise-to-sunset duration across all 365 days of the year. Future posters will not all be
location-based.

This raises two coupled questions that this plan answers:

1. **Account architecture** — one Etsy shop for everything, or a shop per poster theme?
2. **Engine architecture** — how does a non-map poster reuse the existing render pipeline without
   forking the brand's look or breaking the working map path?

Decisions confirmed with the founder: the daylight poster targets **general home decor / gifting**
(adults — birthdays, anniversaries, housewarming), not the kids/nursery audience; and v1 plots
**geometric daylight duration** computed locally, not cloud-adjusted sunshine hours.

---

# Part 1 — Etsy Account Strategy

## Decision: one shop, renamed to a neutral umbrella brand. Do not open a second shop.

### Why not a shop per theme

Two different units are at play, and conflating them is the trap:

- **The listing is the unit of discovery.** Etsy search ranks individual listings on their own
  title, tags, attributes, and conversion history. A daylight poster ranks identically whether it
  sits beside playground maps or in a dedicated "sun shop." *Niche purity is not a ranking
  mechanism* — the repo's own research already concluded ranking follows conversion signals over
  keyword arrangement (`research/research_etsy_traffic_tips_20260801.md:15-27`).
- **The shop is the unit of trust**, and it is the part you cannot clone: review count, star
  rating, sales count, Star Seller status, repeat buyers, favorites, and shop-level conversion
  history. A second shop starts every one of those at zero.

Concrete costs of a second shop, verified against Etsy policy:

- Requires a **separate Etsy account with a different email**; one account = one shop.
- You **must publicly disclose every shop you run** in the Public Profile of each account, so the
  separation is not even opaque to buyers.
- Same taxpayer ID and address required — no legal or tax benefit.
- Duplicated ops: shipping profiles, shop policies, payment/VAT setup, Prodigi order handling,
  message inbox, ads budget, Pinterest account, and a second `ETSY_API_KEY` + OAuth token file for
  `scripts/commerce/etsy_orders.py`.

That is a multiplied operating burden for zero ranking gain — precisely the feature-bloat failure
mode `CLAUDE.md` Operating Principle 2 warns against.

A second shop is only justified by a **different fulfilment model, a different legal entity, or a
product that would actively damage the first brand**. None apply here.

### Why rename now rather than later

The current name has *two* narrowing words, and the confirmed adult-decor audience breaks both:

| Word | Constrains to | Daylight poster fit |
|---|---|---|
| `Hopscotch` | children, nursery, play | Wrong — buyer is an adult buying for a home |
| `Maps` | cartography | Wrong — a daylight chart is not a map |

Dropping only `Maps` does not rescue it; `Hopscotch` alone still signals kids. The name needs to
change, and **renaming is at its cheapest right now** — every additional sale, review, pin, and
backlink raises the switching cost from here on.

What a rename costs and does not cost:

- **Survives the rename** (attached to the shop, not its name): all reviews, star rating, sales
  count, Star Seller progress, favorites, order history, and listing URLs (which are keyed on
  listing ID).
- **Lost**: brand recall with past buyers, and any external copy or link that spells out
  "Hopscotch" — Pinterest pins, printed package inserts, social bios.
- **Mechanics**: Etsy permits **5 shop-name changes** from Shop Manager after opening; further
  changes need Etsy Support approval. Capitalization changes and reverting to a previous name do not
  count against the 5.

### What the new name should be

The constant across a playground map, a daylight chart, and whatever comes third is **not the
subject** — it is (a) one hand-illustrated art style and (b) "your place, your data, made into
something worth hanging." `brand/README.md:22-24` already names the art style as the moat. Name the
**studio**, not the product.

Selection rules:

- **No product noun** — not Map, Print, Poster, Chart, Atlas-as-literal.
- **No age signal** — not Little, Tiny, Kids, Baby, Hopscotch.
- **No subject noun** — not Playground, Sun, Star.
- Two words or one compound, pronounceable, spellable after hearing it once.
- Must clear **four** checks in a single pass before committing: Etsy shop name availability,
  `.com` domain, Instagram handle, Pinterest handle.

Starting shortlist to run through those checks (not a final answer — pick by feel, then verify):
`NorthAndNoon`, `PaperLatitude`, `TheQuietAtlas`, `LonghandStudio`, `HomeAndHorizon`,
`SmallHoursStudio`, `FieldnoteStudio`, `TwoBirchStudio`.

`brand/store-name.md:61` already anticipated this need ("If you later add nursery prints or other
family keepsakes, a name like … stretches") — the plan is to stretch it further than that note
assumed, because the audience widened from families to general decor.

### The honest risk

A shop selling both toddler playground maps and adult daylight charts reads as unfocused to a
browsing buyer **unless the art style visibly unifies them**. This is a design constraint, not a
branding one, and it is the single biggest execution risk in this plan: the daylight poster must be
rendered in the same visual language as the 14 existing themes — same palette tokens, same `type`
block, same `border` block, same margins and title band. If it looks like a generic infographic, the
shop looks like a dropshipper and the moat evaporates. Part 2 is built to enforce this structurally.

### Rename runbook (ordered — do not reorder steps 1 and 2)

1. **Verify availability first**, before touching anything: Etsy shop name, `.com`, Instagram,
   Pinterest. Do not change the Etsy name until all four are confirmed free.
2. Change the shop name: Shop Manager → Settings → Info & Appearance.
3. Claim the Instagram and Pinterest handles the same day.
4. Post a shop announcement explaining the rename so existing buyers and reviewers are not confused.
5. Create shop **sections** — this is how you segment products, instead of segmenting shops. Start
   with two, e.g. "Family Keepsakes" and "Sun & Sky".
6. Update shop title, announcement, and About story from `brand/store-description.md`.
7. Regenerate the logo/wordmark (`brand/logo.png`, prompts in `brand/logo-prompts.md:16,90` already
   flag "Swap the name").
8. Sweep the repo for the old name and update every occurrence — 10 files:
   `brand/store-name.md`, `brand/etsy-listing-READY.md`, `brand/store-description.md`,
   `brand/pinterest-guide.md`, `brand/logo-prompts.md`,
   `research/roadmap_etsy_traffic_20260801.md`, `research/research_etsy_traffic_tips_20260801.md`,
   `research/etsy_seasonal_calendar_20260801.md`, `scripts/commerce/build_sku_workbook.py:2`,
   `scripts/assets/make_listing_mockups.py:2`.
9. **Existing listing titles and tags need no change** — they do not contain the shop name, and the
   13 tags in `brand/etsy-listing-READY.md:88-90` stay correct for the playground line.

---

# Part 2 — Daylight Poster Build

## Data: computed locally, no API

Daylight duration (sunrise → sunset) is pure astronomy from latitude and day-of-year. Implement the
NOAA solar equations in **`scripts/engine/solar.py`** using only `math` and `datetime` — no new
dependency, no API key, no rate limit, no cost, works offline for any coordinate on Earth.

Required pieces: fractional-year angle, equation of time, solar declination, and the hour angle at
the standard **−0.833°** zenith correction (refraction + solar disc radius). Must handle the polar
case where no hour-angle solution exists → return 24h (polar day) or 0h (polar night) rather than
raising.

Deliberately rejected: Open-Meteo's `sunshine_duration`. Its data is CC BY 4.0, but **the free API
tier is licensed for non-commercial use only** — selling posters built on it requires a paid
subscription. Free commercial alternatives exist (NASA POWER, Copernicus ERA5) but each adds a real
per-address network pipeline. Revisit only if the poster proves it sells, as a premium variant.

**Known limitation, to be handled by design not by data:** geometric daylight depends only on
latitude, so Stockholm and Tallinn produce an identical curve. Personalization therefore comes from
three other places — the **place name**, the **coordinates label**, and **marked personal dates**
annotated on the curve (birthday, anniversary, the day we moved in). That last one is what converts
a physics chart into a keepsake, and it is the same "ritual, not a finder" logic that drives the
playground product (`CLAUDE.md` Operating Principle 3). Treat the personal-date annotation as core
to v1, not as a later nicety.

## Engine: extract shared chrome, do not refactor the map path

The current renderer is 1045 lines of SVG-as-f-strings rasterized by `cairosvg` — no matplotlib, no
PIL. `compose_svg` (`scripts/engine/render_poster.py:557`) has a clean internal seam: lines 577–631
are pure page-layout math and are already poster-type agnostic; lines 632–653 hardwire the content
list.

**Approach: extract, don't restructure.** Move the functions that are *already* generic into a new
`scripts/engine/poster_chrome.py`, have `render_poster.py` import them back, then have the new
renderer import the same module. This buys shared brand chrome without reorganizing the working,
revenue-generating map path.

Functions to move verbatim (a pure move — no behaviour change):

| Function | Current location |
|---|---|
| `render_border(W, H, theme)` | `render_poster.py:427` |
| `_title_block(...)` | `render_poster.py:460` |
| `coords_label(home)` | `render_poster.py:509` |
| `format_locality(display_name)` | `render_poster.py:533` |
| `export_pdf` / `export_png` | `render_poster.py:874` / `:879` |
| `write_deliverable_notes` / `build_zip` | `render_poster.py:853` / `:862` |
| SVG primitives `_num`, `path_d`, `chunk_path_ds`, `star_path`, `heart_path` | `render_poster.py:186-235` |
| `SIZES`, `DIGITAL_BUNDLE` | `render_poster.py:55-66` |

Note `write_deliverable_notes` and `build_zip` carry playground-specific copy
(`render_poster.py:800,830`) — parameterize that copy rather than duplicating the functions.

New files:

- `scripts/engine/solar.py` — daylight math, ~80 lines, stdlib only.
- `scripts/engine/render_sunposter.py` — composes the chart body, imports all chrome from
  `poster_chrome.py`.
- `scripts/engine/make_sunposter.py` — CLI mirroring `make_map.py`'s flag names exactly
  (`--address --theme --title --subtitle --size --variant --orientation --out --preview --zip`) so
  muscle memory and the dashboard schema transfer.

## Chart design

v1 renders the classic daylight band: 365 vertical bars, x = day of year, y = time of day, each bar
spanning that day's sunrise to sunset. Produces the recognizable lens/leaf silhouette. Night fill
and day fill drawn as two contrasting regions; solstice and equinox marked; month ticks along x.

Two variants, mirroring the map's `clean` / `annotate` split:

- `clean` — chart, title, coordinates, border.
- `dates` — adds labelled vertical rules for personal dates supplied via a `--mark` flag
  (repeatable, e.g. `--mark 2019-06-14="Ella born"`).

A polar/radial variant is a good second product later; not v1 (harder to read, and legibility at
print size is unproven).

## Theme schema extension

The theme JSONs already carry everything needed for chrome: `palette.page/text/muted/border/
annotation_box/annotation_line`, all of `type`, all of `border`. Missing: any chart, grid, or axis
color.

Add an **optional** `chart` block to the theme schema:

```json
"chart": { "day": "#…", "night": "#…", "curve": "#…", "grid": "#…", "axis": "#…", "marker": "#…" }
```

Critically, implement a **derivation fallback** that synthesizes these from existing palette keys
when the block is absent — so all 14 themes render on day one without editing 14 files. Hand-tune
the `chart` block only on the 3–4 themes actually chosen for listings.

Also worth knowing: `texture` is a **dead key** in every theme JSON — zero code references. Do not
model the new block on it.

## Run store: add a kind discriminator

`runstore.py` describes itself as "pure plumbing … no OSM knowledge" (`runstore.py:17-18`), but the
key/index layer is map-shaped and has a real latent bug for a second poster type:

- `cache_key` basis is `f"{address}|{radius}|{merge}"` (`runstore.py:52`) — a daylight poster has
  neither radius nor merge threshold.
- Run IDs embed `r{radius}` (`runstore.py:61`).
- Index entries hardcode `address` / `radius_m` / `merge_threshold_m` (`runstore.py:97-106`), and
  `data/index.json` has no `type` field.
- **`newest_run_id()` (`runstore.py:117`) returns the newest run across all queries with no type
  filter**, and `resolve_run("latest")` is what `render_poster --run latest` uses. Mixing two poster
  types in `data/runs/` will silently resolve `latest` to the wrong kind of run.

Changes: add `"kind": "map" | "sun"` to `run.json` and to each `data/index.json` entry; make
`cache_key` accept a kind and prefix the hash basis with it; give `newest_run_id()` and
`resolve_run()` an optional `kind` filter. Bump `data/index.json` `version` to 2 and tolerate
version-1 entries by defaulting them to `kind: "map"`.

## Dashboard

`scripts/dashboard/dashboard.py` has one hardcoded target script (`MAKE_MAP`, `:48`), one flat
17-flag `META` schema built at import time (`:80-141`), and `discover_themes()` (`:59`) offers all
14 map themes with no filtering. The frontend is already schema-driven (fetches `/api/meta`), so new
fields surface automatically.

Minimum change: turn `MAKE_MAP` into a `{poster_type: script_path}` map, build one `META` per poster
type, and add a poster-type selector to `/api/meta`. Guard `previous_addresses()` (`:144`), which
currently assumes every index entry has `address` + `radius_m`. `dashboard.html` hardcodes the title
"Playground Map" (lines 6, 182) and the displayed command prefix (line 275) — update both.

## Attribution

Daylight is computed locally, so **no OSM data enters the poster** — ODbL does not attach to the
chart itself. But the address→lat/lon step still goes through Nominatim (`osm_common.py:158`). Keep
a small attribution line whenever geocoding was used; it costs one line of 6pt text and keeps
`CLAUDE.md` Guardrail 2 satisfied without having to reason about edge cases. Note `_attribution()`
(`render_poster.py:497`) anchors to the *map frame* rect, so it needs a rect parameter to be reused
here.

## Commerce

No new SKUs needed. The daylight poster ships on the **existing Prodigi products and sizes** —
`GLOBAL-BLP-*` posters, `GLOBAL-BFP-*` framed, same 30×40 / 40×50 / 50×70 cm. Add rows to
`scripts/commerce/build_sku_workbook.py` under a new SKU prefix (e.g. `SUNMAP-*`) reusing the
existing cost snapshots and fee model (`:96-105`). Pricing can start identical to the map line.

Side note surfaced during exploration, worth fixing while in these files: **Gelato is not wired up
anywhere** — Prodigi is the live vendor, and `CLAUDE.md:22,28,54,79`, `README.md:9`, and
`docs/playground_map_prd_digital_gelato.md` are all stale on this point.

---

## Verification

**Solar math** — unit-test `solar.py` against published values before rendering anything:
Stockholm (59.33°N) summer solstice ≈ 18h37m; equator ≈ 12h05m year-round; Tromsø (69.65°N) returns
24h across late May–July and 0h across late November–January. Assert monotonic behaviour between
solstices and symmetry about them.

**Chrome extraction is behaviour-neutral** — before touching anything, render a known existing run
(`data/runs/20260730-221413__15_rue_joseph_bara_75006_paris_france__r1000__db1f697e`) and keep the
SVG. After moving functions into `poster_chrome.py`, re-render and diff: output must be byte-for-byte
identical. This is the safety net for the live product.

**Run store migration** — with both a map run and a sun run present in `data/runs/`, confirm
`resolve_run("latest")` returns the right one for each poster type, and that a pre-existing
version-1 `data/index.json` entry still resolves.

**End-to-end** — `uv run python scripts/engine/make_sunposter.py --address "Stockholm, Sweden"
--theme all --size A2 --variant both --preview`, then open the PNGs. Judge one thing above all: does
it sit beside `brand/listing-photos/01-framed-whimsy.png` and read as the same studio? If not, the
theme `chart` derivation needs hand-tuning before anything gets listed.

**Print check** — export A2 PDF, confirm true-size vector output (the SVG root uses physical mm with
a 1:1 viewBox, `render_poster.py:635`), and verify the thinnest gridline is still visible at print
scale. Note `export_png` defaults to 150 DPI (`render_poster.py:879`) and is not exposed on the CLI
or dashboard — fine for previews, but confirm the PDF path is what goes to Prodigi.

---

## Out of scope

- Cloud-adjusted actual sunshine hours (needs a paid or heavier data pipeline).
- Radial/polar chart variant.
- Product B physical annotation kit.
- Etsy listing creation via API — no such code exists in the repo, and none is planned here; list
  the new product manually.
- Migrating the stale Gelato references (flagged above, tracked separately).
