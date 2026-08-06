import logging
from datetime import timedelta

import requests
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 10
TOKEN_REFRESH_MARGIN = timedelta(minutes=5)


def _is_configured() -> bool:
    return bool(
        settings.AMOCRM_BASE_URL
        and settings.AMOCRM_CLIENT_ID
        and settings.AMOCRM_CLIENT_SECRET
    )


def _post(path: str, payload: list, token: str) -> dict:
    response = requests.post(
        f"{settings.AMOCRM_BASE_URL}{path}",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def _refresh_tokens(auth) -> str:
    """Exchange the refresh token for a new token pair and store it.

    amoCRM rotates the refresh token on every refresh, so the new pair
    (access + refresh + expiry) is written to the ``auth`` singleton at once.

    Args:
        auth: The :class:`~apps.leads.models.AmoCRMAuth` singleton; updated in place.

    Returns:
        The new access token.

    Raises:
        requests.HTTPError: If amoCRM rejected the refresh request.
    """
    response = requests.post(
        f"{settings.AMOCRM_BASE_URL}/oauth2/access_token",
        json={
            "client_id": settings.AMOCRM_CLIENT_ID,
            "client_secret": settings.AMOCRM_CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": auth.refresh_token,
            "redirect_uri": settings.AMOCRM_REDIRECT_URI,
        },
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    data = response.json()
    auth.access_token = data["access_token"]
    auth.refresh_token = data["refresh_token"]
    auth.expires_at = timezone.now() + timedelta(seconds=data["expires_in"])
    auth.save()
    logger.info("amoCRM: tokens refreshed")
    return auth.access_token


def _get_access_token(auth) -> str:
    """Return a valid access token, refreshing it if needed.

    The token counts as expired (and is refreshed proactively)
    ``TOKEN_REFRESH_MARGIN`` before its actual expiry, so a request never goes
    out with a token that dies in flight.

    Args:
        auth: The :class:`~apps.leads.models.AmoCRMAuth` singleton holding the tokens.

    Returns:
        A valid access token.
    """
    expired = (
        not auth.access_token
        or not auth.expires_at
        or auth.expires_at <= timezone.now() + TOKEN_REFRESH_MARGIN
    )
    return _refresh_tokens(auth) if expired else auth.access_token


def _create_contact(lead, token: str) -> int:
    custom_fields = [
        {"field_code": "PHONE", "values": [{"value": lead.phone, "enum_code": "WORK"}]},
    ]
    if lead.email:
        custom_fields.append(
            {
                "field_code": "EMAIL",
                "values": [{"value": lead.email, "enum_code": "WORK"}],
            }
        )
    payload = [{"name": lead.name, "custom_fields_values": custom_fields}]
    data = _post("/api/v4/contacts", payload, token)
    return data["_embedded"]["contacts"][0]["id"]


def _create_lead(lead, contact_id: int, token: str) -> int:
    deal = {
        "name": f"Заявка с сайта — {lead.name}",
        "_embedded": {"contacts": [{"id": contact_id}]},
    }
    if settings.AMOCRM_PIPELINE_ID:
        deal["pipeline_id"] = settings.AMOCRM_PIPELINE_ID
    if settings.AMOCRM_STATUS_ID:
        deal["status_id"] = settings.AMOCRM_STATUS_ID
    data = _post("/api/v4/leads", [deal], token)
    return data["_embedded"]["leads"][0]["id"]


def push_lead_to_amocrm(lead_id: int) -> None:
    """Push a lead to amoCRM: create a contact and a deal linked to it.

    Runs as a django-q2 background task. Uses OAuth 2.0 with automatic token
    refresh (see :func:`_get_access_token`).

    Silently skips the lead (warning, no retry) if the integration is not
    configured (no ``AMOCRM_*`` in the environment) or the initial authorization
    has not been done yet (the ``amocrm_auth`` command). HTTP errors raised while
    creating the contact or the deal propagate, so the worker retries the task.

    Args:
        lead_id: PK of the lead (:class:`~apps.leads.models.Lead`).
    """
    from apps.leads.models import AmoCRMAuth, Lead

    if not _is_configured():
        logger.warning(
            "amoCRM skipped: integration is not configured (lead %s)", lead_id
        )
        return

    auth = AmoCRMAuth.get_solo()
    if not auth.refresh_token:
        logger.warning(
            "amoCRM skipped: not authorized (run the amocrm_auth command), lead %s",
            lead_id,
        )
        return

    lead = Lead.objects.get(id=lead_id)
    token = _get_access_token(auth)
    contact_id = _create_contact(lead, token)
    _create_lead(lead, contact_id, token)
    logger.info("amoCRM: lead %s pushed (contact %s)", lead_id, contact_id)
