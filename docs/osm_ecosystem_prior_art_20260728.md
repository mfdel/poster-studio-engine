---
idea: "FAM-001 Playground Map"
phase: 3
date: 2026-07-28
type: prior-art / OSM ecosystem scan
verdict: 🟡
---

# FAM-001 — OSM Ecosystem & Prior-Art Scan (`leisure=playground` consumers)

> **Source:** [taginfo projects for `leisure=playground`](https://taginfo.openstreetmap.org/tags/leisure=playground) — 41 unique projects (60 references) that consume the tag, investigated via their sites/GitHub on 2026-07-28. Base tag stats: **1,000,761 playgrounds globally** (216,882 nodes · 777,440 ways · 6,439 relations).

## Bottom line

Of 41 projects, **~35 are generic OSM plumbing** (renderers, editors, geocoders, offline-nav apps, data schemas) that merely draw a playground icon — not competitors. **~6 are genuinely playground/family-relevant, and every single one is a free utility or data-editor — none is a printed keepsake or a gift product.** This **confirms and sharpens the Phase 3 white-space thesis**: the "find a playground" job is owned by free open-source tools (don't build a finder — you can't beat free), while the "printed, co-created keepsake / gift" job is wide open. **Compete on the artifact + emotion + gift, never on the finder utility.**

## The ~6 relevant projects

| Project | What it is | Status / signal | Link | Relevance to FAM-001 |
|---|---|---|---|---|
| **Berliner Spielplatzkarte** | Closest prior art. Interactive **Berlin** playground webmap: shows equipment on click, **computes shade by time-of-day/season**, filters/searches by equipment, flags OSM data problems | Hobby project — **9 stars, 1 contributor, last commit ~2 yr ago**, Berlin-only, GPL-3.0, needs GeoServer + PostGIS | [GitHub](https://github.com/SupaplexOSM/spielplatzkarte) · [live](https://osmbln.uber.space/spielplatzkarte/) | No commercial threat, but an **open reference**; its *shade* + *equipment filter* features are worth borrowing |
| **Babykarte** | Family/baby POI **finder** map; shows playgrounds, hides `access=private` / age-restricted | Free, non-commercial, OSM-community | [site](https://babykarte.openstreetmap.de/) · GitHub `babykarte` | Finder, not keepsake — no threat |
| **MapComplete Playgrounds** | Open-source crowd-mapping theme to **view *and edit*** playground attributes (equipment, surface, age…) directly in OSM | Active OSS, documented layer | [theme](https://mapcomplete.org/playgrounds) · docs `Layers/playground` | **A tool you can use** to enrich your own city's playground data before generating/printing |
| **AnyFinder** | General OSM POI finder; playgrounds are one browse category | "private, free, non-commercial" | [anyfinder.app](https://anyfinder.app/) | No threat |
| **PlayScout / PlaygroundBuddy** *(from Phase 3 research)* | Playground **finder** apps (700k / 400k playgrounds, ratings) | Live free apps | [PlayScout](https://apps.apple.com/us/app/playscout-playground-finder/id6471904451) · [PlaygroundBuddy](https://www.playgroundbuddy.com/) | Finder, not keepsake — no threat |
| **Bubatzkarte** | Cannabis-consumption map: playgrounds rendered as **forbidden zones** (German 200 m rule) | Live | [bubatzkarte.app](https://bubatzkarte.app/) | Irrelevant — just an example of a totally different use of the tag |

*(Notable "plumbing" that could theoretically move up-stack: **Grafomap** is already an OSM-based commercial map-poster seller — see Phase 3 market doc — so a competitor with the pipeline already exists; none of the taginfo utilities are a productization threat, but Grafomap is.)*

## Build insight — the "note the equipment" feature is partly pre-solvable from OSM

The OSM wiki confirms each playground can carry, beyond the footprint:
- **Attributes:** `surface` (grass/sand/rubbercrumb/woodchips), `wheelchair`, `min_age`/`max_age`, `stroller`, `fenced`, `access`, `fee`, `opening_hours`, `operator`, `playground:theme`.
- **Equipment** (individual nodes via `playground=*`): swing, slide, sandpit, climbingframe, roundabout, etc. — or a summary via `playground:*=*` prefix tags.
- **Nearby comfort features:** `amenity=toilets` / `bench` / `picnic_table`, `natural=tree` (→ shade).

**Product implication:** auto-print each playground's *known* equipment icons + a shade/toilet/bench indicator, and **leave blank space for the family's own notes/ratings/drawings**. Berliner Spielplatzkarte's *shade-by-time-of-day* calculation is a delightful, differentiating auto-feature worth replicating.

⚠️ **Caveat (reinforces Phase 3 data-quality note):** the wiki states equipment-level tagging is done by "fewer mappers." So the **base footprint is well-covered** (1M+ globally; DE 135k · UK 47k · FR 45k · NL 33k · SE 20k) but **rich attributes are patchy and uneven**. Treat auto-filled equipment as "bonus where available"; the family fills the gaps — which *is* the annotation ritual, so sparse data is a feature, not a blocker.

## Net effect on the FAM-001 verdict (unchanged: 18/25 🟡)

- **Competition (3):** unchanged. The scan found **no keepsake/gift competitor** — but reaffirmed the moat is thin: the data + finder utilities are free and abundant, and Grafomap already has a commercial OSM pipeline. Defensibility stays art/brand/niche/gift-framing only.
- **Ease (4):** slightly *reinforced* — open-source references (Berliner Spielplatzkarte) and a data-editing tool (MapComplete) exist, and rich attributes are already in OSM to auto-populate the equipment feature.
- **Strategic line sharpened:** don't build a finder; build the printed, co-created keepsake, and auto-enrich it with OSM equipment/shade data where available.
