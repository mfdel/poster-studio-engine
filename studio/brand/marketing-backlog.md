# Marketing Backlog — Hopscotch Maps

The queue for the recurring shop session. Every task carries a status, and the status decides what
an unattended run may do with it.

| Status | An unattended run may |
|---|---|
| `approved` | Do the task in full, and publish the result |
| `draft` | Build the artifact, then stop before publishing |
| `needs-review` | Write a recommendation into the log, and change nothing |
| `blocked` | Nothing. Record why it is still blocked |
| `done` | Nothing |

**Only the founder promotes a task to `approved`.** A task that a run invents starts at `draft`.

Edit the status in place. Move a finished task to the *Done* section with its date. The procedure
is [`.claude/skills/shop-run/SKILL.md`](../../.claude/skills/shop-run/SKILL.md).

---

## Open

### BL-010 · Re-measure the Halloween keywords, then fix the tags
**Status:** `needs-review` · **Due:** first week of September 2026 · **Platform:** eRank + Etsy

FAM-002 went live on 2026-08-22, 19 days before the target date and before the September
re-measure. The title is Option A and it is unchanged. Two tags are open questions.

- ~~`halloween sign` measures 1,130 searches, and the sheet is not a sign.~~ **Removed 2026-08-22**
  in the post-publish audit. `halloween party game` took the slot. It measures 0, but it describes
  the object and it agrees with the new category.
- Seven of the thirteen tags are unmeasured long-tail phrases. Replace any that the new numbers
  do not support.
- **The title still leads with `halloween decor`, 9,760 searches.** The category moved out of Wall
  Decor on 2026-08-22, so the title is now the last field that chases decor traffic for a sheet a
  child writes on. Re-open the Option A choice with the September numbers.

Run the eRank Bulk Keyword Tool once with 20 Halloween phrases. Then edit listing `4560524378`.
Record the numbers in `studio/research/`.

### BL-017 · Watch the Halloween listing after the category move
**Status:** `needs-review` · **Due:** next run · **Platform:** Etsy

On 2026-08-22 listing `4560524378` moved from Home & Living → Home Decor → Wall Decor to Paper &
Party Supplies → Party Supplies → Party Favours & Games → Party Games. The listing was one day old
and had 0 orders, so the move was cheap. Section 14 of
[`posters/fam002-halloween-night/brand/etsy-listing-READY.md`](../../posters/fam002-halloween-night/brand/etsy-listing-READY.md)
holds the reasoning.

Read views and favourites for this listing on the next two runs. A category move can cost search
placement for a short time. Record the numbers in `metrics.csv`. Do not move the category again
inside the season.

**2026-08-24 reading:** 1 view month to date, 0 favourites, 0 orders. One more reading needed.

### BL-012 · Build the 5 Halloween Pinterest pins
**Status:** `draft` · **Due:** publish from 2026-09-15 · **Platform:** Pinterest

Use measured kickers only. Wait for BL-010, so the kickers use September numbers. The listing link
must be the Share & Save form:
`https://hopscotchmaps.etsy.com/se-en/listing/4560524378/halloween-decor-printable-personalized`.

### BL-013 · Decide the Etsy Ads share for the Halloween season
**Status:** `needs-review` · **Due:** next run · **Platform:** Etsy

Etsy added listing `4560524378` to the Etsy Ads campaign automatically. The daily budget is
shop-level, so three listings now split one budget. FAM-002 is seasonal and the other two are not.
Decide whether to pause a listing or raise the budget for six weeks.

### BL-003 · Save pins from other accounts onto the young boards
**Status:** `approved` · **Due:** every run · **Platform:** Pinterest

All boards are 100% our own pins. A young account wants roughly 3 to 4 saved pins from elsewhere
per pin of ours, on every board except *Personalized Playground Map*. Save 5 to 10 relevant pins
per run. Never save a direct competitor's product pin.

