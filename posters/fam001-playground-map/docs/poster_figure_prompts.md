# Poster Figure Prompts — Childish Decorative Characters (FAM-001)

Prompts for generating **decorative figures/characters** (kids, animals, playground bits, corner
ornaments) to sprinkle onto a Playground Map poster and make it feel warmer and more childlike.

Each of the **6 styles** below maps 1:1 to an existing render theme in
[studio/themes](../../../studio/themes) so the generated art drops straight onto a matching poster:

| # | Figure style | Matching poster theme | Feel |
|---|---|---|---|
| 1 | Whimsy Hand-Drawn | `whimsy` | Warm cream, hand-illustrated — the **brand hero** |
| 2 | Crayon Box | `crayon` | Bright primary crayon on white, loud and happy |
| 3 | Dino Explorer | `dino` | Jungle-adventure, cute dinos, mint & safari orange |
| 4 | Bubblegum Pop | `bubblegum` | Candy/kawaii pastels, sparkles, girly-joyful |
| 5 | Meadow Storybook | `meadow` | Soft botanical, muted sage, gentle picture-book |
| 6 | Vintage Treasure Map | `vintage` | Aged sepia, ink-line, storybook adventure |

---

## How to use these

- **Model-agnostic.** Works with Midjourney, DALL·E 3, Ideogram, Flux, SDXL, etc. Paste
  `STYLE` + `IMAGE` together as one prompt.
- **Keep one style per poster.** Mixing styles breaks the "made just for them" look. Pick a style,
  generate its 5–7 figures, decorate a single poster with that set.
- **Keyable background — do NOT ask for "transparent".** Image models like Gemini can't write a
  real alpha channel; asking for "transparent" makes them *paint a fake checkerboard* that is
  actually opaque. Ask for a **plain solid single-colour background** that contrasts with the
  figure, then key it out to alpha afterward. Good contrast colours: solid white for dark or
  colourful figures; a solid mid-grey or vivid chroma (e.g. `#00B140` green) for light or
  cream-bordered figures.
- **Aspect ratio:** square (`1:1`) for characters; where noted, wide (`3:1`) for banners/borders.
- **No text.** Figures must contain **no words or letters** — the poster owns all typography.
- **Naming:** save as `assets/figures/<style>/<subject>.png` (e.g.
  `assets/figures/whimsy/child-on-swing.png`).

### Global technical suffix (already baked into every `STYLE` below)

> flat vector sticker illustration, bold clean rounded outlines, soft cel shading, single subject
> centered with generous safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters,
> no logo, no watermark, front-on storybook view, crisp edges, print-ready at 300 DPI

> **Licence note:** these figures are **original decorative art**, separate from the map data. The
> **ODbL "© OpenStreetMap contributors"** attribution still stays on the rendered map itself.

---

## Style 1 — Whimsy Hand-Drawn  *(theme: `whimsy` — brand hero)*

**Palette:** cream paper `#fbf6ea` · coral `#ef5a5a` · rose `#e0455f` · teal water `#9fd3e0` ·
leaf green `#bfe0a8` · warm brown ink `#4a3b2a`

**Shared STYLE token** *(reused verbatim in each prompt below):*
> Warm hand-illustrated children's-book character, wobbly hand-drawn ink outline in soft brown
> `#4a3b2a`, gentle gouache/crayon texture, cozy muted palette of cream `#fbf6ea`, coral `#ef5a5a`,
> rose `#e0455f`, teal `#9fd3e0` and leaf green `#bfe0a8`; rounded friendly shapes, flat sticker
> illustration, soft cel shading, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on storybook view, print-ready 300 DPI.

