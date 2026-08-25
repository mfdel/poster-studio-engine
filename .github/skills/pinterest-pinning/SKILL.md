---
name: pinterest-pinning
description: USE FOR running the Hopscotch Maps Pinterest account end to end — generating 2:3 pin images from the brand photo bank, publishing and scheduling pins through Pin Builder in a real browser, picking the right board, and linking with Etsy Share & Save URLs. Covers the browser session's failure modes, the AI-content disclosure rules, and the posting cadence that keeps a young account out of spam territory. Triggered by "post to Pinterest", "make pins", "schedule pins", "manage my Pinterest", "drive traffic to Etsy from Pinterest", or any work on the boards at pinterest.com/fuatdeligoz.
---

# Running the Pinterest Account

Pinterest is the shop's only free channel where every post carries a clickable link, and it is a
search engine rather than a social network — distribution comes from keywords and boards, not
followers. The strategy lives in [`studio/brand/pinterest-guide.md`](../../../studio/brand/pinterest-guide.md);
this skill is the execution procedure. Read the guide's §2 (boards), §3 (image rules) and §4
(paste-ready copy) before writing new pin copy, and log the run in
[`studio/brand/pinterest-log.md`](../../../studio/brand/pinterest-log.md) when finished.

## 0. Account facts

| | |
|---|---|
| Profile | `https://se.pinterest.com/fuatdeligoz/` (business account, Swedish locale) |
| Display name | `Hopscotch Maps · Personalized Maps & Sunrise Sunset Prints` |
| Boards | The eight from guide §2, plus *Sunrise Sunset Wall Art*, *Nordic & Scandinavian Wall Art* and *Personalized Housewarming Gifts* for PRT-006 (added 2026-08-16, no descriptions yet) |
| Etsy shop | `https://hopscotchmaps.etsy.com` |
| FAM-001 listing | `https://hopscotchmaps.etsy.com/se-en/listing/4547086425/personalized-playground-map-custom` |
| PRT-006 listing | `https://hopscotchmaps.etsy.com/se-en/listing/4556527075/sun-year-poster-personalized-year-of` |

## 1. Check the browser session first

The Playwright MCP server keeps its own persistent Chrome profile, so the Pinterest login usually
survives between sessions — but Pinterest does drop it, and a dropped session fails *late*, after a
pin is fully composed:

```
Authorisation failed.
Cannot create Pin because the image could not be uploaded.
```

Once that happens the draft is unrecoverable — reload and redo the pin. So check before starting:

```js
// browser_evaluate
() => !!document.querySelector('[data-test-id="header-accounts-options-button"]')
```

If it returns `false`, navigate to `https://se.pinterest.com/login/` and ask the user to log in in
that window. Do not try to log in on their behalf.

## 2. Generate the pin images

Pinterest optimises for **2:3**; the Etsy listing photos are 4:5, and the info graphics in
`listing-photos/` are unusable as pins because their body type is illegible at feed size (~200px
wide). Build pins instead with:

```bash
uv run python studio/assets/make_pin_images.py
```

It renders 1000×1500 JPGs into `posters/fam001-playground-map/brand/pinterest-pins/` — a cream band
across the top third carrying a small-caps keyword kicker and a two-line emotional headline, over a
full-bleed room photo from `brand/ai-photos/`, with a `hopscotchmaps · etsy` footer.

To add pins, append to the `PINS` list in that script: `(source_image, kicker, [line1, line2],
output_name)`. Keep headlines ≤22 characters per line so they render at 74px, and lead with the
feeling ("Every playground you'll grow up loving"), not the spec ("300 DPI printable PDF"). Make the
kicker a phrase buyers actually search — see the evidence table in
[`studio/research/etsy_keyword_evidence_20260816.md`](../../../studio/research/etsy_keyword_evidence_20260816.md).

The same script builds the **PRT-006** pins from the `SUN_PINS` list, into
`posters/prt006-sun-year/brand/pinterest-pins/`. Those use `pin_poster()`, which letterboxes the
artwork onto the poster's own background instead of cropping it — a crop cuts the city name off the
top. The band, fonts and footer are identical, so both products read as one shop. Uploading is the
same, with two differences:

- **Five pins ship, not eleven.** The sample cities render as near-identical gold rings at feed
  size. Only the high-latitude shapes with a visible polar-night notch (Tromsø, Kiruna, Reykjavík)
  are distinct, plus one plain ring. A board of near-duplicates reads as spam.
- **No AI disclosure.** The sun artwork and its framed mockup come from our own code, not from a
  generator. Only the FAM-001 room photos need the badge.

Review the output as a contact sheet before uploading — bad crops and text collisions are obvious
in a grid and invisible one file at a time.

## 3. Compose each pin

