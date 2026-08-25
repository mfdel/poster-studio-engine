#!/usr/bin/env node
// gemini_gen.mjs — drive Gemini's web UI to generate images, no LLM in the loop.
//
// The browser is a *detached* Google Chrome on a fixed CDP port with a persistent
// profile, so it survives between CLI invocations: every command reconnects to the
// same window (sign-in included) instead of launching a fresh one. See SKILL.md.
//
// Commands (all print one JSON object on stdout; progress goes to stderr):
//   status                      is the browser up? signed in?
//   ensure                      launch/reconnect the browser, open Gemini, report sign-in
//   recon                       dump interactive elements of the current page (selector probe)
//   gen   --prompt P --out F     one image in a fresh chat  [--ref a.png,b.png] [--model pro]
//   batch --manifest M.json      many images; items sharing a --ref set reuse one chat
//                                de-watermarks each render as it lands (raw -> _work/raw/),
//                                which is what keeps a chained edit from baking the mark in;
//                                --no-clean opts out. See dewatermark() below.
//   close                       quit the browser
//
// `--account NAME` (any command) selects a Google account. It is handled by the
// ./gemini-gen wrapper, which turns it into the GEMINI_PROFILE + GEMINI_PORT pair this
// file reads; each profile is pinned to its signed-in address so a run cannot end up on
// the wrong account's quota. See assertAccount().
//
// Exit code is non-zero on failure; the JSON carries {ok:false, stage, item, error}.

import { spawn, spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const PORT = Number(process.env.GEMINI_PORT || 9333);
const PROFILE = process.env.GEMINI_PROFILE || path.join(os.homedir(), '.gemini-cli-profile');
const CHROME = process.env.GEMINI_CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const GEMINI = 'https://gemini.google.com/app';
const DEBUG_DIR = process.env.GEMINI_DEBUG_DIR || '/tmp';
// Where Chrome drops a file when Playwright does NOT capture the download — see
// downloadFullSize(). This browser is detached and connected over CDP, so it keeps its own
// download settings and the interception is not guaranteed to hold for a whole run.
const CHROME_DOWNLOAD_DIR = process.env.GEMINI_DOWNLOAD_DIR || path.join(os.homedir(), 'Downloads');
// Each profile is pinned to the address it was first signed in as, so a run can prove
// it is on the account it was asked for. See assertAccount().
const ACCOUNT_PIN = path.join(PROFILE, '.gemini-account');

// playwright-core ships bundled with @playwright/mcp; the wrapper resolves it and
// passes the absolute path in GEMINI_PWCORE so this file needn't guess a version.
const PWCORE = process.env.GEMINI_PWCORE;
if (!PWCORE) die('bootstrap', 'GEMINI_PWCORE not set — run through the ./gemini-gen wrapper');
const { chromium } = await import(PWCORE);

// ---------- tiny output helpers ------------------------------------------------
function log(...a) { process.stderr.write(a.join(' ') + '\n'); }
function ok(obj) { process.stdout.write(JSON.stringify({ ok: true, ...obj }) + '\n'); process.exit(0); }
function die(stage, error, extra = {}) {
  process.stdout.write(JSON.stringify({ ok: false, stage, error: String(error), ...extra }) + '\n');
  process.exit(1);
}

// ---------- de-watermarking ----------------------------------------------------
// A render carries Gemini's sparkle, and an EDIT that attaches that render makes the model
// paint the sparkle in as picture content — which no profile can remove afterwards, because
// it is now part of the picture. So a chain has to be cleaned *between* renders, not at the
// end. `batch` therefore cleans every render as it lands: the raw moves to `_work/raw/` and
// the cleaned image takes its place at `out`, so the next item attaches a clean source.
// Found on the sleep channel's lit-room probe, 2026-08-05.
const HERE = path.dirname(fileURLToPath(import.meta.url));
const DEWM = path.resolve(HERE, '../../dewatermark-stills/dewatermark.py');
const PROFILES = path.resolve(HERE, '../../dewatermark-stills/profiles');
const PYTHON = process.env.GEMINI_PYTHON || 'python3';

// Profiles are per-resolution; there is no safe fallback, since unblending with the wrong
// box smears a rectangle of picture. A missing profile is reported, never guessed around.
function profileFor(w, h) {
  const dir = path.join(PROFILES, `gemini-${w}x${h}`);
  return fs.existsSync(path.join(dir, 'profile.json')) ? dir : null;
}

// `--no-residual` because this channel's content is photographic and the residual pass reads
// photographic texture as leftover watermark. See dewatermark-stills/SKILL.md.
function dewatermark(outPath, profileDir) {
  const dest = path.resolve(outPath);
  const dir = path.dirname(dest);
  const rawDir = path.join(dir, '_work', 'raw');
  fs.mkdirSync(rawDir, { recursive: true });
  const raw = path.join(rawDir, path.basename(dest));
  fs.renameSync(dest, raw);
  const r = spawnSync(PYTHON, [DEWM, 'apply', raw, profileDir, dir, '--no-residual'], { encoding: 'utf8' });
  if (r.status !== 0 || !fs.existsSync(dest)) {
    fs.renameSync(raw, dest);   // put the render back; an uncleaned still beats a lost one
    throw new Error(`dewatermark failed: ${(r.stderr || r.stdout || r.error?.message || '').trim().split('\n').pop()}`);
  }
  return raw;
}

// ---------- image dimensions without a dependency ------------------------------
function imageSize(buf) {
  // PNG: 8-byte sig, then IHDR at 16..24
  if (buf.length > 24 && buf[0] === 0x89 && buf[1] === 0x50) {
    return { w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) };
  }
  // JPEG: scan for a Start-Of-Frame marker
  if (buf[0] === 0xff && buf[1] === 0xd8) {
    let o = 2;
    while (o < buf.length) {
      if (buf[o] !== 0xff) { o++; continue; }
      const m = buf[o + 1];
      if (m >= 0xc0 && m <= 0xcf && m !== 0xc4 && m !== 0xc8 && m !== 0xcc) {
        return { h: buf.readUInt16BE(o + 5), w: buf.readUInt16BE(o + 7) };
      }
      o += 2 + buf.readUInt16BE(o + 2);
    }
  }
  return { w: 0, h: 0 };
}

