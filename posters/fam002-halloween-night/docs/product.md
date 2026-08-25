# FAM-002 — Halloween night sheet, print at home

Build note for backlog item BL-012. Written on 2026-08-17. Split into its own product on
2026-08-19.

This was first built as `--variant halloween` inside FAM-001. It is now its own product directory.
It shares the street map (`posterlab.map`), the page furniture (`posterlab.chrome`) and the studio
art style (`studio/themes/`); it fetches no playgrounds of its own.

---

## What the product is

A parent buys a digital file. The parent prints the file at home on A4 paper or US Letter paper.
The parent gives the sheet to the child before the trick-or-treat walk. The child fills in the
sheet during the night or after the night.

The map shows the streets and the houses around one address. The child's own house carries a
marker.

### The rule that must never break

The sheet never says which houses give treats. The sheet never says which houses take part. The
sheet never says which houses are safe. Nobody can know any of that before the evening. A neighbour
decides it on the night, and the only signal is a porch light.

This rule holds in the listing copy, on the printed sheet, and in the download notes. Break the
rule and you create a refund risk and a review risk.

Nextdoor has run a crowd-sourced Treat Map for 13 years, for free. It wins on live data. This
product does not compete there. This product competes on the object the child keeps afterwards.

---

## What was built

| File | Purpose |
|---|---|
| `posters/fam002-halloween-night/make.py` | Entry point. Geocodes, fetches streets and buildings, saves the run |
| `posters/fam002-halloween-night/render.py` | Composes the panel sheet. Delegates the four bleed sheets to `layouts.py` |
| `posters/fam002-halloween-night/panel.py` | The framed sheet: the log panel and the how-to note |
| `posters/fam002-halloween-night/layouts.py` | The four full-bleed sheets. See [`layouts.md`](layouts.md) |
| `posters/fam002-halloween-night/sheet_text.py` | Every printed string, shared by both renderers |
| `posterlab/map/overpass.py` | The opt-in `buildings` layer, the classifier entry, and the radius cap |
| `posterlab/map/body.py` | Draws the building footprints under the roads |
| `studio/themes/lantern.json` | New theme. See *Themes* below |
| `studio/themes/ink.json`, `studio/themes/nocturne.json` | Added `buildings` and `buildings_edge` colours |

Buildings are **off by default** in the shared fetcher. FAM-001 renders exactly as before, and every
cache key of an existing run is unchanged, so no old run refetches from Overpass.

### The panel

The panel is one of five layouts, and it is the default. The other four bleed the map to the paper
edge; see [`layouts.md`](layouts.md). `--layout` selects one, or `all`.


The sheet carries five things to fill in.

1. A `Costume` line.
2. A `We walked with` line.
3. A treat tally of 40 boxes to colour.
4. A drawing box for the best costume the child saw.
5. A `The house we liked best` line.

A legend shows the same home glyph that the map draws.

---

## How to run it

```
uv run python posters/fam002-halloween-night/make.py \
    --address "<street, city, state>" --radius 400 \
    --theme lantern --size A4 --layout panel \
    --title "<Name> Halloween Night" --night "31 October 2026" --preview
```

The buildings layer is always on for this product — the sheet cannot be drawn without it. Render the
same run again for the second paper size. This costs no network call.

```
uv run python posters/fam002-halloween-night/render.py --run latest \
    --theme lantern --size Letter --preview
```

---

## The radius decision

A home printer takes A4 paper or US Letter paper. On A4 the map frame is about 184 mm wide. A house
is about 10 m wide.

| Radius | Sheet shows | A house prints at | Buildings fetched | Result |
|---|---|---|---|---|
| 400 m | 800 m across | 2.3 mm | 873 | Houses a child can mark |
| 2000 m | 4000 m across | 0.45 mm | 9333 | Grey mush |

Both versions were rendered from real data for the same address. Compare
`brand/samples/halloween_boise_400m_lantern_A4.png` against
`brand/samples/halloween_boise_2000m_lantern_A4.png`.