**1.1 — Child on a swing**
```
STYLE: Warm hand-illustrated children's-book character, wobbly hand-drawn ink outline in soft brown #4a3b2a, gentle gouache/crayon texture, cozy muted palette of cream #fbf6ea, coral #ef5a5a, rose #e0455f, teal #9fd3e0 and leaf green #bfe0a8; rounded friendly shapes, flat sticker illustration, soft cel shading, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on storybook view, print-ready 300 DPI.
IMAGE: a happy little child mid-swing on a wooden swing, hair and scarf flying back, legs kicked out, huge joyful smile, rosy cheeks.
```

**1.2 — Kid at the top of a slide**
```
STYLE: Warm hand-illustrated children's-book character, wobbly hand-drawn ink outline in soft brown #4a3b2a, gentle gouache/crayon texture, cozy muted palette of cream #fbf6ea, coral #ef5a5a, rose #e0455f, teal #9fd3e0 and leaf green #bfe0a8; rounded friendly shapes, flat sticker illustration, soft cel shading, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on storybook view, print-ready 300 DPI.
IMAGE: a small child at the top of a curly coral slide, both arms thrown up in the air, delighted open-mouth grin, about to whoosh down.
```

**1.3 — Toddler and parent walking hand in hand**
```
STYLE: Warm hand-illustrated children's-book character, wobbly hand-drawn ink outline in soft brown #4a3b2a, gentle gouache/crayon texture, cozy muted palette of cream #fbf6ea, coral #ef5a5a, rose #e0455f, teal #9fd3e0 and leaf green #bfe0a8; rounded friendly shapes, flat sticker illustration, soft cel shading, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on storybook view, print-ready 300 DPI.
IMAGE: a parent and a toddler walking hand in hand toward the playground, the toddler carrying a tiny red bucket, both smiling, gentle stride.
```

**1.4 — Friendly sun with rosy cheeks**
```
STYLE: Warm hand-illustrated children's-book character, wobbly hand-drawn ink outline in soft brown #4a3b2a, gentle gouache/crayon texture, cozy muted palette of cream #fbf6ea, coral #ef5a5a, rose #e0455f, teal #9fd3e0 and leaf green #bfe0a8; rounded friendly shapes, flat sticker illustration, soft cel shading, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on storybook view, print-ready 300 DPI.
IMAGE: a cheerful smiling sun with rosy cheeks, soft coral-and-cream wobbly rays, closed happy eyes.
```

**1.5 — Puffy cloud with a little bird**
```
STYLE: Warm hand-illustrated children's-book character, wobbly hand-drawn ink outline in soft brown #4a3b2a, gentle gouache/crayon texture, cozy muted palette of cream #fbf6ea, coral #ef5a5a, rose #e0455f, teal #9fd3e0 and leaf green #bfe0a8; rounded friendly shapes, flat sticker illustration, soft cel shading, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on storybook view, print-ready 300 DPI.
IMAGE: a soft rounded puffy cloud with a tiny coral songbird perched on top, a couple of little motion lines, calm and sweet.
```

**1.6 — Leafy tree with a kite in its branches**
```
STYLE: Warm hand-illustrated children's-book character, wobbly hand-drawn ink outline in soft brown #4a3b2a, gentle gouache/crayon texture, cozy muted palette of cream #fbf6ea, coral #ef5a5a, rose #e0455f, teal #9fd3e0 and leaf green #bfe0a8; rounded friendly shapes, flat sticker illustration, soft cel shading, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on storybook view, print-ready 300 DPI.
IMAGE: a round leafy green tree with a red diamond kite gently tangled in the top branches, string trailing down, playful and whimsical.
```

**1.7 — Flower-and-bush corner cluster** *(decorative, use aspect `3:2`)*
```
STYLE: Warm hand-illustrated children's-book character, wobbly hand-drawn ink outline in soft brown #4a3b2a, gentle gouache/crayon texture, cozy muted palette of cream #fbf6ea, coral #ef5a5a, rose #e0455f, teal #9fd3e0 and leaf green #bfe0a8; rounded friendly shapes, flat sticker illustration, soft cel shading, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on storybook view, print-ready 300 DPI.
IMAGE: a low decorative cluster of rounded bushes and simple coral and rose wildflowers, designed to sit along a bottom corner of a poster.
```