// ---------- browser lifecycle --------------------------------------------------
async function tryConnect() {
  try { return await chromium.connectOverCDP(`http://127.0.0.1:${PORT}`, { timeout: 2500 }); }
  catch { return null; }
}

async function ensureBrowser() {
  let browser = await tryConnect();
  let launched = false;
  if (!browser) {
    if (!fs.existsSync(CHROME)) die('launch', `Chrome not found at ${CHROME}`);
    log('launching chrome (detached) on port', PORT);
    const child = spawn(CHROME, [
      `--remote-debugging-port=${PORT}`,
      `--user-data-dir=${PROFILE}`,
      '--no-first-run', '--no-default-browser-check',
      GEMINI,
    ], { detached: true, stdio: 'ignore' });
    child.unref();
    for (let i = 0; i < 30 && !browser; i++) {
      await new Promise(r => setTimeout(r, 1000));
      browser = await tryConnect();
    }
    launched = true;
    if (!browser) die('launch', 'chrome started but no CDP endpoint appeared');
  }
  return { browser, launched };
}

async function getPage(browser) {
  const ctx = browser.contexts()[0];
  if (!ctx) die('page', 'no browser context');
  const pages = ctx.pages();
  return pages.find(p => p.url().includes('gemini.google.com')) || pages[0] || await ctx.newPage();
}

// ---------- generic page helpers ----------------------------------------------
// Gemini is web-component heavy: its menus, "Create image" item, and image toolbar
// live in OPEN SHADOW ROOTS. Playwright locators pierce those automatically;
// page.evaluate + querySelectorAll does NOT. So all element finding goes through
// locators, never evaluate. (Verified 2026-08-04 against app build shipping "Pro".)
const flatten = (s) => s.replace(/\s*\n\s*/g, ' ').replace(/\s+/g, ' ').trim();

async function clickText(page, text, { exact = true, timeout = 6000, which = 'first' } = {}) {
  const loc = page.getByText(text, typeof text === 'string' ? { exact } : undefined);
  if (!(await loc.count())) return false;
  await (which === 'last' ? loc.last() : loc.first()).click({ timeout }).catch(() => {});
  return true;
}

async function clickBtn(page, re, { timeout = 6000, which = 'first' } = {}) {
  const loc = page.getByRole('button', { name: re });
  if (!(await loc.count())) return false;
  await (which === 'last' ? loc.last() : loc.first()).click({ timeout }).catch(() => {});
  return true;
}

async function dismissConsent(page) {
  // "Before you continue to Google" cookie banner
  await clickBtn(page, /reject all|accept all/i).catch(() => {});
}

async function isSignedIn(page) {
  if (/accounts\.google\.com/.test(page.url())) return false;
  // the signed-out app shows a visible "Sign in" button; the signed-in app has a composer
  if ((await page.getByRole('button', { name: /^sign in$/i }).count().catch(() => 0)) > 0) return false;
  return (await page.locator('rich-textarea, [contenteditable=true]').count()) > 0;
}

// Which Google account is this window signed in as? Read from the account button's
// aria-label, which carries the address ("Google Account: Name (a@b.com)"). Matching
// any aria-label containing an address rather than that exact wording keeps this from
// breaking on a copy change. Returns null when it can't tell — the caller must treat
// that as "unknown", never as "wrong".
async function accountEmail(page) {
  const loc = page.locator('[aria-label*="@"]');
  const n = Math.min(await loc.count().catch(() => 0), 10);
  for (let i = 0; i < n; i++) {
    const label = await loc.nth(i).getAttribute('aria-label').catch(() => null);
    const m = label && label.match(/[\w.+-]+@[\w-]+\.[\w.-]+/);
    if (m) return m[0].toLowerCase();
  }
  return null;
}

const readPin = () => { try { return fs.readFileSync(ACCOUNT_PIN, 'utf8').trim() || null; } catch { return null; } };

