---
name: gemini-image-generation
description: USE FOR driving a real browser to generate images with Gemini (Nano Banana / Imagen) as an AI agent — there is no public image API in this setup, so the web UI is the interface. Covers getting a browser at all (Playwright MCP, and the fallback when its profile is locked), signing in, switching Gemini into image mode, sending a prompt, detecting when generation finished, resolving the A/B "which response is more helpful" experiment, and downloading the FULL-SIZE render instead of the ~89% on-screen preview. Triggered by "generate an image with Gemini", "generate the stills", "make images in the browser", "drive Gemini", "Nano Banana", "browser automation for image generation", "the image came out too small".
---

# Generating Images with Gemini Through a Browser

Gemini's image model is reachable here only through its **web UI**, so generating an image means
driving a real browser: type a prompt, wait, resolve whatever interstitial appears, download the
result. In this repo that's how episode stills get made before they reach
`make_capcut_draft.py`.

**The one rule that matters most:** the on-screen image is a **downscaled preview**. Reading pixels
off it silently gives you a smaller image than the model made. Always click download.
See [§5](#5-download-the-full-size-render-not-the-preview).

---

## Fast path: the `cli/` tool (use this first)

Most of the time you should **not** drive the browser click-by-click from the agent loop — it
burns tokens and is flaky. [`cli/gemini-gen`](cli/README.md) scripts the whole §1–§5 flow behind a
few commands; the agent calls one per image (or one per *batch*) and reads back a single JSON line.
It keeps a **detached, persistent Chrome** on CDP port 9333, so runs reconnect to the same
signed-in window.

```bash
cd .github/skills/gemini-image-generation/cli
./gemini-gen ensure                                   # first run: sign into Google in the window
./gemini-gen gen --prompt "…, 16:9, no text." --out episodes/XXX_slug/assets/beat01.png
./gemini-gen batch --manifest board.json              # many images; shared --ref uploads once
```

`batch` clusters consecutive manifest items that share a `ref` set into one thread, so a reference
image uploads **once** and thread context carries it (which also aids consistency). Output is
verified full-size (**1376×768** for 16:9) and dimensions come back in the JSON. On failure it
stops and prints `{ok:false, stage, completed, lastDone, screenshot}`. Full docs and the manifest
schema: [`cli/README.md`](cli/README.md).

Drive the browser by hand (the rest of this doc) only when the CLI can't — a UI change it hasn't
caught up to, a new interstitial, or a one-off probe. When a selector drifts, `./gemini-gen recon`
dumps the page's interactive elements and a screenshot to re-lock it.

---

## 1. Get a browser

Two routes, in order of preference. Details and a working script scaffold:
[browser-setup.md](browser-setup.md).

1. **Playwright MCP** (`mcp__playwright__*`). Preferred when connected — the tools are interactive,
   so you can look at the page and decide what to do next. Confirm with `claude mcp list` showing
   `playwright` as `✔ Connected`. MCP servers are scoped to the launch directory and initialize only
   at session start, so one registered in another project won't load, and a freshly added one needs a
   session restart.
2. **Scripted `playwright-core`** when MCP is unavailable — including the common case where its
   Chrome profile is **locked by a leftover browser** from an earlier session. That process is
   launched with `--remote-debugging-pipe`, not a TCP port, so you cannot attach to it or open a tab
   in it; only its spawning process can. Don't kill the user's browser to get past this. Launch a
   separate one with its own profile instead.

**Login.** Automated browsers run their own profile, not the user's everyday signed-in Chrome, so
expect a Google sign-in wall on a fresh profile. Sign in once inside that browser; a persistent
profile remembers it. Never ask the user to paste credentials or tokens into the conversation — have
them sign in in the browser window, or use an already-authenticated persistent profile.

## 2. Put Gemini in image mode

Navigate to the Gemini app, then enable image generation from the composer's tool menu (observed as
**+ → "Create image"**, after which the composer reads *"Create with Nano Banana…"*). Selecting the
**Pro** text model routes generation to the higher-quality image model. A one-time disclaimer about
creating content from images and files may appear on first file attach — accept it.

Use **one fresh thread per batch** if prompts are self-contained; it keeps thread state small and
makes "the newest image is mine" a safe assumption. Keep one thread per episode's stills so a
re-run doesn't pick up a previous episode's images.

## 3. Send the prompt

Type the prompt and submit in one action. Two failure modes to design around:

- **Newlines can submit early.** Join the prompt to a single line. If the prompt is a structured
  block, flatten it before typing rather than pasting multi-line text.
- **Attach reference images before sending**, if the prompt needs them (character reference figures,
  a style anchor), via the file-upload tool. Hidden `input[type=file]` elements accept files
  directly — you do not need to click the visible dropzone first.

## 4. Detect when generation finished

Generation takes roughly 10–30 s. **Wait, then read, and read again if unfinished — don't spin in a
tight poll.** Prefer a positive completion probe over a fixed sleep: count the finished images and
check that no progress indicator remains.

```js
() => {
  const gen = [...document.querySelectorAll('img')].filter(i => i.alt === ', AI generated');
  return { count: gen.length, stillGenerating: /Creating|Generating/.test(document.body.innerText) };
}
```

