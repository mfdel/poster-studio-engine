# Halloween Figure Prompts — FAM-002 night sheet

Prompts for the decorative Halloween figures that sit in the margins of the print-at-home
trick-or-treat sheet. See [`product.md`](product.md) for the product.

These figures are ornaments. They are not map data and they are not markers.

---

## The rule that must never break

A figure must never sit on a house, or point at a house, or touch a house. A figure must never
suggest that a house gives treats. A figure must never suggest that a house is safe. That data does
not exist. Read the rule in [`product.md`](product.md).

Keep every figure in the outer margin or beside the fill-in panel. Keep the map frame clean, because
the child marks houses inside it. Keep the ODbL attribution line clear.

---

## Where the figures go

| Slot | Aspect | Good subjects |
|---|---|---|
| Top corners | `1:1` | Bats, moon, cobweb, witch hat |
| Bottom corners | `1:1` or `3:2` | Pumpkin, cat, gravestones, lantern |
| Bottom edge band | `3:1` | Pumpkin row, candy scatter, drip band |
| Side rail beside the panel | `2:3` or `1:2` | Bare tree, spider on a thread, skeleton |

Use **4 to 6 figures per sheet**. More figures make the sheet busy and cost more ink.

---

## Two style tokens, one per theme

The sheet ships in two themes. `lantern` is the dark screen version and the listing hero. `ink` is
the light version that a home printer handles well. A figure drawn for one theme fails on the other.

Generate the set you need. Use the same subject list for both.

**Token A — `lantern` (dark sheet)**

> Hand-illustrated Halloween ornament in a warm storybook style, wobbly hand-inked outline in pale
> bone `#f4ece1` (the stroke itself is bone coloured, never dark), flat matte gouache fill with a
> faint paper grain, night palette of deep plum `#171220`, dusk violet `#372c46` and lilac grey
> `#93849f`, with one warm lantern amber `#eb8f3c` reserved for glowing light only. No gloss, no
> gradient shading, and a background that stays perfectly flat and untextured.

**Token B — `ink` (light sheet, print at home)**

> Hand-illustrated Halloween ornament in a warm storybook style, wobbly hand-drawn ink outline in
> near-black ink `#26231d`, soft flat gouache fill on warm off-white `#f6f3ec`, soft graphite grey
> `#8a8578` for shading and one warm ochre accent `#b98a3c` used sparingly, sparse open linework
> that saves printer ink.

Every numbered prompt below embeds **Token A** in full, so you can paste one block and send it. To
make the `ink` version of the same figure, replace the colour clause with Token B and keep the rest
of the `STYLE` line word for word.

---

## Rules baked into every prompt

- **No orange-and-black clip art.** Operating Principle 4 makes the one art style the moat. The
  figures must read as the same shop as the playground map.
- **No text.** No words, letters or numbers. The sheet owns all typography.
- **Cute, not gory.** The buyer is a parent of a small child. Keep the spook gentle.
- **Keyable background, never "transparent".** The model cannot write an alpha channel. It paints a
  fake checkerboard instead. Ask for flat chroma green `#00B140`, then key it out with
  `studio/assets/cutout_figures.py`.
- **Single subject, centered, generous padding.** The cutout step crops to the figure.

---

## How to generate and save

The whole set was generated this way on 2026-08-18. Repeat these steps for the `ink` set.

1. Start the browser once. It keeps a signed-in Chrome on CDP port 9333.

```
.github/skills/gemini-image-generation/cli/gemini-gen ensure
```

2. Build a manifest of `{prompt, out}` items from the prompts below. Each `out` is
   `studio/themes/lantern/<slug>.png`. Add the aspect sentence to the prompt: `Square 1:1
   composition.`, `Wide 16:9 composition.` or `Tall 9:16 composition.`
3. Generate the set. The `pro` model returns 2048x2048, 2752x1536 or 1536x2752.

```
.github/skills/gemini-image-generation/cli/gemini-gen batch --manifest board.json --model pro --no-clean
```

