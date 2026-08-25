---
name: shop-run
description: USE FOR a recurring shop-marketing work session for Hopscotch Maps — measure the Etsy shop and the Pinterest account in a real browser, pull keyword evidence from eRank, publish or schedule the pins that the backlog approved, apply the approved Etsy listing edits, and write the run into the shop log. Reads the last runs first so each session continues the plan instead of restarting it. Triggered by "/shop-run", "run the shop session", "do this week's marketing", "check Etsy and Pinterest numbers", or a scheduled launchd run.
---

# Shop Run — the recurring marketing session

One run of this skill is one work session on the shop. The session always follows the same five
phases. Phase 5 is not optional: a run that publishes a pin but writes no log has made the next run
worse, because the next run cannot tell what happened.

**Scope.** Two live Etsy listings, one Pinterest account, one eRank account. Nothing else.

| Thing | Where |
|---|---|
| Etsy execution procedure | [`.github/skills/etsy-shop/SKILL.md`](../../../.github/skills/etsy-shop/SKILL.md) |
| Pinterest execution procedure | [`.github/skills/pinterest-pinning/SKILL.md`](../../../.github/skills/pinterest-pinning/SKILL.md) |
| eRank procedure | [`.github/skills/erank-keywords/SKILL.md`](../../../.github/skills/erank-keywords/SKILL.md) |
| Pinterest strategy | [`studio/brand/pinterest-guide.md`](../../../studio/brand/pinterest-guide.md) |
| Keyword evidence | [`studio/research/etsy_keyword_evidence_20260816.md`](../../../studio/research/etsy_keyword_evidence_20260816.md) |

Those three skill files hold the selectors, the traps and the compliance rules. Read the one you
need before you touch that platform. This file holds the loop, the limits and the log format.

## The three state files

| File | Purpose | Who writes it |
|---|---|---|
| [`studio/brand/shop-log.md`](../../../studio/brand/shop-log.md) | Append-only run log. One entry per session. | Every run, always |
| [`studio/brand/marketing-backlog.md`](../../../studio/brand/marketing-backlog.md) | The living queue. Each task carries a status. | Every run |
| [`studio/brand/metrics.csv`](../../../studio/brand/metrics.csv) | One row of numbers per run. | Every run that reads numbers |

[`studio/brand/pinterest-log.md`](../../../studio/brand/pinterest-log.md) stays as the Pinterest
memo. Write a long entry there only when the Pinterest strategy changes. Routine pinning goes in
`shop-log.md`.

---

## Phase 1 — Orient

Do this before you open a browser. It costs 30 seconds and it prevents repeated work.

1. Read the last two entries of `shop-log.md`.
2. Read all of `marketing-backlog.md`.
3. Read the last three rows of `metrics.csv`.
4. Get today's date with `date "+%Y-%m-%d"`. Never guess the date.
5. Write a three-line plan for this session before you act.

If the last run ended with `BLOCKED`, fix that block first. Do not start new work on top of it.

## Phase 2 — Check the sessions

All platform work runs through the **Playwright MCP** server (`mcp__playwright__*`). The server
keeps its own persistent Chrome profile, so logins usually survive between runs.

Check each platform you plan to use, before you plan the work:

```js
// browser_evaluate, after navigating to the platform
// Pinterest
() => !!document.querySelector('[data-test-id="header-accounts-options-button"]')
// Etsy   — load /your/shops/me/dashboard and check you were not redirected to /signin
() => !/signin|\/join/.test(location.pathname)
// eRank  — load erank.com/dashboard and check the same way
() => !/login/.test(location.pathname)
```

Three failure modes, and the answer to each:

- **Login dropped.** Do not try to log in. Navigate to the login page, leave the window there,
  record `NEEDS LOGIN: <platform>` in the log, skip that platform, and continue with the others.
- **Profile lock** — `Browser is already in use for .../mcp-chrome-<hash>, use --isolated`.
  **Retry the same navigate once first.** This lock is often stale: on 2026-08-16 the first
  navigate failed, no Chrome process held the profile, and the identical second navigate worked.
  If the retry also fails, an older Chrome really does hold the profile. Ask the user to quit that
  window. In an unattended run, record `BLOCKED: profile lock` and stop. Do not kill the process,
  and do not fall back to a throwaway profile, because that loses every login.

  > A **scheduled** run should not meet this. `studio/ops/shop_run.sh` ends any Chrome started
  > against an `mcp-chrome-*` profile before the session begins. If a scheduled run still reports
  > the lock, the wrapper did not run, or a second Chrome started after it. Say so in the log.
  > This clean-up belongs to the wrapper only. The rule above still binds every agent.
- **Two failures in a row on one platform.** Stop that platform for this run. Log it. Move on.

## Phase 3 — Measure

Read numbers before you make anything. The numbers decide the work.

**Etsy** — `/your/shops/me/stats`:

- visits, orders, revenue, favourites, conversion rate
- traffic sources, broken out by `utm_campaign`, because that names the pin that sold

