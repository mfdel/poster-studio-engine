---
name: etsy-shop
description: USE FOR running the HopscotchMaps Etsy shop in a real browser — auditing a live listing against the plan, editing listings (title, description, tags, attributes, variations, prices, SKUs, photos), managing shop-level settings (About story, production partners, GPSR, delivery and processing profiles), and verifying every change on the public page afterwards. Covers the listing editor's DOM traps that silently drop edits, and the compliance rules this shop must not break. Triggered by "review my Etsy listing", "fix the listing", "update Etsy", "change prices/variations/photos", "open the Etsy store", or any work under etsy.com/your/shops/me.
---

# Running the Etsy Shop

The shop is **HopscotchMaps** (Sweden). It sells **two listings**, each one product with
format × size variations: FAM-001 (personalized playground map) and, since 2026-08-15, PRT-006
(sun-year poster). The commercial plan for FAM-001 lives in
[`posters/fam001-playground-map/brand/etsy-listing-READY.md`](../../../posters/fam001-playground-map/brand/etsy-listing-READY.md);
this skill is the execution procedure for the browser work, plus the traps that cost real time.

> The plan document still describes a *three-listing* structure and prices in EUR. The live shop is
> deliberately one listing priced in SEK with launch pricing. When they disagree, the live shop wins —
> and say so rather than "fixing" the listing back to the doc.

## 0. Shop facts

| | |
|---|---|
| Shop Manager | `https://www.etsy.com/your/shops/me/dashboard` |
| Listing | `4547086425` — "Nursery Wall Art, Personalized Playground Map, Custom Map Print, New Baby Gift, Kids Decor" |
| Public URL (buyer view) | `https://www.etsy.com/se-en/listing/4547086425/personalized-playground-map-custom` |
| Share & Save URL (for any link you publish) | `https://hopscotchmaps.etsy.com/se-en/listing/4547086425/...` |
| Category | Home & Living → Home Decor → Wall Decor · physical · made to order |
| Variations | `Print, Frame or Digital` (Printed Poster · Poster + Frame · Digital (all sizes)) × `Size` (30x40 · 40x50 · 50x70 cm · All sizes included) — 12 combos, 7 enabled |
| Prices (SEK, launch) | Poster 350 / 380 / 420 · Framed 800 / 900 / 1 000 · Digital 100 (US 30, because the US delivery profile adds 70) |
| SKUs | `PGMAP-POS-{3040,4050,5070}` · `PGMAP-FRM-{3040,4050,5070}` · `PGMAP-DIG` |
| Delivery profile | `EU0-US70` — EU free, US 70 kr |
| Processing profile | Made to order · 3-5 days |
| Returns | No returns or exchanges (personalized) |
| Production partner | Prodigi (Prodigi Print Group Ltd), Bude, England — shown to buyers, attached to the listing |
| Custom options | `color theme` (required, 3 options) · `Title` (optional text) |

Frame colour is **wood only** — deliberately not a variation dimension. Digital is deliberately a
*variation of the physical listing*, not a separate listing or an Etsy Digital-type listing.

### Listing 2 — PRT-006 Sun-Year Poster (published 2026-08-15)

Built as a deliberate clone of listing 1's commercial shape, so everything above applies unchanged
except the rows below.

| | |
|---|---|
| Listing | `4556527075` — "Sunset Wall Art, Scandinavian Wall Art, Personalized Daylight Poster, Housewarming Gift, Custom Coordinates Print" |
| Public URL | `https://www.etsy.com/se-en/listing/4556527075/sun-year-poster-personalized-year-of` |
| Share & Save URL | `https://hopscotchmaps.etsy.com/se-en/listing/4556527075/...` |
| Prices (SEK) | **identical ladder to FAM-001** — Poster 350 / 380 / 420 · Framed 800 / 900 / 1 000 · Digital 100 (US 30) |
| SKUs | `SUNYR-POS-{3040,4050,5070}` · `SUNYR-FRM-{3040,4050,5070}` · `SUNYR-DIG` |
| Custom options | one required text box: *"Place, year and your one line of text"* |
| Artwork | `posters/prt006-sun-year/render_1b.py`; listing photos from `studio/assets/make_sunyear_listing_images.py` |
| Product rule | the **latitude gate** is in the copy: sell freely ≥48°, preview first 35–48°, refuse below ~35° |

