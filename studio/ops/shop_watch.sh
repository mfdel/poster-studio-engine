#!/bin/bash
# Live view of the scheduled shop-marketing session.
#
# The transcript in temp_dir/shop-run/ stays empty until the run ends, because `claude -p` buffers
# its output. This script follows the Claude Code session file instead, which is appended after
# every step, and prints one readable line per step.
#
# Usage:
#   studio/ops/shop_watch.sh          follow the newest session
#   studio/ops/shop_watch.sh --status one-line check, then exit

set -uo pipefail

SESSIONS="$HOME/.claude/projects/-Users-fuat-deligoz-code-playground-map"
LOG_DIR="/Users/fuat.deligoz/code/playground-map/temp_dir/shop-run"
LABEL="com.hopscotchmaps.shoprun"

running_pid="$(pgrep -f 'studio/ops/shop_run.sh' | head -1)"

if [ -n "$running_pid" ]; then
  started="$(ps -o etime= -p "$running_pid" | tr -d ' ')"
  echo "shop-run RUNNING — pid $running_pid, elapsed $started"
else
  echo "shop-run not running. Last transcript:"
  ls -1t "$LOG_DIR"/*.log 2>/dev/null | head -1
  echo "Next fire: $(launchctl print "gui/$(id -u)/$LABEL" 2>/dev/null | grep -m1 'next fire' || echo 'Mon and Thu 13:00')"
fi

[ "${1:-}" = "--status" ] && exit 0

# Pick the newest session that is a shop run, not an interactive chat. Every scheduled run starts
# with the marker below, so it separates the run from any Claude Code window that is also open.
SESSION=""
while IFS= read -r candidate; do
  if grep -lq 'scheduled AUTO run' "$candidate" 2>/dev/null; then
    SESSION="$candidate"
    break
  fi
done < <(ls -1t "$SESSIONS"/*.jsonl 2>/dev/null | head -12)

# Fall back to the newest session of any kind.
if [ -z "$SESSION" ]; then
  SESSION="$(ls -1t "$SESSIONS"/*.jsonl 2>/dev/null | head -1)"
  echo "No shop-run session found. Falling back to the newest session."
fi

if [ -z "$SESSION" ]; then
  echo "No session file in $SESSIONS"
  exit 1
fi

echo "Following $(basename "$SESSION")  (Ctrl-C to stop)"
echo "---"

tail -n 20 -f "$SESSION" | python3 -u -c '
import sys, json, time

def show(line):
    try:
        d = json.loads(line)
    except Exception:
        return
    msg = d.get("message") or {}
    content = msg.get("content")
    stamp = time.strftime("%H:%M:%S")
    if isinstance(content, str):
        content = [{"type": "text", "text": content}]
    if not isinstance(content, list):
        return
    for block in content:
        kind = block.get("type")
        if kind == "text":
            text = " ".join(block.get("text", "").split())
            if text:
                print(f"{stamp}  . {text[:160]}")
        elif kind == "tool_use":
            name = block.get("name", "?")
            args = json.dumps(block.get("input", {}))
            args = " ".join(args.split())
            print(f"{stamp}  > {name}  {args[:120]}")
        elif kind == "tool_result":
            if block.get("is_error"):
                body = block.get("content")
                if isinstance(body, list):
                    body = " ".join(b.get("text", "") for b in body if isinstance(b, dict))
                body = " ".join(str(body).split())
                print(f"{stamp}  ! ERROR  {body[:160]}")

for line in sys.stdin:
    show(line)
'
