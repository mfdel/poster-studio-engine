# Getting a browser to drive

Two routes. Try MCP first; fall back to a scripted browser when it isn't available.

## Route 1 — Playwright MCP

Preferred, because the tools are interactive: you can snapshot the page, decide, then act, all
within one turn. Confirm availability before planning around it:

```
claude mcp list          # want: playwright  ✔ Connected
```

If it's missing, register it and **restart the session** — MCP servers initialize only at startup,
and they are scoped to the directory the session was launched in, so one registered in a parent
workspace will not load in a subdirectory project:

```
claude mcp add playwright -s user -- playwright-mcp    # -s user = every project
```

Downloads land in `.playwright-mcp/` relative to the launch directory.

## Route 2 — scripted `playwright-core`

Use when MCP tools are absent, or when they fail with:

```
Browser is already in use for .../ms-playwright/mcp-chrome-<hash>, use --isolated
```

That means a Chrome from an earlier session still holds the profile. **It cannot be shared.** The
process runs with `--remote-debugging-pipe` rather than a TCP debugging port, so there is no CDP
endpoint to attach to and no way to open a tab in it — only its spawning process can. Probing the
usual ports confirms nothing is listening:

```bash
for p in 9222 9223 9224; do curl -s -m 2 "http://127.0.0.1:$p/json/version" >/dev/null && echo "$p OPEN" || echo "$p closed"; done
ps -o command= -p <pid> | tr ' ' '\n' | grep -E "remote-debugging|user-data-dir"
```

**Don't kill the user's browser to get past this** — it may hold state they care about. Launch a
separate one instead. The MCP package bundles `playwright-core`, and `channel: 'chrome'` reuses the
**already-installed** Google Chrome, so no browser download is needed (the `ms-playwright` cache may
contain only profiles, no binaries):

```js
import { chromium } from '<global-node-modules>/@playwright/mcp/node_modules/playwright-core/index.mjs';

const ctx = await chromium.launchPersistentContext('<scratchpad>/chrome-profile', {
  channel: 'chrome',          // reuse installed Chrome; no `playwright install` needed
  headless: false,            // visible: needed for login, and some UIs behave differently headless
  viewport: { width: 1440, height: 950 },
  acceptDownloads: true,
});
const page = ctx.pages()[0] ?? (await ctx.newPage());
```

Resolve the module path rather than hardcoding a version:

```bash
npm ls -g --depth=0                                   # find the global root
find "$(npm root -g)/@playwright" -maxdepth 3 -name playwright-core -type d
```

A **persistent** profile (not `launch()`) is what makes a login survive between runs.

### Two-stage pattern

The browser closes when the script exits, so state does not carry across script runs. Recon in one
script, act in a second.

**Stage 1 — recon.** Dump the interactive elements and screenshot, so the next script can target
things precisely instead of guessing:

```js
const info = await page.evaluate(() => {
  const vis = (e) => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
  return {
    fileInputs: [...document.querySelectorAll('input[type=file]')]
      .map((e) => ({ accept: e.accept, multiple: e.multiple, hidden: !vis(e) })),
    buttons: [...document.querySelectorAll('button,a[role=button]')].filter(vis)
      .map((e) => (e.innerText || e.getAttribute('aria-label') || '').trim()).filter(Boolean),
    text: document.body.innerText.slice(0, 2000),
  };
});
await page.screenshot({ path: '<scratchpad>/recon.png' });
```

**Stage 2 — act**, using what recon showed.

### Uploading files

Set files straight onto the input, even when it's visually hidden — no need to click a dropzone:

```js
await page.setInputFiles('input[type=file]', ['/abs/path/a.png', '/abs/path/b.png']);
```

### Capturing downloads

Register the handler **before** triggering the download, and save explicitly:

```js
page.on('download', async (d) => {
  await d.saveAs(path.join(OUTDIR, d.suggestedFilename()));
});
```

Then verify the file on disk — a click that "worked" is not a file that arrived. Check existence,
size, and for images the dimensions.

### Waiting for long jobs

Poll a **positive completion signal**, with a bounded number of attempts, rather than sleeping a
guessed total:

```js
for (let i = 0; i < 60; i++) {
  await page.waitForTimeout(5000);
  const busy = await page.evaluate(() => /Processing|Generating|Creating|Queued/i.test(document.body.innerText));
  if (!busy && i > 2) break;
}
```

### Inspecting where data actually goes

When a page makes a load-bearing claim about handling data locally, verify it rather than trusting
the copy. Watch for non-GET traffic and check payloads — note that `request.postData()` returns
`null` for blob/file-backed bodies, which can make a real upload look empty; use
`postDataBuffer()`, and read the `content-type` (a `multipart/form-data` boundary means a file is
being posted):

```js
page.on('request', (r) => {
  const buf = r.postDataBuffer();
  if (r.method() !== 'GET') {
    console.log(r.method(), r.url(), buf ? buf.length : 'null', r.headers()['content-type']);
  }
});
```

Absence of WASM, web workers, and any large script is corroborating evidence that heavy work is
**not** happening client-side:

```js
await page.evaluate(() => performance.getEntriesByType('resource')
  .filter((r) => /\.wasm|worker/i.test(r.name) || r.transferSize > 80000)
  .map((r) => `${Math.round(r.transferSize / 1024)}KB ${r.name.slice(-60)}`));
```