---

## Style 2 — Crayon Box  *(theme: `crayon`)*

**Palette:** white paper `#ffffff` · red `#e63946` · blue `#3f7fd4` · sun yellow `#ffd24d` ·
orange `#ff7a3d` · grass green `#8ed94f` · sky `#4fc3e8`

**Shared STYLE token:**
> Bright bold children's crayon-drawing character with a slightly waxy hand-colored texture and
> chunky rounded outlines, loud primary palette of red `#e63946`, blue `#3f7fd4`, sun-yellow
> `#ffd24d`, orange `#ff7a3d`, grass-green `#8ed94f` and sky-blue `#4fc3e8` on white; cheerful and
> energetic, flat sticker illustration, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on view, print-ready 300 DPI.

**2.1 — Two kids on a seesaw**
```
STYLE: Bright bold children's crayon-drawing character with a slightly waxy hand-colored texture and chunky rounded outlines, loud primary palette of red #e63946, blue #3f7fd4, sun-yellow #ffd24d, orange #ff7a3d, grass-green #8ed94f and sky-blue #4fc3e8 on white; cheerful and energetic, flat sticker illustration, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on view, print-ready 300 DPI.
IMAGE: two laughing kids balancing on a red-and-yellow seesaw, one up one down, arms out, big crayon smiles.
```

**2.2 — Kid building a sandcastle**
```
STYLE: Bright bold children's crayon-drawing character with a slightly waxy hand-colored texture and chunky rounded outlines, loud primary palette of red #e63946, blue #3f7fd4, sun-yellow #ffd24d, orange #ff7a3d, grass-green #8ed94f and sky-blue #4fc3e8 on white; cheerful and energetic, flat sticker illustration, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on view, print-ready 300 DPI.
IMAGE: a happy kid kneeling in a sandbox building a sandcastle, holding a blue bucket and red spade, little sand pile beside them.
```

**2.3 — Kid kicking a ball**
```
STYLE: Bright bold children's crayon-drawing character with a slightly waxy hand-colored texture and chunky rounded outlines, loud primary palette of red #e63946, blue #3f7fd4, sun-yellow #ffd24d, orange #ff7a3d, grass-green #8ed94f and sky-blue #4fc3e8 on white; cheerful and energetic, flat sticker illustration, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on view, print-ready 300 DPI.
IMAGE: an energetic child kicking a bouncy ball, one leg raised, motion lines, joyful expression.
```

**2.4 — Spinning roundabout**
```
STYLE: Bright bold children's crayon-drawing character with a slightly waxy hand-colored texture and chunky rounded outlines, loud primary palette of red #e63946, blue #3f7fd4, sun-yellow #ffd24d, orange #ff7a3d, grass-green #8ed94f and sky-blue #4fc3e8 on white; cheerful and energetic, flat sticker illustration, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on view, print-ready 300 DPI.
IMAGE: two kids gripping a colorful spinning playground roundabout, hair flying, spin motion swirls around them, laughing.
```

**2.5 — Big smiling sun**
```
STYLE: Bright bold children's crayon-drawing character with a slightly waxy hand-colored texture and chunky rounded outlines, loud primary palette of red #e63946, blue #3f7fd4, sun-yellow #ffd24d, orange #ff7a3d, grass-green #8ed94f and sky-blue #4fc3e8 on white; cheerful and energetic, flat sticker illustration, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on view, print-ready 300 DPI.
IMAGE: a big beaming sun with a wide crayon smile and thick yellow-and-orange spiky rays.
```

**2.6 — Cloud with a rainbow**
```
STYLE: Bright bold children's crayon-drawing character with a slightly waxy hand-colored texture and chunky rounded outlines, loud primary palette of red #e63946, blue #3f7fd4, sun-yellow #ffd24d, orange #ff7a3d, grass-green #8ed94f and sky-blue #4fc3e8 on white; cheerful and energetic, flat sticker illustration, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on view, print-ready 300 DPI.
IMAGE: a fluffy white cloud with a short bright crayon rainbow arcing out of it.
```

