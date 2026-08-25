---
idea: "FAM-001 Playground Map"
doc: PRD — Product A (Digital Map Generator) + Gelato Integration
phase: 4 (build)
date: 2026-07-29
status: draft v1
owner: Fuat (founder / build-and-ship)
---

# PRD — Digital Playground Map Generator + Gelato Integration

> **Scope of this PRD:** the **Product A digital map engine** and the **Gelato print-on-demand
> integration** for it. Product B (physical annotation gift kit) and a self-serve web app are
> **explicitly out of scope** here — deferred until the smoke test proves demand (see market doc §C4).

---

## 1. Context — why this, why now

The plan (`playground_map_plan.md`) and market analysis (`playground_map_market_and_execution.md`)
converge on one move: **ship the digital map engine first**, sell it semi-manually on Etsy, and only
automate once strangers buy. The current prototype ([`playgrounds.py`](../playgrounds.py))
proves the **data half** — it geocodes an address, pulls every `leisure=playground` in a radius from
OpenStreetMap (with Overpass mirror-failover + equipment tags), and renders an **interactive
Leaflet/folium HTML** preview.

That HTML preview is a *finder*, not the product. The docs are blunt: **"if the art looks like a raw
OSM export, this fails — the incumbents are gorgeous and that's the bar."** This PRD covers the missing
half: turning the pulled data into a **distinctive, print-ready keepsake poster** and getting it
**printed and shipped via Gelato** — with the minimum machinery to fulfill real orders by hand.

**Intended outcome:** a founder can take an address from an Etsy order note and, in a few minutes of
their own time, produce a **gift-worthy ≥300 DPI print-ready PDF** (clean *and* annotate-me variants,
in standard sizes) that either downloads to the buyer or uploads to Gelato for a printed poster.

### Decisions carried into this PRD (locked)

| Decision | Choice | Consequence for the build |
|---|---|---|
| **v1 automation** | **Semi-manual per-order** | CLI tool, no web app, no accounts, no auto-ordering. Founder runs it per order. |
| **Art direction** | **Prototype style-agnostic** | Style is a **swappable theme layer** (palette/type/icons/textures as config). Ship 2–3 starter themes to A/B; lock the winner post-smoke-test. |
| **Gelato depth** | **Manual dashboard now, API spec'd for later** | v1 = documented manual upload + print spec. §6.4 fully specs the API phase so nothing blocks it later. |
| **Poster content** | **Both variants per order** | Every render produces a **clean** framable poster **and** an **annotate-me** version (numbered list, rating legend, blank note/photo boxes). |

### Positioning assumptions inherited from the docs (not re-litigated here)

- **Lead with the gift**, not "playground map" search traffic (market doc §A2, decision 1).
- **Digital-first, no paid ads**; defer the physical kit (market doc §C1–C2, decision 2).
- **Launch geography = dense-OSM markets**: Sweden (home / Malmö) first, then Nordics + DE/NL/UK/FR.
- **ODbL attribution is mandatory** on every rendered/printed artifact (§7).

---

## 2. Goals & non-goals

**Goals**
1. Produce a **print-ready PDF** from an address that is genuinely gift-worthy, not a clinical OSM dump.
2. Make **visual style a swappable theme** so art direction can be tuned/locked without re-architecting.
3. Emit **both a clean and an annotate-me variant**, in **standard print sizes**, at **≥300 DPI**.
4. Define the **Gelato manual fulfillment** flow + exact print-file spec so posters can ship today.
5. Keep the whole thing runnable **by one person, per order, in minutes** — no ops burden.

