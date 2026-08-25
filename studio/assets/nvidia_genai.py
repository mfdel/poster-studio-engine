#!/usr/bin/env python3
"""Generate images and short videos with NVIDIA-hosted models (build.nvidia.com NIM API).

Free-tier API key from https://build.nvidia.com (click a model card -> "Get API Key").
This is NOT the OpenAI-compatible chat endpoint — image/video models use NVIDIA's own
`ai.api.nvidia.com/v1/genai/...` REST schema, one JSON shape per model.

Auth: put your key in a .env file at the repo root (gitignored):
    NVIDIA_API_KEY=nvapi-...

Run:
    uv run python studio/assets/nvidia_genai.py image "a watercolor illustration of a playground slide"
    uv run python studio/assets/nvidia_genai.py video temp_dir/nvidia_genai/some_image.jpg
    uv run python studio/assets/nvidia_genai.py edit brand/poster.png "place this poster in a sunlit room" --aspect-ratio 4:5

Notes:
  - `video` is image-to-video only (animates a still image) — Stable Video Diffusion has
    no text-to-video mode on this endpoint.
  - `edit` is image-conditioned generation (FLUX.1 Kontext dev) — composites/restyles a
    reference image per a text instruction. Diffusion-based, so fine detail (small text,
    thin lines) in the reference isn't guaranteed pixel-perfect in the output; regenerate
    with a different --seed if a result drifts too far.
  - `video`/`edit` reference images are auto-downscaled/recompressed to fit the API's
    inline base64 limit (<200KB, longest side <=1568px) — no manual prep needed.
  - Outputs default to temp_dir/ (gitignored, throwaway). Pass --out to keep a result
    somewhere permanent (e.g. brand/).

Docs:
  Image  (Stable Diffusion 3 Medium): https://docs.api.nvidia.com/nim/reference/stabilityai-stable-diffusion-3-medium-infer
  Video  (Stable Video Diffusion):    https://docs.api.nvidia.com/nim/reference/stabilityai-stable-video-diffusion-infer
  Edit   (FLUX.1 Kontext dev):        https://docs.api.nvidia.com/nim/reference/black-forest-labs-flux_1-kontext-dev-infer
"""
from __future__ import annotations

import argparse
import base64
import os
import sys
import time
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
IMAGE_URL = "https://ai.api.nvidia.com/v1/genai/stabilityai/stable-diffusion-3-medium"
VIDEO_URL = "https://ai.api.nvidia.com/v1/genai/stabilityai/stable-video-diffusion"
EDIT_URL = "https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.1-kontext-dev"
DEFAULT_OUT_DIR = REPO_ROOT / "temp_dir" / "nvidia_genai"
ASPECT_RATIOS = ["1:1", "16:9", "9:16", "5:4", "4:5", "3:2", "2:3"]
MAX_INLINE_IMAGE_BYTES = 200_000
REFERENCE_IMAGE_MAX_SIDE = 1568  # FLUX.1 Kontext's max supported width/height


