# FAM-003 Shelf Room — roadmap

Written 2026-08-21. Status of the product on that date: **draft, not listed.**

**Phase 0 is complete. 2026-08-21.** See section 2 for what each fix did.
The next task is section 3, the design pass.

---

## 1. Where the product stands

The engine is finished. The product is not.

**Done and correct.**

- `make.py` runs end to end. It needs no network.
- `posterlab/chrome/tiling.py` is complete. It has no stubs.
- Every sheet count in `docs/product.md` reproduces exactly. A4 eco is 11 art sheets.
- The pack ships a calibration page, an assembly map page, cut lines, and a 10 mm overlap.
- The bundle carries `HOW-TO-PRINT.txt` and `LICENSE-ATTRIBUTION.txt`.
- `poster.toml` holds the Inter IKEA disclaimer in a `[compat]` block.
- The dashboard finds the product with no registry edit.

**Not done.**

- The artwork is a first draft. See section 3.
- No `brand/` directory exists. There are no samples, no listing photos, and no pins.
- There is no market document, no price, and no keyword evidence.
- There is no Etsy listing copy.
- There is no item for this product in `studio/brand/marketing-backlog.md`.
- No one has printed the pack and built a real room.

The product is 100 percent done on the engine axis. It is close to 0 percent done on
the go-to-market axis.

---

## 2. Phase 0 — fix the known defects — **DONE 2026-08-21**

1. **Done.** `pypdf` is now in the `dependencies` list in `pyproject.toml`.
   `make.py` imports it, so a fresh `uv pip install -e .` used to give a `make.py`
   that cannot run.
2. **Done.** `howto()` in `make.py` now takes one plan per paper size.
   With `--size both` the shared `HOW-TO-PRINT.txt` named only Letter. It now names
   both papers, tells the buyer to pick the PDF that matches the paper, and reports
   the sheet count and the paper use for each size.
3. **Done.** `dashboard.json` now says the ceiling costs 2 more sheets on A4 and 3 on
   Letter. Measured: A4 goes 11 to 13, Letter goes 11 to 14.
4. **Not a defect. No change to the code.** `make.py` uses `action="store_true"`, so the
   command line default is false. `dashboard.json` sets it true. FAM-001 and FAM-002 do
   exactly the same, because the dashboard needs the PNG for its thumbnail and a command
   line run does not. The help string in `dashboard.json` now matches the other two
   products and says why: "Needed to show thumbnails on this dashboard."
5. **Done.** The `tiling.py` docstring says `FAM-003`, not `KID-001`.
6. **Done, by code, not by narrowing the claim.** `room.py` read only `seams["x"][0]` and
   `seams["y"][-1]`, and `roof()` read no seams at all.
   - `_band_width` is replaced by `_band_edges`. It gives each gap between consecutive
     seams its own repeat, so every seam is a band edge on any cube size.
   - `wall_base` puts the skirting on the lowest seam in the bottom of the wall, a picture
     rail on every seam above it, and a moulding line on any seam inside the skirting.
   - `floor` draws a plank joint on every vertical seam and an unstaggered end-joint row
     on every horizontal seam.
   - `roof` draws a moulding line on every seam, so the flat ceiling never shows a bare
     step.
   Measured on a 600 x 500 x 500 cube: 8 blank seams before, 0 after.
   `docs/product.md` now states the wider claim and says it holds for any cube size.
7. **Done.** The repository now has tests. `pytest` is in the `dev` extra of
   `pyproject.toml`. Install with `uv pip install -e ".[dev]"`. Run with `python -m pytest -q`.
   51 tests pass and `ruff` is clean on every changed file.
   - `tests/test_tiling.py` — 38 tests. A split sums to `length + (k-1) * overlap`. A piece
     never runs off the sheet and never overlaps another piece on the same sheet. Pieces
     tile each face and lap by exactly the overlap. Packing never loses to one piece per
     sheet. Every seam falls on a piece boundary. Kallax A4 eco is 11 sheets.
   - `tests/test_room_seams.py` — 13 tests. Every seam that `seam_lines` reports carries a
     drawn line, on 5 cube and paper cases from 120 mm to 900 mm. No artwork is drawn
     outside its own face. This is the test that fails if item 6 regresses.