**2.7 — Puppy chasing a ball**
```
STYLE: Bright bold children's crayon-drawing character with a slightly waxy hand-colored texture and chunky rounded outlines, loud primary palette of red #e63946, blue #3f7fd4, sun-yellow #ffd24d, orange #ff7a3d, grass-green #8ed94f and sky-blue #4fc3e8 on white; cheerful and energetic, flat sticker illustration, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on view, print-ready 300 DPI.
IMAGE: a cheerful cartoon puppy running after a red ball, ears flapping, tongue out, tiny motion dust puffs.
```

---

## Style 3 — Dino Explorer  *(theme: `dino`)*

**Palette:** mint paper `#eefbef` · dino green `#2e9e57` · leaf `#6cc24a` · teal water `#37b6c9` ·
safari orange `#ff8c2b`

**Shared STYLE token:**
> Cute jungle-adventure cartoon character, friendly baby-dinosaur / safari style with rounded
> squishy shapes and clean bold outlines, bright outdoorsy palette of dino-green `#2e9e57`, leaf
> `#6cc24a`, teal `#37b6c9` and safari-orange `#ff8c2b` on mint; playful and adventurous, flat
> sticker illustration, soft cel shading, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on view, print-ready 300 DPI.

**3.1 — Waving baby T-rex**
```
STYLE: Cute jungle-adventure cartoon character, friendly baby-dinosaur / safari style with rounded squishy shapes and clean bold outlines, bright outdoorsy palette of dino-green #2e9e57, leaf #6cc24a, teal #37b6c9 and safari-orange #ff8c2b on mint; playful and adventurous, flat sticker illustration, soft cel shading, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on view, print-ready 300 DPI.
IMAGE: a chubby friendly baby green T-rex waving one tiny arm, big happy eyes, little rounded teeth, standing upright.
```

**3.2 — Brontosaurus peeking over a bush**
```
STYLE: Cute jungle-adventure cartoon character, friendly baby-dinosaur / safari style with rounded squishy shapes and clean bold outlines, bright outdoorsy palette of dino-green #2e9e57, leaf #6cc24a, teal #37b6c9 and safari-orange #ff8c2b on mint; playful and adventurous, flat sticker illustration, soft cel shading, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on view, print-ready 300 DPI.
IMAGE: a long-necked friendly brontosaurus peeking curiously over a rounded green bush, gentle smile.
```

**3.3 — Stegosaurus going down a slide**
```
STYLE: Cute jungle-adventure cartoon character, friendly baby-dinosaur / safari style with rounded squishy shapes and clean bold outlines, bright outdoorsy palette of dino-green #2e9e57, leaf #6cc24a, teal #37b6c9 and safari-orange #ff8c2b on mint; playful and adventurous, flat sticker illustration, soft cel shading, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on view, print-ready 300 DPI.
IMAGE: a happy little orange stegosaurus whooshing down an orange playground slide, back plates and tail up, delighted face.
```

**3.4 — Triceratops with a party hat**
```
STYLE: Cute jungle-adventure cartoon character, friendly baby-dinosaur / safari style with rounded squishy shapes and clean bold outlines, bright outdoorsy palette of dino-green #2e9e57, leaf #6cc24a, teal #37b6c9 and safari-orange #ff8c2b on mint; playful and adventurous, flat sticker illustration, soft cel shading, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on view, print-ready 300 DPI.
IMAGE: a small round triceratops wearing a striped party hat, cheerful grin, three little horns.
```

