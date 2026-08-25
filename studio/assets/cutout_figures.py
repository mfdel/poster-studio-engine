#!/usr/bin/env python3
"""
Cut figure stickers out of a flat solid-colour background → transparent PNG.

The image models (Gemini/"Nano Banana") cannot emit a real alpha channel, so we
prompt for a **plain solid single-colour background** (see
``docs/poster_figure_prompts.md``) and key it out here.

How it works
------------
1. Sample the background colour as the *median* of the border ring (robust even
   when part of the figure touches an edge).
2. **Flood-fill from the borders** through pixels close to that background colour,
   turning only the *border-connected* background transparent. Same-coloured
   regions fully enclosed by the figure are preserved (that's why we flood-fill
   instead of a global colour key). Pass ``--key-enclosed`` on a true chroma-key
   background (e.g. #00B140) to key those enclosed pockets too — a web's cells,
   the gap under a handle, the space between fence pickets.
3. Feather the 1px edge so no hard colour fringe remains.
4. Auto-crop to the figure's bounding box (+ padding) and save ``<name>_cut.png``.

If the border is *not* one uniform colour (e.g. a baked-in checkerboard from an
older generation), the file is skipped with a warning — re-generate it on a solid
background first.

Usage
-----
    python cutout_figures.py studio/themes/whimsy/Gemini_Generated_Image_i398ghi398ghi398.png
    python cutout_figures.py "studio/themes/whimsy/*.png" --pad 16 --tolerance 45
    python cutout_figures.py studio/themes/whimsy --outdir assets/figures/whimsy
"""
from __future__ import annotations

import argparse
import glob
import sys
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image


def _sample_background(rgb: np.ndarray) -> np.ndarray:
    """Median colour of the 1px border ring (robust to figure-touches-edge)."""
    top, bottom = rgb[0, :, :], rgb[-1, :, :]
    left, right = rgb[:, 0, :], rgb[:, -1, :]
    ring = np.concatenate([top, bottom, left, right], axis=0)
    return np.median(ring, axis=0)


def _border_uniformity(rgb: np.ndarray, bg: np.ndarray, tol: float) -> float:
    """Fraction of border pixels within ``tol`` of ``bg`` (checkerboard guard)."""
    top, bottom = rgb[0, :, :], rgb[-1, :, :]
    left, right = rgb[:, 0, :], rgb[:, -1, :]
    ring = np.concatenate([top, bottom, left, right], axis=0).astype(np.float32)
    dist = np.sqrt(((ring - bg) ** 2).sum(axis=1))
    return float((dist <= tol).mean())


def _flood_background(bg_like: np.ndarray) -> np.ndarray:
    """Boolean mask of background-like pixels *connected to the image border*."""
    h, w = bg_like.shape
    is_bg = np.zeros((h, w), dtype=bool)
    q: deque[tuple[int, int]] = deque()

    # Seed every border pixel that is background-like.
    for x in range(w):
        if bg_like[0, x]:
            q.append((0, x)); is_bg[0, x] = True
        if bg_like[h - 1, x]:
            q.append((h - 1, x)); is_bg[h - 1, x] = True
    for y in range(h):
        if bg_like[y, 0]:
            q.append((y, 0)); is_bg[y, 0] = True
        if bg_like[y, w - 1]:
            q.append((y, w - 1)); is_bg[y, w - 1] = True

    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and bg_like[ny, nx] and not is_bg[ny, nx]:
                is_bg[ny, nx] = True
                q.append((ny, nx))
    return is_bg