Shared with listing 1 and re-used verbatim: delivery profile `EU0-US70`, processing profile
*Made to order · 3-5 days*, *No returns or exchanges*, the Prodigi production partner, and the GPSR
manufacturer + safety text. The editor pre-fills all of these from the other listing on a new
listing — check them rather than re-entering them.

### Listing 3 — FAM-002 Halloween Night Sheet (published 2026-08-22)

The first listing in the shop with **nothing physical to ship**. It is still a *physical,
made-to-order* listing, because Etsy Digital delivers a fixed file the moment a buyer pays and the
map is drawn for the buyer's address after the order. The files go out by Etsy message.

| | |
|---|---|
| Listing | `4560524378` — "Halloween Decor Printable, Personalized Kids Halloween Activity, Trick or Treat Map, First Halloween Keepsake" |
| Public URL | `https://www.etsy.com/se-en/listing/4560524378/halloween-decor-printable-personalized` |
| Share & Save URL | `https://hopscotchmaps.etsy.com/se-en/listing/4560524378/...` |
| Category | Paper & Party Supplies → Party Supplies → Party Favours & Games → **Party Games** · physical · made to order (moved out of Wall Decor on 2026-08-22) |
| Price | 76 SEK flat · no variations · quantity 999 |
| SKU | `HALMAP-DIG` |
| Delivery profile | `DIGITAL-FREE` — free everywhere, 1-2 days, origin 21874 |
| Processing profile | *Made to order · 1-2 days* |
| Production partner | **none** — nothing is printed and nothing is shipped |
| Custom options | one required text box: *"Your address, the title, and the date"* |
| Attributes | `Celebration = Halloween`. `Materials` deliberately empty |
| Plan | [`posters/fam002-halloween-night/brand/etsy-listing-READY.md`](../../../posters/fam002-halloween-night/brand/etsy-listing-READY.md) — section 13 records what changed at publish, section 14 the 2026-08-22 audit |

Four rules specific to this listing:

1. **Never state which houses give treats, take part, or are safe.** That data does not exist before
   the evening. It must stay out of the title, tags, description, photos and buyer messages.
2. **No production partner, ever.** Etsy pre-fills Prodigi from the other two listings on every new
   listing. Remove it here, or the listing claims a printer that never touches the order.
3. **`Materials` stays empty.** "Paper" is the Etsy suggestion and it would be a false claim,
   because the buyer supplies the paper.
4. **Do not put it back in Wall Decor.** The other two listings are wall art, so Etsy keeps
   offering that category. This one is a sheet a child writes on and carries. A Wall Decor
   breadcrumb over a description that reads "This is not wall art" is the fault that was fixed on
   2026-08-22 — and it is the same fault that got the `halloween wall art` tag removed.


## 1. Browser session

Etsy work runs through the **Playwright MCP** server (`mcp__playwright__*`). Two session facts:

- **Login is the user's job.** Navigate to the Shop Manager URL and ask them to sign in in that
  window; the MCP Chrome profile usually keeps the session between runs.
- **The profile lock.** If a Chrome from an earlier session still holds the MCP profile, every
  navigate fails with `Browser is already in use for .../mcp-chrome-<hash>, use --isolated`. That
  Chrome runs with `--remote-debugging-pipe`, so nothing can attach to it. Ask the user to quit that
  window — killing it may be blocked by the permission classifier, and the fallback of scripting
  `playwright-core` with a throwaway profile loses the Etsy login.

`browser_take_screenshot` on Shop Manager pages frequently times out on font loading. Read state with
`browser_evaluate` (`document.body.innerText`, input values, `aria-*` attributes) and reserve
screenshots for judging *images*.

## 2. Where things live

| Task | URL |
|---|---|
| Listings list (SKUs, price ranges, tag facets) | `/your/shops/me/tools/listings` |
| Listing editor | `/your/shops/me/listing-editor/edit/4547086425` |
| — sections | append `#media`, `#item-details`, `#item-options`, `#pricing-logistics`, `#how-its-made` |
| Shop name, tagline, **About story** | `/your/shops/me/settings/your-shop/shop-basics` (`#shopStory`) |
| Production partners + economic operators | `/your/shops/me/partners` |
| Delivery & processing profiles | `/your/shops/me/tools/shipping-profiles` |
| Search visibility, stats, traffic sources | `/your/shops/me/search-visibility`, `/your/shops/me/stats` |