// Guard for the multi-account setup: a profile remembers the address it was signed in
// as, and a generating run refuses to proceed against a different one. Without this a
// port collision or a hand-switched window shows up only as someone else's quota
// draining, the same way a silent model fallback shows up 100 stills later as style
// drift. Unreadable address = warn and continue, so a Gemini UI change can't brick the
// whole CLI over a check that is only meant to catch a mix-up.
async function assertAccount(page) {
  const pinned = readPin();
  if (!pinned) return null;
  const actual = await accountEmail(page).catch(() => null);
  if (!actual) { log(`warn: cannot read signed-in account; expected ${pinned} (profile ${PROFILE})`); return null; }
  if (actual !== pinned) {
    die('account', `profile ${PROFILE} is pinned to ${pinned} but the browser is signed in as ${actual}`,
        { expected: pinned, actual, profile: PROFILE, port: PORT,
          hint: `sign this window back into ${pinned}, or delete ${ACCOUNT_PIN} to re-pin it` });
  }
  return actual;
}

async function gotoGemini(page) {
  if (!page.url().includes('gemini.google.com')) {
    await page.goto(GEMINI, { waitUntil: 'domcontentloaded' }).catch(() => {});
  }
  await page.waitForTimeout(1500);
  await dismissConsent(page);
  // Being on the host is not being on the app. /usage, /settings and the other sub-pages
  // carry no composer, and isSignedIn() reads a missing composer as signed out — so a
  // window left parked on one of them fails every run with a bogus "not signed in".
  // Found 2026-08-05 with the browser sitting on /usage after a quota check.
  const composers = await page.locator('rich-textarea, [contenteditable=true]').count().catch(() => 0);
  if (!composers && !/accounts\.google\.com/.test(page.url())) {
    await page.goto(GEMINI, { waitUntil: 'domcontentloaded' }).catch(() => {});
    await page.waitForTimeout(1500);
    await dismissConsent(page);
  }
}

// ---------- Gemini-specific steps ---------------------------------------------
async function waitForComposer(page, timeout = 20000) {
  await page.locator('rich-textarea .ql-editor, [contenteditable=true]').first()
    .waitFor({ state: 'visible', timeout })
    .catch(() => { throw new Error('composer (prompt box) never appeared'); });
}

async function newChat(page) {
  // Match a real button, never bare text. With the sidebar collapsed the only "New chat"
  // in the DOM is its hidden tooltip div, and clickText happily "succeeded" on it: 6s of
  // click retries, swallowed, then `true` — so the thread never reset and every image in
  // a run piled into one chat. Found on EP001, 2026-08-05.
  const btn = page.getByRole('button', { name: /^new chat$/i });
  const usable = (await btn.count().catch(() => 0)) > 0
    && await btn.first().isVisible().catch(() => false);
  if (usable) await btn.first().click({ timeout: 6000 }).catch(() => {});
  else await page.goto(GEMINI, { waitUntil: 'domcontentloaded' }).catch(() => {});
  await page.waitForTimeout(1500);
  await waitForComposer(page);
}

async function openToolsMenu(page) {
  // Wait for the button instead of counting once: the composer re-renders whenever the
  // mode chip changes, and a count taken during that window reads 0.
  const btn = page.getByRole('button', { name: /upload & tools|tools/i });
  await btn.first().waitFor({ state: 'visible', timeout: 8000 }).catch(() => {});
  if (!(await btn.count().catch(() => 0))) return false;
  await btn.first().click({ timeout: 6000 }).catch(() => {});
  return true;
}

// Is the composer in image mode? Read the composer, not a text node: "Describe your
// image" is a `data-placeholder` attribute on the Quill editor, so getByText() never
// matched it — and because the check is what guards the toggle, setImageMode clicked
// "Create image" on a composer already in image mode and turned it OFF. Found on EP001,
// 2026-08-05 (account b): the composer fell back to "Ask Gemini" with no error anywhere,
// the same silent-wrong-mode failure the model check exists to catch.
async function imageModeOn(page) {
  const ph = await page.evaluate(
    () => document.querySelector('.ql-editor')?.getAttribute('data-placeholder') || ''
  ).catch(() => '');
  if (/describe your image/i.test(ph)) return true;
  // while image mode is on, the mode chip's control reads "Deselect Images"
  return (await page.getByRole('button', { name: /deselect images/i }).count().catch(() => 0)) > 0;
}

