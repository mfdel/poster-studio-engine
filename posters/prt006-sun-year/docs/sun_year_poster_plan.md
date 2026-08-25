---
idea: "PRT-006 Sun-Year Poster"
phase: 2
date: 2026-08-03
verdict: 🟡
---

# PRT-006 Sun-Year Poster — Phase 2 Product One-Pager

> **Positioning in one line:** A portrait of **a year of light at one address** — 365 sunrises and sunsets rendered as a single ring of gold on darkness — with **one day marked and its real sunrise time printed**. Not "when the sun rose"; *"the sun rose at 08:41 the morning you were born, here."*

> **Emotional hook (the thing that must carry the whole product):** for anyone living above ~55°N, the **10.5-hour gap between the June day and the December day is not data — it is what the year feels like.** The poster is a picture of the dark you got through and the light you got back. Sold to people for whom light is a cultural obsession, anchored to one date that belongs to them.

> **Founder framing:** side hustle. This is **SKU #2 in an Etsy store that already exists and has sold nothing.** Evaluate it as a cheap, different-audience second shot at the same channel — not as a new business.

---

## 1. Problem & who has it

Be honest: **there is no pain point here.** Nobody wakes up needing a sunrise poster. This is a **discretionary gift/décor purchase**, and the "problem" it solves is the gift-buyer's problem: *I want to give something personal that isn't a mug with a name on it, and I want it to mean something in five years.*

The specific gap it fills sits inside a proven buying motive — **personalized astronomical keepsakes tied to a date** (the star-map category: "the night sky the night we met"). That category proved people will pay €30–60 for a beautiful, mathematically-derived print anchored to one meaningful date. The sun-year poster is the **same motive, a different celestial body, and a far more culturally loaded one in the Nordics**, where the star map's "night we met" is generic but "the winter we made it through" is not.

**ICP — narrower and sharper than FAM-001:**
1. **The Nordic/northern identity buyer (self-purchase).** Lives at ≥55°N. Owns the light/dark cycle as part of who they are — Lucia, midsommar, *mörkret*, the SAD lamp on the desk. Buys the poster of their own city because it is a picture of their own year.
2. **The occasion gift-buyer.** Anchored to a date: a birth, a wedding, **the day they moved into the house** ("our first year here"), a first anniversary. This is the higher-intent, higher-AOV buyer, exactly as in FAM-001.
3. **The northern expat.** Moved from a low-latitude country to Scandinavia/Scotland/Canada; the extremity of the ring *is* their culture-shock story.

**Why now:** the pipeline is already built. Etsy store open, Gelato configured, FAM-001's print-ready-PDF spec already defined. The marginal cost of testing a second product is one or two weekends, not a launch.

---

## 2. How we solve it (core insight)

**The core insight, stated as bluntly as it deserves: the astronomy is not the product. The astronomy is the *shape generator*. The product is the marked date.**

This matters because the obvious failure mode of this idea is being **beautiful but emotionally cold** — a pretty gradient donut that nobody feels anything about. The defence is structural, not decorative:

- **The ring alone is décor.** Nice, forgettable, worth maybe €12, competes with every abstract print on Etsy.
- **The ring + your city + one marked day + the actual sunrise time on that day** is a keepsake. It says *this specific year of light, at this specific place, and this one morning inside it.* That is a sentence about a person, not a chart.

So the personalization axes are **not garnish — the annotation IS the product** and the data-art is the frame around it. Any version of this that ships without a marked date is the cold version and will fail.

The second structural asset: **the shape is genuinely different per latitude and cannot be faked.** Malmö's asymmetric crescent, Kiruna's polar-night notch. The buyer can see it is *theirs*. That is what separates this from generic abstract wall art — and it is also precisely what breaks near the equator (see §3).

---

## 3. What we're building (concrete — what the artwork actually looks like)

**The core artwork — one composition, rendered per location.**

A **filled ring on a dark ground.** The circle is the year: 1 January at the top, running clockwise through the twelve months. The **radial axis is the 24-hour clock** (midnight at the centre, midnight again at the rim). For each of the 365 days, the band of daylight — from that day's sunrise to that day's sunset — is filled in warm light against the dark. The result is a **closed band of gold that swells and narrows around the year**: fat at midsummer, pinched at midwinter.