4. Check the bottom-right corner of one render for a watermark. The `pro` renders of 2026-08-18
   carried none, so the batch ran with `--no-clean`. If a mark is present, remove it with
   [`.github/skills/dewatermark-stills/`](../../../.github/skills/dewatermark-stills/SKILL.md) and
   the profile for that exact resolution. Never upload a render to a watermark-removal website.
5. Cut the green background out to alpha. `--key-enclosed` is required here: the plain flood fill
   keeps green that the art encloses, which leaves the cells of the cobweb, the gap under the pail
   handle and the space between the fence pickets filled.

```
uv run python studio/assets/cutout_figures.py studio/themes/lantern/<slug>.png \
    --pad 16 --key-enclosed --tolerance 60
```

Each cut figure is written beside its source as `<slug>_cut.png`. **Use the `_cut.png` files on the
sheet.** The source PNG keeps the flat green background.

> **Licence note.** These figures are original decorative art. They are separate from the map data.
> The **© OpenStreetMap contributors, ODbL** attribution stays on the rendered sheet.

---

## The 20 prompts

### 1 — Bat trio in flight → `bats-corner-trio` · `1:1`
```
STYLE: Hand-illustrated Halloween ornament in a warm storybook style, wobbly hand-inked outline in pale bone #f4ece1 — the outline stroke itself is bone coloured, never dark — flat matte gouache fill with a faint paper grain, night palette of deep plum #171220, dusk violet #372c46 and lilac grey #93849f, with one warm lantern amber #eb8f3c reserved for glowing light only; rounded friendly shapes, gentle spook, cute and never gory, no blood, no realistic horror; flat matte picture-book illustration, no gloss, no shine, no specular highlights, no gradient shading, no drop shadow, single subject centered with generous safe padding, isolated on a plain solid single-colour background (flat even chroma green #00B140, no checkerboard, no gradient, no scenery, no cast shadow), no text, no letters, no numbers, no logo, no watermark, front-on storybook view, crisp edges, print-ready 300 DPI. The background must stay perfectly smooth, flat and untextured: the paper grain and the brush texture appear only inside the subject. The subject is drawn art, not a die-cut sticker: no extra cream or white band tracing the outer silhouette, no sticker cut line.
IMAGE: three small round bats flying in a loose diagonal cluster, scalloped wings, big friendly eyes, tiny fangs, one bat smaller and trailing behind, arranged to tuck into a top corner.
```

### 2 — Bat hanging from a twig → `bat-hanging` · `2:3`
```
STYLE: Hand-illustrated Halloween ornament in a warm storybook style, wobbly hand-inked outline in pale bone #f4ece1 — the outline stroke itself is bone coloured, never dark — flat matte gouache fill with a faint paper grain, night palette of deep plum #171220, dusk violet #372c46 and lilac grey #93849f, with one warm lantern amber #eb8f3c reserved for glowing light only; rounded friendly shapes, gentle spook, cute and never gory, no blood, no realistic horror; flat matte picture-book illustration, no gloss, no shine, no specular highlights, no gradient shading, no drop shadow, single subject centered with generous safe padding, isolated on a plain solid single-colour background (flat even chroma green #00B140, no checkerboard, no gradient, no scenery, no cast shadow), no text, no letters, no numbers, no logo, no watermark, front-on storybook view, crisp edges, print-ready 300 DPI. The background must stay perfectly smooth, flat and untextured: the paper grain and the brush texture appear only inside the subject. The subject is drawn art, not a die-cut sticker: no extra cream or white band tracing the outer silhouette, no sticker cut line.
IMAGE: one plump bat hanging upside down from a short bare twig, wings folded around itself like a cloak, one round eye open and one closed, sleepy and sweet.
```

