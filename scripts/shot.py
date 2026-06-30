"""
Скриншоты страниц через Playwright (для визуальной проверки вёрстки).

Запуск (dev-сервер должен быть поднят отдельно):
    uv run python scripts/shot.py /catalog/ /catalog/kanistry/

Опции:
    --base   базовый URL (по умолчанию http://127.0.0.1:8009)
    --out    папка для скриншотов (по умолчанию .screenshots)
    --only   desktop | mobile (по умолчанию оба)

Имена файлов: <slug>__desktop.png / <slug>__mobile.png
"""

import argparse
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

VIEWPORTS = {
    "desktop": {"width": 1440, "height": 900},
    "mobile": {"width": 390, "height": 844},  # iPhone 12-ish
}


def slugify(path: str) -> str:
    s = path.strip("/").replace("/", "_") or "home"
    return s


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", help="пути страниц, напр. / /catalog/")
    ap.add_argument("--base", default="http://127.0.0.1:8009")
    ap.add_argument("--out", default=".screenshots")
    ap.add_argument("--only", choices=["desktop", "mobile"], default=None)
    ap.add_argument(
        "--consent",
        action="store_true",
        help="предустановить cookie_consent=accepted (скрыть баннер)",
    )
    ap.add_argument(
        "--selector",
        default=None,
        help="CSS-селектор: снять только этот элемент, а не всю страницу",
    )
    args = ap.parse_args()

    from urllib.parse import urlparse

    host = urlparse(args.base).hostname or "127.0.0.1"

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    targets = {args.only: VIEWPORTS[args.only]} if args.only else VIEWPORTS

    saved = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name, vp in targets.items():
            ctx = browser.new_context(viewport=vp, device_scale_factor=1)
            if args.consent:
                ctx.add_cookies(
                    [
                        {
                            "name": "cookie_consent",
                            "value": "accepted",
                            "domain": host,
                            "path": "/",
                        }
                    ]
                )
            page = ctx.new_page()
            for path in args.paths:
                url = args.base.rstrip("/") + path
                resp = page.goto(url, wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(350)  # дать отрисоваться шрифтам/анимации
                fname = out / f"{slugify(path)}__{name}.png"
                if args.selector:
                    page.locator(args.selector).first.screenshot(path=str(fname))
                else:
                    page.screenshot(path=str(fname), full_page=True)
                code = resp.status if resp else "?"
                saved.append(f"[{code}] {fname}")
            ctx.close()
        browser.close()

    print("\n".join(saved))
    return 0


if __name__ == "__main__":
    sys.exit(main())