Open a **fresh** `https://www.pinterest.com/pin-builder/` per pin; reusing a draft after any error
carries the error forward. Field ids carry a per-draft UUID, so select by prefix:

| Field | Selector | Notes |
|---|---|---|
| Image | `input[id^="media-upload-input"]` | `setInputFiles(<abs path>)` via `browser_run_code_unsafe` — skips the file chooser entirely. Wait ~6s for the upload |
| Title | `textarea[id^="pin-draft-title"]` | keyword phrase first, ≤40 chars visible |
| Description | `div[aria-label="Tell everyone what your Pin is about"]` | **contenteditable — `fill()` silently does nothing, type into it** |
| Alt text | `textarea[id^="pin-draft-alttext"]` | behind a `button:has-text("Add alt text")` |
| Link | `textarea[id^="pin-draft-link"]` | see §4 |
| Schedule | `input[id^="pin-draft-schedule-publish-later"]` | then `input[id^="pin-draft-schedule-date-field"]` opens a calendar |
| AI disclosure | `input[id^="pin-draft-ai-disclosure"]:not([name])` | see §5 |
| AI person | `input[id$="-synthetic-performer"]` | see §5 |
| Board | `[data-test-id="board-dropdown-select-button"]`, then `div[title="<Board name>"]` | **carries over from the previous pin — always set it explicitly** |
| Publish | `[data-test-id="board-dropdown-save-button"]` | |

Verify the composed draft in one `browser_evaluate` before publishing, then confirm the result:
`You created a Pin` for an immediate publish, `Scheduled to publish on …` for a scheduled one.
An onboarding tour modal sometimes covers the builder — dismiss it with Escape or its Cancel button.

**Do not trust the builder's own text as proof.** After a save the page can still read `Pin builder`
and `Publish`, which looks like a failure and is not. Confirm on a real page instead:

| What | Where |
|---|---|
| A published pin | the board page, for example `/fuatdeligoz/sunrise-sunset-wall-art/` — the pin count rises and the title appears |
| A scheduled pin | **`https://se.pinterest.com/fuatdeligoz/scheduled-pins/`** — lists every scheduled pin with its day, time and board |

`/_scheduled/` is **not** a valid path and redirects to the home feed. Use `/scheduled-pins/`.

The date field opens a calendar. Type nothing into it. Click the day by its aria-label, in the
page locale's wording: `[aria-label="Choose Tuesday, 18 August 2026"]`. Past days carry
`Not available …` and are disabled. The default time is 12:00 PM.

## 4. Destination links — always Share & Save

Etsy credits **4% of the order value** back against the Etsy bill when the buyer arrives on a
Share & Save link, which is the **shop-subdomain** form. Never publish a `www.etsy.com` URL.

```
https://hopscotchmaps.etsy.com/se-en/listing/4547086425/personalized-playground-map-custom
  ?utm_source=Pinterest&utm_medium=organic&utm_campaign=<pin-slug>
```

Give every pin its own `utm_campaign` slug so Etsy → Shop Manager → Stats → Traffic sources shows
which pin actually sells. Link to the **listing**, never the shop homepage — fewer clicks to buy.

> A pin that Pinterest has converted into an Etsy **product pin** ignores link edits and keeps its
> original URL. The only fix is to delete it and post it again.

## 5. Disclose AI content

The room photos are Gemini/ChatGPT renders, so every pin built from them sets **Mark as AI-modified**,
and any pin showing a person — hands included — also ticks **This Pin includes an AI-generated
person**. Pins built from a real photograph set neither. This is honesty about the imagery and it
keeps the account clean; the badge costs nothing in distribution.

## 6. Cadence and board fit

- **3–5 pins per day**, steady. A two-week-old account dumping ten pins in an hour reads as spam.
- Publish a few now and schedule the rest one per day via *Publish at a later date* (up to 30 days
  out) — the native scheduler is enough, Tailwind is not needed.
- **One image → one board**, its best fit. Reposting the same image across five boards is the old
  strategy and now reads as spam.
- Only `Personalized Playground Map` should be all our own pins. The other seven want roughly 3–4
  saved pins from elsewhere per pin of ours while the account is young.
- Pinterest users plan 45–60 days ahead: Christmas pins go live in **early October**, Mother's and
  Father's Day about six weeks out.

## 7. What to measure

Only **outbound clicks** matter at this stage — impressions and saves feel good and buy nothing.
Read them in Pinterest Analytics, and reconcile against Etsy → Stats → Traffic sources. Expect
near-zero for 4–6 weeks; Pinterest is slow to start and then compounds. If after 90 days of
consistent pinning there are under ~50 outbound clicks a month, the **images** are the problem —
go back to guide §3 and shoot the real printed map on a real wall.