Verified against a rendered test (`temp_dir/sunyear_ring_test.png`): **it reads as an object/emblem, not a chart.** That was the open wall-worthiness risk and it clears. What you see is a sun, a halo, a wedding-band of light — the underlying data is invisible unless you go looking for it.

**Layered depth (the single biggest art upgrade for near-zero code):** don't render one hard-edged gold band. Render **nested twilight bands** — night → astronomical → nautical → civil twilight → full day — as a graded palette. `astral` returns dawn/dusk alongside sunrise/sunset for free. This turns a flat shape into something with atmosphere and is the difference between "chart" and "print."

**What's printed on it (the emotional payload):**
- **Place name** in large type — `MALMÖ` — and the **coordinates to four decimals**, `55.6050° N / 13.0038° E`. The precision is a keepsake signal, not an accuracy claim.
- **The marked day**: a fine radial hairline through the ring at that date, with a small annotation off the rim — `14 MARCH 2025 · SUNRISE 06:22 · SUNSET 18:04`.
- **One line of the buyer's own text** at the foot (`the year we lived on Föreningsgatan` / a child's name). Optional, free-text, one line only.
- Month ticks, kept whisper-quiet — enough to orient, never enough to read as an axis.

**The variants worth having:**
- **Calendar year** (Jan–Dec) — the default, the identity product.
- **365 days from a chosen date** — *"Wilma's first year of light"*, *"our first year here."* **Identical compute, strictly better as a gift**, and it lands directly in the proven first-birthday / new-baby / housewarming occasions FAM-001's Phase 3 already identified as the real demand. Ship both from day one; they are the same code path.
- **Above the Arctic Circle** the ring becomes spectacular and needs its own handling: Kiruna gets **22 days of polar night** (the band closes to nothing — a black notch in the gold) and **100 days of midnight sun** (the band fills the entire radius — a solid disc). Longyearbyen: 112 and 159. These are the hero images for the listing even if few people order them.

**The "two places" variant — my judgement: OUT for v1, and probably out entirely in its obvious form.** Two rings side by side is a *comparison*, and a comparison is an infographic. It splits the emotional focus, doubles the composition problem, and pushes straight into the failure mode the user already rejected. There is one version worth testing later — a **single ring with the second place's daylight drawn as a thin contrast outline over the first**, so the expat sees how much light they gained or lost as one shape rather than two. Even that is a v2 experiment, not a launch SKU.

**What it feels like:** a warm, quiet, slightly astronomical object — planetarium-adjacent but restrained. Closer to a well-made star map or a mid-century sun print than to a data visualization. If a viewer's first reaction is "what does this measure?", the design has failed; the correct first reaction is "what is that?", and the second, on reading the small type, is "oh — *that's their year.*"

---

## 4. Moat / why not ChatGPT

**Passes the ChatGPT Test on the same grounds as FAM-001 — a printed emotional keepsake is not something an LLM ships — but it passes more weakly, and that must be said plainly.**

- **What protects it:** the buyer is purchasing a physical, art-directed, print-ready object with an emotional anchor. No general LLM delivers a framed poster to a wall, and no gift-buyer is going to prompt their way to one. Foundation-model progress does not erode a gift.
- **What does *not* protect it, and this is the honest weakness:** unlike FAM-001, there is **no data layer at all**. FAM-001 at least required OSM extraction, tag knowledge, ODbL handling, and coverage QA — mild but real friction. Here the entire computational core is **~30 lines of `astral` + a polar plot**. ChatGPT with code execution can produce a *credible* version of this artwork in one prompt today. It cannot produce a *good* one — palette, typography, twilight grading, print-ready vector output and the emotional copy are all taste, not intelligence — but the gap between "ChatGPT's output" and "the product" is thinner here than anywhere else in the portfolio.
- **None of the 6 durable moats apply.** No data flywheel, no workflow execution, no context/regulatory/orchestration/outcome moat. The defensible assets are exactly three: **(1) art direction and an ownable palette/typographic system, (2) the Nordic-identity positioning and copy voice, (3) the occasion/gift framing.** All three are brand assets. They protect a side hustle. They do not protect anything larger, and a competent competitor can copy the format in an evening.
- **The symmetric truth to internalise:** *this is the cheapest build in the portfolio, which means it is also the lowest barrier to entry in the portfolio.* Cheap-to-build and easy-to-copy are the same fact seen from two sides. Win on taste and positioning or don't play.