### 3 — Floating sheet ghost → `ghost-floating` · `1:1`
```
STYLE: Hand-illustrated Halloween ornament in a warm storybook style, wobbly hand-inked outline in pale bone #f4ece1 — the outline stroke itself is bone coloured, never dark — flat matte gouache fill with a faint paper grain, night palette of deep plum #171220, dusk violet #372c46 and lilac grey #93849f, with one warm lantern amber #eb8f3c reserved for glowing light only; rounded friendly shapes, gentle spook, cute and never gory, no blood, no realistic horror; flat matte picture-book illustration, no gloss, no shine, no specular highlights, no gradient shading, no drop shadow, single subject centered with generous safe padding, isolated on a plain solid single-colour background (flat even chroma green #00B140, no checkerboard, no gradient, no scenery, no cast shadow), no text, no letters, no numbers, no logo, no watermark, front-on storybook view, crisp edges, print-ready 300 DPI. The background must stay perfectly smooth, flat and untextured: the paper grain and the brush texture appear only inside the subject. The subject is drawn art, not a die-cut sticker: no extra cream or white band tracing the outer silhouette, no sticker cut line.
IMAGE: a rounded sheet ghost floating with a wobbly scalloped hem, two soft dark eyes and a small open mouth, tiny stub arms lifted in a friendly boo, a faint warm amber glow inside the fabric.
```

### 4 — Ghosts peeking over an edge → `ghost-trio-peek` · `3:2`
```
STYLE: Hand-illustrated Halloween ornament in a warm storybook style, wobbly hand-inked outline in pale bone #f4ece1 — the outline stroke itself is bone coloured, never dark — flat matte gouache fill with a faint paper grain, night palette of deep plum #171220, dusk violet #372c46 and lilac grey #93849f, with one warm lantern amber #eb8f3c reserved for glowing light only; rounded friendly shapes, gentle spook, cute and never gory, no blood, no realistic horror; flat matte picture-book illustration, no gloss, no shine, no specular highlights, no gradient shading, no drop shadow, single subject centered with generous safe padding, isolated on a plain solid single-colour background (flat even chroma green #00B140, no checkerboard, no gradient, no scenery, no cast shadow), no text, no letters, no numbers, no logo, no watermark, front-on storybook view, crisp edges, print-ready 300 DPI. The background must stay perfectly smooth, flat and untextured: the paper grain and the brush texture appear only inside the subject. The subject is drawn art, not a die-cut sticker: no extra cream or white band tracing the outer silhouette, no sticker cut line.
IMAGE: three small ghosts of different heights peeking up over a straight horizontal ledge, only heads and little gripping hands visible, curious wide eyes, designed to sit on the top edge of a panel.
```

### 5 — Carved jack-o-lantern → `jack-o-lantern` · `1:1`
```
STYLE: Hand-illustrated Halloween ornament in a warm storybook style, wobbly hand-inked outline in pale bone #f4ece1 — the outline stroke itself is bone coloured, never dark — flat matte gouache fill with a faint paper grain, night palette of deep plum #171220, dusk violet #372c46 and lilac grey #93849f, with one warm lantern amber #eb8f3c reserved for glowing light only; rounded friendly shapes, gentle spook, cute and never gory, no blood, no realistic horror; flat matte picture-book illustration, no gloss, no shine, no specular highlights, no gradient shading, no drop shadow, single subject centered with generous safe padding, isolated on a plain solid single-colour background (flat even chroma green #00B140, no checkerboard, no gradient, no scenery, no cast shadow), no text, no letters, no numbers, no logo, no watermark, front-on storybook view, crisp edges, print-ready 300 DPI. The background must stay perfectly smooth, flat and untextured: the paper grain and the brush texture appear only inside the subject. The subject is drawn art, not a die-cut sticker: no extra cream or white band tracing the outer silhouette, no sticker cut line.
IMAGE: a squat carved pumpkin with a crooked friendly grin and two triangle eyes, warm amber candlelight pouring out of the carved shapes, a curled stem and one leaf, ribbed skin drawn in plum and violet.
```

