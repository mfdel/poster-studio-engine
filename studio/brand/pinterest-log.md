# Pinterest Marketing Memo

Running log of what the Hopscotch Maps Pinterest account has actually done, and why. Strategy lives
in [pinterest-guide.md](pinterest-guide.md); the execution procedure lives in
[`.github/skills/pinterest-pinning/SKILL.md`](../../.github/skills/pinterest-pinning/SKILL.md).
One short entry per working session — decisions and outcomes, not steps.

**Account:** `pinterest.com/fuatdeligoz` · business · display name
`Hopscotch Maps · Personalized Maps & Sunrise Sunset Prints`
**Destination:** the FAM-001 or PRT-006 Etsy listing, always via the Share & Save shop subdomain
(`hopscotchmaps.etsy.com`), one `utm_campaign` per pin.
**Metric that counts:** outbound clicks to Etsy. Nothing else, for now.

---

## 2026-08-16 — Sun-Year enters the account

**Before:** eleven pins, all playground. The profile name and bio described playground maps only, so
a sun pin would have read as a different shop. Account lifetime traffic: 3 monthly views.

**Shipped:**

- Profile widened to both products. The display name now carries `Sunrise Sunset Prints`, and the
  bio names both the neighborhood maps and the year-of-light prints.
- Three new boards, each named after a phrase buyers search: *Sunrise Sunset Wall Art*,
  *Nordic & Scandinavian Wall Art*, *Personalized Housewarming Gifts*.
- Five PRT-006 pins built by `make_pin_images.py` into
  `posters/prt006-sun-year/brand/pinterest-pins/`. Three published, two scheduled for 17 and 19 Aug.
- Every sun pin carries alt text and a Share & Save link with its own campaign tag
  (`sun-hero`, `sun-tromso`, `sun-stockholm`, `sun-reykjavik`, `sun-kiruna`).

**Decisions worth remembering:**

- **Five pins, not eleven.** The eleven sample cities render as almost the same gold ring at feed
  size. Only the high-latitude shapes with a visible notch are distinct. A board of near-duplicates
  reads as spam, so Oslo, Copenhagen and Edinburgh were cut.
- **No AI disclosure on sun pins.** The sun artwork and its framed mockup are drawn by our own code,
  not generated. The FAM-001 room photos remain AI and keep their badge.
- The sun poster letterboxes onto its own background instead of cropping, because a crop cuts the
  city name off the top. The hero is a room photo, so it still crops.
- Pin copy leads with the keyword phrase, because Pinterest reads the first 50 to 100 characters.

- The broken hero pin was **kept, not deleted**. Pinterest converted it to a product pin, so
  `/pin/<id>/edit/` redirects away and the `www.etsy.com` link cannot be fixed. Deleting it would
  have destroyed the account's only traction (18 impressions, 4 clicks, 1 save) to recover a 4%
  credit worth almost nothing at that volume. A correctly linked replacement, `p11-hero-neighborhood`,
  now runs beside it on the same board under campaign `fam-hero-neighborhood`.

**Open:**

- Pin kickers still carry the pre-eRank keywords. `custom neighborhood map print` and
  `sunrise sunset wall art` both measure near zero. Rebuild the kickers from
  [`etsy_keyword_evidence_20260816.md`](../research/etsy_keyword_evidence_20260816.md) on the next run.
- Boards are still 100% our own pins. Nothing saved from elsewhere yet.
- No photograph of a real printed poster on a real wall exists, for either product.

**Expect:** nothing before late September. Review outbound clicks by campaign around 2026-09-26.

---

## 2026-08-15 — First real pinning run

**Before:** account set up two weeks earlier and then left idle — bio, logo and all eight boards in
place with descriptions, but a single pin. The boards were empty shelves.

**Shipped:**

- A pin-native image set: ten 2:3 pins built from the room-photo bank, each with a keyword kicker
  and an emotional headline readable at thumbnail size. The 4:5 Etsy listing graphics were
  deliberately left out — their type is illegible in the feed.
- Five pins published across *New Baby Gifts*, *Baby Shower Gift Ideas*, *Nursery Wall Art & Decor*,
  *Screen-Free Activities for Toddlers* and *Family Keepsakes & Memory Ideas*.
- Five pins scheduled one per day, 16–20 Aug, covering *First Birthday Gift Ideas*,
  *Playground Adventures*, *Family Keepsakes* and the money board twice. Every board now has content.
- All new pins carry alt text, an AI-content disclosure, and a Share & Save link with its own
  campaign tag.
- Profile tightened: display name now carries the search keywords, and the website field points at
  the Share & Save shop URL.

**Decisions worth remembering:**

- Five published, five scheduled rather than ten at once — a two-week-old account posting in a burst
  reads as spam, and Pinterest rewards steadiness over volume.
- Room-context and ritual photos lead. The map shown flat is the weaker pin; buyers are imagining a
  wall.
- The AI-modified badge stays on. The imagery is generated, saying so costs nothing in reach.

**Open:**

- The original hero pin still points at a `www.etsy.com` URL and so earns no Share & Save credit —
  Pinterest converted it to a product pin, which ignores link edits. Needs a delete-and-repost.
- Boards are 100% our own pins. Healthy while young is ~3–4 saved pins from elsewhere per pin of
  ours; nothing has been saved yet.
- No photograph of a real printed map on a real wall exists. Per the guide this is the shot most
  likely to out-perform every render we have.

**Expect:** near-zero for 4–6 weeks. Review outbound clicks around 2026-09-26 and rebuild variations
of whichever pin earned the most.
