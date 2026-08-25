# Halloween sheet layouts — build note (FAM-002)

Four full-bleed halloween layouts are added beside the existing panel sheet. The
`_cut.png` art in `studio/themes/lantern/` is embedded into the render as
decoration.

    band    solid title band top, all writing in a footer band
    sheet   map to all four edges, title and fields on scrims
    ledger  map full bleed, writing in a right-hand column
    bonus   no map — the spotting game, tally and drawing box

`bonus` is independent by design. It carries no sheet numbering. It pairs with
any map layout, or it sells alone. This was a deliberate change from the first
comps. The first comps numbered it "2 of 2" and locked it to one bundle.

## Files

| file | action |
| --- | --- |
| `posters/fam002-halloween-night/layouts.py` | the four bleed sheets |
| `posters/fam002-halloween-night/render.py` | composes `panel`, delegates the rest |
| `posters/fam002-halloween-night/make.py` | passes `--layout` through |
| `posters/fam002-halloween-night/dashboard.json` | the layout select |
| `studio/themes/lantern.json` | adds a `decor` block |
| `studio/themes/ink.json` | adds the same `decor` block |

The `decor` block names the folder under `studio/themes/` that holds the
`*_cut.png` files:

```json
  "decor": {
    "dir": "lantern"
  },
```

Both themes point at the same folder. The cut-outs are dark-bodied silhouettes.
They read on cream as well as on plum. A second tinted set would be two sets to
maintain for no visible gain.

## How the render splits

`render.compose_panel` composes the framed sheet, because it uses the shop's
shared page furniture. Every other layout delegates to `layouts.compose`.
`render` still draws the map body, because the map is the part that must not be
duplicated. `layouts` never imports `render`, so there is no cycle.

`render_run` renders one file per layout. The file name carries the layout, for
example `..._A4_ledger_portrait.pdf`.

## Rendering

```bash
# one sheet
uv run python posters/fam002-halloween-night/render.py --run latest \
    --layout ledger --theme lantern --size A4 \
    --night "31 October 2026" --title "Hillcrest Halloween" --preview

# the kit: a map sheet plus the bonus game, both themes, A4 + Letter
uv run python posters/fam002-halloween-night/render.py --run latest \
    --theme lantern,ink --layout sheet,bonus --size A4,Letter \
    --night "31 October 2026" --title "Hillcrest Halloween" --zip
```

`--theme`, `--layout` and `--size` each take one name, `all`, or a
comma-separated list. One call renders every combination and writes **one** ZIP
that holds all of them. Render a kit in one call. A loop of one-sheet calls
rebuilds the ZIP each time, and the buyer gets the last sheet only.

`--layout all` renders the panel sheet and all four bleed layouts in one pass.

## Type is fitted, not fixed

Every heading in the comps was transcribed as a fixed fraction of the page. That
fraction only holds for the string the comp showed. The first render of a real
address pushed the title, the meta line, the ledger heading and the spotting-grid
captions off the paper.

`layouts._fit` now returns the largest size at or below the declared
size that keeps a line inside its box. `_fit_all` returns one size for a block of
lines, so a heading does not change size between its own lines. The estimate uses
average glyph advance, the same method as `posterlab.chrome.title_block`.
cairosvg gives no text metrics, so an estimate is the only option. The ratios are
0.66 for upper case and 0.53 for mixed case. Both were measured off this renderer
at the theme font stack, then rounded up so the estimate never under-reports a
width.

Two placements also moved:

- The bonus hint sits a fixed gap above the spotting grid. It used to hang off
  the title height, which put it inside the first row of boxes.
- The ledger memory field is lifted clear of the cat cut-out. On the shorter
  Letter page the two collided.

## Notes and open items

- **Art is embedded, not linked.** Each `_cut.png` goes into the SVG as a base64
  data URI. An exported PDF is one portable file, and cairosvg needs no
  `--unsafe` path resolution. A sheet's file size tracks its art. The four-piece
  bonus sheet is the heaviest.
- **`_cut` files only.** The unsuffixed siblings still carry their own background
  plate. They would print as a grey rectangle over the map.
- **Two pieces are unused.** `drip-banner` buries the title at page width. Its
  drips fall a third of the header height. `witch-hat` on the bonus sheet lands
  under the spotting grid. Both stay in the folder. They want a layout with space
  reserved for them, not a nudge.
- **Ledger framing.** The map is projected into the clear half of the page and
  clipped to the full sheet. It still bleeds under the column, and home stays
  framed where you can see it. Projection into the whole page put the home glyph
  behind the writing lines about half the time.
- **`--orientation landscape` is untested on these four.** The band and footer
  fractions are tuned for portrait. On a landscape page the footer band takes a
  third of the sheet. This needs either a landscape set of fractions or an
  explicit refusal.
- **Letter and A4 both compose.** All geometry is page fractions. Both sizes were
  rendered in both themes.