### 6 — Pumpkin row for the bottom edge → `pumpkin-row` · `3:1`
```
STYLE: Hand-illustrated Halloween ornament in a warm storybook style, wobbly hand-inked outline in pale bone #f4ece1 — the outline stroke itself is bone coloured, never dark — flat matte gouache fill with a faint paper grain, night palette of deep plum #171220, dusk violet #372c46 and lilac grey #93849f, with one warm lantern amber #eb8f3c reserved for glowing light only; rounded friendly shapes, gentle spook, cute and never gory, no blood, no realistic horror; flat matte picture-book illustration, no gloss, no shine, no specular highlights, no gradient shading, no drop shadow, arranged as a wide horizontal band with generous safe padding, isolated on a plain solid single-colour background (flat even chroma green #00B140, no checkerboard, no gradient, no scenery, no cast shadow), no text, no letters, no numbers, no logo, no watermark, front-on storybook view, crisp edges, print-ready 300 DPI. The background must stay perfectly smooth, flat and untextured: the paper grain and the brush texture appear only inside the subject. The subject is drawn art, not a die-cut sticker: no extra cream or white band tracing the outer silhouette, no sticker cut line.
IMAGE: a low horizontal row of five pumpkins of different sizes sitting in a tangle of curling vines and broad leaves, two of them carved and glowing amber, the others plain, built to run along the bottom edge of a sheet.
```

### 7 — Arched black cat → `black-cat-arched` · `1:1`
```
STYLE: Hand-illustrated Halloween ornament in a warm storybook style, wobbly hand-inked outline in pale bone #f4ece1 — the outline stroke itself is bone coloured, never dark — flat matte gouache fill with a faint paper grain, night palette of deep plum #171220, dusk violet #372c46 and lilac grey #93849f, with one warm lantern amber #eb8f3c reserved for glowing light only; rounded friendly shapes, gentle spook, cute and never gory, no blood, no realistic horror; flat matte picture-book illustration, no gloss, no shine, no specular highlights, no gradient shading, no drop shadow, single subject centered with generous safe padding, isolated on a plain solid single-colour background (flat even chroma green #00B140, no checkerboard, no gradient, no scenery, no cast shadow), no text, no letters, no numbers, no logo, no watermark, front-on storybook view, crisp edges, print-ready 300 DPI. The background must stay perfectly smooth, flat and untextured: the paper grain and the brush texture appear only inside the subject. The subject is drawn art, not a die-cut sticker: no extra cream or white band tracing the outer silhouette, no sticker cut line.
IMAGE: a small black cat with an arched back and a bottlebrush tail held high, round amber eyes, whiskers, one paw lifted, playful rather than frightening.
```

### 8 — Cat on a fence post → `cat-on-fence` · `3:2`
```
STYLE: Hand-illustrated Halloween ornament in a warm storybook style, wobbly hand-inked outline in pale bone #f4ece1 — the outline stroke itself is bone coloured, never dark — flat matte gouache fill with a faint paper grain, night palette of deep plum #171220, dusk violet #372c46 and lilac grey #93849f, with one warm lantern amber #eb8f3c reserved for glowing light only; rounded friendly shapes, gentle spook, cute and never gory, no blood, no realistic horror; flat matte picture-book illustration, no gloss, no shine, no specular highlights, no gradient shading, no drop shadow, single subject centered with generous safe padding, isolated on a plain solid single-colour background (flat even chroma green #00B140, no checkerboard, no gradient, no scenery, no cast shadow), no text, no letters, no numbers, no logo, no watermark, front-on storybook view, crisp edges, print-ready 300 DPI. The background must stay perfectly smooth, flat and untextured: the paper grain and the brush texture appear only inside the subject. The subject is drawn art, not a die-cut sticker: no extra cream or white band tracing the outer silhouette, no sticker cut line.
IMAGE: a rounded cat sitting on top of a short picket fence section, tail curled around its paws, amber eyes, two loose pickets leaning, a few blades of grass at the base, no house and no building in view.
```

