---
idea: "FAM-001 Playground Map"
phase: 2
date: 2026-07-28
verdict: 🟡
---

# FAM-001 Playground Map — Phase 2 Product One-Pager

> **Positioning in one line:** A beautiful, personalized printed map of a family's local playgrounds — not to *find* a park (Google Maps does that), but to **choose one together**, and to let a child co-create a keepsake by rating parks, noting the equipment, drawing, and sticking photos. Sold digital-first (instant download + print-on-demand poster) with a physical **annotation gift kit** as the premium/new-parent-gift upsell.

> **Founder framing:** explicitly a **side hustle, not a full-time business.** Fuat is building this for his daughter anyway — that authentic motivation is the single biggest reason it will actually get built and marketed with a real voice. Evaluate ROI on *joy + modest income + low risk*, not venture upside.

---

## 1. Problem & who has it

**The pain (soft, but real).** Parents of young kids face the same tiny daily friction: "Where should we go today?" The decision is made *for* the child, in the parent's head, in 10 seconds. Two things are missing:

- **No shared ritual.** Choosing a playground could be a moment the child participates in — looking at a map, discussing what's there ("the one with the big slide" / "the one near the ice-cream place"), building anticipation. Today it's invisible.
- **No memory artifact.** The dozens of little playground outings of early childhood leave no trace. There's no object the child helped make that says "these were *our* places."

**ICP (two distinct buyers):**
1. **The parent (self-purchase)** — a parent of a 1–6-year-old who values ritual, screen-free activities, and keepsakes; likely already buys personalized/Montessori-ish/"slow parenting" products.
2. **The gift-buyer** — a friend/relative buying for **first-time or new parents** (baby shower, birth, first-birthday). This is arguably the *stronger* commercial wedge: personalized new-baby gifts are a proven, high-intent, emotion-driven Etsy category with real willingness to pay.

**Why now.** Print-on-demand (Gelato, prints locally in-country in ~30+ countries) has removed the inventory + cross-border-shipping barrier that used to make a Sweden-based physical-gift business painful. A solo founder can now sell a printed, personalized product globally with **zero stock and near-zero ops.**

---

## 2. How we solve it (core insight)

The core insight: **the value is emotional and physical, not informational.** Anyone can look up nearby playgrounds. What no app delivers is a *tangible, co-created object* and the *family ritual* around it. So we don't build a "playground finder" (a red ocean of apps and a job Google Maps already owns). We build a **keepsake + ritual** — and we make it *scalable* by generating the map automatically from open data so it works for any address, anywhere with good coverage.

Two products, one engine:
- **The engine** turns "any location" into "a beautiful playground map" automatically → geography-agnostic, zero manual drawing per order.
- **The product** is the map as a *canvas for a family ritual and a childhood keepsake.*

---

## 3. What we're building (concrete features & flow)