async function setImageMode(page) {
  // + / tools → "Create image". The menu entry is a *toggle*, so this has to be
  // idempotent — clicking it on a composer already in image mode leaves image mode.
  // Hence the imageModeOn() check at the top of every attempt: never click twice.
  //
  // Retry, and WAIT for the entry rather than sleeping a guess. The tools menu is
  // populated asynchronously and a fixed 700ms read lands before "Create image" exists
  // whenever the app is still hydrating — clickText then finds 0 matches, swallows it,
  // and the only symptom is this function's own error, which reads exactly like an
  // exhausted image quota. Found on EP001, 2026-08-05 (account a): four runs failed here
  // while a hand-driven probe on the same profile put the composer into image mode every
  // time, the difference being that the probe waited for the sidebar to finish loading.
  for (let attempt = 1; attempt <= 3; attempt++) {
    if (await imageModeOn(page)) return;
    if (await openToolsMenu(page)) {
      const item = page.getByText('Create image', { exact: true });
      await item.first().waitFor({ state: 'visible', timeout: 6000 }).catch(() => {});
      if (await item.count().catch(() => 0)) {
        await item.first().click({ timeout: 6000 }).catch(() => {});
        await page.waitForTimeout(900);
      }
      await page.keyboard.press('Escape').catch(() => {});
      await page.waitForTimeout(400);
    }
    if (await imageModeOn(page)) return;
    await page.waitForTimeout(1200 * attempt);   // let a slow hydrate settle, then retry
  }
  // Verify, don't assume — same reason selectModel verifies. Generating a board's worth
  // of stills out of image mode is a whole run wasted, and nothing else would report it.
  throw new Error('could not put the composer into image mode ("Create image")');
}

async function selectModel(page, model) {
  if (!model) return;
  const menu = page.locator('[data-test-id=bard-mode-menu-button]');
  if (!(await menu.count())) throw new Error(`model menu not found, cannot select "${model}"`);
  await menu.first().click().catch(() => {});
  await page.waitForTimeout(600);

  // Match the option's own title line, scoped to the open menu. A page-wide
  // getByText(/pro/i) hits a sidebar chat named "...Prompt..." long before it
  // reaches the menu, and clicking that just opens the chat -- found on EP001,
  // 2026-08-05. "Extended thinking / Complex problem solving" is a sibling item
  // that also carries "pro", so match the first line only, not the description.
  const re = new RegExp(model, 'i');
  const opts = page.locator('[data-test-id^=bard-mode-option-]');
  const n = await opts.count();
  let picked = null;
  for (let i = 0; i < n; i++) {
    const title = ((await opts.nth(i).innerText().catch(() => '')) || '').split('\n')[0].trim();
    if (re.test(title)) { picked = opts.nth(i); break; }
  }
  if (!picked) {
    const all = [];
    for (let i = 0; i < n; i++) all.push(((await opts.nth(i).innerText().catch(() => '')) || '').split('\n')[0].trim());
    await page.keyboard.press('Escape').catch(() => {});
    throw new Error(`no model option matches "${model}" -- menu offers: ${all.join(' | ') || '(none)'}`);
  }
  await picked.click({ timeout: 6000 }).catch(() => {});
  await page.waitForTimeout(400);
  await page.keyboard.press('Escape').catch(() => {});

  // Verify, don't assume. When an image quota runs out Gemini silently falls back
  // to another model, and every later render comes out in a different style with
  // no error anywhere -- found on EP001, 2026-08-05, after two stills rendered in
  // Flash (filled shapes, a glow around the candle) landed mid-run among Pro ones.
  await page.waitForTimeout(400);
  const label = ((await menu.first().innerText().catch(() => '')) || '').trim();
  if (!new RegExp(model, 'i').test(label)) {
    throw new Error(`model is "${label || 'unknown'}" after selecting "${model}" `
      + `-- refusing to generate in the wrong model (image quota exhausted?)`);
  }
}

async function attachRefs(page, refs) {
  if (!refs || !refs.length) return;
  for (const f of refs) if (!fs.existsSync(f)) throw new Error(`ref not found: ${f}`);
  const abs = refs.map(f => path.resolve(f));
  // A hidden file input only exists after the upload menu opens, and "Upload files"
  // triggers a native chooser — so drive the filechooser event rather than clicking blind.
  if (!(await openToolsMenu(page))) throw new Error('could not open the upload menu');
  await page.waitForTimeout(500);
  const [fc] = await Promise.all([
    page.waitForEvent('filechooser', { timeout: 8000 }).catch(() => null),
    clickText(page, 'Upload files', { exact: true }),
  ]);
  if (fc) {
    await fc.setFiles(abs);
  } else {
    const input = page.locator('input[type=file]');            // fallback: hidden input
    if (!(await input.count())) throw new Error('no file chooser or input for reference upload');
    await input.first().setInputFiles(abs);
  }
  await page.waitForTimeout(1200);
  await clickBtn(page, /^(got it|ok|accept|i understand|continue)$/i).catch(() => {}); // one-time disclaimer
  await page.waitForTimeout(1500);                             // let the thumbnail register
}

// Did the turn actually leave the composer? A sent prompt clears the editor and adds a
// user-query bubble; either one is proof. Polled, because both happen a beat after the key.
async function promptWasSent(page, before, timeoutMs = 8000) {
  const end = Date.now() + timeoutMs;
  while (Date.now() < end) {
    await page.waitForTimeout(500);
    if ((await page.locator('user-query').count().catch(() => 0)) > before) return true;
    const left = await page.evaluate(
      () => (document.querySelector('.ql-editor')?.innerText || '').trim().length
    ).catch(() => 1);
    if (!left) return true;
  }
  return false;
}