**Non-goals (v1)**
- Self-serve web app, customer accounts, live preview, payment handling.
- Automated Gelato order creation (spec'd in §6.4, not built in v1).
- The physical annotation kit (Product B).
- Multi-country storefront / subscriptions / interactive digital annotation app.

---

## 3. Product & SKUs

| SKU | Retail (illustrative) | Landed COGS (Sweden, verified) | What ships | Fulfillment |
|---|---|---|---|---|
| **Digital download** | €15–19 | €0 | ZIP: print-ready PDFs across standard sizes/ratios, **both** clean + annotate-me variants, a "how to print" note, license/attribution note | Instant, via Etsy digital delivery |
| **POD poster (unframed)** | €29–49 by size (50×70 hero @ **€39**) | **€12.41–16.90** (50×70 = **€15.28**) | One printed poster in the ordered size | Gelato dashboard upload (v1) |
| **POD framed poster** (premium / gift) | €59–149 by size/frame (50×70 @ **€99**) | **€34.66–109.44** (50×70 ready-to-hang = **€65.66–69.58**) | Framed, assembled, ready-to-hang poster | Gelato (frames + ships, zero inventory) |

> **Landed COGS is now verified** for Sweden ship-to from the Gelato dashboard export (see §6.3 for the
> full per-size table + provenance). **Retail figures remain illustrative** — chosen to show margin
> headroom, not market-validated; confirm against competitor listings before locking (market doc §C1).
> Framed is the gift upsell Gelato fulfills for us — it does **not** require building Product B.

---

## 4. Order flow (semi-manual, v1)

```
Etsy order (address + personalization in order note)
        │
        ▼
1. RUN generator ──► geocode + Overpass pull ──► intermediate playground list + draft preview
        │
        ▼
2. HUMAN QA  ──► fix names, drop private/duplicate/bad points, set radius/framing, pick theme + size
        │
        ▼
3. FINAL RENDER ──► clean.pdf + annotate-me.pdf  (+ full size/ratio bundle for digital SKU)
        │
        ├─ Digital SKU ─► deliver ZIP via Etsy
        └─ Poster SKU ─► upload print PDF to Gelato dashboard ─► enter buyer shipping addr ─► place order
        │
        ▼
4. LOG order (orders.csv: order#, address, theme, size, SKU, Gelato order id, date)
```

**Why human-in-the-loop is mandatory:** OSM coverage is crowdsourced and uneven — rich attributes are
patchy and some points are private/mis-tagged (prior-art scan §caveat). A per-order QA pass is what
keeps quality gift-worthy and is cheap at side-hustle volume.

---

## 5. Functional requirements

### 5.1 Data pipeline (extend the existing prototype)

Reuse from [`playgrounds.py`](../playgrounds.py): `geocode()`, `fetch_playgrounds()`
(mirror failover + retry/backoff + `nwr` node/way/relation handling + equipment-tag extraction),
`haversine_m()`, and the real User-Agent. **Add:**

- **Basemap geometry pull** — a beautiful map needs more than dots. Fetch, for the poster bounding box:
  roads (by class: motorway/primary/secondary/residential/footway), water (`natural=water`,
  `waterway`), green/park areas (`leisure=park`, `landuse=grass/recreation_ground`,
  `natural=wood`), and coastline (matters for Malmö). Via Overpass or `osmnx`.
- **Optional comfort layers** for the annotate-me variant: `amenity=toilets|bench|cafe`,
  `natural=tree` (→ shade hint). Bonus where tagged; never required.
- **Be a good API citizen:** keep the existing rate-limit/backoff/mirror-failover. For a fixed launch
  city, prefer a **Geofabrik `.osm.pbf` extract filtered locally with `osmium`** over repeated
  Overpass calls (plan doc §7). Per-order lookups elsewhere can still hit Overpass.
- **Reviewable intermediate artifact:** keep the existing `data/playgrounds.{geojson,csv}` output so
  the founder can eyeball/edit the point list before the final render (feeds step 2 QA).

### 5.2 Rendering engine — **style-agnostic, vector-first**

The renderer treats **visual style as data**, not code. A **theme** is a config object (JSON/py)
defining every look decision; swapping the theme swaps the entire aesthetic.

**Theme schema (starter):**
```
theme = {
  palette:   { land, water, green, coastline, roads:{motorway,primary,…}, playground_marker,
               home_marker, text, annotation_box, border },
  type:      { title_font, label_font, body_font, sizes },
  markers:   { playground_style, home_style, numbered:true },
  icons:     { icon_set_ref },          # custom playground-equipment glyphs
  texture:   { background, paper, border_style },
}
```

**Ship 2–3 starter themes** to A/B during the smoke test (directly serves the "prototype
style-agnostic, lock later" decision), e.g.:
- `whimsy` — kid-facing, warm, hand-illustrated feel, custom equipment icons (the intended moat).
- `minimal` — clean modern (incumbent-like baseline / control).
- `vintage` — storybook / treasure-map, hand-lettered, decorative border.

**Rendering approach — recommended: SVG-first composition.**
1. Pull OSM geometry (§5.1) → project to the poster's pixel/point frame (Web Mercator → poster box).
2. Emit **styled SVG layers** (land → water → green → roads → labels → playground/home markers),
   colored/weighted from the active theme.
3. **Compose the full poster in SVG**: map frame + title block + numbered markers + (variant-dependent)
   annotation furniture + attribution footer + optional compass/scale + bleed/registration marks.
4. **Export to PDF at exact print dimensions** via `cairosvg` / `rsvg-convert` (or `svglib`+`reportlab`).

**Why vector-first:** true resolution independence → the **≥300 DPI "crisp at any size"** promise is
structural, not a raster gamble, and it's a genuine selling point vs. raster-only Etsy competitors
(plan doc §3). It also gives full control over typography and the annotation furniture.

**Alternate map-body renderer (allowed behind the same theme interface):** `prettymaps`/`prettymapp`
(`osmnx` + `matplotlib`) reaches a "pretty" map body fast; if used, still compose the poster
furniture + export around it so the theme layer and output contract are identical. Pick one to
prototype with; keep the theme boundary clean so swapping is cheap.

### 5.3 Poster layout & the two variants

Both variants share the **map body, title, home marker, numbered playground markers, and attribution**.
They differ only in the furniture:

| Element | Clean variant | Annotate-me variant |
|---|---|---|
| Map body + numbered markers | ✅ | ✅ |
| Title / child's name / coordinates | ✅ | ✅ |
| ODbL attribution footer | ✅ | ✅ |
| **Numbered playground list** (matches map numbers) | — | ✅ |
| **Rating legend** (stars / faces) | — | ✅ |
| **Blank note lines / boxes** per park | — | ✅ |
| **Photo-corner spots** | — | ✅ |
| Aesthetic intent | gallery-clean, framable | co-created keepsake, writable blank space |

Auto-fill each playground's **known** equipment icons + shade/toilet/bench hints **where OSM has them**;
leave blank space for the family to fill the rest — sparse data is a *feature* here (prior-art scan).

### 5.4 Personalization inputs (from the Etsy order note)

| Input | Required | Default | Notes |
|---|---|---|---|
| Address / location | ✅ | — | → geocoded home marker |
| Title / child's name | ✅ | "Our Playground Map" | e.g. "Sofia's Playground Map" |
| Radius / framing | — | ~2–3 km (walkable, dense) | tighter than the prototype's 10 km — a poster wants a dense, legible frame; founder tunes in QA |
| Theme | — | launch default | one of the starter themes |
| Size(s) + aspect ratio | — | 50×70 (poster) / bundle (digital) | see §5.5 |
| Include/exclude specific parks | — | all in-radius, QA'd | founder edits the point list in step 2 |

### 5.5 Output / export spec

- **Resolution:** **≥300 DPI at final print size** (vector → non-issue, but validate the raster of any
  embedded texture/icon).
- **Standard sizes (digital bundle):** metric **A4 / A3 / A2** (1:√2) + imperial **US Letter / 16×20″ /
  18×24″**. Covers home printers *and* local print shops without buyer resizing (plan doc §3).
- **Aspect variants:** provide **portrait 2:3 and 5:7** where the map framing allows; bundle 2–3 as the
  docs suggest (cheap to generate, raises perceived value).
- **Formats:** print-ready **PDF** (primary). Add high-res **PNG** for buyers who ask.
- **Digital deliverable = ZIP:** all sizes/ratios × {clean, annotate-me} + `HOW-TO-PRINT.txt` +
  `LICENSE-ATTRIBUTION.txt`.
- **Naming:** `sofia_playground_A2_clean.pdf`, `sofia_playground_A2_annotate.pdf`, …

### 5.6 Human-in-the-loop QA gate (step 2)

Before final render, the founder must be able to: rename/relabel points, drop private/duplicate/bad
points, nudge the frame/radius, and choose theme+size — from the intermediate `data/*.csv` + a quick
draft preview. This is the quality gate that keeps output gift-worthy given patchy OSM data.

---

## 6. Gelato integration

### 6.1 v1 — manual dashboard fulfillment

For each poster order: export the correct print file → **upload to the Gelato dashboard** → select the
matching product/size → enter the **buyer's shipping address** → place the order → record the Gelato
order id in `orders.csv`. **No API keys, no code** in v1.

### 6.2 Print-file spec (⚠️ verify every "confirm" against the live Gelato dashboard)

| Requirement | Value | Status |
|---|---|---|
| File format | PDF (also accepts PNG/JPG) | confirm current Gelato accepted formats |
| Resolution | ≥300 DPI at final size | ✅ our standard |
| **Bleed** | typ. ~3 mm all sides | **confirm** exact per-product bleed in dashboard — do **not** assume |
| **Safe margin** | keep title/list/attribution inside | **confirm** safe-zone spec |
| **Color** | design RGB; Gelato converts to CMYK | **confirm** recommended profile; expect some color shift |
| Poster sizes | map our sizes → Gelato poster SKUs (e.g. 30×40 / 50×70 / 70×100 cm; A-series; 18×24″) | **confirm** exact catalog + which we sell |
| Paper / product | matte/premium poster | **confirm** product + finish |

**Render implication:** the SVG composer must support a **per-target bleed + safe-margin frame** and a
**Gelato export profile** distinct from the digital-download profile (the download needs no bleed).

### 6.3 SKU / price / size mapping — **Gelato COGS verified (Sweden, 2026-07-29)**

**Source:** Gelato dashboard price export, ship-to **Sweden**, product = **Classic Semi-Glossy Paper
Poster** (unframed) and **Classic Semi-Glossy Paper Wooden Framed Poster** (framed). Files in
[`gelato/`](../../../studio/print_on_demand/gelato/). All figures **EUR**, **Vertical = Horizontal** (Gelato prices both the
same). **"Landed COGS" = Gelato product price + Gelato shipping** — i.e. what *we* pay Gelato to print
and deliver one unit to the buyer.

> ⚠️ Scope of these numbers: **Sweden ship-to only**, single unit, semi-glossy paper, captured
> 2026-07-29. Re-pull for any other launch geo before promising it (§11). Confirm whether Gelato's
> quoted prices are **VAT-inclusive** before treating contribution as net. Etsy/payment-processing
> fees (listing + ~6.5% transaction + payment %) and any VAT are **not** deducted in the contribution
> columns below — they are **gross contribution before platform fees**.

#### A) Unframed poster (Classic Semi-Glossy Paper)

| Size | Gelato product | Gelato ship | **Landed COGS** | Illustrative retail† | Gross contribution† |
|---|---|---|---|---|---|
| A3 (29.7×42) | 5.82 | 7.07 | **12.89** | 29 | ~16.11 |
| 30×40 / 12×16″ (**Poster S**) | 5.34 | 7.07 | **12.41** | 29 | ~16.59 |
| 40×50 / 16×20″ | 6.64 | 7.16 | **13.80** | 35 | ~21.20 |
| A2 (42×59.4) | 7.74 | 7.07 | **14.81** | 39 | ~24.19 |
| 45×60 / 18×24″ | 8.05 | 7.07 | **15.12** | 39 | ~23.88 |
| **50×70 / 20×28″ (Poster M — hero)** | **8.21** | **7.07** | **15.28** | **39** | **~23.72** |
| 70×100 / 28×40″ (**Poster L**) | 9.07 | 7.83 | **16.90** | 49 | ~32.10 |

> This replaces the earlier "€39 poster, ~€14 contribution" estimate: at €39 the 50×70 hero actually
> clears **~€23.7 gross** (before Etsy/VAT), because landed COGS is €15.28, not the ~€25 the old guess
> implied. Even the small 30×40 at €29 clears ~€16.6.

#### B) Framed poster (Classic Semi-Glossy + wooden frame) — premium / gift SKU

Gelato frames, assembles, and ships — **zero inventory**, so this is the natural gift upsell **without**
building Product B. Frame colors: **White / Black** (cheaper) and **Wood / Dark wood** (dearer); each
in **Ready-to-hang** (gift-ready, recommended) or **Not assembled** (~€3–7 cheaper). Landed COGS below
uses **Ready-to-hang**; W/B → Wood-Dark shown as a range.

| Size | Landed COGS (RTH, White/Black → Wood/Dark) | Illustrative retail† | Gross contribution† |
|---|---|---|---|
| 30×40 / 12×16″ | 34.66 → 36.42 | 59 | ~22.6–24.3 |
| 40×50 / 16×20″ | 51.64 → 54.47 | 79 | ~24.5–27.4 |
| A2 (42×59.4) | 53.62 (all frames) | 89 | ~35.4 |
| 45×60 / 18×24″ | 54.14 → 57.16 | 89 | ~31.8–34.9 |
| **50×70 / 20×28″ (hero)** | **65.66 → 69.58** | **99** | **~29.4–33.3** |
| 70×100 / 28×40″ | 102.19 → 109.44 | 149 | ~39.6–46.8 |

> † **Retail and contribution are illustrative placeholders to show margin headroom — NOT
> market-researched price points.** Landed COGS is the hard, verified figure; validate retail against
> live competitor listings before locking (§11, market doc §C1). "Not assembled" framed variants cut
> COGS ~€3–7 if we'd rather protect margin than ship gift-ready.

**Shipping-tier note:** Gelato shipping steps up with size — **€7.07–7.16** (≤A2 / 45×60), **€7.83**
(70×100 / A1 unframed), and for **framed**: **€6.21** (≤A3), **€10.51** (40×50–50×50), **€12.52**
(50×70 and up). Size choice moves the shipping line, not just the print line.

> Sweden is a Gelato local-production country (in-country print, ≤5-day delivery, GDPR/ISO-27001, EU
> data residency) — this is the lever that makes a Swedish seller globally viable (market doc §C1).

### 6.4 Phase 2 — Gelato API automation (spec now, build later)

Trigger to build: manual fulfillment becomes the bottleneck (roughly sustained double-digit
orders/week). Scope when we get there:

- **Auth:** Gelato API key in **`.env` (gitignored)** — never committed (CLAUDE.md guardrail).
- **Product catalog:** resolve our sizes → Gelato product UIDs via the catalog endpoint; cache the map.
- **Order creation:** `POST` order with { product UID, quantity, **print-file URL** (host the rendered
  PDF at a temporary signed URL), buyer shipping address }.
- **Idempotency:** attach our Etsy order # as the external reference to prevent double-printing on retry.
- **Status/webhooks:** subscribe to order-status callbacks (printed / shipped / tracking) → update
  `orders.csv` (or a small DB) → optionally push tracking to the buyer.
- **Errors:** preflight/validation failures, address failures, print rejection → surface to the founder,
  never silently drop. Retries with backoff; fall back to manual dashboard on hard failure.
- **Test first:** use Gelato's sandbox/test mode before any live order.

> This section is a **spec, not a v1 deliverable.** No Gelato code, keys, or endpoints are built until
> the smoke test clears (§9 M4).

---

## 7. Licensing & attribution (non-negotiable)

- OSM data is **ODbL** → commercial derivative maps + resale are allowed **with attribution**.
- Every rendered/printed/sold artifact carries **"© OpenStreetMap contributors"** in the footer —
  clean variant, annotate-me variant, digital, and poster (plan doc §7, CLAUDE.md guardrails).
- The **styling/theme is our own layer** on top of ODbL data (the same posture Mapiful/Grafomap use).
- Include a `LICENSE-ATTRIBUTION.txt` in the digital ZIP.
- In listing copy: be honest — **digital = no physical item shipped; colors vary by printer/paper**
  (reduces refund/review risk; CLAUDE.md guardrail).

---

## 8. Tech architecture & recommended stack

```
scripts/
  playgrounds.py        # (exists) geocode + Overpass pull — reuse geocode(), fetch_playgrounds()
  basemap.py           # NEW: pull roads/water/green/coastline for the poster bbox
  render.py           # NEW: geometry → projected SVG layers → poster composition → PDF export
  themes/                    # NEW: whimsy.json, minimal.json, vintage.json (+ icon sets)
  fulfill.py                 # NEW: orchestrate an order → outputs clean.pdf, annotate.pdf, digital ZIP
data/                        # (exists) intermediate + reviewable playground list
output/<order>/              # per-order rendered PDFs + ZIP + a draft preview
orders.csv                   # NEW: lightweight order log
```

- **Env:** `uv` + Python 3.12 (per CLAUDE.md). New deps (candidate): `osmnx`/`shapely`/`pyproj` for
  geometry, `cairosvg`/`svgwrite` (or `svglib`+`reportlab`) for SVG→PDF, plus `prettymaps` if used as
  the alternate map-body renderer. Add to `requirements.txt`.
- **Config over code:** all look decisions live in `themes/*`; `render.py` is style-agnostic.
- **Determinism:** same address + theme + size ⇒ same output (cache the OSM pull per order).

---

## 9. Milestones

| # | Milestone | Definition of done |
|---|---|---|
| **M0** | Basemap fetch | `basemap.py` returns roads/water/green/coastline for a bbox; reuses mirror-failover. |
| **M1** | Style-agnostic renderer | `render.py` turns geometry + a theme into a composed **clean** poster PDF at one size; theme swap visibly changes the look. |
| **M2** | Both variants + sizes | Annotate-me furniture (list/legend/note/photo) added; export across the standard size/ratio set; digital ZIP assembled. |
| **M3** | Gelato print profile | Bleed/safe-margin/color export profile verified against the dashboard; one real test poster ordered and inspected in hand. |
| **M4** | Fulfillment loop | `fulfill.py` runs an end-to-end order from address → deliverables; `orders.csv` logging; **the founder's own daughter's map is the first finished artifact + product photography**. |
| **M5** | Smoke test live | 2–3 themes A/B'd; listings up (gift angle lead). *(Marketing milestone — gates the §6.4 API build.)* |

---

## 10. Success metrics

- **Engineering:** a QA'd, gift-worthy print-ready PDF for any launch-geo address in **< ~5 min of
  founder time**; passes Gelato preflight; in-hand color/quality judged acceptable.
- **Business (from market doc §C4):** **≥10–20 organic sales to strangers in 60–90 days**, with the
  **gift angle converting** → proceed to art-direction lock + API automation. If only downloads sell →
  stay digital-only. If nothing sells → ~€0 sunk cost; the founder still has his daughter's map.

---

## 11. Open items to verify (before locking)

1. ~~**Gelato COGS** per poster size~~ — **✅ resolved for Sweden** (unframed + framed, semi-glossy,
   2026-07-29; see §6.3). Remaining: (a) confirm whether Gelato prices are **VAT-inclusive**;
   (b) **re-pull COGS for each additional launch geo** (Nordics/DE/NL/UK/FR) before promising it;
   (c) validate **retail** prices against competitor listings (still illustrative, not market-set).
2. **Gelato bleed / safe-margin / color profile / accepted formats** — gates the print export profile.
3. **Which exact Gelato poster SKUs** we sell (size catalog + finish).
4. **Launch-geo QA:** spot-check OSM playground density for each market we *promise* (only sell
   markets we've verified — e.g. Malmö/Copenhagen/Berlin/Stockholm/London confirmed dense).
5. **Radius default** that yields a legible, dense poster frame (tune during M1–M2).

---

## 12. Explicitly out of scope (v1)

Self-serve web app · customer accounts / live preview · payment handling · **built** Gelato API
automation (spec only) · physical annotation kit (Product B) · multi-country storefront ·
subscriptions · interactive digital annotation app.
