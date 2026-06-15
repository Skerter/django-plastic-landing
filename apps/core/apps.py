from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Основные настройки'

    def ready(self):
        from django.contrib import admin
        from django.contrib.admin.sites import NotRegistered
        from django_q.models import Failure, OrmQ, Schedule, Success

        # Прячем служебные модели django_q из админки — заказчику они не нужны.
        for model in (Failure, OrmQ, Schedule, Success):
            try:
                admin.site.unregister(model)
            except NotRegistered:
                pass
