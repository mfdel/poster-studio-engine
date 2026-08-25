# gemini-gen — CLI for Gemini image generation

Automates the [`gemini-image-generation`](../SKILL.md) skill so an LLM doesn't have to drive the
browser click-by-click (which burns tokens and is flaky). The LLM calls one command per image — or
one command per *batch* — and reads a single JSON line back.

## What it does

Drives Gemini's web UI in a **detached, persistent Chrome** on a fixed CDP port (`9333`). The
browser survives between invocations, so every command reconnects to the same signed-in window
instead of launching a fresh one. Each command:

1. reconnects to Chrome (or launches it on first use),
2. opens Gemini, opens a **new chat**, switches to **Create image** mode,
3. attaches reference images if asked, types the prompt, waits for generation,
4. clicks **Download full size image** and saves the FULL-RES PNG (not the ~89% preview),
5. prints one JSON line and exits.

On any failure it stops and prints `{ok:false, stage, error, ...}` plus a debug screenshot path,
so you know exactly where it halted.

## First-time setup

Node + Chrome must be installed (they are on this machine). The wrapper finds node and the
`playwright-core` bundled with `@playwright/mcp` automatically.

The automation uses its **own** Chrome profile (`~/.gemini-cli-profile`), not your everyday
browser, so it starts signed out. Once:

```bash
./gemini-gen ensure          # opens the Chrome window; sign into Google in it
./gemini-gen status          # -> {"ok":true,"running":true,"signedIn":true,...}
```

The profile is persistent — you only sign in once.

## More than one Google account

`--account NAME` (valid on every command) selects an account by setting the profile **and** the
CDP port together. `a` (the default) is the original setup — `~/.gemini-cli-profile` on port 9333 —
so nothing changes if you never pass the flag. Any other name gets `~/.gemini-cli-profile-<name>`
and its own deterministic port.

```bash
./gemini-gen --account b ensure     # sign into the second account in the window that opens
./gemini-gen --account b status     # -> {"ok":true,"signedIn":true,"account":"…","port":9381,…}
./gemini-gen --account b batch --manifest board-b.json
```

Both browsers can run at once on their own ports, so two manifests can generate in parallel —
but split by **episode**, never by beats within one, since a shared chat thread is what carries
style consistency across a cluster.

- **Never set `GEMINI_PROFILE` without `GEMINI_PORT`.** The CLI probes the port *before* it looks
  at the profile, so a stale browser on the old port is reused and the run quietly spends the
  wrong account's quota. `--account` sets both, and deliberately overrides an exported pair — a
  forgotten `export` is the thing it exists to prevent.
- **Each profile is pinned to the address it first signed in as** (`<profile>/.gemini-account`),
  and `gen`/`batch` refuse to run against a different one. This is what catches a hand-switched
  window or a port collision; without it a mix-up surfaces only as someone else's quota draining,
  the same way a silent model fallback surfaces 100 stills later as style drift. An address the
  page won't reveal warns and continues, so a Gemini UI change can't brick the CLI. Delete the
  file to re-pin.
- **A second free account is not a second helping of the same quota** — its daily image allowance
  is the free-tier one, and Pro may be absent from its model picker entirely. `--model pro` throws
  rather than falling back when the *picker* has no Pro, so that case is a hard failure.
- **The model check does NOT catch a downgrade that happens server-side, and there is one.**
  Account `b` offers Pro, selects it, and passes `selectModel`'s read-back — the composer button
  says Pro — and then renders **1376×768, half of Pro's 2752×1536** (measured 2026-08-05, twice,
  once in a `batch` and once with an isolated `gen` probe). So the resolution in the returned JSON
  is the only honest signal of which model actually ran. **Check `w`/`h`, not the model button**,
  when an account's output matters — and note this lands as *two* silent defects at once: stills
  at half the episode's resolution, and, until `profiles/gemini-1376x768` was calibrated, renders
  with no matching de-watermark profile feeding a 71-link edit chain.
- Using extra accounts to get around usage limits is against Google's terms; the exposure is
  rate-limiting or action on the secondary account.

## Commands