**The 2000 m version fails.** The houses merge into one grey mass. A child cannot mark a single
house. The sheet also stops looking like a neighbourhood and starts looking like a city map, which
is a different product.

The 2000 m fetch is also the proof for the cap. It took about 10 minutes. Two Overpass mirrors
returned a 504 timeout before a third answered. That is the load this cap exists to prevent.

**The default radius is 400 m.** The cap is 1000 m, and `basemap.check_buildings_radius` enforces
it. Two reasons hold the cap.

1. Above 1000 m the houses stop reading as houses.
2. A building query over a large box is heavy for a public Overpass endpoint.

Pass `--allow-wide-buildings` to lift the cap. Use it only for a comparison render.

A trick-or-treat walk covers a few blocks. It does not cover 3 km. The small radius matches the real
night.

---

## Themes

`lantern` is the new Halloween theme. It starts from `nocturne`. It keeps the Spectral serif, the
violet-grey road hierarchy, and the studio page furniture. It changes one thing. The accent moves
from gold to one warm amber, and that amber marks the home.

The theme is **not** orange and black clip art. Operating Principle 4 makes the single art style the
moat. A clip-art sheet would read as a dropshipper.

### The ink problem

`lantern` covers the whole sheet in a dark colour. A home inkjet prints that badly. It costs a lot
of ink. It wets plain paper. It bands.

The same sheet renders in `ink`, the light studio theme, and that version prints well at home. Both
versions were rendered for the same address.

**Recommendation.** Sell both files in one download. Make `ink` the file the buyer sees first. Show
`lantern` as the screen version and as the listing hero image. Say in the listing which file suits a
home printer.

---

## What was measured

Address, picked at random in the United States: **West Hillcrest Drive, Boise, Idaho**.
Home point 43.58278 N, 116.23407 W.

| Test | Radius | Buildings | Result | Sample file |
|---|---|---|---|---|
| United States suburb, `lantern` | 400 m | 873 | Houses read at 2.3 mm. Streets and river read | `halloween_boise_400m_lantern_A4.png` |
| Same sheet, `ink` (light) | 400 m | 873 | The version that prints well at home | `halloween_boise_400m_ink_A4.png` |
| Rural town, Ovacik, Tunceli, Turkey | 400 m | 267 | Sparse and older data. Sheet still looks finished | — |
| Same Boise data, buildings removed | 400 m | 0 | Sheet still looks finished. Degrades to a street map | `halloween_boise_400m_zero_buildings.png` |
| Wide comparison | 2000 m | 9333 | Grey mush. Rejected | `halloween_boise_2000m_lantern_A4.png` |

The sample files are in `posters/fam002-halloween-night/brand/samples/`. They are tracked, because the
2000 m fetch is slow and heavy and nobody should repeat it.

Both page orientations were rendered. The panel packs the 40 tally boxes as 10 by 4 in portrait and
20 by 2 in landscape, and the drawing box keeps its space in both.

The zero-building test proves work item 3. OpenStreetMap building coverage changes by country and by
street. The render must never look broken when a box holds no buildings. It does not. The renderer
prints a warning to the operator, and the sheet degrades to a clean street map with the home marked.

---

## What is not built

This list is the work left before the product can go live.

1. The Etsy listing. No listing exists. No listing was published.
2. The price. The plan says 6 to 9 United States dollars.
3. The listing photos and the mockups.
4. The keyword evidence. Measure the Halloween terms in eRank before you write a title.
5. The digital download bundle. `--zip` writes the correct how-to text, but no bundle was shipped.

---

## Timing

Halloween searches rise through September. A listing that goes live after 2026-10-20 earns no
ranking history before the peak.

**Stop rule.** If the listing slips past 2026-09-20, hold the idea for 2027.

---

## Why it can repeat

The value arrives after the walk. The filled sheet becomes the record of one night. A parent can buy
it again every year, with a new year and a new costume on it. Nextdoor cannot hold that part.

---

Map data © OpenStreetMap contributors, ODbL. The attribution prints on every sheet.