def cutout(path: Path, tolerance: float, pad: int, outdir: Path | None,
           suffix: str, key_enclosed: bool = False) -> tuple[bool, str]:
    im = Image.open(path).convert("RGBA")
    arr = np.asarray(im).astype(np.uint8).copy()
    rgb = arr[:, :, :3].astype(np.float32)

    bg = _sample_background(rgb)
    uniform = _border_uniformity(rgb, bg, tolerance)
    if uniform < 0.5:
        return False, (f"SKIP {path.name}: border only {uniform:.0%} uniform "
                       f"(baked-in checkerboard? re-generate on a solid background)")

    dist = np.sqrt(((rgb - bg) ** 2).sum(axis=2))
    bg_like = dist <= tolerance
    # Border-connected fill keeps same-coloured regions *enclosed* by the figure.
    # On a chroma-key background nothing inside the figure is ever that colour, so
    # --key-enclosed drops the flood fill and keys every matching pixel (a spider
    # web's cells, the gap under a bucket handle, the space between fence pickets).
    is_bg = bg_like if key_enclosed else _flood_background(bg_like)

    alpha = arr[:, :, 3].copy()
    alpha[is_bg] = 0

    # Feather: partly fade the 1px fringe just outside the cut to kill colour halo.
    # Pixels kept but adjacent to a cut pixel and still close-ish to bg → scale alpha.
    fringe = dist <= (tolerance * 1.6)
    edge = np.zeros_like(is_bg)
    edge[1:, :] |= is_bg[:-1, :]
    edge[:-1, :] |= is_bg[1:, :]
    edge[:, 1:] |= is_bg[:, :-1]
    edge[:, :-1] |= is_bg[:, 1:]
    soft = (~is_bg) & edge & fringe
    if soft.any():
        frac = np.clip((dist[soft] - tolerance) / (tolerance * 0.6), 0.0, 1.0)
        alpha[soft] = (alpha[soft] * frac).astype(np.uint8)

    arr[:, :, 3] = alpha

    # Auto-crop to the opaque bounding box (+ padding).
    ys, xs = np.where(alpha > 0)
    if len(xs) == 0:
        return False, f"SKIP {path.name}: nothing left after keying (tolerance too high?)"
    h, w = alpha.shape
    x0, x1 = max(0, xs.min() - pad), min(w, xs.max() + 1 + pad)
    y0, y1 = max(0, ys.min() - pad), min(h, ys.max() + 1 + pad)
    cropped = Image.fromarray(arr[y0:y1, x0:x1])

    dest_dir = outdir if outdir else path.parent
    dest_dir.mkdir(parents=True, exist_ok=True)
    stem = path.stem
    out = dest_dir / (f"{stem}{suffix}.png" if outdir is None
                      else f"{stem}.png")
    cropped.save(out)

    removed = 100 * is_bg.mean()
    return True, (f"OK   {path.name} -> {out.relative_to(Path.cwd()) if out.is_absolute() else out}"
                  f"  bg=rgb({int(bg[0])},{int(bg[1])},{int(bg[2])}) "
                  f"removed={removed:.0f}% crop={x1-x0}x{y1-y0}")


def _expand(inputs: list[str]) -> list[Path]:
    paths: list[Path] = []
    for item in inputs:
        p = Path(item)
        if p.is_dir():
            paths += sorted(x for x in p.glob("*.png") if not x.stem.endswith("_cut"))
        elif any(ch in item for ch in "*?[]"):
            paths += [Path(m) for m in sorted(glob.glob(item))
                      if not Path(m).stem.endswith("_cut")]
        else:
            paths.append(p)
    return paths


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+",
                    help="PNG file(s), a glob, or a folder of PNGs")
    ap.add_argument("--tolerance", type=float, default=42.0,
                    help="RGB distance treated as background (default 42)")
    ap.add_argument("--pad", type=int, default=14,
                    help="transparent padding kept around the figure (px, default 14)")
    ap.add_argument("--outdir", type=Path, default=None,
                    help="write here (keeps original name); default: next to source with --suffix")
    ap.add_argument("--key-enclosed", action="store_true",
                    help="also key background-coloured regions enclosed by the figure "
                         "(chroma-key backgrounds only — the figure must contain no such colour)")
    ap.add_argument("--suffix", default="_cut",
                    help="filename suffix when writing in place (default _cut)")
    args = ap.parse_args()

    paths = _expand(args.inputs)
    if not paths:
        sys.exit("No input PNGs found.")

    ok = 0
    for path in paths:
        if not path.exists():
            print(f"MISS {path}")
            continue
        success, msg = cutout(path, args.tolerance, args.pad, args.outdir,
                              args.suffix, args.key_enclosed)
        ok += success
        print(msg)
    print(f"\nDone: {ok}/{len(paths)} cut out.")


if __name__ == "__main__":
    main()