Every command prints exactly one JSON object on stdout. Progress goes to stderr.

`--account NAME` may be added to any of these; see *More than one Google account* above.

| command | what |
|---|---|
| `status` | is the browser up / signed in (reports `account`, `pinned`, `profile`, `port`) |
| `ensure` | launch-or-reconnect, open Gemini, report sign-in |
| `recon` | dump interactive elements + screenshot (selector probe, for when the UI drifts) |
| `gen --prompt P --out F [--ref a.png,b.png] [--model pro] [--no-new-chat]` | one image |
| `batch --manifest m.json [--model pro]` | many images, with reference clustering |
| `close` | quit the browser |

### `gen` — one image

```bash
./gemini-gen gen \
  --prompt "A dark, low-contrast candle burned halfway down on an oak desk, muted tones, 16:9, no text." \
  --out episodes/XXX_slug/assets/beat01.png
```

Returns: `{"ok":true,"file":"…/beat01.png","bytes":1637918,"w":1376,"h":768,"imagesInThread":1}`

- `--ref a.png,b.png` attaches reference images (comma-separated) before sending.
- `--model pro` selects a model by name (applied *after* refs, since uploading can reset it).
  Omit to use whatever the account defaults to.
- `--no-new-chat` continues the current thread instead of opening a fresh one.

### `batch` — many images, one reference upload per run of shared refs

The manifest is a JSON array of `{prompt, out, ref?}`. **Consecutive items with the same `ref`
set are clustered into one Gemini thread**, so a shared reference uploads *once* and thread
context carries it across the run (which also helps character/style consistency). Items with no
`ref`, or a different `ref` set, start a new chat.

```json
[
  {"prompt":"Wide establishing shot, muted palette, 16:9, no text.", "out":"assets/b01.png", "ref":["assets/char_ref.png"]},
  {"prompt":"Same figure, closer, seated, 16:9, no text.",           "out":"assets/b02.png", "ref":["assets/char_ref.png"]},
  {"prompt":"An empty rowboat on a still lake at dawn, 16:9, no text.","out":"assets/b03.png"}
]
```

```bash
./gemini-gen batch --manifest board.json
```

Above: two clusters — items 1–2 share `char_ref.png` (one chat, one upload), item 3 is standalone.

Returns on success:
`{"ok":true,"generated":3,"total":3,"cleaned":3,"dirty":0,"items":[{"out":…,"w":2752,"h":1536,"bytes":…,"cleaned":true,"raw":"…/_work/raw/b01.png"}, …]}`

On failure it stops and reports how far it got:
`{"ok":false,"stage":"batch","error":"…","completed":1,"total":3,"lastDone":"assets/b01.png","screenshot":"/tmp/gemini_error.png"}`

Ordering is preserved: to keep a cluster together, keep those items adjacent in the manifest.

### `batch` de-watermarks as it goes

**Each render is cleaned the moment it lands**: the raw moves to `_work/raw/<name>.png` beside it
and the de-watermarked image takes its place at `out`. `--no-clean` turns this off.

This is not a convenience — **it is the only order that works for a chained edit.** An item whose
`ref` is an earlier item's `out` attaches that *render*, watermark and all, and the model then
paints the sparkle into the new image as **picture content**. A profile removes the real overlay;
it cannot remove a copy that is part of the picture, and the copies stack down the chain. Cleaning
between renders is what stops it. (Found on the sleep channel's lit-room probe, 2026-08-05, after
the same defect had already put an unremoved mark into 78 finished stills of an episode.)

**A missing profile is reported, never guessed around.** Profiles are keyed to an exact
resolution and unblending with the wrong box smears a rectangle of picture, so if
`profiles/gemini-<w>x<h>` does not exist the item is left raw, logged as
`! NOT DE-WATERMARKED`, and returned with `cleaned:false` and a `reason`. If a **later item
attaches that render**, the run stops instead — the mark would be permanent.

Full-size renders are **1376×768** (16:9) on the default model, but **`--model pro` emits
2752×1536** — double, measured 2026-08-05. `profiles/gemini-2752x1536/` covers the Pro 16:9
renders (plus `-2730x1536`/`-2754x1536`, since Pro's width isn't perfectly fixed), and
`profiles/gemini-1376x768/` covers the half-size ones, so **both sizes now chain**.