## 3. Editor mechanics — the traps

The listing editor is React + dnd-kit. These cost the most time, in rough order of nastiness:

- **An open `wt-menu` freezes the whole page.** A stray click on an attribute chip opens a menu that
  sets `overflow: hidden` on `<body>`. From then on *every* click fails with `element is outside of
  the viewport` and `scrollIntoView` does nothing, because the page cannot scroll. It looks like a
  broken selector and it is not. Press `Escape` until
  `getComputedStyle(document.body).overflow === 'visible'`, then retry.
- **The category control is a `div`, and its search field is `readonly` until you uncover it.** The
  card is `[aria-label="Expand to edit category section"]` (`role="button"`, no `<button>` tag) — a
  Playwright click on it works once the page can scroll. That reveals
  `#listing-editor_category-search-typeahead`, which is `readonly` and covered by
  `div.le-category-search__committed`. JS-click the committed div to clear it, wait a beat for the
  re-render, then `focus()` + `page.keyboard.type()` — the typeahead needs real keystrokes. Options
  arrive as `#category-search-option-<taxonomyId>` inside `[id^="category-search-options"]`; click
  the id, never the text. Changing the category to another "Physical or digital" node keeps the
  listing type and keeps `Celebration`; it does drop category-specific attributes such as `Craft`.
- **`element.click()` on a checkbox or radio updates the DOM but not the editor's change set.** The
  toggle looks flipped and publishes nothing. Click **`label[for="<input id>"]`** instead, then
  confirm the footer's "You changed: …" text names the field. Buttons are the exception — a JS click
  on a `<button>` works, and is the way past the point below.
- **The sticky unsaved-changes footer intercepts pointer clicks** on anything it overlaps
  (`… intercepts pointer events`). Use `browser_evaluate` to `scrollIntoView({block:'center'})` then
  `.click()` the button, or Playwright's `{ force: true }`.
- **Typing appends.** `browser_type` with `slowly` uses `pressSequentially`, which *adds* to the
  existing value (`MinimalistContemporary`). Use `browser_fill_form` (`fill`) to replace, and only
  fall back to slow typing for typeaheads that need keystroke events.
- **Typeaheads need a suggestion click.** The production partner's *Location* field rejects free
  text ("Please fill out all the required fields") until you type and click a real suggestion —
  `Bude, United Kingdom` → click `Bude, England, United Kingdom`.
- **Variation option values cap at 20 characters** and cannot be renamed in place. Renaming means
  *add the new value, delete the old one* — and on Apply, Etsy **re-enables all 12 combos** and
  leaves the new rows' price/SKU **empty**. After any option-list edit you must re-enter the row's
  SKU + all three prices (`domesticPrice` = Sweden, `usPrice` = US, `price` = everywhere else) and
  re-disable the combos that shouldn't sell. Inputs are
  `input[name="variations.tables.0.rows.<n>.controls.{sku,domesticPrice,usPrice,price}"]`;
  the visibility switches are `input[id^="variation-switch"]` in row order.
- **Photo edits are immediate and are NOT covered by "Discard changes".** Deleting a photo hits the
  server the moment you click; discarding or reloading will not bring it back. Before deleting,
  confirm the *selected* photo by reading the full-size preview's id
  (`#wt-portals img[alt^="Listing image"]` → `il_fullxfull.<id>_`), because
  `button[data-delete-selected-media="true"]` acts on whatever is selected, not on what you last
  hovered. Re-uploads are possible from `brand/ai-photos/` but lose their position in the gallery.
- **Reordering photos (and setting the hero) is a dnd-kit drag.** `dragTo` does nothing and the
  keyboard protocol (Space, arrows, Space) stalls. What works: `browser_run_code_unsafe` with
  `mouse.down()`, a 6px jiggle, ~40 interpolated `mouse.move()`s with 25ms waits, a pause, then
  `mouse.up()`. **Primary photo = position 1**; there is no "make primary" action.
