"""
Prepares product photos for the catalogue cards.

The sources are studio packshots: the product on a flat light-blue background
(193,215,254). The script replaces that background with the brand light
#F4F6F9 (the surface token), fits the product into a square with margins,
resizes and saves as WebP. This is a chroma key over a flat background, NOT a
neural-network cutout (rembg is not needed).

Layout: input/ holds one subdirectory per product slug; the output names match
the slugs (for uploading into the admin as ProductImage) and the order is kept.

    input/
      kanistra-20l/  20-1.png 20-2.png ...
    →
    output/
      kanistra-20l/  kanistra-20l-1.webp kanistra-20l-2.webp ...

Usage:
    uv run python scripts/prep_photos.py "C:/photos/input" "C:/photos/output"

Options:
    --bg        background colour, hex (default #F4F6F9 — the surface token)
    --key       source blue background colour, hex (default #C1D7FE)
    --size      square side in px (default 1200)
    --margin    margin around the product, as a fraction of the side (default 0.06)
    --quality   WebP quality (default 82)
"""

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def hex_to_rgb(s: str) -> tuple[int, int, int]:
    s = s.lstrip("#")
    return tuple(int(s[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def swap_background(src: Path, bg: np.ndarray, key: np.ndarray) -> Image.Image:
    """Replace the flat blue source background with bg, return RGB without fringing."""
    a = np.asarray(Image.open(src).convert("RGB")).astype(float)
    dist = np.sqrt(((a - key) ** 2).sum(axis=2))

    # product mask 0..1 (1 = product), soft ramp over the distance to the background
    lo, hi = 30, 85
    prod = np.clip((dist - lo) / (hi - lo), 0, 1)

    # eat ~2px of fringe (erode) and soften the edge
    m = Image.fromarray((prod * 255).astype("uint8"))
    m = m.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(1.2))
    prod = np.asarray(m).astype(float) / 255

    # decontaminate: pull the blue out of the edge zone (towards luminance grey)
    edge = ((prod > 0.05) & (prod < 0.95))[..., None]
    neutral = np.repeat(a.mean(axis=2, keepdims=True), 3, axis=2)
    a = np.where(edge, a * 0.5 + neutral * 0.5, a)

    prod = prod[..., None]
    out = a * prod + bg * (1 - prod)
    return Image.fromarray(out.clip(0, 255).astype("uint8"))


def fit_square(
    img: Image.Image, bg: np.ndarray, size: int, margin: float
) -> Image.Image:
    """Crop to the product and fit it into a square on bg with margins."""
    arr = np.asarray(img).astype(int)
    # the product is the pixels that differ noticeably from the background
    mask = np.abs(arr - bg).sum(axis=2) > 24
    ys, xs = np.where(mask)
    canvas = Image.new("RGB", (size, size), tuple(int(c) for c in bg))
    if len(xs) == 0:  # nothing found — return a clean background
        return canvas

    box = img.crop((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1))
    inner = int(size * (1 - 2 * margin))
    w, h = box.size
    scale = min(inner / w, inner / h)
    box = box.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
    canvas.paste(box, ((size - box.width) // 2, (size - box.height) // 2))
    return canvas


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="directory with slug subdirectories of raw photos")
    ap.add_argument("output", help="output directory")
    ap.add_argument("--bg", default="#F4F6F9")
    ap.add_argument("--key", default="#C1D7FE")
    ap.add_argument("--size", type=int, default=1200)
    ap.add_argument("--margin", type=float, default=0.06)
    ap.add_argument("--quality", type=int, default=82)
    args = ap.parse_args()

    in_root = Path(args.input)
    out_root = Path(args.output)
    if not in_root.is_dir():
        print(f"no such directory: {in_root}", file=sys.stderr)
        return 1

    bg = np.array(hex_to_rgb(args.bg), dtype=float)
    key = np.array(hex_to_rgb(args.key), dtype=float)
    total = 0

    for sub in sorted(p for p in in_root.iterdir() if p.is_dir()):
        slug = sub.name
        files = sorted(
            (f for f in sub.iterdir() if f.suffix.lower() in EXTS),
            key=lambda f: f.name,
        )
        if not files:
            continue
        dst = out_root / slug
        dst.mkdir(parents=True, exist_ok=True)
        for i, src in enumerate(files, start=1):
            img = swap_background(src, bg, key)
            img = fit_square(img, bg, args.size, args.margin)
            out_file = dst / f"{slug}-{i}.webp"
            img.save(out_file, "WEBP", quality=args.quality, method=6)
            print(f"  {src.name} -> {out_file.name}")
            total += 1

    print(f"\ndone: {total} photos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