### 9 — Spider on a thread → `spider-drop` · `1:2`
```
STYLE: Hand-illustrated Halloween ornament in a warm storybook style, wobbly hand-inked outline in pale bone #f4ece1 — the outline stroke itself is bone coloured, never dark — flat matte gouache fill with a faint paper grain, night palette of deep plum #171220, dusk violet #372c46 and lilac grey #93849f, with one warm lantern amber #eb8f3c reserved for glowing light only; rounded friendly shapes, gentle spook, cute and never gory, no blood, no realistic horror; flat matte picture-book illustration, no gloss, no shine, no specular highlights, no gradient shading, no drop shadow, single subject centered with generous safe padding, isolated on a plain solid single-colour background (flat even chroma green #00B140, no checkerboard, no gradient, no scenery, no cast shadow), no text, no letters, no numbers, no logo, no watermark, front-on storybook view, crisp edges, print-ready 300 DPI. The background must stay perfectly smooth, flat and untextured: the paper grain and the brush texture appear only inside the subject. The subject is drawn art, not a die-cut sticker: no extra cream or white band tracing the outer silhouette, no sticker cut line.
IMAGE: a small round spider hanging on one long straight silk thread that runs from the very top of the frame, eight short bent legs, four little eyes, a shy smile, plenty of empty thread above it.
```

### 10 — Cobweb corner → `cobweb-corner` · `1:1`
```
STYLE: Hand-illustrated Halloween ornament in a warm storybook style, wobbly hand-inked outline in pale bone #f4ece1 — the outline stroke itself is bone coloured, never dark — flat matte gouache fill with a faint paper grain, night palette of deep plum #171220, dusk violet #372c46 and lilac grey #93849f, with one warm lantern amber #eb8f3c reserved for glowing light only; rounded friendly shapes, gentle spook, cute and never gory, no blood, no realistic horror; flat matte picture-book illustration, no gloss, no shine, no specular highlights, no gradient shading, no drop shadow, single subject centered with generous safe padding, isolated on a plain solid single-colour background (flat even chroma green #00B140, no checkerboard, no gradient, no scenery, no cast shadow), no text, no letters, no numbers, no logo, no watermark, front-on storybook view, crisp edges, print-ready 300 DPI. The background must stay perfectly smooth, flat and untextured: the paper grain and the brush texture appear only inside the subject. The subject is drawn art, not a die-cut sticker: no extra cream or white band tracing the outer silhouette, no sticker cut line.
IMAGE: a quarter-circle spider web anchored into one corner, uneven hand-drawn radial threads and four sagging rings, a few tiny dew beads, one very small spider resting near the anchor point.
```

### 11 — Sleepy crescent moon → `crescent-moon` · `1:1`
```
STYLE: Hand-illustrated Halloween ornament in a warm storybook style, wobbly hand-inked outline in pale bone #f4ece1 — the outline stroke itself is bone coloured, never dark — flat matte gouache fill with a faint paper grain, night palette of deep plum #171220, dusk violet #372c46 and lilac grey #93849f, with one warm lantern amber #eb8f3c reserved for glowing light only; rounded friendly shapes, gentle spook, cute and never gory, no blood, no realistic horror; flat matte picture-book illustration, no gloss, no shine, no specular highlights, no gradient shading, no drop shadow, single subject centered with generous safe padding, isolated on a plain solid single-colour background (flat even chroma green #00B140, no checkerboard, no gradient, no scenery, no cast shadow), no text, no letters, no numbers, no logo, no watermark, front-on storybook view, crisp edges, print-ready 300 DPI. The background must stay perfectly smooth, flat and untextured: the paper grain and the brush texture appear only inside the subject. The subject is drawn art, not a die-cut sticker: no extra cream or white band tracing the outer silhouette, no sticker cut line.
IMAGE: a fat crescent moon in warm amber with a closed sleepy eye and a small smile, one thin wisp of violet cloud crossing its lower horn, three tiny four-point stars around it.
```

