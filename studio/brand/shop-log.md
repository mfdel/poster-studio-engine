# Shop Log — Hopscotch Maps

Append-only record of every shop-marketing session. Newest entry first. One entry per run.

The procedure is [`.claude/skills/shop-run/SKILL.md`](../../.claude/skills/shop-run/SKILL.md).
The queue is [`marketing-backlog.md`](marketing-backlog.md). The numbers are
[`metrics.csv`](metrics.csv). Pinterest strategy changes still go in
[`pinterest-log.md`](pinterest-log.md).

`AUTO` marks a run started by the launchd schedule. `MANUAL` marks a run the founder started.

Keep each entry under 25 lines. Every future run reads this file first.

---

## 2026-08-24 — outbound clicks drop to 0, drafts flagged · AUTO

**Status:** OK
**Sessions:** etsy OK · pinterest OK · erank OK (not used, no keyword decision due)

**Numbers:** Etsy 17 visits month to date (01-24 Aug), 0 orders, 0 favourites, Etsy search 0 ·
Pinterest 7d 118 impressions, **0 outbound clicks**, 0 saves · 30d 198 impressions, 1 outbound click.

**Did:**
- Closed one cycle of `BL-003`. 10 outside pins saved: 5 to *New Baby Gifts*, 5 to *First Birthday
  Gift Ideas*. Both verified through the action-bar text, not the toast. 3 boards remain uncovered:
  *Family Keepsakes & Memory Ideas*, *Nordic & Scandinavian Wall Art*, *Personalized Housewarming
  Gifts*.
- Opened all 6 drafts under `BL-016`. Every draft is an untitled FAM-001 room-scene photo (gift-wrapped
  map, dad and child, mum and toddler, empty playroom, hands at a window, child with a star sticker).
  None carries a title, a board or a link. Expiry now reads 7 days, matching the 11-day reading of
  2026-08-20. No draft was published or deleted — that decision needs the founder. Details in
  `BL-016`.
- Read `BL-017`. FAM-002 Halloween listing `4560524378`: 1 view month to date, 0 favourites, 0 orders.

**Decided:**
- **Pinterest outbound clicks read 0 in 7 days for the first time in five runs.** The prior four runs
  held exactly 1. The 30-day window still shows 1, so the click sits just outside the 7-day cut, not
  gone — but 7-day impressions also fell 164 to 118. Watch the next run before calling this a trend.
- No eRank run spent. `BL-010`'s Halloween re-measure is due first week of September, not yet.

**Next run:**
- `BL-003` on the 3 remaining boards. `BL-016` needs a founder call before the drafts expire
  (~2026-08-31). `BL-017` again next run.

---

## 2026-08-20 — Christmas and Halloween words measured · AUTO

**Status:** OK
**Sessions:** etsy OK · pinterest OK · erank OK

**Numbers:** Etsy 8 visits month to date (01-20 Aug), 0 orders, 0 favourites, **Etsy search 0** ·
Pinterest 7d 164 impressions, **1 outbound click**, 0 saves · 30d 157 impressions, 1 outbound click.

**Did:**
- Closed one cycle of `BL-003`. 8 outside pins saved: 2 to *Nursery Wall Art & Decor*, 3 to *Baby
  Shower Gift Ideas*, and 1 each to *Screen-Free Activities for Toddlers*, *Sunrise Sunset Wall Art*
  and *Playground Adventures*. The two boards that the run of 2026-08-19 missed are now covered.
- Closed the measurement half of `BL-014`. eRank run 1 of 2, 20 Christmas phrases. Best is
  `christmas wall art` at 4,370. `christmas gift` is 2,210 with 7,614,738 competing listings and
  difficulty 100. 12 of 20 phrases measure 0.
- Spent eRank run 2 of 2 on the **Halloween** phrases for `BL-012`, which had no evidence at all.
  `halloween decor` 9,760, `halloween wall art` 2,720, `first halloween` 1,210. `trick or treat map`
  measures **0**. Both tables are in `studio/research/etsy_keyword_evidence_20260816.md`, runs 4 and 5.

**Decided:**
- **Keep the evergreen kickers on the Christmas pins.** `personalized gift` is 18,820, which no
  Christmas phrase beats. Re-measure in the first week of October, because July is the season trough.
- **FAM-002 must not take its title from the product name.** `trick or treat map` and
  `neighborhood map print` both measure 0, exactly like `personalized playground map` did.
  Re-measure the Halloween batch in the first week of September, before the title is written.
- Pinterest holds **1 outbound click for the fourth run**, and the rate of `fam-nursery` fell from
  20.0% to 12.5% as impressions grew 96 to 164. Impressions are not the limit. The click is.
