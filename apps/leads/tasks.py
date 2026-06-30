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
    """Поставить в очередь уведомления о заявке по включённым каналам.

    Для каждого канала из ``NOTIFICATION_TASKS`` проверяет соответствующий
    флаг в ``SiteSettings``: выключенный канал не ставится в очередь вовсе.
    Постановка каждой задачи обёрнута в try/except, поэтому сбой одного канала
    (например, недоступность брокера) не мешает остальным и не ломает форму.

    Вызывается из вьюхи заявки после сохранения ``Lead`` в БД.

    Args:
        lead_id: PK сохранённой заявки (:class:`~apps.leads.models.Lead`).
    """
    from apps.core.models import SiteSettings

    # Демо-режим: заявка уже сохранена в БД (source of truth), но наружу ничего
    # не уходит — публичное демо работает без реальных ключей CRM/Telegram/SMTP.
    if settings.DEMO_MODE:
        logger.info("DEMO_MODE: уведомления для заявки %s пропущены", lead_id)
        return

    site_settings = SiteSettings.get_solo()
    for task, flag in NOTIFICATION_TASKS:
        if not getattr(site_settings, flag):
            continue
        try:
            async_task(task, lead_id)
        except Exception:
            logger.exception(
                "Не удалось обработать уведомление %s (заявка %s)", task, lead_id
            )
