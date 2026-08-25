# Ops — the scheduled shop session

This directory runs the marketing session on a schedule. The session itself is the `/shop-run`
skill in [`.claude/skills/shop-run/SKILL.md`](../../.claude/skills/shop-run/SKILL.md).

| File | Purpose |
|---|---|
| `shop_run.sh` | Runs `claude -p "/shop-run"`, writes a transcript, posts a macOS notification |
| `com.hopscotchmaps.shoprun.plist` | The launchd schedule — Monday and Thursday at 13:00 |
| `shop_watch.sh` | Shows a run step by step while it happens |

## Two ways to start a session

**By hand, in Claude Code:**

```
/shop-run
```

**On the schedule.** Install the LaunchAgent once:

```bash
chmod +x studio/ops/shop_run.sh
cp studio/ops/com.hopscotchmaps.shoprun.plist ~/Library/LaunchAgents/
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.hopscotchmaps.shoprun.plist
launchctl print gui/$(id -u)/com.hopscotchmaps.shoprun   # confirm it loaded
```

`bootstrap` often answers `Bootstrap failed: 5: Input/output error`. **This is not a failure.**
macOS loads a LaunchAgent by itself as soon as the plist appears in `~/Library/LaunchAgents/`, and
a second `bootstrap` of a label that is already loaded returns that error. Confirm the real state
with `launchctl print`. The job is installed when it prints `state = running` and
`active count = 1`.

Test it at once, without waiting for Monday:

```bash
launchctl kickstart -p gui/$(id -u)/com.hopscotchmaps.shoprun
```

Remove it:

```bash
launchctl bootout gui/$(id -u)/com.hopscotchmaps.shoprun
rm ~/Library/LaunchAgents/com.hopscotchmaps.shoprun.plist
```

Change the days or the time by editing `StartCalendarInterval` in the plist. After any edit you
must do three things in this order:

1. Copy the plist to `~/Library/LaunchAgents/` again.
2. Run `launchctl bootout gui/$(id -u)/com.hopscotchmaps.shoprun`.
3. Run `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.hopscotchmaps.shoprun.plist`.

launchd reads the copy in `~/Library/LaunchAgents/`, not the file in this repository. An edit that
is not copied has no effect.

## What the schedule needs

1. **You are logged in to the Mac desktop.** The Playwright MCP server drives a real Chrome window.
   A locked screen is usually fine. A logged-out account is not.
2. **The Mac is awake at the fire time.** launchd runs a missed job after the Mac wakes, but not
   while it sleeps.
3. **The platform logins are alive** in the MCP Chrome profile. Log in by hand once, in the Chrome
   window that the MCP server opens. The session then usually survives for weeks.
4. **The MCP profile must be free.** `shop_run.sh` handles this for you: before each run it ends
   any Chrome started against an `mcp-chrome-*` user-data-dir. Your personal Chrome uses a
   different directory and is never matched, so your own windows and tabs are safe. Platform
   logins live in the profile folder on disk and survive.

   Without that step a scheduled run fails, because an interactive Claude session leaves its
   automation Chrome running and that process holds the lock.

## Watch a run while it happens

```bash
studio/ops/shop_watch.sh            # follow the current run, one line per step
studio/ops/shop_watch.sh --status   # one line, then exit
```

The script prints one line per step: `>` is a tool call, `.` is the agent speaking, `!` is a tool
error. Stop it with Ctrl-C. Ctrl-C stops the watcher only. The run continues.

Do not watch `temp_dir/shop-run/<date>-<time>.log` for progress. That file stays empty until the run
ends, because `claude -p` holds its output until the end. `shop_watch.sh` follows the Claude Code
session file in `~/.claude/projects/-Users-fuat-deligoz-code-playground-map/`, which grows after
every step.

The second live view is the Chrome window itself. The Playwright MCP server drives a real window, so
you can watch each Etsy and Pinterest action.

## Where the output goes

- **Transcripts:** `temp_dir/shop-run/<date>-<time>.log`, last 40 kept. Not tracked by git.
- **launchd stdout and stderr:** `temp_dir/shop-run/launchd.out` and `launchd.err`.
- **The real record:** `studio/brand/shop-log.md`, `studio/brand/marketing-backlog.md` and
  `studio/brand/metrics.csv`. The run commits those three files, and does not push.

## When a run does nothing

Read the transcript first. The three usual causes are a dropped login, the profile lock, and an
empty backlog with no `approved` task. The run writes each of those into `shop-log.md` as well.

If the transcript shows tools being denied, add the missing rule to
`.claude/settings.local.json` under `permissions.allow`. Do not add
`--dangerously-skip-permissions` to `shop_run.sh`: this agent edits a live shop, and the allowlist
is the only thing between a bad step and the buyer-facing page.