**3.5 — Jungle fern cluster**
```
STYLE: Cute jungle-adventure cartoon character, friendly baby-dinosaur / safari style with rounded squishy shapes and clean bold outlines, bright outdoorsy palette of dino-green #2e9e57, leaf #6cc24a, teal #37b6c9 and safari-orange #ff8c2b on mint; playful and adventurous, flat sticker illustration, soft cel shading, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on view, print-ready 300 DPI.
IMAGE: a decorative cluster of leafy jungle ferns and big rounded tropical leaves, for a bottom corner of a poster.
```

**3.6 — Little volcano with soft smoke**
```
STYLE: Cute jungle-adventure cartoon character, friendly baby-dinosaur / safari style with rounded squishy shapes and clean bold outlines, bright outdoorsy palette of dino-green #2e9e57, leaf #6cc24a, teal #37b6c9 and safari-orange #ff8c2b on mint; playful and adventurous, flat sticker illustration, soft cel shading, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on view, print-ready 300 DPI.
IMAGE: a friendly cartoon volcano with a soft orange glow and gentle rounded smoke puffs, not scary, storybook style.
```

**3.7 — Little explorer kid with binoculars**
```
STYLE: Cute jungle-adventure cartoon character, friendly baby-dinosaur / safari style with rounded squishy shapes and clean bold outlines, bright outdoorsy palette of dino-green #2e9e57, leaf #6cc24a, teal #37b6c9 and safari-orange #ff8c2b on mint; playful and adventurous, flat sticker illustration, soft cel shading, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on view, print-ready 300 DPI.
IMAGE: a small child in a safari hat holding binoculars up, on tiptoe as if spotting a dinosaur, excited expression.
```

---

## Style 4 — Bubblegum Pop  *(theme: `bubblegum`)*

**Palette:** pink paper `#fff0f6` · grape `#b45ce0` · hot pink `#ff5ea8` · turquoise `#7fe0e0` ·
lime `#b9ec8a`

**Shared STYLE token:**
> Adorable kawaii candy-pop character, glossy pastel style with rounded shapes, tiny sparkles and
> clean outlines, sugary palette of grape-purple `#b45ce0`, hot-pink `#ff5ea8`, turquoise `#7fe0e0`
> and lime `#b9ec8a` on pale pink; cute happy faces, flat sticker illustration, soft cel shading,
> single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no
> letters, no watermark, front-on view, print-ready 300 DPI.

**4.1 — Girl holding a bunch of balloons**
```
STYLE: Adorable kawaii candy-pop character, glossy pastel style with rounded shapes, tiny sparkles and clean outlines, sugary palette of grape-purple #b45ce0, hot-pink #ff5ea8, turquoise #7fe0e0 and lime #b9ec8a on pale pink; cute happy faces, flat sticker illustration, soft cel shading, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on view, print-ready 300 DPI.
IMAGE: a happy little girl holding a bunch of pink, purple and turquoise balloons floating above her, twirling skirt, big smile.
```

**4.2 — Kawaii ice-cream cone character**
```
STYLE: Adorable kawaii candy-pop character, glossy pastel style with rounded shapes, tiny sparkles and clean outlines, sugary palette of grape-purple #b45ce0, hot-pink #ff5ea8, turquoise #7fe0e0 and lime #b9ec8a on pale pink; cute happy faces, flat sticker illustration, soft cel shading, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on view, print-ready 300 DPI.
IMAGE: a cute ice-cream cone with a smiling face and rosy cheeks, two pastel scoops with a cherry on top, sparkles around it.
```

**4.3 — Kitten on a swing**
```
STYLE: Adorable kawaii candy-pop character, glossy pastel style with rounded shapes, tiny sparkles and clean outlines, sugary palette of grape-purple #b45ce0, hot-pink #ff5ea8, turquoise #7fe0e0 and lime #b9ec8a on pale pink; cute happy faces, flat sticker illustration, soft cel shading, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on view, print-ready 300 DPI.
IMAGE: a fluffy pastel kitten sitting on a little swing, paws holding the ropes, sweet blinking eyes, tail curled.
```