**Last done 2026-08-24.** 10 pins saved: 5 to *New Baby Gifts*, 5 to *First Birthday Gift Ideas*.
That covers the two boards the run of 2026-08-20 missed. Not covered: *Family Keepsakes & Memory
Ideas*, *Nordic & Scandinavian Wall Art* and *Personalized Housewarming Gifts*. Take those next. The
ratio is still below 3 to 4 saved pins per own pin. Repeat every run.

Search terms that worked on 2026-08-20, because they return blog pins and not product listings:
`nursery room tour ideas`, `baby shower games ideas`, `outdoor play ideas for kids` and
`sunset sky photography`.

**Choose search terms that cannot return a product pin.** Searching `nursery wall art neutral`
returned mostly other sellers' print listings, and one was rejected for that reason. Terms like
`screen free activities for toddlers`, `first birthday party ideas`, `childhood memory keepsake
ideas`, `scandinavian living room interior`, `housewarming party ideas` and `sunset sky photography`
return blog and inspiration pins instead. Also reject a pin whose title sells a personalized item,
for example "the Ultimate Personalized Baby Gift", which was skipped on 2026-08-19.

**Verify with the action bar, not the toast.** The toast text is unreliable: on 2026-08-19 a save to
*Family Keepsakes & Memory Ideas* produced no `Saved to ...` string, yet the save was real. Read
`document.querySelector('[data-test-id="closeupActionBar"]').innerText` instead, which settles to
`<count> | <Board name> | Saved`. Board names that hold `&` must use the plain character in the
selector, not the HTML entity.

Procedure: open the pin page, click `[data-test-id="closeupActionBar"]
[data-test-id="PinBetterSaveDropdown"]`, then the row `[data-test-id="board-row-<Board name>"]`.
Two dropdowns carry the same test id, so take the first match.

### BL-011 · Propose 3 to 4 designs for a two-city sun poster
**Status:** `draft` · **Due:** 2026-08-30 · **Platform:** product

A new product idea puts **two places on one sun poster**. The buyer is a person who lives apart
from someone. Examples are a long-distance couple, a family that emigrated, and a parent of a
student. The gift dates are Valentine's Day on 2027-02-14, graduation in May, and Christmas.

**The maths needs no new work.** `posters/prt006-sun-year/render_1b.py` already computes the four
twilight bands for any latitude and longitude. A second place is a second call to `day_series()`.
Only the composition is unsolved. This task designs that composition. It writes no listing and
publishes nothing.

**One decision comes before every design.** Today each ring uses its own local standard time
(`render_1b.py:194-233`). Two places in different time zones cannot share a ring on that basis.
Pick one shared clock for both places, or state on the poster that each ring keeps its own clock.
Design C below is only meaningful on a shared clock.

#### Design A — twin rings
Draw two complete rings on one sheet. Stack them on the portrait sizes. Give each ring its own
place name and its own coordinate line. Keep one shared quote line at the foot.

*Strength:* it is honest and easy to read. *Weakness:* each ring drops to about 42% of the sheet
width. The thin astronomical band may disappear at that size. Test this at 30x40 cm first.

#### Design B — nested rings
Draw one ring. Give the outer radial half to the first place and the inner radial half to the
second place. Both places keep day-of-year as the angle.

*Strength:* the poster reads as one object, not two charts. *Weakness:* the two places no longer
share a radial scale. A buyer may read the smaller inner ring as the smaller place.

#### Design C — one ring, two colours, and the overlap
Draw both places on the same ring in two colours. Draw the intersection of the two day bands in a
third colour. That overlap is the daylight the two people shared at the same moment.

*Strength:* this is the only design that carries a story the other three cannot. It turns a physics
chart into the reason a person buys the poster. *Weakness:* it needs the shared clock decided
above, and it needs three colours that stay legible in every theme.

#### Design D — mirrored half rings
Split the disc down the middle. Compress each place's year into one half circle. Mirror the two
halves against each other.

*Strength:* the strongest picture of two halves of one life. *Weakness:* the angle no longer maps
to the day of the year in the way PRT-006 buyers already see.