### 2.1 Found while fixing, not in the original list

- `posterlab/chrome/tiling.py` imported `dataclasses.field` and never used it. Removed.
- `make.py` raised `SystemExit` inside an `except ValueError` with no `from`. Fixed, because
  the diff-scoped `ruff` gate flags it as soon as the file is touched.

---

## 3. Phase 1 — the design pass (the real blocker)

**Yes, you need to work on design. It is the largest remaining task and it gates every
listing asset.** You cannot photograph artwork that is about to change.

The render at `output/room/20260821-105811__whimsy_cube__330mm__local/` shows the problems.

### 3.1 The room does not use the house style

`room.py` imports only `num` from `posterlab.svg.primitives`. It never imports
`posterlab/svg/hand_drawn.py`. The Woodruff wobble is what gives FAM-001 its look.
Without it the room reads as clip art, and the shop reads as a dropshipper.
`CLAUDE.md` names one shared art style as the moat.

Decide first: does a cut-and-glue panel want a wobbly line, or a crisp one?
A wobbly cut line is hard to follow with scissors. A wobbly *drawing* is not.
The likely answer is a crisp cut line and a hand-drawn interior.

### 3.2 The colours are accidental, not chosen

`room.py` calls `posterlab.themes.room_tokens(theme)`. **No theme JSON in `studio/themes/`
contains a `room` block.** All 16 themes fall through to the derived mapping at
`themes.py:67-80`. A wall colour is a map annotation box. A floor colour is a residential
road. A sky is water. A rug is a playground marker.

The green stripes and the red rug in the current render are a side effect of that mapping.
No one chose them.

Action: hand-tune a `room` block for 2 or 3 themes. Do not tune all 16.
A print-at-home product sells better with three named rooms than sixteen derived ones.

### 3.3 Specific artwork faults visible in the render

- The rug is a flat red block. It has no pattern and no texture.
- The curtains are heavy red slabs.
- The plant and the door knob are almost invisible at print size.
- The door is a plain white rectangle on a striped wall.
- The bookcase spines are random. They read as noise.
- The floor plank joints barely show.
- The skirting board is a 58 mm pale band. Its height comes from the seam position at
  `y=272`, not from taste. Set the height by eye and move the seam feature to something else.

### 3.4 Ink economics

The walls cover a whole sheet in flat colour. A home inkjet prints that badly and slowly.
FAM-002 already learned this and ships its light `ink` theme first.
Choose a light default theme for FAM-003. Keep any dark room as a hero image only.

### 3.5 Design pass output

- 2 or 3 `room` blocks written into `studio/themes/*.json`.
- A decision on hand-drawn line work, applied in `room.py`.
- Redrawn rug, curtains, door, and bookcase.
- A skirting height that is set by design, not by the seam.
- One named default theme that is cheap to print.

Estimate: this is the biggest single block of work in the roadmap. Treat it as several
sessions, not one.

---

## 4. Phase 2 — build the real thing (one session plus glue drying)

Do this immediately after the design pass. Do not skip it. Do not do it after the photos.

1. Print the A4 eco pack at 100 percent scale. Turn off fit-to-page.
2. Check the 50 mm calibration square with a ruler.
3. Cut every panel on the dashed lines.
4. Glue the panels into a real cube shelf.
5. Record what fails.

Things this test can prove or kill:

- Does the 360 mm cover depth really hide behind the shelf lip?
- Do the 10 mm overlaps line up, or do the seams show a step?
- Does the paper curl or wrinkle when glued?
- Do the seam features actually hide the joins?
- How long does the build take? That number goes in the listing.
- Do the panels survive a child pushing a figure against them?