- **The `Style` attribute cannot be saved from this editor — treat it as unavailable.** It sits
  behind *Show all attributes*, and its options are `<button role="menuitemradio">` in a portal.
  Every approach tried on 2026-08-16 failed the same way: a JS click, `getByText().click()`, keyboard
  arrow navigation, and `pressSequentially` + `ArrowDown` + `Enter` all *paint the chip*, and two of
  them even made the footer count an attribute and publish cleanly — but the value is **gone after a
  reload, on both listings**. The row then stops rendering at all. Do not spend time on it, and do
  not report it as set without reloading the editor and re-reading the row.
  `Room`, `Materials` and `Craft` are **not** affected: a forced click on the option works and
  persists. `Room` takes up to 5 values and is the one that maps to buyer-facing wall-art filters,
  so it is the one worth getting right.
- **`Occasion` is meant to be empty here.** Its tooltip: *"Add to items designed for the occasion …
  not for items that could be gifted for an occasion."* A giftable poster is the second case. Leave
  `Occasion` and `Celebration` unset except for a deliberate seasonal swap.
- **A `<select>` can hold the right value and still block the save.** After a Playwright
  `selectOption`, Etsy's delivery-time dropdowns kept `aria-invalid="true"`, and *Save profile* did
  nothing with no error text. The fix is `focus()` → `selectOption()` → `dispatchEvent('change')` →
  `dispatchEvent('blur')`. Before any save, assert that
  `document.querySelectorAll('[aria-invalid="true"]')` is empty.
- **Collapsed fields need a native JS click, not a Playwright click.** `Add SKU` is a disclosure
  button whose input carries `aria-hidden="true"` until it opens. `click({force:true})` left
  `aria-expanded="false"`; a plain `element.click()` inside `page.evaluate` opened it.
- **A new listing inherits the production partner, the processing profile and the delivery profile
  from the other listings.** All three came in wrong for FAM-002. Read every pre-filled field on a
  new listing and change it before publishing.
- **Personalization field limits:** field title **45** characters, instructions **120** characters,
  buyer answer box up to **1024**. Longer text is accepted by the input and then blocks *Done*.
- **`Celebration` holds Halloween, `Occasion` does not.** The `Occasion` list has no Halloween
  value. `Celebration` does, and unlike `Style` it survives a publish and a reload.
- **Publishing a NEW listing takes two clicks.** The first `Publish` opens a confirmation dialog
  naming the non-refundable 0,20 USD listing fee. Click `Publish` inside that dialog too.
- **Publishing.** JS-click the `Publish changes` button; a redirect to `/tools/listings` means it
  saved. Photo-only changes still need a publish for the *order* to stick.

## 4. Verify on the public page, always

Shop Manager will happily show state that buyers never see. After publishing, load the public
listing URL and check the things that actually matter:

```js
// browser_evaluate — buyer-visible truth
() => {
  const t = document.body.innerText;
  const [fmt, size] = [...document.querySelectorAll('select')].slice(0,2)
    .map(s => [...s.options].map(o => o.text.trim()));
  return { fmt, size,
    dispatch: (t.match(/Get it by[^\n]*/)||[''])[0],
    partner: /Prodigi/.test(t),
    gpsr: /Vindögats/.test(t) };
}
```

Then walk the picker: select each format with `browser_run_code_unsafe` and read the Size options
back. Every format must offer exactly its own sizes and no dead ends — a disabled combo shows up as
a size that vanishes or a price of `undefined`.

## 5. Compliance — non-negotiable for this shop

1. **Production partner disclosure.** Prodigi prints and ships the physical items; "Who made it: I
   did" plus no partner is a policy violation. Keep Prodigi attached to any physical listing.
2. **GPSR** (physical goods, EEA buyers, listings created after 13 Dec 2024). The listing carries
   manufacturer name + postal address + email, and a safety block (indoor décor, not a toy,
   packaging-film warning, acrylic glazing, recycling). Editor fields:
   `#gspr-manufacturer-info-textarea`, `#gspr-safety-warnings-textarea`.
3. **Never write "instant download"** anywhere — listing, About story, tags, photos. Nothing is
   auto-delivered; every map is hand-styled after the order and sent by Etsy message.
4. **Processing time must cover the preview-approval loop** on the two poster listings. 1-2 days will
   be missed there; 3-5 is the current setting, and framed can take its own 5-7 profile via *Manage
   variations → Processing profiles vary*. FAM-002 is the exception: it has no preview loop, only a
   render and a message, so it deliberately runs *Made to order · 1-2 days*.
5. **OpenStreetMap ODbL attribution** stays on the rendered poster (the chrome carries it).
6. **Mockups must match what ships.** The room photos are AI renders; every one of them must show
   the same address and coordinates as the real product, and item details must not claim a single
   fixed size when three sizes are sold.

