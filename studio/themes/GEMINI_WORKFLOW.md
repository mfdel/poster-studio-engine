# Gemini Figure-Generation Workflow (FAM-001 poster figures)

How to generate the decorative poster figures in
[`docs/poster_figure_prompts.md`](../../docs/poster_figure_prompts.md) using Gemini's built-in
image model, driven through the **Playwright browser MCP**, and save each one under its theme folder
in `studio/themes/<theme>/`.

> **Looking for the general method?** The reusable, project-agnostic version of this workflow —
> getting a browser at all, signing in, switching Gemini into image mode, detecting completion,
> downloading the full-size render, and writing automation that survives UI drift — lives in
> [`.github/skills/gemini-image-generation/SKILL.md`](../../.github/skills/gemini-image-generation/SKILL.md).
> **This** document is the FAM-001 application of it: the poster-figure prompts, theme folders and
> subject slugs.

Two things make this workflow specific:

1. **Prompts are self-contained.** Each figure prompt already embeds the complete `STYLE` token +
   `IMAGE` line, so there is **no reference image to attach** and no name-stripping to do. Just paste
   the prompt. *(If you adapt this loop to prompts that DO need a reference image — e.g. the listing
   photos in [`brand/gemini-photo-prompts.md`](../../brand/gemini-photo-prompts.md) — attach the
   reference with `mcp__playwright__browser_file_upload` before sending the prompt; everything else in
   the loop is identical.)*
2. **Gemini runs an A/B "Which response is more helpful?" experiment** on some image turns. When it
   appears, pick **Choice A** ("This response is more helpful") to collapse to a single image, then
   extract. When it doesn't appear, extract directly.

---

## Prerequisite — the Playwright browser MCP must be connected

This whole workflow drives a real browser (type into Gemini, read the page, download the finished
image). **Those tools are not built into Claude Code** — they come from a **Playwright MCP server**
that must be registered *for this project* and loaded at session start.

**Check it's available.** `claude mcp list` should show `playwright` as `✔ Connected`, and the
`mcp__playwright__*` tools should be present in the session.

**If it's missing.** MCP servers are scoped to the directory Claude Code was launched in, so a server
registered in another project (e.g. a parent workspace) will **not** load while you're in
`playground-map`. Register it, then relaunch:

```
claude mcp add playwright -s user -- playwright-mcp   # -s user = available in every project
claude mcp list                                        # confirm ✔ Connected
```

Then **restart the Claude Code session** — MCP servers only initialize at startup, so a freshly added
server won't appear in the running session until you relaunch.

**Login caveat.** The Playwright MCP drives its **own** browser profile, which is *not* your everyday
signed-in Chrome. Gemini requires a Google login, so on a fresh profile you'll hit the sign-in wall.
Sign in once inside the MCP-controlled browser (navigate to the Google sign-in page, type the
credentials, skip the optional "recovery info" / "home address" prompts) and the persistent profile
remembers you for later runs.

**The Playwright tools this workflow uses:**

| Step | Tool |
|---|---|
| Open a page / start a fresh thread | `mcp__playwright__browser_navigate` |
| Read the page (get element refs) | `mcp__playwright__browser_snapshot` |
| Type + submit a prompt | `mcp__playwright__browser_type` (`submit: true`) |
| Click a button (A/B choice, download, menu) | `mcp__playwright__browser_click` |
| Attach a reference image (only if a prompt needs one) | `mcp__playwright__browser_file_upload` |
| Wait for generation | `mcp__playwright__browser_wait_for` (`time`) |
| Inspect image sizes / DOM | `mcp__playwright__browser_evaluate` |

Downloads land in the MCP output directory **`.playwright-mcp/`** (relative to the launch dir).

---

## 0. Session facts (fill in per run)

- Page: `https://gemini.google.com/app` (already signed in as the user).
- **Image model:** turn on the **Create image** tool from the **+** ("Upload & tools") menu — the
  composer then reads *"Create with Nano Banana …"*, Gemini's built-in image model. Selecting the
  **Pro** text model in the mode picker routes image generation to the higher-quality image model;
  use Pro when you want the best output. (The first time you attach a file, Gemini shows a one-time
  "Creating content from images and files" disclaimer — click **Agree**.)