This build is also the source of the listing hero photo. A real photographed cube beats
any mockup for this product.

---

## 5. Phase 3 — go to market (nothing exists yet)

Run this only after phases 1 and 2 pass. Each item mirrors what FAM-001 already has.

| # | Item | Model to copy |
|---|---|---|
| 1 | Market and execution document | `posters/fam001-playground-map/docs/playground_map_market_and_execution.md` |
| 2 | Price, backed by the sheet count and the build time | Section 2b of the FAM-001 listing file |
| 3 | eRank keyword evidence before any title or tag | `.github/skills/erank-keywords/SKILL.md` |
| 4 | `brand/samples/` — one render per shipped theme | `posters/prt006-sun-year/brand/samples/` |
| 5 | `brand/listing-photos/` — 9 numbered cards | `posters/fam001-playground-map/brand/listing-photos/` |
| 6 | `brand/pinterest-pins/` — 2:3 pins | `posters/fam001-playground-map/brand/pinterest-pins/` |
| 7 | `brand/etsy-listing-READY.md` — title, 13 tags, description | `posters/fam001-playground-map/brand/etsy-listing-READY.md` |
| 8 | Backlog item `BL-0NN`, created as `draft` | `studio/brand/marketing-backlog.md` |
| 9 | Flip `status` to `live` in `poster.toml` | — |

### 5.1 What this product does not need

It is a digital download. These FAM-001 items do not apply:

- No Prodigi SKU and no production partner disclosure.
- No shipping profile and no processing time.
- No GPSR manufacturer block, because nothing physical ships.

### 5.2 What this product needs instead

- The Inter IKEA disclaimer in the listing body.
- A title that leads with the dimension, for example "fits 33 x 33 cm cube shelves".
- No trademark in the shop name, the domain, the logo, or the first words of the title.

### 5.3 Keyword risk

The buyer for this product does not search for the words in `docs/product.md`.
Test these search terms in eRank before writing any copy:

- printable dollhouse
- cube shelf insert
- dollhouse wallpaper printable
- shelf diorama
- doll room printable

If every term returns near-zero volume, the product has no search demand on Etsy.
That result changes the plan. It does not mean stop, but it does mean the product sells
through Pinterest and not through Etsy search.

---

## 6. Sequence and dates

FAM-002 has a hard date. Halloween does not move. Its backlog item `BL-012` sets a kill
date of 2026-09-20. FAM-003 has no clock, but it has a natural one: a cube shelf room is
a Christmas gift, and Etsy gift traffic climbs from October.

Recommended order:

1. **Now to 2026-09-10.** Finish FAM-002 and list it. It expires. FAM-003 does not.
2. **Done 2026-08-21.** Phase 0 defect fixes for FAM-003.
3. **2026-09-10 to 2026-09-30.** FAM-003 design pass, then the real build.
4. **2026-10-01 to 2026-10-15.** FAM-003 go-to-market. List before the gift season starts.
5. **Kill date: 2026-11-01.** If the artwork is not finished by then, the Q4 window is gone.
   Hold the product until 2027 rather than list weak artwork.

---

## 7. The honest risk

The shop has 2 live listings, 8 Etsy visits month to date, and **0 orders to date**.
Pinterest has been stuck at 1 outbound click for four runs.

A third listing does not fix a traffic problem. Before you invest several sessions in
FAM-003 artwork, decide which statement you believe:

- **The products are fine and the traffic is the problem.** Then the highest value work is
  marketing on the two live listings, and FAM-003 waits.
- **The niches are wrong and FAM-003 is a better niche.** Then build it, and accept that
  the first two listings taught you what does not sell.

The second statement is defensible. A printable cube-shelf room has a clearer buyer than a
playground map. The buyer already owns the shelf and already buys figures.
But make the choice on purpose. Do not add a third listing by default.
