from django.contrib.sitemaps import Sitemap
from .models import Category, Product


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Category.objects.filter(is_active=True)

    def location(self, obj):
        return f"/catalog/{obj.slug}/"


class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Product.objects.filter(is_active=True)

    def location(self, obj):
        return f"/catalog/{obj.category.slug}/{obj.slug}/"
