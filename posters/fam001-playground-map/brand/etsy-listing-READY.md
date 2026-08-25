# Etsy Listing — READY TO PASTE

Everything needed to open the shop and publish the three products — **Digital file · Printed poster ·
Framed poster**. Because **size is now a priced variation**, sell them as **three separate listings**
(a size that changes price can't share a listing with a size-less digital file). Fill the
`[bracketed]` blanks (shop name availability, your name in the story), then paste.

> **All three are MADE-TO-ORDER.** Buyers pick size (and, for framed, frame color) at checkout and send
> their address in a note; you hand-style the map, then either deliver the file or place the print/frame
> order with Prodigi. That gives you a human checkpoint on every order and justifies your processing time.
>
> - **Digital** = a file delivered by Etsy message, **one price, no size variation** (all sizes are in
>   the file). Do **not** use Etsy's *Digital* listing type — it auto-delivers instantly, which is the
>   instant download you're not selling. Never write "instant download" anywhere in the shop.
> - **Printed / Framed** = we print in-country via **Prodigi** and ship to the buyer. No inventory.
>   **Price varies by size**; framed also varies by frame color (same price).
> - **One SKU per variation** — the SKU you enter on Etsy is also the code you use to pick the Prodigi
>   product (see `studio/print_on_demand/sku_manager.xlsx`).

---

## 1. Shop setup

| Field | Value |
|---|---|
| **Shop name** (4–20 chars, no spaces) | `HopscotchMaps` — backups: `OurLittleMap`, `LittleWayfinders` |
| **Shop Title / tagline** (≤55 chars, SEO) | `Personalized Playground Map · Family Keepsake Gift` |
| **Currency / location** | Your local (Sweden) |

> Check `HopscotchMaps` availability on Etsy sign-up + grab the Instagram handle before committing.

**Shop announcement (banner):**
> 🌿 Warm, hand-illustrated maps of your family's local playgrounds — a keepsake your little one helps
> create by rating parks, drawing, and adding photos. Choose a digital file, a printed poster, or a
> framed print. Made-to-order. Made by a dad, for families like yours. 💛

---

## 2. The listing (one listing, three formats)

**Listing title** (front-loaded keywords, ≤140 chars — paste as-is):
```
Personalized Playground Map, Custom Family Keepsake Print, New Baby & Nursery Gift, Kids Adventure Map, Digital, Poster or Framed
```

**Description** (paste-ready):
```
A keepsake map of your family's playgrounds, that your little one helps make. ✨

Tell us your address and how far you'd like to roam, and we'll hand-style a warm, illustrated map of every playground around you, ready to rate, draw on, and fill with photos. A gentle screen-free ritual and a childhood keepsake in one.

AVAILABLE THREE WAYS (each is its own listing, see our shop):
• Digital file: a print-ready PDF you print at home or at a local shop
• Printed poster: we print it in your country and ship it, ready for the wall (choose 30×40 / 40×50 / 50×70 cm)
• Framed poster: printed and framed in wood, ready to hang (choose your size)

PLEASE NOTE, every format is MADE TO ORDER, not an instant download. We hand-style your map for your address after you order. Digital files arrive by Etsy message within 2–3 days; printed and framed maps are produced and shipped locally after you approve the look.

WHAT YOU GET:
• A distinctive, hand-styled map of your playgrounds, numbered list, a star-rating legend, and blank spots for notes, drawings & photo corners
• Personalization: your title ("Sofia's Playground Map"), a color theme, and a home marker
• Digital: a print-ready PDF at 300+ DPI, crisp at any size, plus a short how-to-print guide
• Printed poster: quality 170gsm silk poster paper, printed in-country and shipped to you
• Framed poster: the poster in a real frame, ready to hang out of the box

CHOOSE YOUR STYLE:
• Whimsy: warm, hand-illustrated, storybook (most popular)
• Ink & Play: soft, timeless, muted tones
• Minimal: clean and modern

PERFECT AS A: new baby gift 🍼 · baby shower present · first-birthday keepsake · nursery wall art ·
a thoughtful gift for a family who loves the outdoors.

HOW TO ORDER:
1. Choose your size (and, for framed, the frame color) and add to cart. In the note to seller, tell us:
   – your address or neighborhood
   – the title/child's name
   – color theme
2. We hand-style your map and send you a preview to approve. We'll message you if your area is very quiet so we can widen the map or re-center it.
3. Digital: we deliver your files by Etsy message (usually within 2–3 days). Poster/framed: we print and ship it in your country once you approve.

Need it for a specific date? Message us before ordering and we'll tell you honestly if we can make it.

```

**Tags (13 — paste individually):**
```
personalized map, playground map, family keepsake, new baby gift, nursery wall art,
kids room decor, first birthday gift, custom map print, framed map print,
made to order gift, keepsake gift, personalized baby gift, family adventure map
```

**Listing attributes** (apply to each of the three listings):
- **Category:** Art & Collectibles → Prints. Use **Digital Prints** for the digital listing; the
  physical **Prints** category for the poster and framed listings.
- **Who made it:** I did · **What is it:** A finished product · **When:** Made to order (2020s)
- **Type:** Digital listing = deliver the file by Etsy message (do *not* use Etsy's auto-delivering
  *Digital* type). Poster/framed listings = physical, shipped via **Prodigi**.
- **Shipping:** attach the matching profile from §2c — *Digital — free* / *Poster — worldwide* /
  *Framed — Europe & US only*.
- **Personalization:** ON (prompt: *"Address/neighborhood, radius, title, color theme, clean or
  adventures layout"*). Size + frame color are **variations**, not personalization.
- **Processing time:** 2–3 business days to hand-style + preview; physical prints then ship via Prodigi.
- **Variations (this is the change — size is now priced):**
  - **Digital listing:** no size variation — **one price** (all sizes are in the file).
  - **Poster listing:** **Size** (priced) — `30×40 cm` · `40×50 cm` · `50×70 cm`.
  - **Framed listing:** **Size** (priced) — `30×40` · `40×50` · `50×70 cm` — **×** **Frame color**
    `Wood` · `White` (same price per size).
  - Turn **on "SKU"** in the variation editor and enter the single SKU per row from `sku_manager.xlsx`
    (e.g. `PGMAP-POS-5070`, `PGMAP-FRM-WO-4050`).
  - Keep **Style** (Whimsy / Ink & Play / Minimal) and **Layout** (Clean / Adventures) as
    personalization notes, not priced variations, to keep the option list short.

---

## 2b. Pricing (per size — size is a priced variation)

Each **size** has its own price **and its own single SKU** (the SKU you enter on Etsy is the same code
you use to order from Prodigi). Prices in EUR — enter in SEK (shop currency). Costs are **live Prodigi
quotes** (item + Budget shipping, **to Sweden**, ex-VAT — pulled 2026-07-31 via
`studio/commerce/prodigi_quotes.py`). Net is **VAT-inclusive** (irrecoverable input VAT while unregistered);
full model in `studio/print_on_demand/sku_manager.xlsx`.

**Digital file** — one price, no size variation (all sizes in the file):

| Price | SKU | Cost | Net (VAT-incl) |
|---|---|---|---|
| **`€24`** | `PGMAP-DIG` | €0 | **~€20** |

**Printed poster** — Budget poster, Silk 170gsm:

| Size | Price | SKU | Prodigi SKU | Cost to SE | Net (VAT-incl) | Margin |
|---|---|---|---|---|---|---|
| 30×40 cm | **`€34`** | `PGMAP-POS-3040` | `GLOBAL-BLP-12X16` | €10.40 | ~€16 | 47% |
| 40×50 cm | **`€39`** | `PGMAP-POS-4050` | `GLOBAL-BLP-16X20` | €10.90 | ~€20 | 50% |
| 50×70 cm | **`€44`** | `PGMAP-POS-5070` | `GLOBAL-BLP-20X28` | €14.00 | ~€20 | 46% |

**Framed poster** — Budget frame, no mount, wood/white (same price per size; SKU suffix `-WO` / `-WH`):

| Size | Price | SKU (wood / white) | Prodigi SKU | Cost to SE | Net (VAT-incl) | Margin |
|---|---|---|---|---|---|---|
| 30×40 cm | **`€79`** | `PGMAP-FRM-WO-3040` / `-WH-3040` | `GLOBAL-BFP-12X16` | €32.95 | ~€27 | 34% |
| 40×50 cm | **`€89`** | `PGMAP-FRM-WO-4050` / `-WH-4050` | `GLOBAL-BFP-16X20` | €37.95 | ~€29 | 33% |
| 50×70 cm | **`€109`** | `PGMAP-FRM-WO-5070` / `-WH-5070` | `GLOBAL-BFP-20X28` | €49.40 | ~€32 | 30% |

**Paper / frame notes:**
- `GLOBAL-BLP-*` = **Budget poster, Silk 170gsm** — cheapest Prodigi poster (avoid `GLOBAL-CONS-BLP-*`,
  which routes with €30+ shipping). Optional **premium-paper upsell:** `GLOBAL-PAP-*` (Photographic Art
  Print 240gsm) at +€2–5/unit, or `GLOBAL-FAP-*` (Enhanced Matte) at the same price as PAP.
- `GLOBAL-BFP-*` = **Budget frame** — `color`: wood → `natural`, white → `white`. Rectangular budget
  frames are wood/white only (no black). Frame attrs: `frame=Budget, glaze=Acrylic / Perspex,
  mount=No mount / Mat, paperType=Silk, substrateWeight=150gsm`. Cheaper than the Classic frame
  (`GLOBAL-CFP-*`), which was chosen against because it netted as little as ~€14 on an A2.

\* Etsy fees (Sweden): 6.5% transaction + 4% payment + ~3 kr + $0.20 listing. Net above is VAT-inclusive
and shipped to SE; costs rise for overseas ship-to (see §2c and the Region surcharges sheet). Excludes
any 15% Offsite Ads fee.

**Why this ladder:**
- **Digital €24** — unchanged; researched against the comp set below. **Launch promo ~€18** (25% off)
  for the first ~10 orders to buy reviews, then hold €24. **Never below €15.**
- **Poster €34 → €44** — priced up the IKEA ladder (30×40 · 40×50 · 50×70); costs €10.40–€14.00 so
  every size nets ~€16–20 (46–50%). Small sizes get an attractive entry price; large sizes carry more.
- **Framed €79 → €109** — the €20 jump to 50×70 keeps its margin at ~30% (frame cost climbs fastest at
  the top). All three sizes net ~€27–32. Sits mid-range vs the comp band (framed seen ~€44–177).
- **⚠️ Destination matters — margins thin out on overseas orders.** Prodigi bills by
  ship-to country: e.g. **50×70 poster** GB €12.68 · SE €14.00 · **US €16.18** · DE €17.06; **50×70
  framed** DE €42.95 · GB €47.27 · SE €49.40 · **US €54.18**. Either add a small physical **shipping
  charge** on Etsy, or **limit physical shipping to the EU/UK at launch** and keep the US on digital only.
- **Fulfiller note:** with the Budget frame, **Prodigi is now cheaper than Gelato for framed too**
  (50×70 wood: Prodigi €49.40 vs Gelato €69.58; 30×40: €32.95 vs €35.32) — and comparable on posters
  (~€1–4 apart). **Prodigi for both tiers** is the simplest call. Re-check anytime with
  `studio/commerce/prodigi_quotes.py` and the Gelato CSVs in `studio/print_on_demand/gelato/`.

| Comparable (custom map) | Digital | Printed | Framed |
|---|---|---|---|
| Mapiful / Grafomap | — | from ~€49 | from ~€79 |
| Craft & Oak | $25 PDF | from $44 | — |
| MapToArt | $15 / $35×3 | — | — |
| Etsy "custom map" band | ~$8–$50 | ~$15–$70 | ~$45–$180 |
| Attached comp (SEK→€ approx) | ~€9–18 | €11–72 (1 print) | €44–177 (1 frame) |

---

## 2c. Etsy shipping profiles (ready to paste)

Etsy sets shipping **per listing**, not per variation, and it can't vary the **item** price by country —
only shipping. Since size is now a priced variation you're already running **three listings**, so give
each its matching profile below. Prices are the region surcharges from `sku_manager.xlsx`, grossed up
for Etsy's 6.5% shipping fee.
Enter them in **SEK** (shop currency); SEK shown at ~11.30/€ — update to your rate.

**Profile 1 — "Digital — free (delivered by message)"**
- Ship from: **Sweden** · Processing time: **2–3 business days**

| Destination | One item | Additional item |
|---|---|---|
| Everywhere | **Free (€0)** | €0 |

> Nothing is mailed — free everywhere. (If you use Etsy's *Digital* listing type this is automatic; we
> deliver by message instead, so keep shipping at €0.)

**Profile 2 — "Poster — worldwide"**
- Ship from: **Sweden** · Processing time: **3–5 business days**

| Destination | One item | Additional item |
|---|---|---|
| European Union (region) | **Free (€0)** | €0 |
| United Kingdom | **Free (€0)** | €0 |
| United States | **Free (€0)** | €0 |
| Everywhere else (Canada, AU, JP, RoW) | **€13 (~147 kr)** | €13 |

> Baseline poster cost (€10–14) is already inside each poster's price, so Europe/US ship free. €13
> covers the +€10–11 that Canada/Australia/Japan add. Add Norway/Switzerland individually at €0 if you
> want them (slight customs risk, cost is similar).

**Profile 3 — "Framed — Europe & US only"**
- Ship from: **Sweden** · Processing time: **5–7 business days** (frame production is slower)

| Destination | One item | Additional item |
|---|---|---|
| European Union (region) | **Free (€0)** | €0 |
| United Kingdom | **Free (€0)** | €0 |
| United States | **€6 (~68 kr)** | €6 |
| *(do NOT add "Everywhere else")* | — | — |

> **Deliberately no "Everywhere else."** Framed to Canada/Australia/Japan ships internationally with no
> local frame (€115–165 cost) — leaving it off makes framed unavailable there, so those buyers see only
> digital/poster. **US:** offer framed in **40×50 / 50×70 only** (Prodigi doesn't fulfil framed 30×40 in
> the US). Optional: allow **Canada** at **€70 (~791 kr)** if you're willing to sell a ~€179 frame there.

Because you're running the three products as **separate listings**, each simply gets its own profile
above — no compromise needed. (This is also why per-size pricing pushed you to the split: a size that
changes price can't live in the same listing as the single-price digital file.)

---

## 3. Buyer message templates

**On order (auto or quick reply):**
> Thank you so much! 💛 I've got your [size / size + frame color] and I'm hand-styling your playground
> map now. Just confirming the rest: your address/area, how far to roam, your title, and color theme.
> I'll send you a preview before we finalize.

**Sparse area (the sparse-address save):**
> Quick note on your map! Your immediate area has [N] playgrounds. I can widen the radius to ~[X] km
> to include more, or re-center on a spot you love — which would you prefer? Want it to feel full and
> lovely for you. 🌿

**Preview to approve:**
> Here's your preview! ✨ Take a look — happy to tweak the color, title, or framing. Once you're happy,
> I'll [deliver your files / send it to print and ship it to you].

**Delivery — digital:**
> Your map is ready! 🎉 Files attached: print-ready PDF in [sizes]. Print at home or at a local shop —
> the how-to-print guide is included. Thank you for letting me be part of your family's ritual. 💛

**Delivery — printed / framed:**
> Your map is off to print! 🎉 It's being produced and shipped to you in [country] and should arrive in
> [X] days — I'll share tracking as soon as it's on the way. Thank you for letting me be part of your
> family's ritual. 💛

---

## 4. Listing photo order (10 slots — see product-photography-ideas.md)

1. Framed on styled wall (hero) — clearly a playground map
2. **Three formats side by side (Digital · Poster · Framed)** — mirrors the format picker ⭐
3. Father & daughter choosing a park (ritual) ⭐ *(needs a real print — add later)*
4. Nursery / kids-room context
5. Color-themes showcase (Whimsy / Ink & Play / Minimal)
6. "Our Playground Adventures" close-up (stars + photo corners)
7. Personalization showcase (title + home marker)
8. Size guide
9. "What you get" info card
10. How-it-works, 3 steps + honest note (colors vary; digital = file only)

*(Mockups for the framed hero, three-format card, style showcase, what-you-get, size guide,
how-it-works, and honest note are generated in `posters/fam001-playground-map/brand/listing-photos/`.)*

---

## 5. Pre-publish checklist
- [ ] `HopscotchMaps` available on Etsy + Instagram handle grabbed
- [ ] **Three listings** created (Digital / Poster / Framed) + SEK conversion checked
- [ ] Per-size prices set — Digital €24 · Poster €34/€39/€44 · Framed €79/€89/€109
- [ ] **Size variation** priced on the poster & framed listings (framed also × frame color); Digital = one price
- [ ] **SKU** turned on per variation and filled from `sku_manager.xlsx` (e.g. `PGMAP-POS-5070`)
- [ ] `[your name]` filled into the About story ([store-description.md](store-description.md) §3)
- [ ] 7+ listing photos uploaded (from `posters/fam001-playground-map/brand/listing-photos/`)
- [ ] Shipping profiles attached (§2c): Digital free · Poster worldwide · Framed EU+US only
- [ ] Personalization ON; processing time set; digital = deliver by message (not Etsy Digital type)
- [ ] No "instant download" wording anywhere (title, description, tags, photos, announcement)
- [ ] Prodigi account connected + a test print ordered of your own map (also becomes your hero shot)
- [ ] Payment/deposit set up (Etsy Payments)
- [ ] One test purchase-flow read-through per listing
