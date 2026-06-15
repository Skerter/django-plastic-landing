from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import AmoCRMAuth, Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'type', 'status', 'created_at']
    list_filter = ['status', 'type']
    readonly_fields = ['name', 'phone', 'email', 'comment', 'type', 'product', 'consent', 'created_at']


@admin.register(AmoCRMAuth)
class AmoCRMAuthAdmin(SingletonModelAdmin):
    readonly_fields = ['access_token', 'refresh_token', 'expires_at']