**Deliverable.** Render each design as a preview PNG for one real pair of cities. Use Malmö and
Istanbul, because that pair holds a large latitude gap and a one-hour time gap. Put the previews in
`posters/prt006-sun-year/brand/samples/`. Add no new listing.

**Decision rule.** Judge the previews on one question. Does the sheet still read as the same studio
as `sunyear_stockholm_ring.png`? Reject any design that does not. The recommendation to beat is
Design C, with Design A held as the safe fallback.

### BL-012 · FAM-002 · Halloween night sheet, print at home
**Status:** `draft` · **Due:** ~~build by 2026-09-06~~ **built 2026-08-17**, list by 2026-09-10 · **Platform:** product, Etsy

**The build is done, on 2026-08-17.** All five work items below are complete and measured. Nothing
was listed and nothing was published, because the status is `draft`. On 2026-08-19 this stopped
being a variant of FAM-001 and became its own product, **FAM-002**, at
`posters/fam002-halloween-night/`. Four full-bleed layouts were added at the same time. The build
notes are
[`posters/fam002-halloween-night/docs/product.md`](../../posters/fam002-halloween-night/docs/product.md)
and [`docs/layouts.md`](../../posters/fam002-halloween-night/docs/layouts.md).

Run it with:

```
uv run python posters/fam002-halloween-night/make.py --address "<address>" --radius 400 \
    --theme lantern --size A4 --layout panel --title "<Name> Halloween Night" \
    --night "31 October 2026" --preview
```

`--layout` picks the sheet: `panel` (framed map + bordered log), `band` / `sheet` / `ledger` (map
bleeds to the paper edge), `bonus` (the spotting game, no map), or `all`.

Measured on a random United States address, **West Hillcrest Drive, Boise, Idaho**:

| Test | Radius | Buildings | Result |
|---|---|---|---|
| United States suburb, `lantern` | 400 m | 873 | Houses read at 2.3 mm. Streets and river read |
| Same sheet, `ink` (light) | 400 m | 873 | The version that prints well at home |
| Rural town, Ovacik, Tunceli | 400 m | 267 | Sparse older data. Sheet still looks finished |
| Same Boise data, buildings removed | 400 m | 0 | Sheet still looks finished. Degrades to a street map |
| Wide comparison | 2000 m | 9333 | Grey mush. Rejected. Confirms the 400 m default |

**The 400 m default is confirmed, and the 1000 m cap holds.** The 2000 m render turns the houses
into one grey mass, and a child cannot mark a single house. That fetch also took about 10 minutes,
and two Overpass mirrors returned a 504 before a third answered. Previews of both are tracked in
`posters/fam002-halloween-night/brand/samples/`.

**One decision needs the founder.** `lantern` is dark, as this task asked. A home inkjet prints a
full dark A4 sheet badly: it costs a lot of ink, it wets plain paper, and it bands. The same sheet
in `ink` prints well. Recommendation: ship both files in one download, make `ink` the file the
buyer prints, and keep `lantern` as the listing hero image.

**The listing copy is written, on 2026-08-21.** It is
[`posters/fam002-halloween-night/brand/etsy-listing-READY.md`](../../posters/fam002-halloween-night/brand/etsy-listing-READY.md).
It holds the title, the description, 13 tags, the attributes, the buyer messages and the publish
checklist. **13 listing photos are built** by `studio/assets/make_halloween_listing_images.py`, off
real renders of Chestnut Street, Salem. **One layout sells: `band` plus the spotting sheet.** The
spotting sheet no longer prints "Bonus sheet" at its head. Nothing is published. Two items need the founder: the price of **79 SEK**, and
the listing structure (one physical made-to-order listing, a new `DIGITAL-FREE` delivery profile,
the bonus sheet included free instead of a second instant-download listing).

**Still open before this can go live.** The title waits on the September
re-measure below.