- The Pin builder holds **6 drafts that expire in about 11 days**. New item `BL-016`.

**Next run:**
- `BL-003` again, on *New Baby Gifts* and *First Birthday Gift Ideas*. Then `BL-016`.

---

## 2026-08-19 — title B live, sun pin live, 08-18 cause retracted · MANUAL

**Status:** OK
**Sessions:** etsy OK · pinterest OK · erank not used

**Numbers:** Etsy 8 visits month to date (01-19 Aug), 0 orders, 0 favourites · Pinterest 7d 96
impressions, **1 outbound click**, 0 saves · 30d 99 impressions, 1 outbound click.

**Did:**
- **Closed `BL-002`.** The founder reaffirmed option B, so B is live on listing `4547086425` and
  verified on the public page: `Nursery Wall Art, Personalized Map Print, Custom Map Print, New Baby
  Gift, Kids Room Decor`. 15 words, 90 characters. Both dead slots are gone and measured volume goes
  7,140 to 8,610. Compliance re-checked: Prodigi present, and the only "instant download" string is
  the honest negation "it is **not** an instant download".
- **Closed `BL-010`.** The founder approved `s06-kiruna-light.jpg`, published to *Sunrise Sunset Wall
  Art* as `sun3-minimalist-kiruna`. Verified on the board page, 6 Pins became 7. Kicker `Minimalist
  wall art`, 2,210 searches. The draft was lost once to an `about:blank` reset and rebuilt fresh.
- **Retracted the cause written on 2026-08-18.** The server started normally here with **no change to
  `~/.claude.json`**. That PATH reasoning rested on the agent's own Bash tool PATH, which is sandboxed
  and is **not** what Claude Code uses to start an MCP server. `BL-013` is now a watch item, not a fix.
- Closed one cycle of `BL-003`. 8 outside pins saved across 8 boards. Two seller product pins
  rejected. 5 pins stay scheduled for 19, 20 and 22 August, so `pins_live` is 25.

**Decided:**
- **`Etsy search` is now the one number that matters.** It sent 0 of 8 visits. Both live titles carry
  only measured phrases from today, so that figure tests the whole keyword rewrite. Read it every run.
- **Third run at exactly 1 outbound click**, impressions 94 to 96. The `s06` test runs to 2026-09-02.
- The 14-word rule is internal, from an Etsy warning, not a hard Etsy limit. The founder accepted the
  one-word overage. Option C was offered and declined.

**Next run:**
- `BL-003` again. Then `BL-014` in eRank before the Christmas pins publish on 2026-10-01.

---

## 2026-08-18 — no browser existed, pins built offline · MANUAL

**Status:** PARTIAL
**Sessions:** etsy NOT REACHED · pinterest NOT REACHED · erank NOT REACHED

**Numbers:** none. No platform was reached, so nothing could be read or changed on any platform.
The numbers of 2026-08-17 stand.

**Did:**
- No browser existed, and it was **not** a profile lock: no `mcp__playwright__*` tool was present.
  The `playwright-mcp` command with an empty `env` is unreachable on a trimmed PATH, so the server
  never started. `shop_run.sh` is safe; VSCode sessions are not. The fix is `BL-013`.
- Closed the measurement half of `BL-010` offline. Four differences between `fam-nursery` and the
  four `sun2-*` pins are in the backlog. Built candidate `s06-kiruna-light.jpg`, unpublished.
- Built the `BL-007` Christmas set, 3 pins on measured kickers, unpublished until 2026-10-01, with a
  new `studio/assets/make_pin_experiments.py`, left uncommitted because it is code.

**Decided:**
- **`BL-002` carried a wrong word count again.** Option B, the founder's pick, is **15 words**.
  Option **C** cuts `New Baby Gift` to `Baby Gift`, 1,710 against 1,310: 14 words, and more volume.
- **The sun pins fail on the image.** At feed width all four are one picture, a gold ring on
  near-black. `s06` fixes brightness and the black bars, but its wall is drawn, not photographed.

**Next run:**
- `BL-013` first; it needs the founder and a restart. Then measure, `BL-002` option C, then `BL-003`.

---

## 2026-08-17 — sun title live, map title held · AUTO

**Status:** PARTIAL
**Sessions:** etsy OK · pinterest OK · erank not used

**Numbers:** Etsy 7 visits month to date (01-17 Aug), 0 orders, 0 favourites, 0 follows · Pinterest
94 impressions, **1 outbound click**, 0 saves in 7 days. 30 days: 80 impressions, 1 outbound click.

