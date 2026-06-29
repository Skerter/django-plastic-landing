"""
Оптимизация сканов сертификатов для галереи на «О компании».

Сертификаты — сканы документов на белом фоне. Замена фона не нужна:
просто ресайз до разумной ширины и конвертация в WebP.
Скан A4 на ~800px по ширине читается в сетке-превью и весит ~40-60КБ
вместо исходных ~400КБ.

    input/   certificate1.jpg certificate2.jpg ...
    →
    output/  certificate-1.webp certificate-2.webp ...

Запуск:
    uv run python scripts/prep_certs.py "C:/photos/certificates" "C:/photos/certificates_out"

Опции:
    --width     ширина в px (по умолчанию 800)
    --quality   качество WebP (по умолчанию 80)
"""
import argparse
import re
import sys
from pathlib import Path

from PIL import Image

EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def natural_key(name: str):
    """Сортировка с числом: certificate2 < certificate10."""
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", name)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="папка с исходными сканами")
    ap.add_argument("output", help="папка для результата")
    ap.add_argument("--width", type=int, default=800)
    ap.add_argument("--quality", type=int, default=80)
    args = ap.parse_args()

    in_dir = Path(args.input)
    out_dir = Path(args.output)
    if not in_dir.is_dir():
        print(f"нет папки: {in_dir}", file=sys.stderr)
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
        print(f"  {src.name} -> {out_file.name}  ({out_file.stat().st_size // 1024}КБ)")

    print(f"\nготово: {len(files)} файлов")
    return 0


if __name__ == "__main__":
    sys.exit(main())