**4.4 — Rainbow with sparkles and a cloud**
```
STYLE: Adorable kawaii candy-pop character, glossy pastel style with rounded shapes, tiny sparkles and clean outlines, sugary palette of grape-purple #b45ce0, hot-pink #ff5ea8, turquoise #7fe0e0 and lime #b9ec8a on pale pink; cute happy faces, flat sticker illustration, soft cel shading, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on view, print-ready 300 DPI.
IMAGE: a pastel candy rainbow arcing from a smiling fluffy cloud, surrounded by little stars and sparkles.
```

**4.5 — Cute unicorn foal**
```
STYLE: Adorable kawaii candy-pop character, glossy pastel style with rounded shapes, tiny sparkles and clean outlines, sugary palette of grape-purple #b45ce0, hot-pink #ff5ea8, turquoise #7fe0e0 and lime #b9ec8a on pale pink; cute happy faces, flat sticker illustration, soft cel shading, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on view, print-ready 300 DPI.
IMAGE: a tiny chubby unicorn foal with a pastel-pink mane, small sparkly horn, hearts for eyes-shine, sitting happily.
```

**4.6 — Lollipop-and-candy trail**
```
STYLE: Adorable kawaii candy-pop character, glossy pastel style with rounded shapes, tiny sparkles and clean outlines, sugary palette of grape-purple #b45ce0, hot-pink #ff5ea8, turquoise #7fe0e0 and lime #b9ec8a on pale pink; cute happy faces, flat sticker illustration, soft cel shading, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on view, print-ready 300 DPI.
IMAGE: a decorative row of swirly lollipops, wrapped candies and a gumdrop, forming a sweet little bottom-border trail.
```

**4.7 — Confetti of stars and hearts**
```
STYLE: Adorable kawaii candy-pop character, glossy pastel style with rounded shapes, tiny sparkles and clean outlines, sugary palette of grape-purple #b45ce0, hot-pink #ff5ea8, turquoise #7fe0e0 and lime #b9ec8a on pale pink; cute happy faces, flat sticker illustration, soft cel shading, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on view, print-ready 300 DPI.
IMAGE: a scattered confetti cluster of little pastel stars, hearts and sparkles, as a decorative accent element.
```

---

## Style 5 — Meadow Storybook  *(theme: `meadow`)*

**Palette:** cream paper `#f4f1e8` · forest green `#5f7a4d` · sage `#cdddb8` · dusty teal `#bcd0cf` ·
terracotta `#c26b4f`

**Shared STYLE token:**
> Soft botanical picture-book illustration, gentle watercolor / gouache texture with delicate
> outlines and calm muted tones, palette of forest-green `#5f7a4d`, sage `#cdddb8`, dusty-teal
> `#bcd0cf` and warm terracotta `#c26b4f` on cream; cozy, understated and sweet, flat sticker
> illustration, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no
> text, no letters, no watermark, front-on view, print-ready 300 DPI.

**5.1 — Child picking wildflowers**
```
STYLE: Soft botanical picture-book illustration, gentle watercolor / gouache texture with delicate outlines and calm muted tones, palette of forest-green #5f7a4d, sage #cdddb8, dusty-teal #bcd0cf and warm terracotta #c26b4f on cream; cozy, understated and sweet, flat sticker illustration, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on view, print-ready 300 DPI.
IMAGE: a gentle child crouched in the grass picking a small bunch of wildflowers, soft calm smile.
```

**5.2 — Little fox sitting in the grass**
```
STYLE: Soft botanical picture-book illustration, gentle watercolor / gouache texture with delicate outlines and calm muted tones, palette of forest-green #5f7a4d, sage #cdddb8, dusty-teal #bcd0cf and warm terracotta #c26b4f on cream; cozy, understated and sweet, flat sticker illustration, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on view, print-ready 300 DPI.
IMAGE: a small terracotta fox sitting curled in a tuft of sage grass, fluffy tail wrapped around, calm friendly eyes.
```

