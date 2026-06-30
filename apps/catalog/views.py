from django.shortcuts import render, get_object_or_404
from .models import Category, Product


def category_list(request):
    categories = Category.objects.filter(is_active=True)
    return render(
        request,
        "catalog/category_list.html",
        {
            "categories": categories,
            "active": "katalog",
        },
    )


def product_detail(request, category_slug, slug):
    product = get_object_or_404(
        Product.objects.select_related("category").prefetch_related("specs", "images"),
        slug=slug,
        is_active=True,
    )
    return render(
        request,
        "catalog/product_detail.html",
        {
            "product": product,
            "active": "katalog",
        },
    )


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = category.products.filter(is_active=True).select_related("category")
    return render(
        request,
        "catalog/category_detail.html",
        {
            "category": category,
            "products": products,
            "active": "katalog",
        },
    )