## Cleaning by hand

`gen` does **not** clean (it generates one image, so there is no chain to protect), and `batch
--no-clean` leaves everything raw. Strip the mark **locally** — never upload stills anywhere:

```bash
python3 ../../dewatermark-stills/dewatermark.py apply \
    <stills_dir_or_one.png> ../../dewatermark-stills/profiles/<profile> <output_dir> --no-residual
```

`--no-residual` is required for photographic content: the residual pass reads photographic
texture as leftover watermark. `apply` takes a single `.png` as well as a folder.

## How it works / gotchas

- **Detached browser, CDP reconnect.** Chrome is launched with `--remote-debugging-port=9333` and
  `--user-data-dir=~/.gemini-cli-profile`, detached, so it outlives the CLI process. Every run does
  `connectOverCDP` first and only launches if nothing answers. `close` quits it.
- **Locators, not `evaluate`.** Gemini's menus, the "Create image" item, and the image toolbar
  live in **open shadow roots**. Playwright locators pierce those; `document.querySelectorAll` does
  not. All element finding uses locators.
- **Model selection is scoped and verified, and both halves matter.** `--model` picks the option by
  its *title line* among `[data-test-id^=bard-mode-option-]`, not by page-wide text. A page-wide
  `getByText(/pro/i)` matches a sidebar chat named "…Prompt…" first and clicking it merely opens that
  chat, leaving the model on Flash — found on EP001, 2026-08-05, after two stills came back in the
  Flash style. Matching the title line also avoids the Pro item's own "Complex problem solving"
  description. The run then re-reads the composer's model button and **throws** if it doesn't say
  what was asked, since a silent fallback shows up only as a style drift 100 stills later.
- **Image mode waits for the menu entry; it does not sleep a guess — and its failure looks like a
  quota wall.** The tools menu is populated asynchronously, so reading it a fixed interval after
  the click lands on an empty menu whenever the app is still hydrating. `clickText` finds no
  match, **swallows that and returns `true`** (it catches its own click errors), so the only
  symptom is `setImageMode`'s own `could not put the composer into image mode ("Create image")` —
  which is indistinguishable from an exhausted image allowance, because that presents the same
  way. Found on EP001, 2026-08-05: four consecutive `batch` runs failed on account a and were
  misread as quota — the failure screenshot showed the sidebar still loading — while a hand-driven
  probe on the same profile entered image mode every time simply by waiting longer.
  `setImageMode` now `waitFor`s the entry and retries 3×, re-checking `imageModeOn` before each
  click so the **toggle** can't be flipped back off. **When diagnosing this error, check the
  screenshot for a half-rendered page before concluding anything about quota** — and note the two
  are genuinely distinguishable there: a real wall shows the model dropped to Flash/Flash-Lite.
- **Completion signal.** The render is not a plain `<img>` (canvas/background), so the reliable
  "an image finished" signal is the appearance of a new **Download full size image** control, not
  counting `<img alt="AI generated">`.
- **Download race.** The full-res asset isn't fetchable the instant generation ends, so the first
  download click can fire nothing. `downloadFullSize` retries a few times.
- **Full size, verified.** Dimensions are read from the saved file's header (no PIL dependency) and
  returned in the JSON — this is how you catch a silent preview capture.
- **UI drift.** Everything past sign-in is a third-party UI that changes without notice. When a
  command starts failing, run `recon` (dumps buttons + a screenshot) and re-lock the selectors in
  `gemini_gen.mjs`. The selectors were verified 2026-08-04.

## Env overrides

`--account` is the safe way to set the first two together; reach for these only to point at
something the flag can't express, and always set the pair.

`GEMINI_PORT` (9333), `GEMINI_PROFILE` (`~/.gemini-cli-profile`), `GEMINI_CHROME` (Chrome path),
`GEMINI_DEBUG_DIR` (`/tmp`, where error/recon screenshots land), `GEMINI_PWCORE` (set by the
wrapper).
