---
name: erank-keywords
description: USE FOR getting real Etsy search volume from eRank in a real browser before any title, tag or pin-kicker decision — batching keywords into the Bulk Keyword Tool inside the free plan's daily limit, reading the Search Trend column, and appending the result to the shop's keyword evidence table. Triggered by "check the keywords", "is anyone searching for X", "rewrite the title", "pick tags", or any claim about Etsy search volume.
---

# Keyword Evidence from eRank

**One rule decides everything in this file: a phrase is worth using only if a tool measured its
search volume.** Etsy autosuggest does not measure volume. It shows that a phrase exists.

The shop already paid for that lesson. On 2026-08-16 both listing titles were built on phrases that
eRank measures at **0 searches a month** — `year of light`, `sun year poster`, `playground map`,
`neighborhood map`. The shop took 7 views in 7 days. The full record is
[`studio/research/etsy_keyword_evidence_20260816.md`](../../../studio/research/etsy_keyword_evidence_20260816.md).

## 0. Account facts

| | |
|---|---|
| Tool | eRank, free plan |
| Login | The founder's account, in the Playwright MCP Chrome profile |
| Tool used | **Bulk Keyword Tool** |
| Marketplace | Etsy |
| Country | USA — the largest buyer pool, and the only country with dependable volume on the free tier |

## 1. The free-plan budget

The free plan allows **5 Bulk Keyword Tool runs a day**, and **20 keywords per run**. That is 100
keywords a day, and it is enough for any decision this shop makes.

- **Never spend a run on one keyword.** Fill all 20 slots, every time.
- **Spend at most 2 runs in one shop-run session.** Leave the rest for the founder.
- The *Search Trend* column shows real monthly volume on the free tier. Most other columns are
  blurred. Do not report a blurred number, and do not estimate one.

## 2. Build the batch before you open the browser

A run is wasted if the 20 phrases are 20 spellings of one idea. Build the batch like this:

1. Take the noun phrase you want to test — for example `wall art`.
2. Write 4 to 6 real variants of it. `scandinavian print` gets 10 searches a month.
   `scandinavian wall art` gets 1,200. **The noun phrase decides everything.**
3. Add the modifiers a buyer would type in front of it: `custom`, `personalized`, `personalised`,
   `nursery`, `housewarming`.
4. Add the phrases already live in the titles and tags, so you learn whether they still earn a slot.
5. Cut anything you have already measured. The evidence table is the memory.

## 3. Run it

1. Navigate to eRank and confirm the session, per phase 2 of the `shop-run` skill.
2. Open the Bulk Keyword Tool.
3. Paste the 20 phrases, one per line.
4. Set marketplace `Etsy` and country `USA`.
5. Run it, and read the result with `browser_evaluate` on the table rather than a screenshot.
   Screenshots of eRank tables are slow and hard to read back.

Selectors are not written down here yet, because eRank's markup has not been captured. Read the
table generically on the first run and add the selectors to this file when you have them.

## 4. Record the result

Append to the evidence table in `studio/research/etsy_keyword_evidence_<YYYYMMDD>.md`, or start a
new dated file for a new batch. Each row keeps four things: the phrase, the monthly searches, the
number of competing listings, and the date measured. Volume changes with the season, so an
undated number is worthless.

Then say what it means for the live listings. A phrase that measures 0 and sits in a live title is
a finding, not a note.

## 5. How to use the numbers

- **Title.** Lead with the highest-volume phrase that honestly describes the product. Etsy allows
  140 characters but warns above **14 words**. Stay at or under 14 words. Sizes belong in the
  variations, never in the title.
- **Tags.** All 13, each **20 characters or fewer**. A longer tag is dropped in silence and you
  ship 12.
- **Pin kickers.** The small-caps line on a pin is a search phrase too. Take it from the same
  evidence table.
- **Volume is not the only test.** A phrase with 18,652 competing listings and difficulty 100 is
  not winnable by a shop with two listings. Prefer a phrase with real volume and beatable
  competition over the largest number on the page.