### 12 — Bare crooked tree → `bare-tree-bats` · `2:3`
```
STYLE: Hand-illustrated Halloween ornament in a warm storybook style, wobbly hand-inked outline in pale bone #f4ece1 — the outline stroke itself is bone coloured, never dark — flat matte gouache fill with a faint paper grain, night palette of deep plum #171220, dusk violet #372c46 and lilac grey #93849f, with one warm lantern amber #eb8f3c reserved for glowing light only; rounded friendly shapes, gentle spook, cute and never gory, no blood, no realistic horror; flat matte picture-book illustration, no gloss, no shine, no specular highlights, no gradient shading, no drop shadow, single subject centered with generous safe padding, isolated on a plain solid single-colour background (flat even chroma green #00B140, no checkerboard, no gradient, no scenery, no cast shadow), no text, no letters, no numbers, no logo, no watermark, front-on storybook view, crisp edges, print-ready 300 DPI. The background must stay perfectly smooth, flat and untextured: the paper grain and the brush texture appear only inside the subject. The subject is drawn art, not a die-cut sticker: no extra cream or white band tracing the outer silhouette, no sticker cut line.
IMAGE: a tall crooked bare tree with twisting branches and a knobbly trunk, one small round hollow glowing amber, two little bats flying away from the top branches, a few loose leaves falling.
```

### 13 — Trick-or-treat pail → `candy-pail` · `1:1`
```
STYLE: Hand-illustrated Halloween ornament in a warm storybook style, wobbly hand-inked outline in pale bone #f4ece1 — the outline stroke itself is bone coloured, never dark — flat matte gouache fill with a faint paper grain, night palette of deep plum #171220, dusk violet #372c46 and lilac grey #93849f, with one warm lantern amber #eb8f3c reserved for glowing light only; rounded friendly shapes, gentle spook, cute and never gory, no blood, no realistic horror; flat matte picture-book illustration, no gloss, no shine, no specular highlights, no gradient shading, no drop shadow, single subject centered with generous safe padding, isolated on a plain solid single-colour background (flat even chroma green #00B140, no checkerboard, no gradient, no scenery, no cast shadow), no text, no letters, no numbers, no logo, no watermark, front-on storybook view, crisp edges, print-ready 300 DPI. The background must stay perfectly smooth, flat and untextured: the paper grain and the brush texture appear only inside the subject. The subject is drawn art, not a die-cut sticker: no extra cream or white band tracing the outer silhouette, no sticker cut line.
IMAGE: a round pumpkin-shaped trick-or-treat pail with a simple carved face and a sturdy handle, heaped and overflowing with wrapped sweets, one lollipop stick poking out, two sweets tumbling beside it.
```

### 14 — Loose sweets scatter → `candy-scatter` · `3:1`
```
STYLE: Hand-illustrated Halloween ornament in a warm storybook style, wobbly hand-inked outline in pale bone #f4ece1 — the outline stroke itself is bone coloured, never dark — flat matte gouache fill with a faint paper grain, night palette of deep plum #171220, dusk violet #372c46 and lilac grey #93849f, with one warm lantern amber #eb8f3c reserved for glowing light only; rounded friendly shapes, gentle spook, cute and never gory, no blood, no realistic horror; flat matte picture-book illustration, no gloss, no shine, no specular highlights, no gradient shading, no drop shadow, several small objects spread evenly across a wide horizontal band with generous safe padding, isolated on a plain solid single-colour background (flat even chroma green #00B140, no checkerboard, no gradient, no scenery, no cast shadow), no text, no letters, no numbers, no logo, no watermark, front-on storybook view, crisp edges, print-ready 300 DPI. The background must stay perfectly smooth, flat and untextured: the paper grain and the brush texture appear only inside the subject. The subject is drawn art, not a die-cut sticker: no extra cream or white band tracing the outer silhouette, no sticker cut line.
IMAGE: a loose scattered row of small sweets seen from above, twist-wrapped toffees, a round lollipop, a striped candy stick, two candy corn kernels and a small plain chocolate bar, spaced apart with clear gaps between them.
```

