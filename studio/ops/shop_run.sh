#!/bin/bash
# Scheduled shop-marketing session for Hopscotch Maps.
#
# Runs the /shop-run skill headless, writes a transcript, and posts a macOS notification.
# Installed by studio/ops/com.hopscotchmaps.shoprun.plist. See studio/ops/README.md.
#
# The Playwright MCP server drives a real Chrome window, so this only works while the founder is
# logged in to the Mac desktop. It does nothing useful over SSH or on a locked-out account.

set -uo pipefail

REPO="/Users/fuat.deligoz/code/playground-map"
CLAUDE="/Users/fuat.deligoz/.nvm/versions/node/v22.22.1/bin/claude"
LOG_DIR="$REPO/temp_dir/shop-run"
STAMP="$(date '+%Y-%m-%d-%H%M')"
LOG="$LOG_DIR/$STAMP.log"

mkdir -p "$LOG_DIR"
cd "$REPO" || exit 1

# launchd gives a bare PATH. Node, git and uv must be findable.
export PATH="/Users/fuat.deligoz/.nvm/versions/node/v22.22.1/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.local/bin"

# Release the Playwright MCP browser profile before the run.
#
# An interactive Claude session leaves its automation Chrome running, and that process holds the
# profile lock. Every navigate then fails with "Browser is already in use for .../mcp-chrome-<hash>".
# The pattern below matches ONLY Chrome started against an `mcp-chrome-*` user-data-dir. A normal
# Chrome uses ~/Library/Application Support/Google/Chrome and never matches, so personal windows,
# tabs and sessions are never touched. Logins live in the profile directory on disk and survive.
if pgrep -f "mcp-chrome-" >/dev/null 2>&1; then
  pkill -f "mcp-chrome-"
  sleep 3
fi

# Pass an argument to override the prompt. Used to smoke-test the plumbing without a real run.
DEFAULT_PROMPT="/shop-run This is the scheduled AUTO run. Follow every phase, respect the approval gate and the hard limits, and finish by writing shop-log.md, marketing-backlog.md and metrics.csv."
PROMPT="${1:-$DEFAULT_PROMPT}"

"$CLAUDE" -p "$PROMPT" --permission-mode acceptEdits >"$LOG" 2>&1
STATUS=$?

# Keep the last 40 transcripts.
ls -1t "$LOG_DIR"/*.log 2>/dev/null | tail -n +41 | while IFS= read -r f; do rm -f "$f"; done

if [ $STATUS -eq 0 ]; then
  SUMMARY="$(tail -n 4 "$LOG" | tr '\n' ' ' | cut -c1-180)"
  TITLE="Shop run finished"
else
  SUMMARY="exit $STATUS — see $LOG"
  TITLE="Shop run FAILED"
fi

osascript -e "display notification \"${SUMMARY//\"/\'}\" with title \"$TITLE\" subtitle \"$STAMP\"" 2>/dev/null

exit $STATUS