**Product A — Digital map generator (ship this first; it's the scale engine):**
- User enters an address / neighborhood / radius.
- System pulls playgrounds from **OpenStreetMap** (`leisure=playground`, plus parks/water-play/toilets/cafés as optional layers) and renders a **print-ready, styled map** in a distinctive art style (see moat) — not a clinical OSM render.
- The map includes **annotation zones**: a numbered playground list, a rating legend (stars/faces), blank boxes beside each park for notes/drawings, and photo-corner spots.
- Personalization: title ("Sofia's Playground Map"), color/theme, optional "home" marker.
- Delivered as **(a) instant high-res PDF download** (print at home or at a local print shop) and/or **(b) a print-on-demand poster shipped** via Gelato.

> **Digital-download spec — match the category standard (competitor reference, 2026-07-28).** A digital-selling competitor describes their download exactly as: *"PDF file specifically designed and formatted for high-quality printing. Delivered at **300 DPI or higher**, this **print-ready PDF** ensures **crisp lines, vibrant colors, and exceptional detail** in every image and text element."* This is the bar for the digital SKU — bake it into both the deliverable and the listing copy:
> - **Vector-first render → export to PDF at ≥300 DPI** so lines/text stay crisp at any print size (a vector map is naturally resolution-independent — this is a strength vs. raster-only sellers).
> - Deliver in **standard print sizes** (e.g. A4/A3/A2 + US Letter/16×20"/18×24") so buyers can print at home *or* a local shop without resizing headaches — a common Etsy complaint to pre-empt.
> - Set expectations clearly: **digital = no physical item shipped**; colors may vary by printer/paper. Reduces refund/review risk.
> - Consider bundling **2–3 aspect ratios / color variants** per order — cheap to generate, raises perceived value vs. a single-file competitor.

**Product B — Physical annotation gift kit (premium/gift upsell, add after A validates):**
- Framed or rolled printed map **+** a small kit: rating stickers, washable markers/crayons, photo corners / instant-photo pockets, and a slim **"Our Playground Adventures" booklet** (prompts: favorite thing, who we went with, what we did).
- Positioned and packaged as a **baby-shower / new-parent gift.**

**Main flow / what it feels like.** Parent (or gift-buyer) enters a location → previews a genuinely beautiful, personalized map → buys the download (€19) or the poster (€39) or the gift kit (€59–89). The family pins/frames it at kid height, and choosing where to go becomes a **two-minute ritual around the map** instead of a decision in the parent's head. Over months it fills with stickers, scribbles, and photos → it becomes the thing that survives when the kids outgrow the swings. It should feel like **a warm, hand-illustrated childhood artifact**, not a utility app.

---

## 4. Moat / why not ChatGPT (be honest here)

**Passes the ChatGPT Test, but not via an LLM moat.** A general LLM can *list* nearby playgrounds; it cannot ship a printed, personalized, hand-illustrated keepsake, and it cannot deliver the tactile "choose together / draw / stick a photo" experience. The value is **physical + emotional + ritual**, which is exactly what LLMs *can't* absorb → LLM-defensibility = 4.

**But the real competitive threat is other humans, and here the moat is thin.** This is the honest red flag to design around:
- The custom-map print-on-demand category is **saturated** (Mapiful, Grafomap, thousands of Etsy sellers). There's no data flywheel and no regulatory/workflow moat — none of the 6 durable moats apply cleanly.
- The only defensible assets are **(1) a distinctive, ownable art style/brand**, **(2) the specific niche** (playgrounds + families, which nobody owns today), and **(3) the ritual/gift framing** (a *reason to buy* that a generic city-map seller doesn't have).
- **Implication:** win on **taste and positioning**, not on tech. The generator is a convenience/scaling tool, not the moat. If the art looks like a raw OSM export, this fails — the incumbents are gorgeous and that's the bar.

---

## 5. MVP scope (80/20)

**The vertical slice — and it already exists in Fuat's own plan:**
1. **Build the generator for his own city, for his daughter.** That single finished map *is* the MVP and the first product photo/listing. (He's doing this regardless → sunk-cost-zero validation.)
2. **List two SKUs on Etsy:** a **€19 instant digital download** (personalized to a submitted address) and **one €59 gift-kit** (or a €39 POD poster to start, to avoid physical assembly). Etsy brings built-in gift-buyer traffic — no need to build a store or run ads to test demand.
3. **Personalization = semi-manual at first.** Don't build a self-serve web app for v1. Take the address in the Etsy order note, run the generator, deliver the PDF/poster by hand. Automate the front-end only *after* orders prove people want it.

**Explicitly out of scope for v1:** self-serve web app, user accounts, a digital/interactive annotation app, multi-country storefront, the full physical kit with sourced components, subscriptions. **Time-to-first-usable-version:** the map for his own city is essentially done as a personal project; the first Etsy listing is a weekend of styling + product photography on top.

---

## 6. How it makes money

- **Digital download** €15–29 — ~95% margin, zero ops, infinitely scalable, any geography with OSM coverage. *The volume/scale product.*
- **POD poster (Gelato)** €35–49 — ~40–60% margin after print+ship, zero inventory. *The middle tier.*
- **Physical gift kit** €59–89 — higher AOV, but component sourcing + assembly + shipping eat margin and time. *The premium/gift tier — add only once the funnel is proven.*
- **Buyer split:** self-purchasing parents (download/poster) + gift-buyers (kit). The **gift** segment likely carries the higher AOV and the emotional willingness-to-pay.
- **Channel:** Etsy first (borrow the gift-buyer traffic), then own Shopify once there's a repeatable seller. **No paid ads** to start — organic/Etsy SEO + the personal story.

---

## 7. Tech approach

- **Map generation:** OpenStreetMap data (`leisure=playground` + park/amenity layers) via Overpass API / `osmnx`; render with a styling layer for a distinctive look — options: Python (`prettymaps`/`prettymapp`, `osmnx` + `matplotlib`), or a vector/tile stack (MapLibre/Mapbox styles) exported to high-res print PDF. He can ship this solo with AI tooling.
- **Data source — validated (2026-07-28, live Overpass test).** OSM is the *only* viable source, for two reasons. (1) **It's the only provider with a first-class, bulk-extractable `leisure=playground` layer** — Google Places has a `playground` type but Apple, Bing/Azure and HERE have *no* playground category (only generic "park/recreation"). (2) **Licensing is decisive for a printed product:** OSM is ODbL → commercial derivative maps + resale are allowed with attribution ("© OpenStreetMap contributors"); Google/Apple/HERE/Azure ToS *prohibit* redistributing their POI data or building a standalone printable map from it. This is exactly why Mapiful/Grafomap/prettymaps all run on OSM. Bonus: OSM also carries per-equipment tags (`playground=swing|slide|sandpit|climbingframe…`) + `min_age`/`max_age`/`surface`/`wheelchair` → free fuel for the product's "note the equipment" annotation feature.
- **How to actually pull "all playgrounds" from OSM (two web tools worth knowing):**
  - **Option 1 — Overpass Turbo ([overpass-turbo.eu](https://overpass-turbo.eu)) — the extraction workhorse.** Paste a query, hit Run, then **Export → GeoJSON/GPX/KML**. Query catches both point + polygon playgrounds via `nwr` (node/way/relation): `nwr["leisure"="playground"]({{bbox}}); out center;` for the current map view, or scope to a named place with `area["name"="Malmö"]->.a; nwr["leisure"="playground"](area.a); out center;`. `out center;` collapses each polygon to one marker-friendly point. Can filter on the combination tags (`["wheelchair"="yes"]`, `["fenced"="yes"]`, etc.). ⚠️ **Don't hammer the public Overpass API for country-scale/bulk pulls** — for that, download a **Geofabrik** regional `.osm.pbf` extract and filter locally: `osmium tags-filter in.osm.pbf nwr/leisure=playground -o playgrounds.osm.pbf`. This is the polite + fast path for production data pulls; the live Overpass API is for spot checks and per-order lookups.
  - **Option 3 — taginfo ([taginfo.openstreetmap.org/tags/leisure=playground](https://taginfo.openstreetmap.org/tags/leisure=playground)) — coverage/sizing, not a map.** Gives global + per-country counts, node/way/relation split, and which combination tags are actually populated. Use it up-front to decide *which markets have data good enough to sell* and *how patchy the rich attributes are* before committing a launch geography (already leveraged in the Phase 3 prior-art scan: 1M+ playgrounds globally; DE 135k · UK 47k · FR 45k · NL 33k · SE 20k).
- **The hard part is *art*, not code.** Budget most effort on the visual style (palette, typography, iconography, hand-drawn feel) — consider commissioning or AI-assisting a custom icon set for playground equipment. This is where the money/moat is.
- **Fulfillment:** Gelato API (Nordic, local printing in ~30+ countries → cheap in-country shipping, GDPR-friendly) for posters; PDF delivery for downloads. Avoid self-shipping anything until the kit tier is validated.
- **Storefront:** Etsy (v1) → Shopify + a small self-serve generator front-end (v2).
- **Build risks:** (a) OSM data gaps/quality per city; (b) achieving a *gift-worthy* aesthetic; (c) semi-manual personalization not scaling — but that's a good problem to have and only worth automating post-demand.

---

## 8. Open questions (resolve before/while building)

1. **Which buyer leads — self-purchasing parent or gift-buyer?** Test both listings; the gift angle may be the real business.
2. **Art direction:** what's the ownable style? (Illustrated/whimsical vs. clean/modern vs. vintage-cartography.) This decision *is* the brand.
3. **Digital-only vs. physical kit:** does the emotional payoff survive as a print-at-home PDF, or does the magic *require* the physical framed object + stickers? (Affects margin and ops enormously.)
4. **Geography scope:** which markets have OSM playground coverage good enough to sell confidently? ✅ *Partially resolved (2026-07-28, live Overpass counts, 2 km radius from center):* Copenhagen 112, Berlin 200, Malmö 61, Stockholm 56, London 46 — Nordics/DE/NL/UK confirmed dense and sellable. Coverage is crowdsourced so it thins in southern/eastern Europe, rural areas, and US suburbs → keep a human-in-the-loop QA step per order and only *promise* markets you've spot-checked.
5. **Personalization boundary:** how much per-order customization can be offered before it stops scaling? (Fixed templates + address only, vs. bespoke.)

*(Market sizing, competitor teardown, and unit-economics validation are Phase 3 items — not resolved here.)*

---

## 9. Updated feasibility scores

| Axis | Score | Note |
|---|---|---|
| **Ease of execution** | **4** | Generator is a few weekends; digital-download path has near-zero ops. Physical kit drags it down → lead digital. |
| **Potential** | 3 *(provisional)* | Proven POD-map category, but playground niche + side-hustle scope = modest. Validate in Phase 3. |
| **Competition** | 3 *(provisional)* | Saturated custom-map POD; winnable only via niche + taste + gift framing. Validate in Phase 3. |
| **LLM-defensibility** | **4** | Safe from LLMs (physical/emotional keepsake). ⚠️ Not an LLM moat — thin vs. human copycats; brand/art/niche only. |
| **Founder fit** | **4** | Personal motivation is decisive for a side hustle; his engineering builds the generator. Drag: ops/design, not his AI/finance edge. |

**Total: 18/25 · Verdict 🟡 Watch** — genuinely 🟢 *as a low-risk side hustle he's building anyway.*

---

## Recommended next move

Build the generator for his own city (already the plan) → that map **is** the MVP. List one **€19 digital download** and one **€59 gift kit** (or €39 POD poster) on Etsy. **Riskiest-assumption test:** will a *stranger* buy the *gift* framing? If yes, invest in art direction + a self-serve front-end. If only the download sells, stay lean and digital-only. Do **not** source physical supplies at scale until the gift tier proves out.