### 15 — Owl on a branch → `owl-on-branch` · `1:1`
```
STYLE: Hand-illustrated Halloween ornament in a warm storybook style, wobbly hand-inked outline in pale bone #f4ece1 — the outline stroke itself is bone coloured, never dark — flat matte gouache fill with a faint paper grain, night palette of deep plum #171220, dusk violet #372c46 and lilac grey #93849f, with one warm lantern amber #eb8f3c reserved for glowing light only; rounded friendly shapes, gentle spook, cute and never gory, no blood, no realistic horror; flat matte picture-book illustration, no gloss, no shine, no specular highlights, no gradient shading, no drop shadow, single subject centered with generous safe padding, isolated on a plain solid single-colour background (flat even chroma green #00B140, no checkerboard, no gradient, no scenery, no cast shadow), no text, no letters, no numbers, no logo, no watermark, front-on storybook view, crisp edges, print-ready 300 DPI. The background must stay perfectly smooth, flat and untextured: the paper grain and the brush texture appear only inside the subject. The subject is drawn art, not a die-cut sticker: no extra cream or white band tracing the outer silhouette, no sticker cut line.
IMAGE: a round fluffy owl perched on a short bare branch, huge amber eyes, two feather tufts, a small hooked beak, patterned chest feathers, head tilted slightly.
```

### 16 — Witch hat with moths → `witch-hat` · `1:1`
```
STYLE: Hand-illustrated Halloween ornament in a warm storybook style, wobbly hand-inked outline in pale bone #f4ece1 — the outline stroke itself is bone coloured, never dark — flat matte gouache fill with a faint paper grain, night palette of deep plum #171220, dusk violet #372c46 and lilac grey #93849f, with one warm lantern amber #eb8f3c reserved for glowing light only; rounded friendly shapes, gentle spook, cute and never gory, no blood, no realistic horror; flat matte picture-book illustration, no gloss, no shine, no specular highlights, no gradient shading, no drop shadow, single subject centered with generous safe padding, isolated on a plain solid single-colour background (flat even chroma green #00B140, no checkerboard, no gradient, no scenery, no cast shadow), no text, no letters, no numbers, no logo, no watermark, front-on storybook view, crisp edges, print-ready 300 DPI. The background must stay perfectly smooth, flat and untextured: the paper grain and the brush texture appear only inside the subject. The subject is drawn art, not a die-cut sticker: no extra cream or white band tracing the outer silhouette, no sticker cut line.
IMAGE: a tall pointed witch hat with a wide floppy brim and a bent tip, a simple band with a square buckle, resting at a slight lean, one small pale moth on the tip and one on the brim.
```

### 17 — Friendly skeleton waving → `skeleton-wave` · `2:3`
```
STYLE: Hand-illustrated Halloween ornament in a warm storybook style, wobbly hand-inked outline in pale bone #f4ece1 — the outline stroke itself is bone coloured, never dark — flat matte gouache fill with a faint paper grain, night palette of deep plum #171220, dusk violet #372c46 and lilac grey #93849f, with one warm lantern amber #eb8f3c reserved for glowing light only; rounded friendly shapes, gentle spook, cute and never gory, no blood, no realistic horror, no wounds; flat matte picture-book illustration, no gloss, no shine, no specular highlights, no gradient shading, no drop shadow, single subject centered with generous safe padding, isolated on a plain solid single-colour background (flat even chroma green #00B140, no checkerboard, no gradient, no scenery, no cast shadow), no text, no letters, no numbers, no logo, no watermark, front-on storybook view, crisp edges, print-ready 300 DPI. The background must stay perfectly smooth, flat and untextured: the paper grain and the brush texture appear only inside the subject. The subject is drawn art, not a die-cut sticker: no extra cream or white band tracing the outer silhouette, no sticker cut line.
IMAGE: a short cheerful cartoon skeleton standing and waving one hand, rounded chunky bones, a friendly wide grin, big dark eye sockets with tiny highlights, slightly wonky ribs, clearly cute and harmless.
```