**Did:**
- The founder promoted `BL-002`, `BL-007` and `BL-008` to `approved` while this run was measuring.
  The run read the new status and executed the two that are due.
- Closed `BL-008`. Set PRT-006 `Craft` to Framing and Printing & printmaking, which was empty.
  Verified after a reload, because the editor paints values it does not save. FAM-001 needed no
  change: `Room` holds all 5 values, `Materials` holds Paper and Wood, `Craft` holds both values.
- Applied half of `BL-002`. PRT-006 now reads `Sunset Wall Art, Scandinavian Wall Art, Minimalist
  Wall Art, Housewarming Gift, Personalized Sun Poster`. Verified on the public listing page.
- Closed one cycle of `BL-003`. Saved 7 outside pins, one to each of 7 boards: Baby Shower Gift
  Ideas, New Baby Gifts, First Birthday Gift Ideas, Family Keepsakes & Memory Ideas, Playground
  Adventures, Nursery Wall Art & Decor, Screen-Free Activities for Toddlers. No competitor pin.
- Verified the scheduled queue. 7 pins are queued for 18, 19, 20 and 22 August, so no pin of ours
  was published this run.

**Decided:**
- **The FAM-001 title was not applied, and this needs a decision.** The approved string is **16
  words**. The backlog states that each proposed title stays at or under 14 words, and the Etsy
  skill sets 14 words as the limit. The approval was given on a wrong word count, so the run did
  not publish it. PRT-006 measured 14 words and was applied.
- **Pinterest reach nearly doubled, and clicks did not follow.** 7-day impressions went 55 to 94.
  Outbound clicks stayed at 1, held by the `fam-nursery` pin at a 20.0% click rate. Every other pin
  is at 0. Second run with this result, so the pin image is the limit, not reach.
- Etsy did not move in 24 hours. All 7 visits are on FAM-001. PRT-006 has 0 views since 15 August.
- The 30-day window ends one day before the 7-day window, so 30-day impressions (80) read lower
  than 7-day impressions (94). Compare like with like across runs.

**Next run:**
- `BL-002` needs a 14-word FAM-001 title. Two options are in the backlog.
- `BL-007` is now `approved`. Build the Christmas pin set before 2026-09-20.
- `BL-003` again. Then `BL-010`, a new pin image for the sun poster.

---

## 2026-08-16 — board copy live, title words measured · AUTO

**Status:** OK
**Sessions:** etsy OK · pinterest OK · erank OK

**Numbers:** Etsy 7 visits month to date (01-16 Aug), 0 orders, 0 favourites · Pinterest 55
impressions, **1 outbound click**, 0 saves in 7 days. 30 days: 57 impressions, 1 outbound click.

**Did:**
- The profile lock is gone. No Chrome held an `mcp-chrome-*` profile. The wrapper works.
- Closed `BL-004`. Pasted all three board descriptions and verified each on its public board page.
- Closed one cycle of `BL-003`. Saved 6 outside pins, one to each of 6 boards: Nordic &
  Scandinavian, Sunrise Sunset, Personalized Housewarming, Nursery, Screen-Free, Playground
  Adventures. No competitor product pin was saved. No pin of ours was published this run.
- Spent 1 of 5 eRank runs on `BL-002`. Measured 20 phrases. Result is in
  `studio/research/etsy_keyword_evidence_20260816.md`, section *Run 3*.

**Decided:**
- **Both products are named with phrases that nobody searches.** `personalized playground map`
  measures **0**, and `personalized daylight poster` measures **0**. Both sit in a live title.
- `kids decor` (60) and `custom coordinates print` (10) are the other two weak slots.
- Best measured replacements: `minimalist wall art` 2,210, `kids room decor` 1,520,
  `custom wall art` 1,200, `playroom decor` 1,200.
- **No title was changed.** `BL-002` is `needs-review`, so this run only reports.
- Pinterest impressions rose from 39 to 55 in 7 days. Outbound clicks stayed at 1. Reach is not
  the limit. The pin-to-click step is.

**Next run:**
- `BL-002` needs the founder to approve or reject the two title rewrites below.
- `BL-003` again, 5 to 10 more saved pins. Then `BL-008` room and materials.

---

## 2026-08-16 — profile lock blocked all platforms · AUTO

**Status:** BLOCKED
**Sessions:** etsy not checked · pinterest BLOCKED · erank not checked

**Numbers:** none. No platform was reached, so `metrics.csv` carries an empty row. The numbers from
the earlier MANUAL run of the same day stand.

**Did:**
- Wrote the three board descriptions for `BL-004` from the measured evidence table. The copy is
  paste-ready in the backlog. It was not published, because Pinterest was unreachable.
