"""
Optimizes certificate scans for the gallery on the "About" page.

Certificates are document scans on a white background. No background
replacement is needed: just a resize to a sensible width and a conversion to
WebP. An A4 scan at ~800px wide is readable in the preview grid and weighs
~40-60KB instead of the original ~400KB.

    input/   certificate1.jpg certificate2.jpg ...
    →
    output/  certificate-1.webp certificate-2.webp ...

Usage:
    uv run python scripts/prep_certs.py "C:/photos/certificates" "C:/photos/certificates_out"

Options:
    --width     width in px (default 800)
    --quality   WebP quality (default 80)
"""

import argparse
import re
import sys
from pathlib import Path

from PIL import Image

EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def natural_key(name: str):
    """Number-aware sorting: certificate2 < certificate10."""
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", name)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="directory with the source scans")
    ap.add_argument("output", help="output directory")
    ap.add_argument("--width", type=int, default=800)
    ap.add_argument("--quality", type=int, default=80)
    args = ap.parse_args()

    in_dir = Path(args.input)
    out_dir = Path(args.output)
    if not in_dir.is_dir():
        print(f"no such directory: {in_dir}", file=sys.stderr)
        return 1
    out_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(
        (f for f in in_dir.iterdir() if f.suffix.lower() in EXTS),
        key=lambda f: natural_key(f.name),
    )
    for i, src in enumerate(files, start=1):
        im = Image.open(src).convert("RGB")
        if im.width > args.width:
            h = round(im.height * args.width / im.width)
            im = im.resize((args.width, h), Image.LANCZOS)
        out_file = out_dir / f"certificate-{i}.webp"
        im.save(out_file, "WEBP", quality=args.quality, method=6)
        print(f"  {src.name} -> {out_file.name}  ({out_file.stat().st_size // 1024}KB)")

    print(f"\ndone: {len(files)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