// VERIFY the submit, never assume it. Enter silently does nothing often enough to matter:
// the composer is a Quill editor that re-renders when a reference thumbnail attaches, and a
// keypress landing in that window is swallowed with the prompt left sitting in the box. Nothing
// downstream notices — waitForGeneration then waits its full 600s for a turn that was never
// sent, the retry sends it into the same state, and the still is skipped after 20 idle minutes.
// Found on EP002, 2026-08-06: the failure screenshot for still 022 shows the full prompt and its
// attached ref still in the composer with the send arrow lit, on an otherwise empty new chat.
async function sendPrompt(page, prompt) {
  const editor = page.locator('rich-textarea .ql-editor, [contenteditable=true]').first();
  if (!(await editor.count())) throw new Error('prompt editor not found');
  const before = await page.locator('user-query').count().catch(() => 0);
  await editor.click();
  await page.keyboard.insertText(flatten(prompt)); // single insert → no early-submit newline
  await page.waitForTimeout(300);
  await page.keyboard.press('Enter');
  if (await promptWasSent(page, before)) return;

  // Enter was swallowed. Click the send control instead, then re-focus and try the key once
  // more — cheap next to the 600s the silent version costs.
  log('  prompt still in the composer after Enter — clicking send');
  const send = page.locator(
    'button.send-button, button[aria-label*="Send" i], button[mattooltip*="Send" i]'
  );
  if (await send.count().catch(() => 0)) {
    await send.last().click({ timeout: 6000 }).catch(() => {});
    if (await promptWasSent(page, before)) return;
  }
  await editor.click().catch(() => {});
  await page.keyboard.press('Enter');
  if (await promptWasSent(page, before)) return;
  throw new Error('prompt never submitted (still in the composer after Enter, send click, Enter)');
}

// Each finished image carries its own "Download full size image" control, so the count
// of those controls is the reliable "how many images exist" signal — the render is NOT a
// plain <img> (canvas/background), so counting <img alt="AI generated"> does not work here.
async function dlButtonCount(page) {
  return page.getByRole('button', { name: /download full size/i }).count().catch(() => 0);
}
// Scoped to the model's own response bubble, NOT the whole page. An unscoped getByText
// also reads the prompt the run just typed and every chat title in the Recents sidebar
// (Gemini titles a chat after its prompt), so any board whose prompt contains one of these
// words made this return true forever: the image finished, the Download control was on
// screen, and waitForGeneration still burned its full 600s and threw. Found on EP002 still
// 018, 2026-08-06 — "pen paused above the open page, thinking" cost two 600s attempts and
// the still was skipped. `model-response` is Gemini's response element (read back off the
// live DOM the same day); before the first response it does not exist and this reports "not
// busy", which is safe because the caller also requires a new Download control.
async function isBusy(page) {
  return (await page.locator('model-response')
    .getByText(/Creating|Generating|Thinking|Working on it/i)
    .count().catch(() => 0)) > 0;
}

async function resolveAB(page) {
  // "Which response is more helpful?" experiment — pick either to collapse to one image.
  if (!(await page.getByText(/which response is more helpful/i).count().catch(() => 0))) return;
  log('  resolving A/B panel');
  await clickBtn(page, /response a|option a|helpful/i).catch(() => {});
  await page.waitForTimeout(1500);
}

// 600s, not 300s, and 300s was already a raise from 150s: the current image model critiques
// its own render and re-draws inside a single turn ("a logical flaw from my previous attempt
// persists"), so one prompt can mean two Pro renders plus reasoning. Found on EP001 still 048,
// 2026-08-05 — the image was on screen and finished, the wait had simply already given up.
// Raised again the same day on still 087, which did exactly that: the thread held a two-part
// answer ("I wasn't able to get the arrangement quite right… " then a corrected second render)
// and the Download control appeared just past the 300s line. The cost of waiting too long is
// idle seconds; the cost of giving up too early is a spent Pro render thrown away AND, before
// the change below, the whole rest of the batch.
//
// ...but a turn that will NEVER produce an image also waits the full 600s, and then the retry
// waits another. Gemini answers some prompts with prose instead of a render, or with an outright
// "something went wrong" — no Download control ever appears and there is nothing left to wait for.
// EP002, 2026-08-06: stills 069/072/073/074 cost 671s, 1200s, 1334s and 687s that way, ~50 min of
// a 2 h board. So bail once the answer has clearly *finished* without one: no new Download control,
// not busy, and the response text has stopped changing.
//
// The stall window is what keeps this from throwing away good renders, because the self-critique
// re-draw above looks similar for a moment. A model that is about to draw again keeps its progress
// text moving; a dead end sits still. 90s of a motionless response is the generic signal, cut to
// 25s when the text says in so many words that it failed. Note REFUSAL deliberately does NOT match
// "I wasn't able to get the arrangement quite right" (EP001 still 087) — that sentence precedes a
// second, better render, and matching it would abort exactly the case the 600s exists for.
const REFUSAL = /(can'?t|cannot|unable to|not able to|won'?t be able to) (create|generate|make|produce|draw)|something went wrong|image generation (request )?failed|violat|against .{0,20}polic|please try again/i;