- Recorded the block as `BL-009`.

**Decided:**
- **The profile lock was real, not stale.** The first navigate failed. The retry that the skill
  requires failed with the same message. Google Chrome PID 68511 held
  `.../ms-playwright/mcp-chrome-d83f129` from 18:05, and `SingletonLock` pointed at that PID.
- **The run stopped instead of working around it.** The process was not killed, and no second
  profile was used. A second profile has none of the logins, and one lost Pinterest session costs
  more than one missed run.
- The three board descriptions each lead with a different measured phrase: `sunset wall art`
  (1,150), `scandinavian wall art` (1,200), `housewarming gift` (3,670). No two boards compete for
  the same search.
- `BL-003`, `BL-002` and `BL-008` did not start. All three need a browser.

**Next run:**
- `BL-009` is closed. The wrapper now frees the `mcp-chrome-*` profile before each run, so this
  block should not repeat. If it does, say in the log that the wrapper did not run.
- Paste the three descriptions and close `BL-004`. Then `BL-003` saved pins, then `BL-002` title
  evidence.

---

## 2026-08-16 — first measured run, sun kickers rebuilt · MANUAL

**Status:** OK
**Sessions:** etsy OK · pinterest OK · erank OK

**Numbers:** Etsy 7 visits month to date, 0 orders, 0 favourites · Pinterest 39 impressions,
**1 outbound click**, 0 saves in 7 days. Etsy traffic: Etsy app 3, direct 2, Pinterest 1,
**Etsy search 0**.

**Did:**
- Measured all three platforms. Wrote the first real `metrics.csv` row.
- Spent 0 of the 5 daily eRank runs. The 2026-08-16 evidence table already held every phrase
  `BL-001` needed.
- Closed `BL-001`. Replaced all 5 PRT-006 kickers with measured phrases, re-rendered, and shipped
  5 pins: `sun2-sunset-hero` and `sun2-scandi-tromso` published now,
  `sun2-personalized-reykjavik` 18 Aug, `sun2-housewarming-kiruna` 20 Aug,
  `sun2-newhome-stockholm` 22 Aug. Every link is a Share & Save URL. No pin was deleted.

**Decided:**
- **`BL-001` is half done already.** The 11 FAM-001 kickers in `make_pin_images.py` were rebuilt
  on measured phrases. Only the 5 PRT-006 sun kickers still carry unmeasured words: `sunrise
  sunset wall art` (under 20 searches, 18,652 competitors), `nordic wall art` (10),
  `scandinavian print` (10), `custom coordinates print` (10), `midnight sun poster` (unmeasured).
- **Pinterest and Etsy reconcile.** The single Pinterest outbound click equals the single Etsy
  Pinterest visit. The winning pin is *Nursery Wall Art With Actual Meaning*, at a 33.3% outbound
  click rate on 3 impressions.
- **Etsy search sent 0 visits.** Every visit came from browsing or from us. Titles are not found.
- Etsy Stats has no 7-day preset, so `metrics.csv` now uses month-to-date columns for Etsy.
- The MCP profile lock cleared on a plain retry. The skill now says to retry once.
- The pin builder still reads `Pin builder` and `Publish` after a successful save. Proof is the
  board page, or `/fuatdeligoz/scheduled-pins/`. Both are now in the Pinterest skill.
- The new `sun2-*` slugs run beside the original `sun-*` slugs on the same product. That pair is
  the shop's first controlled test of measured keywords against invented ones.

**Next run:**
- `BL-004` board descriptions, then `BL-003` saved pins.
- `BL-002` is now the highest-value open item, because Etsy search sent 0 visits.

---

## 2026-08-16 — log system created, baseline recorded · MANUAL

**Status:** OK
**Sessions:** etsy not checked · pinterest not checked · erank not checked

**Numbers** (as recorded earlier the same day, not re-measured):
Etsy 7 views in 7 days, 0 orders · Pinterest 3 monthly views lifetime, 4 outbound clicks on the
original hero pin.

**Did:**
- Created the recurring session procedure, the run log, the backlog and the metrics file.
- Added the eRank procedure as its own skill, and the `shop-marketer` agent.
- Seeded the backlog from the open items in `pinterest-log.md` and from
  `studio/research/etsy_keyword_evidence_20260816.md`.

**Decided:**
- The backlog gates unattended work. Only a task at `approved` may be published without the
  founder watching.
- Routine pinning is logged here. `pinterest-log.md` keeps only strategy changes, so it stays
  readable.

**Next run:**
- Measure all three platforms and write the first real `metrics.csv` row.
- Rebuild the pin kickers from the eRank evidence table (backlog `BL-001`).
