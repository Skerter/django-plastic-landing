from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from apps.catalog.sitemaps import CategorySitemap, ProductSitemap


admin.site.site_header = "Панель управления"  # large heading at the top of the admin
admin.site.site_title = "Панель управления"  # the browser tab text (<title>)
# the subheading on the admin index page
admin.site.index_title = "Настройка каталога, заявок и контактов сайта"

sitemaps = {
    "categories": CategorySitemap,
    "products": ProductSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.pages.urls")),
    path("catalog/", include("apps.catalog.urls")),
    path("", include("apps.leads.urls")),
    path("", include("apps.core.urls")),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]

# Serving uploaded media files from the dev server (Nginx/WhiteNoise in production).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
