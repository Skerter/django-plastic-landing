import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

API_URL = "https://api.telegram.org/bot{token}/sendMessage"


def notify_telegram(lead_id: int) -> None:
    """Send a Telegram notification about a new lead.

    Sends ``Lead.as_message()`` through the Bot API (``sendMessage``). The bot
    token comes from ``settings.TELEGRAM_BOT_TOKEN``, the chat from
    ``SiteSettings.telegram_chat_id`` (set in the admin).

    Runs as a django-q2 background task. If the token or the chat_id is missing,
    logs a warning and exits quietly (there is nothing to retry). Network errors
    and non-2xx responses propagate, so the worker retries the task.

    Args:
        lead_id: PK of the lead (:class:`~apps.leads.models.Lead`).
    """
    from apps.core.models import SiteSettings
    from apps.leads.models import Lead

    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = SiteSettings.get_solo().telegram_chat_id
    if not token or not chat_id:
        logger.warning("Telegram skipped: no token or chat_id (lead %s)", lead_id)
        return

    lead = Lead.objects.get(id=lead_id)
    response = requests.post(
        API_URL.format(token=token),
        json={"chat_id": chat_id, "text": lead.as_message()},
        timeout=10,
    )
    response.raise_for_status()
    logger.info("Telegram sent for lead %s", lead_id)
