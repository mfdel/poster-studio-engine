#!/usr/bin/env python3
"""
Decode a PNG that was captured as base64 from the Gemini browser session.

The integrated browser can't reliably trigger a file download for
googleusercontent/blob image URLs (CORS), so the Gemini figure workflow grabs
the generated image off a ``<canvas>`` as a base64 PNG via ``run_playwright_code``.
That base64 lands in a tool "resource file" on disk. This script pulls the PNG
base64 out of any such text file (it locates the PNG magic prefix
``iVBORw0KGgo`` and reads the contiguous base64 run) and writes the decoded
image to the target path.

Usage
-----
    python studio/assets/save_b64_png.py <resource_or_b64_file> <output.png>

The input may be the raw base64 itself or the full ``Result: "<b64>" ...`` tool
dump — either works, because extraction keys off the PNG magic prefix.
"""
from __future__ import annotations

import base64
import re
import sys
from pathlib import Path

PNG_B64_PREFIX = "iVBORw0KGgo"  # base64 of the PNG signature bytes


def extract_png_b64(text: str) -> str:
    start = text.find(PNG_B64_PREFIX)
    if start == -1:
        raise SystemExit("error: no PNG base64 (magic prefix) found in input")
    match = re.match(r"[A-Za-z0-9+/=]+", text[start:])
    if not match:
        raise SystemExit("error: could not read a base64 run at the PNG prefix")
    return match.group(0)


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(f"usage: {sys.argv[0]} <resource_or_b64_file> <output.png>")
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    text = src.read_text(encoding="utf-8", errors="replace")
    b64 = extract_png_b64(text)
    raw = base64.b64decode(b64)
    if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
        raise SystemExit("error: decoded bytes are not a valid PNG")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(raw)
    print(f"wrote {out} ({len(raw):,} bytes)")


if __name__ == "__main__":
    main()
