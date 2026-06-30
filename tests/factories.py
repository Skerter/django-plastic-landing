import factory

from apps.catalog.models import Category, Product, ProductImage, ProductSpec
from apps.leads.models import Lead
from apps.pages.models import Certificate


class LeadFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Lead

    name = "Иван"
    phone = "+79001234567"
    type = "order"
    consent = True


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Категория {n}")
    slug = factory.Sequence(lambda n: f"category-{n}")


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    category = factory.SubFactory(CategoryFactory)
    name = factory.Sequence(lambda n: f"Товар {n}")
    slug = factory.Sequence(lambda n: f"product-{n}")


class ProductSpecFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductSpec

    product = factory.SubFactory(ProductFactory)
    label = "Объём"
    value = "20"
    unit = "л"


class ProductImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductImage

    product = factory.SubFactory(ProductFactory)
    image = factory.django.ImageField(color="blue")
    alt = "вид сбоку"


class CertificateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Certificate

    title = factory.Sequence(lambda n: f"Сертификат {n}")
    image = factory.django.ImageField(color="blue")