**5.3 — Rabbit with a picnic basket**
```
STYLE: Soft botanical picture-book illustration, gentle watercolor / gouache texture with delicate outlines and calm muted tones, palette of forest-green #5f7a4d, sage #cdddb8, dusty-teal #bcd0cf and warm terracotta #c26b4f on cream; cozy, understated and sweet, flat sticker illustration, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on view, print-ready 300 DPI.
IMAGE: a soft little rabbit standing upright carrying a small woven picnic basket, gentle smile, ears up.
```

**5.4 — Songbird on a branch**
```
STYLE: Soft botanical picture-book illustration, gentle watercolor / gouache texture with delicate outlines and calm muted tones, palette of forest-green #5f7a4d, sage #cdddb8, dusty-teal #bcd0cf and warm terracotta #c26b4f on cream; cozy, understated and sweet, flat sticker illustration, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on view, print-ready 300 DPI.
IMAGE: a small round songbird perched on a slender leafy branch, a few soft leaves, peaceful pose.
```

**5.5 — Wildflower and fern sprig** *(border accent)*
```
STYLE: Soft botanical picture-book illustration, gentle watercolor / gouache texture with delicate outlines and calm muted tones, palette of forest-green #5f7a4d, sage #cdddb8, dusty-teal #bcd0cf and warm terracotta #c26b4f on cream; cozy, understated and sweet, flat sticker illustration, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on view, print-ready 300 DPI.
IMAGE: a delicate sprig of wildflowers and a curling fern frond, designed as a light corner or border accent.
```

**5.6 — Gentle sun behind soft clouds**
```
STYLE: Soft botanical picture-book illustration, gentle watercolor / gouache texture with delicate outlines and calm muted tones, palette of forest-green #5f7a4d, sage #cdddb8, dusty-teal #bcd0cf and warm terracotta #c26b4f on cream; cozy, understated and sweet, flat sticker illustration, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on view, print-ready 300 DPI.
IMAGE: a soft muted sun peeking gently from behind two calm rounded clouds, warm and quiet mood.
```

**5.7 — Wooden swing hanging from a tree branch**
```
STYLE: Soft botanical picture-book illustration, gentle watercolor / gouache texture with delicate outlines and calm muted tones, palette of forest-green #5f7a4d, sage #cdddb8, dusty-teal #bcd0cf and warm terracotta #c26b4f on cream; cozy, understated and sweet, flat sticker illustration, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, front-on view, print-ready 300 DPI.
IMAGE: a simple wooden plank swing hanging by two ropes from a leafy tree branch, a couple of soft leaves falling.
```

---

## Style 6 — Vintage Treasure Map  *(theme: `vintage`)*

**Palette:** parchment `#efe6d0` · sepia ink `#5c3a1e` · rust red `#a6432a` · faded olive `#d3cfa0` ·
muted teal-green water `#bcc9b0`

**Shared STYLE token:**
> Old storybook treasure-map illustration, hand-inked engraving / woodcut line style with fine
> cross-hatching on aged parchment, muted antique palette of sepia-ink `#5c3a1e`, rust-red
> `#a6432a`, faded-olive `#d3cfa0` and muted teal-green `#bcc9b0`; nostalgic and adventurous but
> kid-friendly, flat illustration, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, print-ready 300 DPI.

**6.1 — Compass rose** *(corner ornament)*
```
STYLE: Old storybook treasure-map illustration, hand-inked engraving / woodcut line style with fine cross-hatching on aged parchment, muted antique palette of sepia-ink #5c3a1e, rust-red #a6432a, faded-olive #d3cfa0 and muted teal-green #bcc9b0; nostalgic and adventurous but kid-friendly, flat illustration, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, print-ready 300 DPI.
IMAGE: an ornate antique compass rose with pointed star directions and decorative flourishes, symmetrical, no lettering.
```