Etsy Stats has **no 7-day preset**, and the `?date_range=` URL parameter is ignored. The default
view is month to date. Record that range, and do not relabel it as 7 days. The `metrics.csv`
columns are named `*_mtd` for this reason.

**Pinterest** — `https://analytics.pinterest.com/`, last 7 days and last 30 days:

- **outbound clicks** — the only number that counts at this stage
- impressions, saves, pin clicks, and the top three pins by outbound clicks

**eRank** — only when a title or a tag decision is queued. The free plan allows **5 Bulk Keyword
Tool runs a day, 20 keywords per run**. Spend at most **2 runs** in one session. Never spend a run
on a single word. See the eRank skill for the batching rule.

Append one row to `metrics.csv` with the columns already in that file. Write `` for a platform you
could not read. Never invent a number, and never carry the previous row forward.

## Phase 4 — Decide, then execute

### What to do, in priority order

1. **A block from the last run.** Clear it.
2. **A dated item in the backlog that is due.** Seasonal pins have hard dates. Pinterest users plan
   45 to 60 days ahead, so Christmas pins go live in early October.
3. **Evidence that contradicts a live title or tag.** A phrase measured at 0 searches in the
   evidence table is costing views every day it stays in a title.
4. **The pinning cadence.** 3 to 5 pins a day, steady. Publish two or three now and schedule the
   rest one a day, up to 30 days out.
5. **The next unstarted `approved` item in the backlog.**

Never open new work while an `approved` item is overdue.

### The approval gate

The backlog gives each task one status. The status decides what an unattended run may do.

| Status | An unattended run may |
|---|---|
| `approved` | Do the task in full, including publishing to Etsy or Pinterest |
| `draft` | Produce the artifact — pin image, copy, keyword table — and stop before publishing |
| `needs-review` | Write the recommendation into the log and change nothing on any platform |
| `blocked` | Nothing. Record why it is still blocked |
| `done` | Nothing |

New work that this run invents starts at `draft`, never at `approved`. Only the founder promotes a
task to `approved`.

### Hard limits on an unattended run

These are not style preferences. Each one exists because the mistake is expensive or irreversible.

1. **Never delete an Etsy photo.** Deletion hits the server at once and "Discard changes" does not
   undo it.
2. **Never change a price, a variation option list, or a SKU.** One option-list edit re-enables all
   12 combinations and blanks their prices.
3. **Never delete a pin**, even a broken one. A pin with traction is worth more than a clean link.
4. **Never accept Etsy's AI-rewritten title** from the Search visibility page. Read it, log it, and
   leave the title alone.
5. **At most 5 pins** published plus scheduled per run.
6. **Never publish a `www.etsy.com` link.** Every published link uses the Share & Save subdomain
   `hopscotchmaps.etsy.com` and carries its own `utm_campaign`.
7. **Keep the compliance set intact** — the Prodigi production partner, the GPSR text, the ODbL
   attribution, and the rule that no text anywhere says "instant download".
8. **Verify on the public page** after any Etsy publish. Shop Manager shows state that buyers never
   see.
9. **Stop and log** rather than improvise, if a page does not look like the skill file describes.

### Execute

Follow the platform skill file step by step. Do not re-derive the selectors.

## Phase 5 — Write the run down

Three writes, always, even for a run that did nothing.

**1. Append an entry to the top of the log body in `shop-log.md`.** Newest first. Use this shape:

```markdown
## YYYY-MM-DD — <five-word summary> · <AUTO|MANUAL>

**Status:** OK | PARTIAL | BLOCKED
**Sessions:** etsy OK · pinterest OK · erank NEEDS LOGIN

**Numbers** (7 days): Etsy 0 visits, 0 orders · Pinterest 0 outbound clicks

**Did:**
- one line per thing that changed on a platform, with the campaign slug or the listing id

**Decided:**
- one line per judgement worth keeping, and the reason

**Next run:**
- one line per task, matching a backlog item
```

Keep the whole entry under 25 lines. The log is read at the start of every future run, so length
costs real tokens every week.

**2. Update `marketing-backlog.md`.** Move finished tasks to `done` with the date. Add the tasks
that this run created, at `draft`. Update the date on anything that slipped.

**3. Append the row to `metrics.csv`.**

Then commit **only** the state files and any generated pin images:

```bash
git add studio/brand/shop-log.md studio/brand/marketing-backlog.md studio/brand/metrics.csv \
        studio/brand/pinterest-log.md studio/research/ posters/*/brand/pinterest-pins/
git commit -m "shop-run YYYY-MM-DD: <summary>"
```

Do not push, and do not commit anything else. A run that also changed code leaves that change
uncommitted for the founder to review.

## Writing style

The log, the backlog and any document for the founder use Simplified Technical English, per
[`.github/skills/ste-writing/SKILL.md`](../../../.github/skills/ste-writing/SKILL.md). Pin copy,
listing copy and any buyer-facing text keep the warm brand voice instead. Chat replies stay caveman.

## Report at the end

Five lines, no more:

1. What ran, and what was skipped.
2. The numbers, against the last run.
3. What changed on which platform.
4. What needs the founder — a login, an approval, a decision.
5. When the next run should happen.