async function latestResponseText(page) {
  return page.evaluate(() => {
    const els = document.querySelectorAll('model-response');
    return els.length ? (els[els.length - 1].innerText || '').trim() : '';
  }).catch(() => '');
}

async function waitForGeneration(page, baseline, timeoutMs = 600000) {
  const end = Date.now() + timeoutMs;
  let lastText = null, lastChange = Date.now();
  while (Date.now() < end) {
    await page.waitForTimeout(3000);
    await resolveAB(page);
    const busy = await isBusy(page);
    if ((await dlButtonCount(page)) > baseline && !busy) {
      await page.waitForTimeout(3000);               // settle: let the full-res asset finalize
      return await dlButtonCount(page);
    }
    const txt = await latestResponseText(page);
    if (txt !== lastText) { lastText = txt; lastChange = Date.now(); }
    if (txt && !busy) {
      const stallMs = REFUSAL.test(txt) ? 25000 : 90000;
      if (Date.now() - lastChange >= stallMs) {
        const why = txt.replace(/\s+/g, ' ').slice(0, 140);
        throw new Error(`answered without an image (settled ${Math.round(stallMs / 1000)}s): "${why}"`);
      }
    }
  }
  throw new Error(`generation timed out (no new image after ${Math.round(timeoutMs / 1000)}s)`);
}

// Files Chrome itself has finished writing into its download folder, newest last.
function chromeDownloadSnapshot() {
  try {
    return new Set(fs.readdirSync(CHROME_DOWNLOAD_DIR));
  } catch { return new Set(); }
}
// A file that appeared since `before`, is not still being written (.crdownload), and has
// stopped growing. Returns its absolute path, or null.
function newChromeDownload(before) {
  let names;
  try { names = fs.readdirSync(CHROME_DOWNLOAD_DIR); } catch { return null; }
  const fresh = names.filter((n) => !before.has(n) && !n.endsWith('.crdownload'));
  if (!fresh.length) return null;
  const best = fresh
    .map((n) => path.join(CHROME_DOWNLOAD_DIR, n))
    .map((p) => { try { return { p, st: fs.statSync(p) }; } catch { return null; } })
    .filter((x) => x && x.st.isFile() && x.st.size > 0)
    .sort((a, b) => b.st.mtimeMs - a.st.mtimeMs)[0];
  return best ? best.p : null;
}

async function downloadFullSize(page, outPath, attempts = 3) {
  const dest = path.resolve(outPath);
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  const btn = page.getByRole('button', { name: /download full size/i });
  if (!(await btn.count())) throw new Error('no "Download full size" control present');
  const finish = (from, move) => {
    if (move) fs.renameSync(from, dest);
    const buf = fs.readFileSync(dest);
    if (!buf.length) throw new Error('downloaded file is empty');
    const { w, h } = imageSize(buf);
    return { file: dest, bytes: buf.length, w, h };
  };
  // The full-res asset isn't always fetchable the instant generation finishes, so the
  // first click can fire no download. Retry a few times before giving up.
  //
  // 90s, not 20s: Gemini fetches the full-res asset before it hands the browser a download
  // ("Downloading full size…" toast), and a 6-8 MB render regularly takes longer than 20s to
  // get there. And the Playwright download event is NOT a reliable signal on this setup —
  // the browser is detached and joined over CDP, so interception can lapse mid-run and Chrome
  // saves the file to its own folder instead. Found on EP002, 2026-08-06: stills 009-010 threw
  // "download did not start after 3 attempts" while nine renders (three items x three retry
  // clicks) sat in ~/Downloads as `Gemini_Generated_Image_*.png`, complete. So watch that
  // folder as well and take whichever lands first.
  for (let i = 0; i < attempts; i++) {
    const before = chromeDownloadSnapshot();
    const dlPromise = page.waitForEvent('download', { timeout: 90000 }).catch(() => null);
    await btn.last().scrollIntoViewIfNeeded().catch(() => {});   // newest image = last control
    await btn.last().click({ timeout: 8000 }).catch(() => {});
    let dl = null, stray = null;
    const end = Date.now() + 90000;
    while (Date.now() < end && !dl && !stray) {
      dl = await Promise.race([dlPromise, page.waitForTimeout(1500).then(() => null)]);
      if (!dl) stray = newChromeDownload(before);
    }
    try {
      if (dl) { await dl.saveAs(dest); return finish(dest, false); }
      if (stray) {
        const settled = fs.statSync(stray).size;                 // let the write finish
        await page.waitForTimeout(1500);
        if (fs.statSync(stray).size !== settled) await page.waitForTimeout(3000);
        log(`  (download captured from ${CHROME_DOWNLOAD_DIR})`);
        return finish(stray, true);
      }
      throw new Error('no download appeared');
    } catch (e) {
      if (i === attempts - 1) throw new Error(`download did not start after ${attempts} attempts`);
      await page.waitForTimeout(2500);
    }
  }
}