- One **fresh chat thread per theme** — navigate to `https://gemini.google.com/app` to start one.
  Prompts are self-contained, so a fresh thread per theme just keeps things tidy.

---

## 1. Per-figure loop

For each figure in the theme's section of `docs/poster_figure_prompts.md`:

### 1a. Send the prompt
Type the figure's **full prompt** (the whole `STYLE: … IMAGE: …` block) into the prompt textbox and
submit. Prefix with `Generate a single image. ` and join it to **one line** (no hard newlines — a
newline can submit the prompt early). Example call:

```
browser_type(target=<textbox ref>, submit=true,
  text="Generate a single image. STYLE: … IMAGE: …")
```

### 1b. Wait for generation
Generation takes ~10–30 s. Call `browser_wait_for(time: 15)`, then re-read. Do **not** poll in a
tight loop — read, and if still generating, read again. A quick `browser_evaluate` that counts images
with `alt === ', AI generated'` and checks for a "Creating" spinner is a reliable "is it done?" probe:

```js
() => {
  const gen = Array.from(document.querySelectorAll('img')).filter(i => i.alt === ', AI generated');
  const stillGenerating = /Creating|Generating/.test(document.body.innerText);
  return { count: gen.length, stillGenerating };
}
```

### 1c. Resolve the A/B experiment (only if it appears)
If the page shows **Choice A / Choice B**, click **"This response is more helpful"** under **Choice
A**. A toast "Selected preferred response" confirms it collapsed to a single image. If there is no
A/B panel, skip this step.

### 1d. Download the FULL-SIZE image — do NOT read it off a `<canvas>`

Click the **"Download full size image"** button on the finished image (`browser_click` on its ref).
The Playwright browser saves the file into **`.playwright-mcp/`** (e.g.
`Gemini-Generated-Image-xxxx.png`).

> **The full-size-image problem.** Gemini loads a **downscaled preview** blob into the on-screen
> `<img>`: its `naturalWidth`/`naturalHeight` are only ~**89 %** of the true render (observed
> **825 × 1024** on screen vs **928 × 1152** full size — identical 4:5 aspect, just scaled down).
> Reading pixels off that `<img>` through a `<canvas>` therefore captures the **smaller preview, not
> the original**. The **"Download full size image"** button fetches the real full-resolution asset,
> and in the Playwright MCP browser that download **succeeds** (some embedded browsers CORS-fail on
> it — this one does not). **Always prefer the download.**

If several images already exist in the thread, there will be several "Download full size image"
buttons — click the **last** one (the newest image), then take the **newest PNG in `.playwright-mcp/`
by modification time**; that's the one you just downloaded.

**Canvas → base64 fallback** — use only if the download is genuinely blocked, and accept that it
yields the *downscaled preview*, not full size. Read the image off a `<canvas>` and decode with
[`studio/assets/save_b64_png.py`](../assets/save_b64_png.py):

```js
const b64 = await page.evaluate(() => {
  const img = Array.from(document.querySelectorAll('img'))
    .find(i => i.alt === ', AI generated' && i.src.startsWith('blob:') && i.naturalWidth > 200);
  if (!img) return 'NO_IMG';
  const c = document.createElement('canvas');
  c.width = img.naturalWidth; c.height = img.naturalHeight;
  c.getContext('2d').drawImage(img, 0, 0);
  return c.toDataURL('image/png').split(',')[1];
});
return b64;
```

### 1e. Save to the theme folder
Move/rename the downloaded PNG to the correct name:

```
mv ".playwright-mcp/<downloaded>.png" studio/themes/<theme>/<subject>.png
```

Then **verify the saved size is the full render** (e.g. `928 × 1152`), not the `825 × 1024` preview:

```
python3 -c "from PIL import Image; print(Image.open('studio/themes/<theme>/<subject>.png').size)"
```

*(If you used the canvas fallback instead, decode the resource file:
`python studio/assets/save_b64_png.py "<resource_file>" studio/themes/<theme>/<subject>.png` —
`save_b64_png.py` finds the PNG base64 by its magic prefix and validates the signature before
writing.)*

### 1f. Strip the sparkle watermark (locally)
Every Gemini render carries a four-pointed **sparkle watermark** in its bottom-right corner. Remove
it with the local script — it inverts the white alpha composite exactly, so the texture underneath is
recovered rather than painted over, and **nothing is uploaded anywhere**:

```
python studio/assets/dewatermark_gemini.py studio/themes/<theme> -o studio/themes/<theme>/clean
python studio/assets/dewatermark_gemini.py <dir> --check    # report glyph presence, write nothing
```

Zero pixels change outside the glyph's 54 × 54 footprint, and already-clean files are refused rather
than corrupted. **This only works on the full-size `928 × 1152` render** — the geometry is calibrated
to it, so a `825 × 1024` canvas-fallback preview (§1d) is skipped as "no glyph detected". That's
another reason to prefer the download over the canvas.

See [`.github/skills/gemini-dewatermark/SKILL.md`](../../.github/skills/gemini-dewatermark/SKILL.md)
for the solved glyph geometry, how to verify a batch, why online watermark removers must not be used,
and the hard line at SynthID.

### 1g. Next figure
Send the next figure's prompt in the **same thread**. Repeat until all figures for the theme are
saved.

---

## 2. Naming (subject slugs)

Save each figure as `studio/themes/<theme>/<subject>.png` using these slugs:

| Theme | Figures (slugs) |
|---|---|
| `whimsy` | child-on-swing, kid-top-of-slide, toddler-parent-walking, friendly-sun, cloud-with-bird, tree-with-kite, flower-bush-corner |
| `crayon` | two-kids-seesaw, kid-sandcastle, kid-kicking-ball, spinning-roundabout, big-smiling-sun, cloud-rainbow, puppy-chasing-ball |
| `dino` | waving-baby-trex, brontosaurus-bush, stegosaurus-slide, triceratops-party-hat, jungle-fern-cluster, little-volcano, explorer-kid-binoculars |
| `bubblegum` | girl-balloons, ice-cream-character, kitten-swing, rainbow-sparkles-cloud, unicorn-foal, lollipop-candy-trail, star-heart-confetti |
| `meadow` | child-picking-wildflowers, fox-in-grass, rabbit-picnic-basket, songbird-branch, wildflower-fern-sprig, gentle-sun-clouds, wooden-swing-branch |
| `vintage` | compass-rose, sea-monster-peeking, paper-boat, kid-with-pinwheel, ribbon-banner-scroll, engraved-tree, x-marks-the-spot |

(These map 1:1 and in order to the numbered prompts `N.1 … N.7` in `docs/poster_figure_prompts.md`.)

---

## 3. After a theme is done

Cut the figures out of their solid background to transparent PNGs (per the repo's figure pipeline):

```
python studio/assets/cutout_figures.py studio/themes/<theme>
```

Writes `<name>_cut.png` next to each raw figure. (See `docs/poster_figure_prompts.md` — never prompt
Gemini for "transparent"; it paints a fake checkerboard.)

---

## 4. Gotchas / what NOT to do

- **Use "Download full size image", not the canvas, for the real resolution.** The on-screen `<img>`
  is a downscaled preview (~89 % linear); a canvas read captures only that. The download button gives
  the true full-size render and works in the Playwright MCP browser. Reserve the canvas → base64 route
  for the rare case where the download is blocked, and know it's lower-res.
- **With multiple images in a thread, click the *last* download button** and take the **newest**
  `.playwright-mcp/` PNG by mtime — don't grab a stale earlier file.
- **Don't paste multi-line prompts.** A hard newline in the textbox can submit early. One line.
- **Don't skip the A/B check.** If Choice A/B is present and you extract without resolving it, you may
  grab the wrong/empty image. Resolve to a single image first.
- **Don't ask for "transparent".** Prompts already ask for a plain solid single-colour background; the
  cutout script keys it out. (Gemini paints a fake checkerboard if asked for transparency.)
- **Don't leave the sparkle watermark on, and don't upload renders to a watermark-removal site.**
  Use `studio/assets/dewatermark_gemini.py` (§1f) — it's local and lossless. Sites that offer this
  were checked: at least one claims "files never leave your browser" while actually POSTing them to a
  server and returning the result from a third-party Google Cloud bucket. Nothing about the visible
  glyph needs an upload.
- Keep the OSM ODbL attribution on the *map* (not these figures) — figures are original art.