**The Halloween keywords are measured, on 2026-08-20.** The table is *Run 5* in
[`studio/research/etsy_keyword_evidence_20260816.md`](../research/etsy_keyword_evidence_20260816.md).

| Phrase | Monthly searches |
|---|---|
| `halloween decor` | 9,760 |
| `halloween wall art` | 2,720 |
| `first halloween` | 1,210 |
| `halloween sign` | 1,130 |
| `halloween printable` | 10, with 308,807 competing listings and difficulty 100 |
| `trick or treat map` | **0** |
| `personalized halloween` | **0** |
| `neighborhood map print` | **0** |

**Do not build the title from the product name.** The three phrases that describe this sheet best
all measure 0, which is the trap that cost FAM-001 its middle title slot. Lead with the decor and
gift phrases that have volume.

**Measure the same batch again in the first week of September**, because Halloween demand rises
through September and these are July numbers. Write the title after that run, not before.

---

*The plan, kept for reference:*

A seasonal variant of FAM-001. The buyer is a parent in the United States, Canada, the United
Kingdom or Ireland. The parent buys a digital file, prints it at home, and gives it to the child
before the trick-or-treat walk on 2026-10-31. The child marks the sheet during or after the night.

**The product draws the neighbourhood and its houses. It says nothing about candy.** Nobody can
know which house hands out candy before the evening. The signal is a porch light and decorations,
and a neighbour decides it on the night. Nextdoor has run a crowd-sourced Treat Map for 13 years,
for free, and it wins on live data. This product does not compete there. It competes on the object
the child keeps afterwards.

**Never write, in copy or on the sheet, which houses are safe or which houses take part.** That is
a refund risk and a review risk, and the data does not exist.

#### The one hard constraint: scale

