import logging

from django.conf import settings
from django_q.tasks import async_task

logger = logging.getLogger(__name__)

NOTIFICATION_TASKS = [
    ("apps.leads.services.mail.notify_email", "notify_email_enabled"),
    ("apps.leads.services.telegram.notify_telegram", "notify_telegram_enabled"),
    ("apps.leads.services.amocrm.push_lead_to_amocrm", "notify_amocrm_enabled"),
]


def schedule_lead_notifications(lead_id: int) -> None:
    """Queue lead notifications for every enabled channel.

    For each channel in ``NOTIFICATION_TASKS`` the matching flag in
    ``SiteSettings`` is checked: a disabled channel is never queued at all.
    Queueing is wrapped in try/except per channel, so a failure in one of them
    (an unreachable broker, say) neither affects the others nor breaks the form.

    Called from the lead view after the ``Lead`` has been written to the database.

    Args:
        lead_id: PK of the saved lead (:class:`~apps.leads.models.Lead`).
    """
    from apps.core.models import SiteSettings

    # Demo mode: the lead is already in the database (the source of truth), but
    # nothing leaves the host — the public demo runs without real CRM/Telegram/SMTP keys.
    if settings.DEMO_MODE:
        logger.info("DEMO_MODE: notifications for lead %s skipped", lead_id)
        return

    site_settings = SiteSettings.get_solo()
    for task, flag in NOTIFICATION_TASKS:
        if not getattr(site_settings, flag):
            continue
        try:
            async_task(task, lead_id)
        except Exception:
            logger.exception("Failed to queue notification %s (lead %s)", task, lead_id)
