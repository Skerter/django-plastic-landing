"""Generates placeholder images for every product so the carousel gallery on the
product page works in the demo.

For each product several PNG views are created (Pillow) in media/products/, one
ProductImage per file. media/ is in .gitignore, so the images are not committed
but generated when the demo starts (see docker compose / README).

Idempotent: a repeated run deletes the previously created demo images
(ProductImage whose alt starts with DEMO_ALT_PREFIX) and creates them again.

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

# The alt prefix marks an image as demo-generated (this is what makes the command idempotent).
DEMO_ALT_PREFIX = "[demo] "

# Views: caption + background colour (the DemoPlast brand palette).
ANGLES = [
    ("вид спереди", (43, 92, 180)),  # brand
    ("вид сбоку", (30, 68, 136)),  # brand-700
    ("горловина", (232, 161, 58)),  # accent
]

SIZE = (900, 900)


def _make_png(title: str, subtitle: str, bg: tuple[int, int, int]) -> bytes:
    img = Image.new("RGB", SIZE, bg)
    draw = ImageDraw.Draw(img)

    # Thin placeholder frame.
    draw.rectangle(
        [20, 20, SIZE[0] - 20, SIZE[1] - 20], outline=(255, 255, 255), width=3
    )

    # Diagonal hatching, so the image reads as a stub.
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
    help = "Generates placeholder product images (so the demo carousel works)."

    def handle(self, *args, **options):
        if Image is None:
            self.stderr.write(
                self.style.ERROR("Pillow is not installed — skipping image generation.")
            )
            return

        deleted, _ = ProductImage.objects.filter(
            alt__startswith=DEMO_ALT_PREFIX
        ).delete()
        if deleted:
            self.stdout.write(f"Previous demo images deleted: {deleted}")

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
                f"Demo images created: {created} for products: {products.count()}"
            )
        )
