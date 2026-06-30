from django.db import migrations


CATEGORIES = [
    {"name": "Канистры", "slug": "kanistry", "order": 1, "is_active": True},
    {"name": "Крышки", "slug": "kryshki", "order": 2, "is_active": True},
]

PRODUCTS = [
    {
        "category_slug": "kanistry",
        "name": "Канистра 1 л круглая с крышкой",
        "slug": "kanistra-1l-kruglaya",
        "badge": "Круглая",
        "description": "Компактная круглая канистра 1 литр с крышкой — для розлива и хранения небольших "
        "объёмов пищевых и технических жидкостей. Узкая горловина 40 мм обеспечивает "
        "аккуратный налив. Возможна окраска в любой цвет и рельефный логотип заказчика.",
        "is_active": True,
        "order": 0,
        "specs": [
            {"label": "Объём", "value": "1", "unit": "л", "order": 0},
            {"label": "Вес", "value": "65 ±10", "unit": "г", "order": 1},
            {"label": "Размеры", "value": "235×85×85", "unit": "мм", "order": 2},
            {"label": "Горловина", "value": "40", "unit": "мм", "order": 3},
            {"label": "Толщина стенки", "value": "0,9", "unit": "мм", "order": 4},
        ],
    },
    {
        "category_slug": "kanistry",
        "name": "Канистра 1 л с крышкой",
        "slug": "kanistra-1l",
        "badge": "Компактная",
        "description": "Канистра 1 литр с крышкой — компактная форма с горловиной 34 мм, удобна для "
        "хранения и транспортировки небольших партий жидкостей. Возможна окраска в любой "
        "цвет и нанесение рельефного логотипа.",
        "is_active": True,
        "order": 1,
        "specs": [
            {"label": "Объём", "value": "1", "unit": "л", "order": 0},
            {"label": "Вес", "value": "60 ±10", "unit": "г", "order": 1},
            {"label": "Размеры", "value": "235×95×55", "unit": "мм", "order": 2},
            {"label": "Горловина", "value": "34", "unit": "мм", "order": 3},
            {"label": "Толщина стенки", "value": "0,9", "unit": "мм", "order": 4},
        ],
    },
    {
        "category_slug": "kanistry",
        "name": "Канистра 5 л евроканистра штабелируемая",
        "slug": "kanistra-5l",
        "badge": "Евроканистра",
        "description": "Евроканистра 5 литров штабелируемая с мерной полосой. Штабелируется при хранении "
        "и перевозке, экономит место на складе. 4-рядная конструкция и горловина 45 мм. "
        "Возможна окраска в любой цвет и рельефный логотип заказчика.",
        "is_active": True,
        "order": 2,
        "specs": [
            {"label": "Объём", "value": "5", "unit": "л", "order": 0},
            {"label": "Вес", "value": "200 ±10", "unit": "г", "order": 1},
            {"label": "Размеры", "value": "245×190×145", "unit": "мм", "order": 2},
            {"label": "Горловина", "value": "45", "unit": "мм", "order": 3},
            {"label": "Толщина стенки", "value": "0,8", "unit": "мм", "order": 4},
            {
                "label": "Особенность",
                "value": "с мерной полосой, 4-рядная",
                "unit": "",
                "order": 5,
            },
        ],
    },
    {
        "category_slug": "kanistry",
        "name": "Канистра 10 л евроканистра штабелируемая",
        "slug": "kanistra-10l",
        "badge": "Евроканистра",
        "description": "Евроканистра 10 литров штабелируемая с мерной полосой. Прочная 3-рядная "
        "конструкция, горловина 45 мм, толщина стенки 1,2 мм. Штабелируется при хранении "
        "и перевозке. Возможна окраска в любой цвет и рельефный логотип.",
        "is_active": True,
        "order": 3,
        "specs": [
            {"label": "Объём", "value": "10", "unit": "л", "order": 0},
            {"label": "Вес", "value": "400 ±10", "unit": "г", "order": 1},
            {"label": "Размеры", "value": "290×215×180", "unit": "мм", "order": 2},
            {"label": "Горловина", "value": "45", "unit": "мм", "order": 3},
            {"label": "Толщина стенки", "value": "1,2", "unit": "мм", "order": 4},
            {
                "label": "Особенность",
                "value": "с мерной полосой, 3-рядная",
                "unit": "",
                "order": 5,
            },
        ],
    },
    {
        "category_slug": "kanistry",
        "name": "Канистра 20 л евроканистра штабелируемая",
        "slug": "kanistra-20l",
        "badge": "Евроканистра",
        "description": "Объёмная евроканистра для пищевых и технических жидкостей. Штабелируется при "
        "хранении и перевозке, оснащена мерной полосой и 2-рядной конструкцией для "
        "прочности. Возможна окраска в любой цвет и рельефный логотип заказчика.",
        "is_active": True,
        "order": 4,
        "specs": [
            {"label": "Объём", "value": "20", "unit": "л", "order": 0},
            {"label": "Вес", "value": "800 ±10", "unit": "г", "order": 1},
            {"label": "Размеры", "value": "310×290×240", "unit": "мм", "order": 2},
            {"label": "Горловина", "value": "55", "unit": "мм", "order": 3},
            {"label": "Толщина стенки", "value": "1,5", "unit": "мм", "order": 4},
            {
                "label": "Особенность",
                "value": "с мерной полосой, 2-рядная",
                "unit": "",
                "order": 5,
            },
        ],
    },
    {
        "category_slug": "kanistry",
        "name": "Канистра 30 л евроканистра штабелируемая",
        "slug": "kanistra-30l",
        "badge": "Евроканистра",
        "description": "Евроканистра 30 литров штабелируемая с мерной полосой — максимальный объём в "
        "линейке. Усиленная 4-рядная конструкция, толщина стенки 2 мм, горловина 55 мм. "
        "Штабелируется при хранении и перевозке. Возможна окраска в любой цвет и "
        "рельефный логотип.",
        "is_active": True,
        "order": 5,
        "specs": [
            {"label": "Объём", "value": "30", "unit": "л", "order": 0},
            {"label": "Вес", "value": "1200 ±10", "unit": "г", "order": 1},
            {"label": "Размеры", "value": "440×300×265", "unit": "мм", "order": 2},
            {"label": "Горловина", "value": "55", "unit": "мм", "order": 3},
            {"label": "Толщина стенки", "value": "2", "unit": "мм", "order": 4},
            {
                "label": "Особенность",
                "value": "с мерной полосой, 4-рядная",
                "unit": "",
                "order": 5,
            },
        ],
    },
    {
        "category_slug": "kryshki",
        "name": "Крышка 45 мм",
        "slug": "kryshka-45-mm",
        "badge": "Крышка",
        "description": "Герметичная крышка диаметром 45 мм под горловину канистр 1, 5 и 10 литров. "
        "Надёжно закрывает тару, предотвращает протекание. Возможна окраска в любой цвет "
        "под партию заказчика.",
        "is_active": True,
        "order": 0,
        "specs": [
            {"label": "Диаметр", "value": "45", "unit": "мм", "order": 0},
            {
                "label": "Совместимость",
                "value": "канистры 1, 5, 10 л",
                "unit": "",
                "order": 1,
            },
        ],
    },
    {
        "category_slug": "kryshki",
        "name": "Крышка 55 мм",
        "slug": "kryshka-55",
        "badge": "Крышка",
        "description": "Герметичная крышка диаметром 55 мм под горловину канистр 20 и 30 литров. Плотно "
        "фиксируется, обеспечивает герметичность при хранении и перевозке. Возможна "
        "окраска в любой цвет.",
        "is_active": True,
        "order": 1,
        "specs": [
            {"label": "Диаметр", "value": "55", "unit": "мм", "order": 0},
            {
                "label": "Совместимость",
                "value": "канистры 20, 30 л",
                "unit": "",
                "order": 1,
            },
        ],
    },
    {
        "category_slug": "kryshki",
        "name": "Клапан сброса давления",
        "slug": "klapan-sbrosa-davleniya",
        "badge": "Клапан",
        "description": "Клапан сброса давления для пластиковой тары. Компенсирует перепады давления "
        "внутри канистры при перевозке и хранении, предотвращает деформацию. Наружный "
        "диаметр 15 мм.",
        "is_active": True,
        "order": 2,
        "specs": [
            {"label": "Высота", "value": "9", "unit": "мм", "order": 0},
            {"label": "Наружный диаметр", "value": "15", "unit": "мм", "order": 1},
            {"label": "Внутренний диаметр", "value": "13", "unit": "мм", "order": 2},
        ],
    },
]


