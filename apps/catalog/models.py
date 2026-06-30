from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to="categories/", blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products"
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    badge = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Метка",
        help_text="Короткая метка-ярлык на фото карточки (напр. «Евроканистра», «Круглая»).",
    )
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="products/", blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.name


class ProductSpec(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="specs")
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=200)
    unit = models.CharField(max_length=50, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Характеристика"
        verbose_name_plural = "Характеристики"

    def __str__(self):
        return f"{self.label}: {self.value}"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="products/")
    alt = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Подпись",
        help_text="Подпись/ракурс (напр. «вид сбоку», «горловина 55 мм»). Используется как alt и подпись миниатюры.",
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Фото товара"
        verbose_name_plural = "Фото товара"

    def __str__(self):
        return self.alt or f"Фото #{self.pk}"