---

## 5. MVP scope (80/20)

**The vertical slice — one weekend of code, one to two weekends of art.**

1. **Generator, single composition.** `astral` → twilight-banded polar ring → **SVG → print-ready PDF**. Handle the polar-day/polar-night edge cases and the DST decision (§7). One layout, three curated palettes. No configurability beyond location, date, and one text line.
2. **Render the hero set for the listing:** Malmö (the founder's own — the authentic one), Stockholm, Edinburgh, Reykjavík, and **Kiruna or Tromsø as the show-stopper**. Order one Gelato print of the Malmö version for real product photography — a screenshot will not sell this.
3. **List two SKUs in the existing Etsy store:** **€19 digital download** (personalized: coordinates + place name + one marked date + one text line) and **€39 Gelato poster**. Fulfilment **semi-manual** via the order note, exactly as FAM-001 — the buyer types their address and date, the founder runs the generator. Do not build a web front-end.
4. **Reuse FAM-001's digital-download spec verbatim** — vector-first, ≥300 DPI print-ready PDF, bundled in standard sizes (A3/A2 + 16×20"/18×24"), explicit "digital, nothing ships" and colour-variance copy. That spec is already the category bar; don't re-derive it.
5. **Ship the latitude gate** (§7) as a preflight check *and* as listing copy.

**Explicitly out of scope for v1:** self-serve web app, accounts, the two-places variant, free colour customisation, animated/interactive versions, framed tiers, physical extras, anything Shopify.

**Realistic time-to-first-listing:** 2–3 weekends, of which **roughly 80% is design and product photography, not code.** The engineering is close to trivial and is not where the risk lives.

---

## 6. How it makes money

Same shape as FAM-001, in the same store, on the same rails:

| SKU | Price | Role |
|---|---|---|
| **Digital download** | **€15–25** | The scale product. ~77–95% contribution, zero ops, instant delivery. Where the money is clean. |
| **Gelato poster 50×70** | **€35–45** | Mid-tier. ~35–40% after print + local EU ship. Zero inventory. |
| **Framed** | €75–85 | Premium; add only if the poster tier moves. |
| **Two-location / couple bundle** | +€10–15 | v2 experiment only. |

- **Who pays:** the occasion gift-buyer (highest intent, highest AOV — birth, anniversary, housewarming) and the Nordic self-purchaser. Lead the listings with the **occasion**, not with the astronomy — the FAM-001 Phase 3 lesson applies unchanged: *do not bet on people searching for the novel category name.*
- **Channel:** the **existing Etsy store**. Zero incremental channel cost — that is the entire commercial argument for building this. **No paid ads**: a €14 poster contribution dies under CAC; only the digital tier survives promotion.
- **Seasonality is a real asset here:** this is a **Q4 / dark-season product**. Nordic Christmas and Lucia gifting land exactly when the emotional premise is most felt. Time the listing for autumn, not spring.

*(Unit economics, real Gelato COGS, and category saturation are Phase 3.)*

---

## 7. Tech approach

**Confirmed by build feasibility check** — script at `/Users/fuat.deligoz/code/Copilot workspace/temp_dir/sunyear_feasibility.py`, render at `temp_dir/sunyear_ring_test.png`.

- **Compute cost is nil.** `astral` 3.2 computes all 365 days for one location in **0.02–0.06 s**. No API, no external data source, no licence, no ODbL attribution, no coverage QA, no per-order cost. This is by a wide margin the cheapest and lowest-risk build in the portfolio.
- **Rendering:** matplotlib proved the *concept*, but ship **hand-written SVG** (`drawsvg`/templated SVG) → PDF via `cairosvg`. Matplotlib's typographic control is too poor for a print product, and FAM-001's spec demands vector-first with crisp text at any size.
- **Twilight bands:** `astral` returns `dawn`/`dusk` (civil) plus `sun()` phases — layer them for depth. Highest visual return per line of code in the whole build.

### The latitude constraint — the decisive product fact

The original premise that this "works for every address on Earth" is **wrong**. There is no *data*-coverage risk, but there is a **latitude-coverage risk**, and it is hard:

| Place | Lat | Shortest day | Longest day | **Range** | Polar nights | Midnight-sun days |
|---|---|---|---|---|---|---|
| Longyearbyen | 78.2 | 0.00 | 24.00 | **24.00** | 112 | 159 |
| Kiruna, SE | 67.9 | 0.00 | 24.00 | **24.00** | 22 | 100 |
| Malmö, SE | 55.6 | 7.02 | 17.51 | **10.49** | 0 | 0 |
| Berlin | 52.5 | 7.64 | 16.82 | 9.19 | 0 | 0 |
| London | 51.5 | 7.82 | 16.63 | 8.81 | 0 | 0 |
| New York | 40.7 | 9.25 | 15.09 | 5.84 | 0 | 0 |
| Sydney | −33.9 | 9.89 | 14.41 | 4.52 | 0 | 0 |
| **Singapore** | **1.4** | 12.04 | 12.19 | **0.15** | 0 | 0 |

**Singapore's ring is a plain, featureless donut.** Nine minutes of annual variation produces nothing anyone would hang. The product is excellent above ~50°, good at 45–50°, mediocre at 30–45°, and **worthless within ~20° of the equator**.

**Turn the constraint into the strategy, not into an apology.** This is a **Nordic / northern-European / Scottish / Baltic / Canadian / Alaskan / northern-US product**, sold to people whose lives are organised around the light. That is a sharper and more ownable position than "global" — and it is exactly where the founder lives, which makes the brand voice authentic rather than researched. The sellable belt (Sweden, Norway, Finland, Denmark, Iceland, UK, Ireland, Netherlands, northern Germany, Poland, Baltics, Canada, Alaska, Seattle/Minneapolis/Maine) is wealthy, English-heavy and gift-dense. It is not a small market.

**Enforce it in the product:**
- **|lat| ≥ 48°** → ship freely.
- **40–48°** → generate, but show the buyer the actual preview before purchase or before fulfilment.
- **< 35°** → **refuse the order** with a short, brand-building explanation: *"Below this latitude the sun barely changes its mind all year — your ring would be a perfect circle. We'd rather not sell you that."* This prevents refunds and one-star reviews, and it doubles as proof that the shape is real data rather than decoration. Scarcity, honestly earned.
- State the latitude limit in the listing copy. It is a feature.

### Other build details that matter

- **Polar day/night edge cases are the one genuine code risk.** `astral` raises `ValueError` when the sun never rises or never sets; the ring must be explicitly closed (polar night) or filled to the rim (midnight sun) rather than crashing or leaving a gap. ~20 lines, already stubbed in the feasibility script.
- **DST is a design decision, not a bug.** Local wall-clock times produce a visible **one-hour step** at the two DST boundaries — an artefact that fights the "smooth object" reading. Recommendation: **render the artwork in standard (non-DST) local time for a clean ring, but print the marked day's time in real local wall-clock**, because that is the time the person actually experienced. Say nothing about it in the copy.
- **Accuracy honesty:** `astral` assumes standard refraction at sea level; mountain and coastal locations differ by minutes. Never claim minute-level accuracy in listing copy. Longitude shifts sunrise ~4 min per degree, so house-level precision is astronomically meaningless — print the coordinates anyway, for the buyer, not for the maths.
- **GDPR:** the only personal data is a coordinate and a date, both of which *are* the product. Minimal, EU-processed via Gelato, not retained. Lower risk than FAM-001.

---

## 8. Open questions (resolve before/while building)

1. **Which hook converts — the marked date or the northern identity?** These are two different products sharing one render. List both ("first year of light" gift vs. "your city's year of light") and let the data decide. This is the single most important thing to learn.
2. **Is the ring the right form?** A spiral (365 days as one unbroken outward coil) is more distinctive but harder to read as an object; the closed ring tested well. Test one spiral variant before committing the brand to a shape.
3. **Where exactly does the latitude line fall, and refuse or warn?** 35° is a first guess; the honest answer depends on what a 6-hour-range ring actually looks like printed.
4. **Does it hold presence at 30×40 cm**, or does the composition need 50×70 to work? Affects the cheapest poster tier's viability.
5. **Palette risk:** does gold-on-dark read as premium, or as planetarium gift shop? Test at least one light-ground, ink-on-paper alternative — it may be the more expensive-looking option.
6. **Calendar year vs. from-a-date as the *default*.** The from-a-date version is the better gift; making it the default may lift AOV.
7. **Is this format already commoditised?** The star-map category is heavily saturated and discount-driven; whether the sun-ring format is already crowded on Etsy is **unverified and is the key Phase 3 question.** Everything said above about the star-map comparable is an assumption to test, not a finding.
8. **Strategic:** the store has zero sales. Is a second SKU the right move, or is the bottleneck traffic and positioning rather than product count? (See verdict.)

---

## 9. Updated feasibility scores

| Axis | Score | Note |
|---|---|---|
| **Ease of execution** | **5** | The cheapest build in the portfolio, verified: 0.02–0.06 s for 365 days, no data source, no API, no licence, no coverage QA. Reuses the existing Etsy store, Gelato pipeline and PDF spec. Real work is art direction, not engineering. |
| **Potential** | **3** *(provisional)* | Rides a proven buying motive (personalized dated astronomical keepsake) and a Q4-seasonal, gift-dense northern market — but the latitude gate removes most of the world's population, and this is side-hustle scope by construction. Validate in Phase 3. |
| **Competition** | **2** *(provisional)* | **Near-zero barrier to entry** — 30 lines of code and no data moat. The adjacent star-map category is saturated and price-eroded, and product-level white space is **unverified**. Scored below FAM-001 deliberately. Validate in Phase 3. |
| **LLM-defensibility** | **3** | Safe as a physical/emotional keepsake — no LLM ships a framed print. **But scored below FAM-001's 4 on purpose:** with no data layer, ChatGPT-with-code can already produce a credible version of the core artwork. Defensibility rests *entirely* on taste, print quality and brand. |
| **Founder fit** | **4** | He lives at 55.6°N inside the exact target market — the brand voice is lived, not researched. Lowest-effort build available to a severely time-poor founder, on rails he has already laid. Drags: it's design/marketing rather than his AI/finance edge, and unlike FAM-001 he has no personal reason to build it anyway. |

**Total: 17/25 · Verdict 🟡 Watch**

**Why 🟡 and not 🟢:** the wall-worthiness gate is cleared and the build is nearly free, but this is **SKU #2 in a store that has sold zero of SKU #1.** Adding products when the bottleneck may be traffic and positioning is a classic time-poor-founder trap, and it should be named as one.

**Why it is still worth doing:** with FAM-001 at zero sales, the founder cannot yet tell whether the problem is *the product* or *the channel*. A second SKU that costs 2–3 weekends, reuses every existing rail, and targets a **different audience and a different occasion** is a legitimate and cheap A/B on exactly that question. That — not "a new business" — is the reason to build it.

---

## Recommended next move

Build the Malmö poster for the founder's own wall first; it is the hero image, the product photograph and the honest brand story in one. Then list **two digital SKUs (€19) in the existing store** — one occasion-framed (*"their first year of light"*), one identity-framed (*"your city's year of light"*) — with the latitude limit stated proudly in the copy and enforced in fulfilment. **Riskiest assumption: not buildability (proven), not wall-worthiness (proven) — but whether the marked date is enough to make a beautiful shape feel personal to a stranger.** Threshold before any further investment: the *dated* listing must outsell the *decorative* one. If neither moves in 60–90 days across two products, the honest conclusion is that the constraint is the channel, not the catalogue — stop building SKUs and fix distribution.