**Scope the progress probe to the response element, never `document.body`.** The page also holds
the prompt you just typed and every chat title in the Recents sidebar, and Gemini titles a chat
after its prompt — so a prompt containing *creating*, *generating*, *thinking* or *working on it*
makes `stillGenerating` true forever, and the wait burns its whole timeout with the finished image
on screen and its Download control present. Read `model-response` instead (EP002 still 018,
2026-08-06: `"pen paused above the open page, thinking"` cost two 600 s attempts and the still was
skipped). Any prose in the *prompt* is a false positive waiting to happen; the board's wording is
not something the runner gets to constrain.

If an **A/B "which response is more helpful"** panel appears, resolve it to a single image before
extracting, or you may grab the wrong or an empty one. If no panel appears, continue.

## 5. Download the full-size render, not the preview

Gemini puts a **downscaled preview** blob in the on-screen `<img>` — observed at ~**89 %** linear on
a 4:5 render (**825 × 1024** on screen versus **928 × 1152** full size). Drawing that `<img>` into a
`<canvas>` captures **the preview**, not the original.

Click the image's **"Download full size image"** control. With several images in a thread there will
be several such controls — take the **last** one, then the **newest file by mtime** in the download
directory (the Playwright MCP writes to `.playwright-mcp/` relative to the launch dir; a scripted
browser writes wherever your download handler saves).

**Do not treat a Playwright `download` event as the only signal, and give it ~90 s, not 20 s.**
Gemini fetches the full-res asset before it hands the browser a download ("Downloading full size…"),
which a 6–8 MB render regularly takes longer than 20 s to reach. And because this browser is
detached and joined over CDP, Playwright's download interception can lapse mid-run: Chrome then
saves to its own folder and the event never fires. Watch `~/Downloads` for a new
`Gemini_Generated_Image_*.png` alongside the event and take whichever lands first (EP002,
2026-08-06: stills 009–010 threw `download did not start after 3 attempts` while nine complete
renders — three items × three retry clicks — sat in `~/Downloads`).

**Then verify the saved dimensions**, every time — this is how you catch a silent preview capture:

```bash
python3 -c "from PIL import Image; print(Image.open('<saved>.png').size)"
```

This matters twice over here: the de-watermarking profiles are **keyed to exact resolutions**
(`gemini-768x1376`, `gemini-1024x1024`, …), so a preview-sized capture won't match any of them and
will need a pointless recalibration — or worse, get cleaned with the wrong profile.

A canvas → base64 read is a **fallback only** for when the download is genuinely blocked; accept
that it yields the smaller preview, and record which stills came from it.

## 6. Remove the watermark

Every Gemini render carries a translucent sparkle mark, usually bottom-right. Strip it **locally**
with the repo's existing tool — never upload stills to a watermark-removal website:

```bash
python3 .github/skills/dewatermark-stills/dewatermark.py apply \
    <stills_dir> .github/skills/dewatermark-stills/profiles/<profile> <output_dir>
```

Full method, profile handling, and failure modes: [`dewatermark-stills/SKILL.md`](../dewatermark-stills/SKILL.md).

> **Why never a removal website.** `geminiwatermark.io` was tested directly. Its "*Files never leave
> your browser*" banner is **false**: it `POST`s `multipart/form-data` to `/api/unwatermark` and
> serves the result from `storage.googleapis.com/watermark-remover-bucket/<uuid>.png`, with no WASM,
> web worker, or large script anywhere — the work is server-side. Uploaded frames land in a
> third-party Google Cloud bucket, and the `X-Goog-Expires=3600` on the signed URL governs only the
> URL signature, **not** object retention. Unreleased episode stills must not go there.

> **The line at SynthID.** Removing the **visible** sparkle from your own renders is the whole
> scope. Do not touch SynthID — Google's *invisible* provenance watermark — or use the "Remove
> SynthID" features such sites advertise. That is a different act from cleaning a logo off your own
> asset, and not a step in this workflow.

---

## Writing automation that survives UI drift

Everything in §2–§5 describes a **third-party UI that changes without notice**. The specifics above
were observed to work; the habits below are what keep a loop working when they stop being true.

- **Probe, don't assume.** Before acting on a page you haven't scripted before, dump its interactive
  elements and take a screenshot, then decide. With a scripted browser the process exits and closes
  the browser, so use **two stages**: one script to recon, a second to act on what you learned.
- **Don't over-fit selectors to visible text.** Button labels are dynamic. A real example: a control
  reading *"Remove watermarks from 10 images"* becomes *"…from 1 image"* for a single file, and a
  regex anchored on the plural silently timed out. Match loosely (`/remove watermarks?/i`), or key
  off role and position instead.
- **Prefer positive completion signals** ("N images present and no spinner") over sleeping a guessed
  interval. Sleeps are both slower and less reliable.
- **Verify the artifact, not the click.** A successful click is not a successful download. Check the
  file exists, then check its dimensions and that it is the file you think it is.
- **Treat "it worked" claims — including a site's own copy — as unverified.** If a page states
  something load-bearing about where data goes, check the network traffic before relying on it.
- **Never send the project's assets to a third-party service to accomplish a local task.**
  Generation needs Gemini; cleaning up the result does not.
