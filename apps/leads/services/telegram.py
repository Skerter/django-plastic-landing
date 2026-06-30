import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

API_URL = "https://api.telegram.org/bot{token}/sendMessage"


def notify_telegram(lead_id: int) -> None:
    """Отправить уведомление о новой заявке в Telegram.

    Шлёт ``Lead.as_message()`` через Bot API (``sendMessage``). Токен бота —
    из ``settings.TELEGRAM_BOT_TOKEN``, чат — ``SiteSettings.telegram_chat_id``
    (задаётся в админке).

    Запускается как фоновая задача django-q2. Если токен или chat_id не заданы —
    логирует предупреждение и тихо выходит (ретраить нечего). Сетевые ошибки и
    не-2xx ответы пробрасываются, чтобы воркер повторил задачу.

    Args:
        lead_id: PK заявки (:class:`~apps.leads.models.Lead`).
    """
    from apps.core.models import SiteSettings
    from apps.leads.models import Lead

    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = SiteSettings.get_solo().telegram_chat_id
    if not token or not chat_id:
        logger.warning("Telegram пропущен: нет токена или chat_id (заявка %s)", lead_id)
        return

    lead = Lead.objects.get(id=lead_id)
    response = requests.post(
        API_URL.format(token=token),
        json={"chat_id": chat_id, "text": lead.as_message()},
        timeout=10,
    )
    response.raise_for_status()
    logger.info("Telegram отправлен для заявки %s", lead_id)
