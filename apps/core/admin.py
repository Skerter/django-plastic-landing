from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonModelAdmin):
    fieldsets = (
        ('Контакты', {
            'fields': (
                'company_name',
                'phone_sales', 'phone_sales_person', 'email_sales',
                'phone_production', 'phone_production_person',
                'phone_accounting', 'email_accounting',
            ),
        }),
        ('Адрес и режим', {
            'fields': ('address', 'work_hours', 'work_hours_weekend', 'map_query'),
        }),
        ('Реквизиты', {
            'fields': (
                'legal_address', 'inn', 'kpp', 'ogrn', 'okpo',
                'account', 'bank', 'bik', 'corr_account',
            ),
        }),
        ('Уведомления и аналитика', {
            'fields': (
                'metrika_id',
                'notify_email_enabled', 'email_notifications',
                'notify_telegram_enabled', 'telegram_chat_id',
                'notify_amocrm_enabled',
            ),
        }),
    )