### 18 — Gravestone cluster → `gravestones` · `3:2`
```
STYLE: Hand-illustrated Halloween ornament in a warm storybook style, wobbly hand-inked outline in pale bone #f4ece1 — the outline stroke itself is bone coloured, never dark — flat matte gouache fill with a faint paper grain, night palette of deep plum #171220, dusk violet #372c46 and lilac grey #93849f, with one warm lantern amber #eb8f3c reserved for glowing light only; rounded friendly shapes, gentle spook, cute and never gory, no blood, no realistic horror; flat matte picture-book illustration, no gloss, no shine, no specular highlights, no gradient shading, no drop shadow, single subject centered with generous safe padding, isolated on a plain solid single-colour background (flat even chroma green #00B140, no checkerboard, no gradient, no scenery, no cast shadow), no text, no letters, no numbers, no logo, no watermark, front-on storybook view, crisp edges, print-ready 300 DPI. The background must stay perfectly smooth, flat and untextured: the paper grain and the brush texture appear only inside the subject. The subject is drawn art, not a die-cut sticker: no extra cream or white band tracing the outer silhouette, no sticker cut line.
IMAGE: a cluster of three leaning rounded gravestones with completely blank faces and no carving, tufts of grass at their base, one small pumpkin in front, a low curl of mist, storybook and gentle.
```

### 19 — Storm lantern → `lantern-glow` · `1:1`
```
STYLE: Hand-illustrated Halloween ornament in a warm storybook style, wobbly hand-inked outline in pale bone #f4ece1 — the outline stroke itself is bone coloured, never dark — flat matte gouache fill with a faint paper grain, night palette of deep plum #171220, dusk violet #372c46 and lilac grey #93849f, with one warm lantern amber #eb8f3c reserved for glowing light only; rounded friendly shapes, gentle spook, cute and never gory, no blood, no realistic horror; flat matte picture-book illustration, no gloss, no shine, no specular highlights, no gradient shading, no drop shadow, single subject centered with generous safe padding, isolated on a plain solid single-colour background (flat even chroma green #00B140, no checkerboard, no gradient, no scenery, no cast shadow), no text, no letters, no numbers, no logo, no watermark, front-on storybook view, crisp edges, print-ready 300 DPI. The background must stay perfectly smooth, flat and untextured: the paper grain and the brush texture appear only inside the subject. The subject is drawn art, not a die-cut sticker: no extra cream or white band tracing the outer silhouette, no sticker cut line.
IMAGE: an old hand-held storm lantern with a wire carry handle and a glass chamber holding one warm amber flame, soft short glow rays around the glass, a little soot on the cap, standing upright.
```

### 20 — Drip band for a top edge → `drip-banner` · `3:1`
```
STYLE: Hand-illustrated Halloween ornament in a warm storybook style, wobbly hand-inked outline in pale bone #f4ece1 — the outline stroke itself is bone coloured, never dark — flat matte gouache fill with a faint paper grain, night palette of deep plum #171220, dusk violet #372c46 and lilac grey #93849f, with one warm lantern amber #eb8f3c reserved for glowing light only; rounded friendly shapes, gentle spook, cute and never gory, no blood, no realistic horror; flat matte picture-book illustration, no gloss, no shine, no specular highlights, no gradient shading, no drop shadow, arranged as a wide horizontal band with generous safe padding, isolated on a plain solid single-colour background (flat even chroma green #00B140, no checkerboard, no gradient, no scenery, no cast shadow), no text, no letters, no numbers, no logo, no watermark, front-on storybook view, crisp edges, print-ready 300 DPI. The background must stay perfectly smooth, flat and untextured: the paper grain and the brush texture appear only inside the subject. The subject is drawn art, not a die-cut sticker: no extra cream or white band tracing the outer silhouette, no sticker cut line.
IMAGE: a solid horizontal band along the top with slow thick candle-wax drips of uneven length hanging below it, a few drips ending in a round bead, one drip catching a warm amber highlight, built to run edge to edge.
```

---

## The blood question

You asked for blood. This prompt set gives you the drip shape without the gore, in prompt 20.

Two reasons hold that choice.

1. The buyer is a parent who prints the sheet for a small child. Gore breaks that promise and it
   raises the refund risk and the review risk.
2. Etsy restricts mature content. A gory thumbnail can also lose the listing its reach.

If you still want the literal read, change one clause in prompt 20. Replace `candle-wax drips` with
`dark red drips in deep oxblood #7a1f1f` and delete `no blood` from the `STYLE` line. Keep it in the
margin. Do not put it on the map frame, and do not use it as the listing thumbnail.
