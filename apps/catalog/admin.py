from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductSpec, ProductImage


class ThumbMixin:
    @admin.display(description="Превью")
    def thumb(self, obj):
        if not obj.image:
            return "—"
        return format_html(
            '<img src="{}" style="height:48px;width:auto;border:1px solid #ddd;" />',
            obj.image.url,
        )


class ProductSpecInline(admin.TabularInline):
    model = ProductSpec
    extra = 1


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(ThumbMixin, admin.ModelAdmin):
    list_display = ["thumb", "name", "order", "is_active"]
    list_filter = ["is_active"]
    prepopulated_fields = {"slug": ["name"]}


@admin.register(Product)
class ProductAdmin(ThumbMixin, admin.ModelAdmin):
    list_display = ["thumb", "name", "category", "badge", "order", "is_active"]
    list_filter = ["is_active", "category"]
    prepopulated_fields = {"slug": ["name"]}
    inlines = [ProductImageInline, ProductSpecInline]