A home printer takes A4 or US Letter. Both sizes already exist in
[`posterlab/chrome/page.py:6-15`](../../posterlab/chrome/page.py#L6-L15), so the page work is done.
The problem is the radius. A house is about 10 metres wide. On an A4 sheet the map frame is about
180 mm wide.

| Radius | Scale | A house prints at | Reads as |
|---|---|---|---|
| 2000 m | 1:22,000 | **0.45 mm** | grey mush |
| 1000 m | 1:11,000 | **0.90 mm** | texture |
| 600 m | 1:6,700 | **1.5 mm** | small blocks |
| 400 m | 1:4,400 | **2.3 mm** | houses |
| 300 m | 1:3,300 | **3.0 mm** | houses a child can mark |

A radius of 2 to 3 km cannot show houses on a sheet a parent prints at home. At that radius the
buildings become one grey mass. A trick-or-treat walk covers a few blocks, not 3 km, so the smaller
radius also matches the real night.

**Recommendation.** Set the default radius to **400 m**. Offer 800 m as a wide option. Cap the
radius at 1000 m and say why in the listing. Build the 2000 m version once as a comparison render,
then judge it against the 400 m version before you decide.

#### Work to do — all five done 2026-08-17

1. ~~**Add a building layer.**~~ **Done.** `basemap.build_query(bbox, buildings=True)` adds
   `way["building"]` and `relation["building"]`, and `classify` returns a `buildings` layer. The
   layer is **opt-in**, so FAM-001 renders exactly as before and every existing cache key is
   unchanged.
2. ~~**Cap the query.**~~ **Done.** `basemap.check_buildings_radius` refuses a building box wider
   than `BUILDINGS_MAX_RADIUS_M` = 1000 m. `--allow-wide-buildings` lifts it for one comparison.
3. ~~**Handle empty data.**~~ **Done and tested.** With zero buildings the sheet degrades to a clean
   street map with the home marked, and the renderer warns the operator. A run with zero playgrounds
   no longer raises.
4. ~~**Add a Halloween theme.**~~ **Done.** `studio/themes/lantern.json`, built from `nocturne`. Same
   Spectral serif, same road hierarchy, same page furniture. One warm amber accent, which also marks
   the home. No orange and black clip art.
5. ~~**Add the annotation furniture.**~~ **Done.** The panel sheet draws a costume line, a
   "we walked with" line, a 40-box treat tally, a drawing box, and a "the house we liked best" line.
   A legend repeats the same home glyph the map draws.

#### Commerce

Digital download only. No physical item ships. Render after the order, the same way FAM-001 works
today, so this adds no new operations. Price it low, between 6 and 9 US dollars, because it is an
impulse buy and not a keepsake price.

**Timing is the real risk.** Halloween searches rise through September. A listing that goes live
after 2026-10-20 earns no ranking history before the peak. If the build slips past 2026-09-20, stop
and hold the idea for 2027.

#### Why it can repeat

The value arrives after the walk. The filled sheet becomes the record of one night, in the same way
the playground map records a childhood. A parent can buy it again every year, with a new year and a
new costume on it. That is the part Nextdoor cannot hold.

### BL-013 · Watch for the Playwright MCP server failing to start
**Status:** `needs-review` · **Due:** on the next occurrence · **Platform:** tooling

**The run of 2026-08-18 reached no platform, and the cause written that day was wrong.** Corrected
2026-08-19.

**What is certain.** No `mcp__playwright__*` tool existed in that session, so there was no browser
to drive. That is a different failure from the profile lock of `BL-009`: a lock returns an error
*from a tool call*, while this shows no tool at all. Keep that test.

**What was wrong.** The 2026-08-18 entry blamed `"command": "playwright-mcp"` with an empty `env`,
on the reasoning that the binary sits only under nvm and the session PATH lacked it. The evidence
for that was the PATH inside the agent's own Bash tool. **That tool is sandboxed, and its PATH is
not the PATH that Claude Code uses to start an MCP server.** So the conclusion did not follow.

**What actually happened.** The server connected later in the same session, with **no change to
`~/.claude.json`** and no restart of the machine. The 2026-08-19 half of the session then drove
Pinterest and Etsy normally. So the start-up failure was transient, and the cause is **unconfirmed**.

**Do not apply a config change for this.** The registration works. Changing it now would be a fix
for a cause that is not proven.

**If it happens again, capture evidence before doing anything else:**

1. Run `claude mcp list` in a terminal and record whether `playwright` reads Connected.
2. Record the MCP server start-up error from the session, which names the real reason.
3. Only then decide. An absolute command path stays the candidate fix, because the `nanobanana`
   server in the same file already uses one, but it needs the error message first.

Offline work is the correct response in the meantime, and the run of 2026-08-18 did that.

### BL-014 · Measure the Christmas keywords in eRank
**Status:** `draft` · **Due:** ~~2026-09-13~~ **measured 2026-08-20, re-measure 2026-10-01** ·
**Platform:** eRank

**The batch is measured.** The full table is *Run 4* in
[`studio/research/etsy_keyword_evidence_20260816.md`](../research/etsy_keyword_evidence_20260816.md).

| Phrase | Monthly searches |
|---|---|
| `christmas wall art` | 4,370 |
| `christmas gift` | 2,210, with 7,614,738 competing listings and difficulty 100 |
| `christmas decor` | 1,710 |
| `stocking stuffer` | 1,010 |
| 12 of the 20 phrases | **0** |

**Recommendation: change no kicker.** The live kickers measure 18,820 (`personalized gift`), 2,720
(`new home gift`) and 1,710 (`baby gift`). Only `christmas wall art` beats two of them, and it does
not describe a personalized map of playgrounds.

**One task is left.** July is the trough of the Christmas season, so every number above is a floor.
Run the same 20 phrases again in the first week of October, before `BL-007` publishes on
2026-10-01. Upgrade a kicker only if a Christmas phrase then beats the evergreen one it replaces.

### BL-015 · Generate a real room scene for the sun poster
**Status:** `draft` · **Due:** 2026-09-06 · **Platform:** Pinterest, Etsy

`BL-010` found that the winning pin shows a room and every sun pin shows a bare specimen. The
`s06` candidate approximates a room with a drawn wall, and it still reads as synthetic beside a
photograph.

PRT-006 has exactly one framed image, `brand/listing-photos/01-hero-framed.jpg`, and it is a flat
dark background, not a room. FAM-001 has eight room scenes and wins on them.

Generate 3 or 4 room scenes for the sun poster with the Gemini image tool, then strip the
watermark locally. The audience is adult decor, so use a living room, a hallway and a bedroom.
**Never a nursery, and never a child's room**, because the sun poster is not sold to that audience.
Skills: `.github/skills/gemini-image-generation/SKILL.md`, then
`.github/skills/dewatermark-stills/SKILL.md`. These images also fill the listing's empty photo
slots, so this task pays twice.

### BL-016 · Clear the 6 pin drafts before they expire
**Status:** `draft` · **Due:** 2026-08-29 · **Platform:** Pinterest

The Pin builder at `https://www.pinterest.com/pin-creation-tool/` shows **Pin drafts (6)**, and each
one reads `11 days until expiry` on 2026-08-20. So they expire near 2026-08-31, and Pinterest
deletes the work.

Nobody knows what these 6 drafts hold. One of them can be the sun pin that a session lost to an
`about:blank` reset on 2026-08-19. Open each draft, record its image, title and board, then decide:
publish it, or delete it. Do not publish a draft that repeats a live pin, because two identical pins
on one board read as spam.

The 5 pin per run limit still applies to anything this task publishes.

**Read on 2026-08-24. None is the lost sun pin** — all 6 are FAM-001 room-scene photos, not sun
posters. Each shows a different lifestyle shot: a gift-wrapped framed map on a bed, a dad and child
pointing at a leaned framed map, a mum and toddler pointing at a framed map on a sage-green wall, an
empty playroom with the map on the wall, hands holding an unframed print at a window, and a child
sticking a gold star on the map close-up. **Every draft is blank** — no title, no board, no link —
so none is ready to publish as-is. Expiry reads 7 days (was 11 on 2026-08-20), so they lapse near
2026-08-31. **Needs the founder:** write title + board + Share & Save link for the ones worth
keeping, or let the rest expire. None was published or deleted this run.

### BL-005 · Photograph a real printed poster on a real wall
**Status:** `blocked` · **Blocked by:** no printed poster exists yet · **Platform:** both

The guide names this as the single shot most likely to beat every render in the bank. It needs a
physical print, so no agent run can clear it. Ask the founder at each run whether a print arrived.

### BL-006 · Review outbound clicks by campaign
**Status:** `approved` · **Due:** 2026-09-26 · **Platform:** Pinterest, Etsy

Both earlier Pinterest entries set this date. Read outbound clicks per `utm_campaign` in Pinterest
Analytics, reconcile against Etsy → Stats → Traffic sources, and rebuild variations of whichever
pin earned the most.

### BL-007 · Build the Christmas pin set
**Status:** `approved` · **Due:** ~~build by 2026-09-20~~ **built 2026-08-18**, publish from 2026-10-01 · **Platform:** Pinterest

Pinterest buyers plan 45 to 60 days ahead, so Christmas pins go live in early October. Both
products are giftable.

**Three pins are built, and none is published.** The publish date is 2026-10-01. Builder is
`studio/assets/make_pin_experiments.py`.

| File | Product | Kicker | Searches | Headline |
|---|---|---|---|---|
| `x01-xmas-grandparents.jpg` | FAM-001 | `Personalized gift` | 18,820 | The gift they unwrap slowly |
| `x02-xmas-in-hands.jpg` | FAM-001 | `Baby gift` | 1,710 | Under the tree, then on the wall |
| `x03-xmas-tromso.jpg` | PRT-006 | `New home gift` | 2,720 | A year of light, wrapped |

**No kicker names Christmas, on purpose.** No Christmas phrase has been measured in eRank yet, and
this shop already lost weeks to unmeasured phrases. Each kicker above is measured, and the
Christmas hook sits in the headline, where it costs no discovery. `BL-014` measures the Christmas
phrases so the kickers can be upgraded before the October publish.

**Two notes for the review.** `x02` deliberately does not reuse the nursery photo behind the live
`p03` pin, because two pins with one photo on one board read as spam. And `x03` shares its
composition with the `BL-010` candidate `s06`, so publish only one of the two in the same window.

---

## Done

### BL-011 · Test render one Halloween pack end to end — **done 2026-08-22**

Rendered a pack for a test address in Springfield, Illinois. All 8 PDF files rendered, and the
OpenStreetMap attribution prints on each sheet.

**It found a defect.** `render.py` built the ZIP from the PDF files of one invocation, and it named
the archive from the title and the theme only. The 8-step loop in section 8 therefore overwrote the
archive on every step, and left 2 archives that each held 1 PDF file and the 2 notes. A seller who
followed the documented procedure would have sent a buyer one sheet of the four. The engine now
takes a comma-separated list for `--theme`, `--layout` and `--size`, so one command builds the whole
pack into one archive. Section 8 of the listing document holds the new command.

### BL-002 · Rewrite the FAM-001 title, at or under 14 words — **done 2026-08-19**

The founder reaffirmed **option B** on 2026-08-19, after this run reported that B is 15 words and not
14. B is live and verified on the public listing page.

```
Nursery Wall Art, Personalized Map Print, Custom Map Print, New Baby Gift, Kids Room Decor
```

15 words, 90 characters. **The 14-word rule is an internal limit** taken from an Etsy warning, not a
hard Etsy limit, and 90 characters is far below the 140-character maximum. The founder accepted the
one-word overage. Option C, at 14 words and 9,010 measured searches, was offered and declined.

Both dead slots are gone. Measured monthly searches, before and after:

| Slot | Before | Searches | After | Searches |
|---|---|---|---|---|
| 1 | Nursery Wall Art | 4,570 | Nursery Wall Art | 4,570 |
| 2 | Personalized Playground Map | **0** | Personalized Map Print | 10 |
| 3 | Custom Map Print | 1,200 | Custom Map Print | 1,200 |
| 4 | New Baby Gift | 1,310 | New Baby Gift | 1,310 |
| 5 | Kids Decor | 60 | Kids Room Decor | **1,520** |
| | **Total** | **7,140** | | **8,610** |

**The test is `Etsy search` in Stats.** It sent **0 of 8** visits month to date on 2026-08-19. Both
live titles now carry only measured phrases, so that number is what proves or disproves the rewrite.
Read it on the next run and every run after.

### BL-010 · Rebuild the sun-poster pin image — **done 2026-08-19**

The comparison is in the log of 2026-08-18. The founder approved `s06-kiruna-light.jpg` on
2026-08-19, and it is published to *Sunrise Sunset Wall Art* under campaign
`sun3-minimalist-kiruna`. Verified on the board page: 6 Pins became 7 and the title appears. Kicker
`Minimalist wall art`, 2,210 searches, which no other pin uses. The old dark pins stay up.

**The test, on or after 2026-09-02**, which is 14 days. Compare `sun3-minimalist-kiruna` against the
four `sun2-*` pins on outbound click rate:

- If the light-wall pin wins, rebuild the rest of the sun set on that pattern, and fold
  `framed_panel` from `studio/assets/make_pin_experiments.py` into `make_pin_images.py`.
- If it does not win, the image is not the whole limit. Run `BL-015` room scenes as the next test,
  because a drawn wall is still not a photographed room.

### BL-008 · Fill `Room`, `Materials` and `Craft` on both listings — **done 2026-08-17**

PRT-006 `Craft` was empty. It now holds `Framing` and `Printing & printmaking`. The value survived
a reload of the editor, so it is really saved. FAM-001 needed no change.

| Listing | `Room` | `Materials` | `Craft` |
|---|---|---|---|
| FAM-001 | Bedroom, Game room, Kids, Living room, Nursery (5 of 5) | Paper, Wood | Framing, Printing & printmaking |
| PRT-006 | Bedroom, Entryway, Living room, Office (4 of 5) | Paper, Wood | Framing, Printing & printmaking |

PRT-006 still has one free `Room` slot. The sun poster is adult decor, so `Kids` and `Nursery` do
not fit. Leave the slot empty until a value is worth measuring.

Procedure that works, for the next attribute. The options are checkboxes in a collapsed typeahead,
so a click fails with `element is not visible` until the menu is open. Click the field's
`input[id^="typeahead-input-"]` first. Then click `label[for="<option input id>"]`, never the input
itself. Confirm the footer reads `You changed: 1 attribute.` before publishing. `Style` is still
unavailable and must not be attempted.

### BL-004 · Write descriptions for the three new boards — **done 2026-08-16**

All three descriptions are live and were verified on the public board page, not in the editor. Each
leads with a different measured phrase, so no two boards compete for the same search.

| Board | Lead phrase | Searches | Length |
|---|---|---|---|
| *Sunrise Sunset Wall Art* | `sunset wall art` | 1,150 | 309 characters |
| *Nordic & Scandinavian Wall Art* | `scandinavian wall art` | 1,200 | 313 characters |
| *Personalized Housewarming Gifts* | `housewarming gift` | 3,670 | 305 characters |

Procedure, for the next board: open the board, click `[aria-label="More board options"]`, then
*Edit info and settings*. The description field is `#boardEditDescription`, a plain textarea. Save
with the `Done` button.

### BL-009 · Clear the Playwright browser profile lock — **fixed in the wrapper 2026-08-16**

The AUTO run reached no platform. Both navigate attempts failed with `Browser is already in use
for .../mcp-chrome-d83f129, use --isolated`. Google Chrome PID 68511, started at 18:05 by an
interactive Claude session, still held that profile.

This is structural, not accidental. An interactive session and the scheduled run share one
Playwright profile, and the interactive session leaves its Chrome running. Left alone, every
scheduled run would fail this way.

`studio/ops/shop_run.sh` now ends any Chrome started against an `mcp-chrome-*` user-data-dir
before it starts the session. That pattern cannot match a personal Chrome, which uses
`~/Library/Application Support/Google/Chrome`. Logins live in the profile directory on disk, so
they survive the restart.

The rule for an **agent** is unchanged: an agent still must not kill the process, and must not use
a second profile. Only the wrapper does this, before any agent is running.

### BL-001 · Rebuild the 5 sun pin kickers from measured keywords — **done 2026-08-16**

The FAM-001 kickers were already measured, so only PRT-006 needed work. All five sun kickers were
replaced in `studio/assets/make_pin_images.py`, the images were re-rendered, and five new pins
went out. The old pins stay up.

| Pin | Kicker before | Searches | Kicker now | Searches | Published |
|---|---|---|---|---|---|
| `s01-hero` | `Sunrise sunset wall art` | under 20, KD 100 | `Sunset wall art` | 1,150 | now |
| `s02-tromso` | `Midnight sun poster` | not measured | `Scandinavian wall art` | 1,200 | now |
| `s03-reykjavik` | `Nordic wall art` | 10 | `Personalized wall art` | 2,350 | 18 Aug |
| `s04-kiruna` | `Scandinavian print` | 10 | `Housewarming gift` | 3,670 | 20 Aug |
| `s05-stockholm` | `Custom coordinates print` | 10 | `New home gift` | 2,720 | 22 Aug |

Campaign slugs: `sun2-sunset-hero`, `sun2-scandi-tromso`, `sun2-personalized-reykjavik`,
`sun2-housewarming-kiruna`, `sun2-newhome-stockholm`. Compare these against the original `sun-*`
slugs on 2026-09-26 under `BL-006`. That comparison is the shop's first real test of whether
measured keywords beat invented ones.