// one image into the CURRENT thread (refs already attached if any)
async function generateInto(page, prompt, outPath) {
  const baseline = await dlButtonCount(page);
  await sendPrompt(page, prompt);
  const count = await waitForGeneration(page, baseline);
  const res = await downloadFullSize(page, outPath);
  return { ...res, imagesInThread: count };
}

// ---------- commands -----------------------------------------------------------
function parseArgs(argv) {
  const a = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith('--')) { const k = argv[i].slice(2); const v = argv[i + 1]?.startsWith('--') || argv[i + 1] === undefined ? true : argv[++i]; a[k] = v; }
  }
  return a;
}

async function cmdStatus() {
  const browser = await tryConnect();
  if (!browser) ok({ running: false, signedIn: false, profile: PROFILE, port: PORT, account: readPin() });
  const page = await getPage(browser);
  const signedIn = await isSignedIn(page).catch(() => false);
  const account = signedIn ? await accountEmail(page).catch(() => null) : null;
  ok({ running: true, signedIn, account, pinned: readPin(), profile: PROFILE, port: PORT, url: page.url() });
}

async function cmdEnsure() {
  const { browser, launched } = await ensureBrowser();
  const page = await getPage(browser);
  await gotoGemini(page);
  const signedIn = await isSignedIn(page);
  let account = null;
  if (signedIn) {
    // First successful sign-in pins the profile; later runs are checked against it.
    account = await assertAccount(page);
    if (!account) {
      account = await accountEmail(page).catch(() => null);
      if (account && !readPin()) fs.writeFileSync(ACCOUNT_PIN, account + '\n');
    }
  }
  ok({ running: true, launched, signedIn, account, profile: PROFILE, port: PORT,
       note: signedIn ? 'ready' : `sign in to Google in the Chrome window (profile ${PROFILE}), then re-run` });
}

async function cmdRecon() {
  const { browser } = await ensureBrowser();
  const page = await getPage(browser);
  await gotoGemini(page);
  const info = await page.evaluate(() => {
    const vis = (e) => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
    return {
      url: location.href,
      fileInputs: [...document.querySelectorAll('input[type=file]')].map(e => ({ accept: e.accept, multiple: e.multiple, hidden: !vis(e) })),
      buttons: [...document.querySelectorAll('button,[role=button],[role=menuitem],[role=option]')].filter(vis)
        .map(e => ({ label: (e.innerText || e.getAttribute('aria-label') || '').trim().slice(0, 50), test: e.getAttribute('data-test-id') || '' }))
        .filter(b => b.label || b.test).slice(0, 80),
      editors: [...document.querySelectorAll('rich-textarea,[contenteditable=true],textarea')].filter(vis).map(e => ({ tag: e.tagName, cls: e.className.slice(0, 40) })),
    };
  });
  const shot = path.join(DEBUG_DIR, 'gemini_recon.png');
  await page.screenshot({ path: shot }).catch(() => {});
  ok({ recon: info, screenshot: shot });
}

async function cmdGen(a) {
  if (!a.prompt || !a.out) die('args', 'gen needs --prompt and --out');
  const refs = a.ref ? String(a.ref).split(',').map(s => s.trim()).filter(Boolean) : [];
  const { browser } = await ensureBrowser();
  const page = await getPage(browser);
  await gotoGemini(page);
  if (!await isSignedIn(page)) die('signin', 'not signed in — run `ensure` and sign in first');
  await assertAccount(page);
  try {
    if (a['no-new-chat'] !== true) await newChat(page);
    else await waitForComposer(page);
    await setImageMode(page);
    if (refs.length) await attachRefs(page, refs);
    if (a.model) await selectModel(page, a.model);   // after refs: upload can reset the model
    const res = await generateInto(page, a.prompt, a.out);
    ok({ ...res });
  } catch (e) {
    const shot = path.join(DEBUG_DIR, 'gemini_error.png');
    await page.screenshot({ path: shot }).catch(() => {});
    die('gen', e.message, { screenshot: shot });
  }
}

