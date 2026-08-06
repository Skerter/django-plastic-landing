import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def notify_email(lead_id: int) -> None:
    """Send an email notification about a new lead.

    The recipient comes from ``SiteSettings.email_notifications`` (set in the
    admin). The body is ``Lead.as_message()``, the sender is
    ``settings.DEFAULT_FROM_EMAIL``.

    Runs as a django-q2 background task. If no recipient is set, logs a warning
    and exits quietly (there is nothing to retry). SMTP errors propagate, so the
    worker retries the task.

    Args:
        lead_id: PK of the lead (:class:`~apps.leads.models.Lead`).
    """
    from apps.core.models import SiteSettings
    from apps.leads.models import Lead

    recipient = SiteSettings.get_solo().email_notifications
    if not recipient:
        logger.warning(
            "Email skipped: no notification address is set (lead %s)", lead_id
        )
        return

    lead = Lead.objects.get(id=lead_id)
    send_mail(
        f"Новая заявка с сайта — {lead.name}",
        lead.as_message(),
        settings.DEFAULT_FROM_EMAIL,
        [recipient],
    )
    logger.info("Email sent for lead %s", lead_id)
