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
    """Обменять refresh-токен на новую пару токенов и сохранить её.

    amoCRM ротирует refresh-токен при каждом обновлении, поэтому новая пара
    (access + refresh + срок) сразу пишется в синглтон ``auth``.

    Args:
        auth: Синглтон :class:`~apps.leads.models.AmoCRMAuth`; обновляется на месте.

    Returns:
        Новый access-токен.

    Raises:
        requests.HTTPError: Если amoCRM отклонил запрос обновления.
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
    logger.info("amoCRM: токены обновлены")
    return auth.access_token


def _get_access_token(auth) -> str:
    """Вернуть действующий access-токен, обновив его при необходимости.

    Токен считается истёкшим (и обновляется проактивно) за
    ``TOKEN_REFRESH_MARGIN`` до фактического срока — так запрос не уйдёт с
    токеном, который протухнет в полёте.

    Args:
        auth: Синглтон :class:`~apps.leads.models.AmoCRMAuth` с токенами.

    Returns:
        Действующий access-токен.
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
    """Выгрузить заявку в amoCRM: создать контакт и привязанную сделку.

    Запускается как фоновая задача django-q2. Использует OAuth 2.0 с
    автоматическим обновлением токена (см. :func:`_get_access_token`).

    Тихо пропускает заявку (warning, без ретрая), если интеграция не настроена
    (нет ``AMOCRM_*`` в окружении) или ещё не пройдена первичная авторизация
    (команда ``amocrm_auth``). Ошибки HTTP при создании контакта/сделки
    пробрасываются, чтобы воркер повторил задачу.

    Args:
        lead_id: PK заявки (:class:`~apps.leads.models.Lead`).
    """
    from apps.leads.models import AmoCRMAuth, Lead

    if not _is_configured():
        logger.warning("amoCRM пропущен: интеграция не настроена (заявка %s)", lead_id)
        return

    auth = AmoCRMAuth.get_solo()
    if not auth.refresh_token:
        logger.warning(
            "amoCRM пропущен: нет авторизации (команда amocrm_auth), заявка %s", lead_id
        )
        return

    lead = Lead.objects.get(id=lead_id)
    token = _get_access_token(auth)
    contact_id = _create_contact(lead, token)
    _create_lead(lead, contact_id, token)
    logger.info("amoCRM: заявка %s выгружена (контакт %s)", lead_id, contact_id)