async function cmdBatch(a) {
  if (!a.manifest) die('args', 'batch needs --manifest path.json');
  let items;
  try { items = JSON.parse(fs.readFileSync(a.manifest, 'utf8')); }
  catch (e) { die('manifest', `cannot read manifest: ${e.message}`); }
  if (!Array.isArray(items) || !items.length) die('manifest', 'manifest must be a non-empty JSON array');
  for (const it of items) if (!it.prompt || !it.out) die('manifest', 'every item needs {prompt, out}');

  // Cluster consecutive items by identical ref-set so a shared reference uploads once.
  const key = (it) => JSON.stringify((it.ref || []).map(String).sort());
  const clusters = [];
  for (const it of items) {
    const k = key(it);
    const last = clusters[clusters.length - 1];
    if (last && last.key === k) last.items.push(it);
    else clusters.push({ key: k, refs: it.ref || [], items: [it] });
  }

  // Which renders a LATER item attaches — those are the ones that must not stay dirty,
  // because an edit reproduces its reference's watermark as picture content.
  const chained = new Set();
  const outs = new Map(items.map((it, i) => [path.resolve(it.out), i]));
  items.forEach((it, i) => (it.ref || []).forEach((r) => {
    const src = path.resolve(r);
    const j = outs.get(src);
    if (j !== undefined && j < i) chained.add(src);
  }));
  const clean = a['no-clean'] !== true;

  const { browser } = await ensureBrowser();
  const page = await getPage(browser);
  await gotoGemini(page);
  if (!await isSignedIn(page)) die('signin', 'not signed in — run `ensure` and sign in first');
  await assertAccount(page);

  const done = [];
  try {
    for (let ci = 0; ci < clusters.length; ci++) {
      const c = clusters[ci];
      log(`cluster ${ci + 1}/${clusters.length}: ${c.items.length} image(s), ${c.refs.length} ref(s)`);
      await newChat(page);
      await setImageMode(page);
      if (c.refs.length) await attachRefs(page, c.refs); // once per cluster; thread keeps it
      if (a.model) await selectModel(page, a.model);     // after refs: upload can reset the model
      for (let ii = 0; ii < c.items.length; ii++) {
        const it = c.items[ii];
        log(`  [${done.length + 1}/${items.length}] ${it.out}`);

        // One item failing must not throw away the rest of the run. A board is ~150 stills
        // at ~1/min against a finite quota, and the common failure is a slow self-critiquing
        // re-draw, not anything wrong with the item — so retry once in a fresh thread, then
        // decide by whether anything CHAINS off this render. Nothing does: skip it and carry
        // on (the runner regenerates absent files next pass). Something does: stop, because
        // every later link would edit a source that isn't there. Found on EP001 still 087,
        // 2026-08-05 — a single 300s timeout aborted the 66 items behind it.
        let res = null, lastErr = null;
        for (let attempt = 1; attempt <= 2 && !res; attempt++) {
          try {
            res = await generateInto(page, it.prompt, it.out);
          } catch (e) {
            lastErr = e;
            log(`  ! attempt ${attempt} failed: ${e.message}`);
            if (attempt < 2) {
              await newChat(page);
              await setImageMode(page);
              if (c.refs.length) await attachRefs(page, c.refs);
              if (a.model) await selectModel(page, a.model);
            }
          }
        }
        if (!res) {
          if (chained.has(path.resolve(it.out)))
            throw new Error(`${lastErr.message} — and a later item attaches this render, so the chain cannot continue without it.`);
          log(`  ! SKIPPED (nothing chains off it): ${it.out}`);
          done.push({ out: it.out, skipped: true, reason: lastErr.message });
          continue;
        }
        const rec = { out: it.out, w: res.w, h: res.h, bytes: res.bytes, cleaned: false };
        if (clean) {
          const prof = profileFor(res.w, res.h);
          if (prof) {
            rec.raw = dewatermark(it.out, prof);
            rec.cleaned = true;
          } else {
            // Silence here is what put an unremoved watermark into all 78 of EP001's
            // stills, so say it every time — and stop outright if a later item would
            // attach this render and bake the sparkle in permanently.
            const why = `no dewatermark profile for ${res.w}x${res.h} (looked for ${path.join(PROFILES, `gemini-${res.w}x${res.h}`)})`;
            rec.reason = why;
            log(`  ! NOT DE-WATERMARKED: ${why}`);
            if (chained.has(path.resolve(it.out)))
              throw new Error(`${why} — and a later item attaches this render, which would bake the watermark into the picture. Calibrate a profile for this resolution, or re-run with --no-clean if you accept that.`);
          }
        }
        done.push(rec);
      }
    }
    // Count skips separately: a skipped item produced no render, so folding it into `dirty`
    // would report a watermark problem that does not exist, and into `generated` a file that
    // is not on disk. A non-zero `skipped` still exits 0 — the run did what it could, and the
    // caller re-runs for the gaps.
    const skipped = done.filter((d) => d.skipped).length;
    const made = done.filter((d) => !d.skipped);
    const dirty = made.filter((d) => !d.cleaned).length;
    ok({ generated: made.length, total: items.length, cleaned: made.length - dirty, dirty,
         skipped, items: done });
  } catch (e) {
    const shot = path.join(DEBUG_DIR, 'gemini_error.png');
    await page.screenshot({ path: shot }).catch(() => {});
    die('batch', e.message, { completed: done.length, total: items.length, lastDone: done.at(-1)?.out || null, screenshot: shot });
  }
}

async function cmdClose() {
  const browser = await tryConnect();
  if (!browser) ok({ running: false });
  await browser.close().catch(() => {});
  ok({ closed: true });
}

// ---------- dispatch -----------------------------------------------------------
const [cmd, ...rest] = process.argv.slice(2);
const a = parseArgs(rest);
try {
  switch (cmd) {
    case 'status': await cmdStatus(); break;
    case 'ensure': await cmdEnsure(); break;
    case 'recon':  await cmdRecon(); break;
    case 'gen':    await cmdGen(a); break;
    case 'batch':  await cmdBatch(a); break;
    case 'close':  await cmdClose(); break;
    default: die('args', `unknown command '${cmd || ''}' — use status|ensure|recon|gen|batch|close`);
  }
} catch (e) {
  die('fatal', e.stack || e.message);
}
