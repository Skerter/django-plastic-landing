import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def notify_email(lead_id: int) -> None:
    """Отправить уведомление о новой заявке на email.

    Получатель берётся из ``SiteSettings.email_notifications`` (задаётся в
    админке). Тело письма — ``Lead.as_message()``, отправитель —
    ``settings.DEFAULT_FROM_EMAIL``.

    Запускается как фоновая задача django-q2. Если получатель не задан —
    логирует предупреждение и тихо выходит (ретраить нечего). Ошибки SMTP
    пробрасываются, чтобы воркер повторил задачу.

    Args:
        lead_id: PK заявки (:class:`~apps.leads.models.Lead`).
    """
    from apps.core.models import SiteSettings
    from apps.leads.models import Lead

    recipient = SiteSettings.get_solo().email_notifications
    if not recipient:
        logger.warning(
            "Email пропущен: не задан email для уведомлений (заявка %s)", lead_id
        )
        return

    lead = Lead.objects.get(id=lead_id)
    send_mail(
        f"Новая заявка с сайта — {lead.name}",
        lead.as_message(),
        settings.DEFAULT_FROM_EMAIL,
        [recipient],
    )
    logger.info("Email отправлен для заявки %s", lead_id)
