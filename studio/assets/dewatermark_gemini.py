#!/usr/bin/env python3
"""
Remove the Gemini sparkle watermark from renders — fully local, no upload.

Gemini stamps a four-pointed sparkle over the bottom-right corner of its renders. It is
a plain **alpha composite of pure white** at a fixed inset from that corner:

    observed = (1 - a) * original + a * 255

so it is not a smudge to be painted over — it is an equation to be *inverted*:

    original = (observed - a * 255) / (1 - a)

Because the glyph is byte-identical in every render, its per-pixel alpha was solved once
from a batch of before/after pairs and stored in ``gemini_sparkle_alpha.png`` (54x54,
16-bit, alpha peak 0.327). Inverting with it recovers the real texture underneath rather
than inventing plausible pixels, and touches nothing outside the glyph's 54x54 footprint.

Peak alpha 0.327 means noise is amplified by at most 1/(1-0.327) = 1.48x — mild. The one
place inversion is inherently uncertain is where the glyph sits on near-white content,
which carries little information about what the overlay hid.

Calibration
-----------
Geometry was measured on 928x1152 Gemini renders: a 54x54 patch inset (147, 147) from the
bottom-right corner. The inset is corner-relative, so other sizes work as long as Gemini
draws the glyph at the same pixel size — spot-check a new size before trusting a batch.
``--check`` reports how strongly the expected glyph is actually present, and files where
it is absent are skipped rather than corrupted.

Usage
-----
    python studio/assets/dewatermark_gemini.py posters/fam001-playground-map/brand/ai-photos/raw -o posters/fam001-playground-map/brand/ai-photos/20260802
    python studio/assets/dewatermark_gemini.py "posters/fam001-playground-map/brand/ai-photos/raw/*.png" -o out/ --prefix ""
    python studio/assets/dewatermark_gemini.py posters/fam001-playground-map/brand/ai-photos/raw --check
"""
from __future__ import annotations

import argparse
import glob
import sys
from pathlib import Path

import cv2
import numpy as np

ALPHA_MASK = Path(__file__).with_name("gemini_sparkle_alpha.png")
INSET = (147, 147)  # (x, y) of the patch's top-left, measured back from the bottom-right corner
GLYPH_COLOUR = 255.0  # solved to exactly pure white
DETECT_MIN = -0.15  # below this the glyph is treated as absent; see glyph_strength()


def load_alpha() -> np.ndarray:
    patch = cv2.imread(str(ALPHA_MASK), cv2.IMREAD_UNCHANGED)
    if patch is None:
        raise SystemExit(f"missing alpha mask: {ALPHA_MASK}")
    return patch.astype(np.float64) / 65535.0


def place(alpha_patch: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    """Position the glyph patch at its fixed inset from the bottom-right corner."""
    h, w = shape
    ph, pw = alpha_patch.shape
    y0, x0 = h - INSET[1], w - INSET[0]
    if y0 < 0 or x0 < 0 or y0 + ph > h or x0 + pw > w:
        raise ValueError(f"glyph does not fit in a {w}x{h} image")
    full = np.zeros((h, w))
    full[y0 : y0 + ph, x0 : x0 + pw] = alpha_patch
    return full


def _edge_energy(gray: np.ndarray, rim: np.ndarray) -> float:
    g = np.abs(cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)) + np.abs(cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3))
    return float(g[rim].mean())


def glyph_strength(bgr: np.ndarray, alpha: np.ndarray) -> float:
    """How much flatter does the glyph's rim get if we un-composite? Positive means present.

    A present watermark leaves a seam exactly where its alpha changes fastest. Inverting the
    composite erases that seam; inverting an image that never had one *manufactures* one. So
    the sign of the change is the test, and it does not depend on image content the way a
    brightness-lift correlation does.

    Measured separation over this batch: glyph present >= -0.04, already clean <= -0.26
    (unrelated photos score far lower). DETECT_MIN sits between, with margin either side.
    """
    ga = np.abs(cv2.Sobel(alpha, cv2.CV_64F, 1, 0, ksize=3)) + np.abs(cv2.Sobel(alpha, cv2.CV_64F, 0, 1, ksize=3))
    if not (ga > 0).any():
        return 0.0
    rim = ga > np.percentile(ga[ga > 0], 60)

    a = alpha[..., None]
    fixed = np.clip((bgr - a * GLYPH_COLOUR) / np.maximum(1.0 - a, 1e-6), 0, 255)
    before = _edge_energy(bgr.mean(2), rim)
    after = _edge_energy(np.where(a > 0, fixed, bgr).mean(2), rim)
    return (before - after) / max(before, 1e-6)


def uncomposite(img: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    bgr = img[..., :3].astype(np.float64)
    a = alpha[..., None]
    out = np.clip((bgr - a * GLYPH_COLOUR) / np.maximum(1.0 - a, 1e-6), 0, 255)
    out = np.where(a > 0, out, bgr).astype(np.uint8)
    return np.dstack([out, img[..., 3]]) if img.ndim == 3 and img.shape[2] == 4 else out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", help="image file, directory, or glob")
    ap.add_argument("-o", "--outdir", help="where to write results (required unless --check)")
    ap.add_argument("--prefix", default="watermark-removed-", help="output filename prefix")
    ap.add_argument("--check", action="store_true", help="report glyph presence, write nothing")
    args = ap.parse_args()

    src = Path(args.src)
    if src.is_dir():
        files = sorted(p for p in src.iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"})
    elif any(c in args.src for c in "*?["):
        files = sorted(Path(p) for p in glob.glob(args.src))
    else:
        files = [src]
    if not files:
        return print(f"no images matched {args.src}") or 1
    if not args.check and not args.outdir:
        return print("need -o/--outdir (or use --check)") or 1

    patch = load_alpha()
    outdir = Path(args.outdir) if args.outdir else None
    if outdir:
        outdir.mkdir(parents=True, exist_ok=True)

    cleaned = skipped = 0
    for f in files:
        img = cv2.imread(str(f), cv2.IMREAD_UNCHANGED)
        if img is None:
            print(f"  !! unreadable: {f.name}")
            continue
        try:
            alpha = place(patch, img.shape[:2])
        except ValueError as e:
            print(f"  !! {f.name}: {e}")
            skipped += 1
            continue

        strength = glyph_strength(img[..., :3].astype(np.float64), alpha)
        if strength < DETECT_MIN:
            print(f"  -- {f.name}: no glyph detected (corr {strength:.2f}) — skipped")
            skipped += 1
            continue
        if args.check:
            print(f"  ok {f.name}: glyph present (corr {strength:.2f})")
            cleaned += 1
            continue

        target = outdir / f"{args.prefix}{f.name}"
        cv2.imwrite(str(target), uncomposite(img, alpha), [cv2.IMWRITE_PNG_COMPRESSION, 6])
        print(f"  ✓ {f.name} → {target.name}  (corr {strength:.2f})")
        cleaned += 1

    verb = "detected in" if args.check else "cleaned"
    print(f"\n{verb} {cleaned} file(s)" + (f", skipped {skipped}" if skipped else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
