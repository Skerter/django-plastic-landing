from django.contrib import admin
from django.utils.html import format_html
from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ["thumb", "title", "order", "is_active"]
    list_editable = ["order", "is_active"]
    list_filter = ["is_active"]

    @admin.display(description="Превью")
    def thumb(self, obj):
        if not obj.image:
            return "—"
        return format_html(
            '<img src="{}" style="height:48px;width:auto;border:1px solid #ddd;" />',
            obj.image.url,
        )
