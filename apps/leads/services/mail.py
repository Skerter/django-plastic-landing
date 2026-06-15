import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def notify_email(lead_id: int) -> None:
    from apps.core.models import SiteSettings
    from apps.leads.models import Lead

    recipient = SiteSettings.get_solo().email_notifications
    if not recipient:
        logger.warning('Email пропущен: не задан email для уведомлений (заявка %s)', lead_id)
        return

    lead = Lead.objects.get(id=lead_id)
    send_mail(
        f'Новая заявка с сайта — {lead.name}',
        lead.as_message(),
        settings.DEFAULT_FROM_EMAIL,
        [recipient],
    )
    logger.info('Email отправлен для заявки %s', lead_id)
    


