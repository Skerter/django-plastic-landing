"""Наполняет БД демо-заявками, чтобы админка (/admin/leads/lead/) не была пустой.

Идемпотентна: повторный запуск удаляет ранее созданные демо-заявки
(по фиктивным телефонам из диапазона +7 495 000-7X-XX) и создаёт их заново.

    python manage.py seed_demo_leads
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.catalog.models import Product
from apps.leads.models import Lead

# Все телефоны — вымышленные, диапазон 495 000-7X-XX зарезервирован под демо-заявки.
DEMO_LEADS = [
    {'name': 'Алексей Смирнов', 'phone': '+7 495 000-70-01', 'email': 'a.smirnov@example.com',
     'type': Lead.Type.ORDER, 'status': Lead.Status.NEW,
     'comment': 'Нужны канистры 20 л, партия 500 шт, окраска синяя.', 'days_ago': 0,
     'product_slug': 'kanistra-20l'},
    {'name': 'Мария Кузнецова', 'phone': '+7 495 000-70-02', 'email': '',
     'type': Lead.Type.CALLBACK, 'status': Lead.Status.NEW,
     'comment': '', 'days_ago': 1, 'product_slug': None},
    {'name': 'Дмитрий Орлов', 'phone': '+7 495 000-70-03', 'email': 'orlov@example.com',
     'type': Lead.Type.ORDER, 'status': Lead.Status.PROCESSED,
     'comment': 'Крышки 55 мм — уточните минимальную партию и сроки.', 'days_ago': 3,
     'product_slug': 'kryshka-55'},
    {'name': 'Елена Васильева', 'phone': '+7 495 000-70-04', 'email': 'e.vasileva@example.com',
     'type': Lead.Type.ORDER, 'status': Lead.Status.PROCESSED,
     'comment': 'Интересует евроканистра 10 л с логотипом.', 'days_ago': 7,
     'product_slug': 'kanistra-10l'},
]


class Command(BaseCommand):
    help = 'Создаёт демонстрационные заявки (Lead) для непустой админки.'

    def handle(self, *args, **options):
        demo_phones = [d['phone'] for d in DEMO_LEADS]
        deleted, _ = Lead.objects.filter(phone__in=demo_phones).delete()
        if deleted:
            self.stdout.write(f'Удалено прежних демо-заявок: {deleted}')

        created = 0
        for data in DEMO_LEADS:
            product = None
            if data['product_slug']:
                product = Product.objects.filter(slug=data['product_slug']).first()

            lead = Lead.objects.create(
                name=data['name'],
                phone=data['phone'],
                email=data['email'],
                comment=data['comment'],
                type=data['type'],
                status=data['status'],
                consent=True,
                product=product,
            )
            # created_at — auto_now_add, поэтому правим отдельным update, чтобы
            # заявки имели разные даты и выглядели реалистично в списке админки.
            Lead.objects.filter(pk=lead.pk).update(
                created_at=timezone.now() - timedelta(days=data['days_ago'])
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f'Создано демо-заявок: {created}'))