**6.2 — Friendly sea/park monster peeking**
```
STYLE: Old storybook treasure-map illustration, hand-inked engraving / woodcut line style with fine cross-hatching on aged parchment, muted antique palette of sepia-ink #5c3a1e, rust-red #a6432a, faded-olive #d3cfa0 and muted teal-green #bcc9b0; nostalgic and adventurous but kid-friendly, flat illustration, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, print-ready 300 DPI.
IMAGE: a friendly cartoon sea-monster with big googly eyes and a curly tail peeking up as on an old map, playful not scary.
```

**6.3 — Little sailing paper boat**
```
STYLE: Old storybook treasure-map illustration, hand-inked engraving / woodcut line style with fine cross-hatching on aged parchment, muted antique palette of sepia-ink #5c3a1e, rust-red #a6432a, faded-olive #d3cfa0 and muted teal-green #bcc9b0; nostalgic and adventurous but kid-friendly, flat illustration, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, print-ready 300 DPI.
IMAGE: a small folded paper boat riding a couple of gentle inked waves, with a tiny rust-red flag, storybook charm.
```

**6.4 — Old-fashioned kid with a pinwheel**
```
STYLE: Old storybook treasure-map illustration, hand-inked engraving / woodcut line style with fine cross-hatching on aged parchment, muted antique palette of sepia-ink #5c3a1e, rust-red #a6432a, faded-olive #d3cfa0 and muted teal-green #bcc9b0; nostalgic and adventurous but kid-friendly, flat illustration, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, print-ready 300 DPI.
IMAGE: a cheerful old-fashioned child in dungarees running while holding a spinning pinwheel, gentle motion lines.
```

**6.5 — Blank ribbon banner scroll** *(for a title, aspect `3:1`)*
```
STYLE: Old storybook treasure-map illustration, hand-inked engraving / woodcut line style with fine cross-hatching on aged parchment, muted antique palette of sepia-ink #5c3a1e, rust-red #a6432a, faded-olive #d3cfa0 and muted teal-green #bcc9b0; nostalgic and adventurous but kid-friendly, flat illustration, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, print-ready 300 DPI.
IMAGE: an empty decorative ribbon banner scroll with curled ends, blank interior left clear for a title to be placed later.
```

**6.6 — Engraved decorative tree**
```
STYLE: Old storybook treasure-map illustration, hand-inked engraving / woodcut line style with fine cross-hatching on aged parchment, muted antique palette of sepia-ink #5c3a1e, rust-red #a6432a, faded-olive #d3cfa0 and muted teal-green #bcc9b0; nostalgic and adventurous but kid-friendly, flat illustration, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, print-ready 300 DPI.
IMAGE: a single stylized engraving-style tree with a round crown and fine hatched shading, as an old-map decoration.
```

**6.7 — "X marks the spot" flag on footprints**
```
STYLE: Old storybook treasure-map illustration, hand-inked engraving / woodcut line style with fine cross-hatching on aged parchment, muted antique palette of sepia-ink #5c3a1e, rust-red #a6432a, faded-olive #d3cfa0 and muted teal-green #bcc9b0; nostalgic and adventurous but kid-friendly, flat illustration, single subject centered with safe padding, isolated on a plain solid single-colour background (flat even colour, no checkerboard, no gradient, no scenery, no shadow), no text, no letters, no watermark, print-ready 300 DPI.
IMAGE: a small rust-red flag planted on a bold X, with a short dashed trail of little footprints leading up to it.
```

---

### Quick prompt-tuning tips

- **Too clip-arty?** add *"hand-painted texture, subtle paper grain, slightly imperfect line."*
- **Colors drifting?** repeat the exact hex codes and add *"strict limited palette, no other colors."*
- **Background not clean?** add *"plain solid flat single-colour background, no checkerboard, no
  scenery, no ground shadow"*. Never ask Gemini for "transparent" — it paints a fake
  checkerboard of opaque pixels instead of writing real alpha.
- **Want a matched set?** generate all figures for one style in a single session / seed so line
  weight and proportions stay consistent.
