"""Генерирует плейсхолдер-картинки для всех товаров, чтобы галерея-карусель
на карточке товара была рабочей в демо.

На каждый товар создаётся несколько PNG-ракурсов (Pillow) в media/products/
и привязывается по одному ProductImage. media/ в .gitignore — поэтому картинки
не коммитятся, а создаются при запуске демо (см. docker compose / README).

Идемпотентна: повторный запуск удаляет ранее созданные демо-картинки
(ProductImage с alt, начинающимся на DEMO_ALT_PREFIX) и создаёт их заново.

    python manage.py seed_demo_images
"""

from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from apps.catalog.models import Product, ProductImage

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover
    Image = None

# Префикс в alt-поле помечает картинку как демо-сгенерированную (для идемпотентности).
DEMO_ALT_PREFIX = "[demo] "

# Ракурсы: подпись + фоновый цвет (фирменная палитра DemoPlast).
ANGLES = [
    ("вид спереди", (43, 92, 180)),  # brand
    ("вид сбоку", (30, 68, 136)),  # brand-700
    ("горловина", (232, 161, 58)),  # accent
]

SIZE = (900, 900)


def _make_png(title: str, subtitle: str, bg: tuple[int, int, int]) -> bytes:
    img = Image.new("RGB", SIZE, bg)
    draw = ImageDraw.Draw(img)

    # Тонкая рамка-плейсхолдер.
    draw.rectangle(
        [20, 20, SIZE[0] - 20, SIZE[1] - 20], outline=(255, 255, 255), width=3
    )

    # Диагональная штриховка — чтобы читалось как заглушка.
    for x in range(-SIZE[1], SIZE[0], 60):
        draw.line([(x, SIZE[1]), (x + SIZE[1], 0)], fill=(255, 255, 255, 30), width=1)

    try:
        font_big = ImageFont.truetype("DejaVuSans-Bold.ttf", 54)
        font_small = ImageFont.truetype("DejaVuSans.ttf", 34)
    except OSError:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()

    def centered(text, y, font):
        box = draw.textbbox((0, 0), text, font=font)
        w = box[2] - box[0]
        draw.text(((SIZE[0] - w) / 2, y), text, fill=(255, 255, 255), font=font)

    centered("DEMO", 300, font_big)
    centered(title, 390, font_small)
    centered(subtitle, 470, font_small)

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


class Command(BaseCommand):
    help = "Генерирует плейсхолдер-картинки товаров (для рабочей карусели в демо)."

    def handle(self, *args, **options):
        if Image is None:
            self.stderr.write(
                self.style.ERROR("Pillow не установлен — пропускаю генерацию картинок.")
            )
            return

        deleted, _ = ProductImage.objects.filter(
            alt__startswith=DEMO_ALT_PREFIX
        ).delete()
        if deleted:
            self.stdout.write(f"Удалено прежних демо-картинок: {deleted}")

        created = 0
        products = Product.objects.all()
        for product in products:
            for order, (angle, bg) in enumerate(ANGLES):
                png = _make_png(product.name[:28], angle, bg)
                pi = ProductImage(
                    product=product,
                    alt=f"{DEMO_ALT_PREFIX}{angle}",
                    order=order,
                )
                fname = f"demo-{product.slug}-{order}.png"
                pi.image.save(fname, ContentFile(png), save=True)
                created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Создано демо-картинок: {created} для товаров: {products.count()}"
            )
        )