## 6. Listing audit checklist

Run this when asked to "review the listing". Report findings worst-first, with the buyer-visible
consequence — not a list of nits.

- **Money:** per-region prices on every enabled row (a US price entered as 30 instead of 300 is
  invisible in Shop Manager but halves your margin); Etsy's "Estimated earnings" floor; prices
  against the ladder in `etsy-listing-READY.md`; discounts/promo state.
- **Structure:** enabled combos vs. dead ends; option names a buyer can actually parse (no `-`);
  SKUs present and matching `studio/print_on_demand/sku_manager.xlsx`.
- **Policy:** production partner, GPSR, returns policy, "instant download" wording, processing time.
- **Category:** does the breadcrumb describe the *object*, or the traffic you wish you had? Etsy
  copies the category from the last listing you made, so a new product silently inherits the old
  one's shelf. A category that fights the description (Wall Decor over "This is not wall art") reads
  as mismatched traffic, and Etsy scores the low conversion against the listing. Check it before the
  tags — it outranks any single tag.
- **Findability:** title (140 chars max, but Etsy warns above **14 words** — stay at or under it, so
  sizes belong in the variations, not the title), front-loaded with a phrase buyers **actually type**,
  13 tags used (**each 20 characters or fewer** — a longer tag is silently rejected and you end up
  with 12), `Room` + `Materials` + `Craft` filled, `Style` unavailable (see §3),
  `Occasion`/`Celebration` left empty except for a seasonal swap, Width/Height empty while sizes
  vary, shop section set.

  > **Every title and tag must be evidence-backed, and the evidence is eRank — not autosuggest.**
  > Etsy's autosuggest tells you a phrase *exists*. It does not tell you anyone searches it.
  > `sunrise sunset wall art` has five autosuggest variants and **under 20 searches a month against
  > 18,652 competing listings**. Use eRank's **Bulk Keyword Tool** instead: 20 keywords per run, and
  > the *Search Trend* column shows real monthly volume even on the free tier (the rest is blurred).
  > The free plan allows 5 runs a day, so batch 20 at a time and never spend a run on one word.
  > The evidence table is
  > [`studio/research/etsy_keyword_evidence_20260816.md`](../../../studio/research/etsy_keyword_evidence_20260816.md).
  >
  > The noun phrase decides everything. `scandinavian print` gets 10 searches; `scandinavian wall
  > art` gets 1,200. `personalized map` gets 10; `custom map print` gets 1,200. Test the variants.
  >
  > This shop shipped for weeks on invented phrases — `year of light`, `sun year poster`,
  > `playground map`, `neighborhood map` all measure **0** — and took 7 views in 7 days.
  >
  > Etsy's own *Search visibility* page will offer an AI-rewritten title. **Read it before accepting.**
  > On 2026-08-16 it proposed renaming the sun poster to `… (Digital File)`, which would have hidden a
  > mainly physical listing from every physical search. It was rejected.
- **Photos:** hero readable as *a playground map* at thumbnail size; no near-duplicate runs; text
  inside AI mockups consistent and correctly spelled; 10+ of the 20 slots used; video present.
- **Copy:** description honest about digital vs. physical, made-to-order timing, colour variation.
- **Shop level:** About story, announcement, policies, and the Share & Save link habit.

Text inside AI mockups is worth a real pass: build a contact sheet, then crop each poster's title
band at 4× and read it. Four of the first 18 photos had garbled addresses ("Rue **Jeseph** Bara",
`2.2328°E` instead of `2.3328°E`) that were invisible at gallery size.

Small text errors in an otherwise good mockup can be repainted locally rather than losing the shot:
erase the line by copying a clean strip of "paper" from below it, re-render the correct text with
PIL at 8× (matched colour, tracking and tilt), downscale, blur ~0.35px, composite, re-upload. See
`hero-framed-wall-textfixed.jpg` in `brand/ai-photos/` for the result.

## 7. Links you publish

Always the shop-subdomain **Share & Save** form (`hopscotchmaps.etsy.com/...`) — Etsy credits 4% of
the order back on those. A `www.etsy.com` link forfeits it. Add `utm_source`/`utm_campaign` so
Shop Manager → Stats → Traffic sources can tell which channel sells.
