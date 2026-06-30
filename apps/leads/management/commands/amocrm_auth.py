from datetime import timedelta

import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone


class Command(BaseCommand):
    help = "Разовый обмен authorization code amoCRM на пару токенов (сохраняет в БД)."

    def add_arguments(self, parser):
        parser.add_argument(
            "code", help="Authorization code из карточки интеграции amoCRM"
        )

    def handle(self, *args, **options):
        from apps.leads.models import AmoCRMAuth

        if not (
            settings.AMOCRM_BASE_URL
            and settings.AMOCRM_CLIENT_ID
            and settings.AMOCRM_CLIENT_SECRET
        ):
            raise CommandError(
                "Не заданы AMOCRM_BASE_URL / CLIENT_ID / CLIENT_SECRET в env."
            )

        response = requests.post(
            f"{settings.AMOCRM_BASE_URL}/oauth2/access_token",
            json={
                "client_id": settings.AMOCRM_CLIENT_ID,
                "client_secret": settings.AMOCRM_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": options["code"],
                "redirect_uri": settings.AMOCRM_REDIRECT_URI,
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        auth = AmoCRMAuth.get_solo()
        auth.access_token = data["access_token"]
        auth.refresh_token = data["refresh_token"]
        auth.expires_at = timezone.now() + timedelta(seconds=data["expires_in"])
        auth.save()

        self.stdout.write(self.style.SUCCESS("amoCRM: токены получены и сохранены."))