def load_dotenv(path: Path) -> None:
    """Minimal .env loader so we don't add a dependency."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def api_key() -> str:
    load_dotenv(REPO_ROOT / ".env")
    key = os.environ.get("NVIDIA_API_KEY")
    if not key:
        print("ERROR: NVIDIA_API_KEY not set (add it to .env).", file=sys.stderr)
        sys.exit(1)
    return key


def generate_image(
    prompt: str,
    out_path: Path,
    *,
    negative_prompt: str = "",
    aspect_ratio: str = "1:1",
    cfg_scale: float = 5,
    steps: int = 50,
    seed: int = 0,
) -> Path:
    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "aspect_ratio": aspect_ratio,
        "cfg_scale": cfg_scale,
        "steps": steps,
        "seed": seed,
        "mode": "text-to-image",
        "model": "sd3",
        "output_format": "jpeg",
    }
    resp = requests.post(
        IMAGE_URL,
        headers={"Authorization": f"Bearer {api_key()}", "Accept": "application/json"},
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("finish_reason") != "SUCCESS":
        raise RuntimeError(f"image generation failed: {data.get('finish_reason')}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(base64.b64decode(data["image"]))
    return out_path


def _prepare_reference_image(
    image_path: Path,
    *,
    max_side: int = REFERENCE_IMAGE_MAX_SIDE,
    max_bytes: int = MAX_INLINE_IMAGE_BYTES,
) -> str:
    """Downscale/recompress an image so it fits inline as base64; return a data: URI."""
    from io import BytesIO

    from PIL import Image

    img = Image.open(image_path).convert("RGB")
    if max(img.size) > max_side:
        scale = max_side / max(img.size)
        size = (max(1, round(img.width * scale)), max(1, round(img.height * scale)))
        img = img.resize(size, Image.LANCZOS)

    data = b""
    for quality in (90, 80, 70, 60, 50, 40, 30):
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=quality)
        data = buf.getvalue()
        if len(data) <= max_bytes:
            break
    return "data:image/jpeg;base64," + base64.b64encode(data).decode()


def generate_video(
    image_path: Path,
    out_path: Path,
    *,
    cfg_scale: float = 1.8,
    seed: int = 0,
) -> Path:
    payload = {
        "image": _prepare_reference_image(image_path),
        "cfg_scale": cfg_scale,
        "seed": seed,
        "motion_bucket_id": 127,  # only value the API currently supports
    }
    resp = requests.post(
        VIDEO_URL,
        headers={"Authorization": f"Bearer {api_key()}", "Accept": "application/json"},
        json=payload,
        timeout=180,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("finish_reason") != "SUCCESS":
        raise RuntimeError(f"video generation failed: {data.get('finish_reason')}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(base64.b64decode(data["video"]))
    return out_path


def edit_image(
    image_path: Path,
    prompt: str,
    out_path: Path,
    *,
    aspect_ratio: str = "match_input_image",
    cfg_scale: float = 3.5,
    steps: int = 30,
    seed: int = 0,
) -> Path:
    """Image-conditioned edit/composite (FLUX.1 Kontext dev) — e.g. place a reference
    image into a new photorealistic scene while keeping its content recognisable."""
    payload = {
        "prompt": prompt,
        "image": _prepare_reference_image(image_path),
        "aspect_ratio": aspect_ratio,
        "cfg_scale": cfg_scale,
        "steps": steps,
        "seed": seed,
        "samples": 1,
    }
    resp = requests.post(
        EDIT_URL,
        headers={"Authorization": f"Bearer {api_key()}", "Accept": "application/json"},
        json=payload,
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    artifact = (data.get("artifacts") or [{}])[0]
    if artifact.get("finishReason") != "SUCCESS":
        raise RuntimeError(f"image edit failed: {artifact.get('finishReason')}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(base64.b64decode(artifact["base64"]))
    return out_path


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Generate images/video via NVIDIA-hosted models.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_img = sub.add_parser("image", help="text-to-image (Stable Diffusion 3 Medium)")
    p_img.add_argument("prompt")
    p_img.add_argument("--out", type=Path, default=None)
    p_img.add_argument("--negative-prompt", default="")
    p_img.add_argument("--aspect-ratio", default="1:1", choices=ASPECT_RATIOS)
    p_img.add_argument("--cfg-scale", type=float, default=5)
    p_img.add_argument("--steps", type=int, default=50)
    p_img.add_argument("--seed", type=int, default=0)

    p_vid = sub.add_parser("video", help="image-to-video (Stable Video Diffusion)")
    p_vid.add_argument("image", type=Path, help="source image, <200KB, scaled to 1024x576")
    p_vid.add_argument("--out", type=Path, default=None)
    p_vid.add_argument("--cfg-scale", type=float, default=1.8)
    p_vid.add_argument("--seed", type=int, default=0)

    p_edit = sub.add_parser("edit", help="image-conditioned edit/composite (FLUX.1 Kontext dev)")
    p_edit.add_argument("image", type=Path, help="reference image to edit/composite into a new scene")
    p_edit.add_argument("prompt")
    p_edit.add_argument("--out", type=Path, default=None)
    p_edit.add_argument("--aspect-ratio", default="match_input_image")
    p_edit.add_argument("--cfg-scale", type=float, default=3.5)
    p_edit.add_argument("--steps", type=int, default=30)
    p_edit.add_argument("--seed", type=int, default=0)

    args = parser.parse_args(argv)
    stamp = time.strftime("%Y%m%d-%H%M%S")

    if args.command == "image":
        out = args.out or DEFAULT_OUT_DIR / f"{stamp}_image.jpg"
        path = generate_image(
            args.prompt,
            out,
            negative_prompt=args.negative_prompt,
            aspect_ratio=args.aspect_ratio,
            cfg_scale=args.cfg_scale,
            steps=args.steps,
            seed=args.seed,
        )
        print(f"Saved {path}")
        return 0

    if args.command == "video":
        out = args.out or DEFAULT_OUT_DIR / f"{stamp}_video.mp4"
        path = generate_video(args.image, out, cfg_scale=args.cfg_scale, seed=args.seed)
        print(f"Saved {path}")
        return 0

    if args.command == "edit":
        out = args.out or DEFAULT_OUT_DIR / f"{stamp}_edit.jpg"
        path = edit_image(
            args.image,
            args.prompt,
            out,
            aspect_ratio=args.aspect_ratio,
            cfg_scale=args.cfg_scale,
            steps=args.steps,
            seed=args.seed,
        )
        print(f"Saved {path}")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