def seed(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Product = apps.get_model("catalog", "Product")
    ProductSpec = apps.get_model("catalog", "ProductSpec")

    cat_by_slug = {}
    for c in CATEGORIES:
        obj, _ = Category.objects.update_or_create(
            slug=c["slug"],
            defaults={
                "name": c["name"],
                "order": c["order"],
                "is_active": c["is_active"],
            },
        )
        cat_by_slug[c["slug"]] = obj

    for p in PRODUCTS:
        specs = p["specs"]
        product, _ = Product.objects.update_or_create(
            slug=p["slug"],
            defaults={
                "category": cat_by_slug[p["category_slug"]],
                "name": p["name"],
                "badge": p["badge"],
                "description": p["description"],
                "is_active": p["is_active"],
                "order": p["order"],
            },
        )
        # спеки key-value без своего ключа → пересоздаём, чтобы не плодить дубли
        product.specs.all().delete()
        for s in specs:
            ProductSpec.objects.create(product=product, **s)


def unseed(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Product = apps.get_model("catalog", "Product")
    slugs = [p["slug"] for p in PRODUCTS]
    Product.objects.filter(slug__in=slugs).delete()  # спеки уйдут каскадом
    Category.objects.filter(slug__in=[c["slug"] for c in CATEGORIES]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0003_productimage"),
    ]
    operations = [
        migrations.RunPython(seed, unseed),
    ]
