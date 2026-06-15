import pytest

from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from unittest.mock import MagicMock, patch
from datetime import timedelta

from apps.leads.forms import LeadForm
from apps.leads.models import AmoCRMAuth, Lead
from apps.leads.services.amocrm import push_lead_to_amocrm
from apps.leads.services.mail import notify_email
from apps.leads.services.telegram import notify_telegram
from apps.leads.tasks import schedule_lead_notifications
from apps.core.models import SiteSettings


VALID_DATA = {
    'name': 'Иван',
    'phone': '+79001234567',
    'type': 'order',
    'consent': True,
    'website': '',  # honeypot пустой — человек
}


@pytest.mark.django_db
def test_lead_form_valid():
    form = LeadForm(data=VALID_DATA)
    assert form.is_valid()


@pytest.mark.django_db
def test_lead_form_rejected_without_consent():
    data = {**VALID_DATA, 'consent': False}
    form = LeadForm(data=data)
    assert not form.is_valid()
    assert 'consent' in form.errors


@pytest.mark.django_db
def test_lead_form_rejected_with_honeypot():
    data = {**VALID_DATA, 'website': 'http://spam.com'}
    form = LeadForm(data=data)
    assert not form.is_valid()
    assert 'website' in form.errors


@pytest.mark.django_db
def test_lead_saved_with_consent_true():
    form = LeadForm(data=VALID_DATA)
    assert form.is_valid()
    lead = form.save(commit=False)
    lead.consent = True
    lead.save()
    assert Lead.objects.filter(name='Иван', consent=True).exists()


@pytest.mark.django_db
def test_email_notification_sent(mailoutbox):
    site_settings = SiteSettings.get_solo()
    site_settings.email_notifications = 'sales@demoplast.test'
    site_settings.save()
    lead = Lead.objects.create(name='Иван', phone='+79001234567', type='order', consent=True)

    notify_email(lead.id)

    assert len(mailoutbox) == 1
    msg = mailoutbox[0]
    assert msg.to == ['sales@demoplast.test']
    assert 'Иван' in msg.body
    assert '+79001234567' in msg.body


@pytest.mark.django_db
def test_email_skipped_without_recipient(mailoutbox):
    site_settings = SiteSettings.get_solo()
    site_settings.email_notifications = ''
    site_settings.save()
    lead = Lead.objects.create(name='Иван', phone='+79001234567', type='order', consent=True)

    notify_email(lead.id)

    assert len(mailoutbox) == 0


@pytest.mark.django_db
def test_lead_form_post_sends_email(client, mailoutbox):
    site_settings = SiteSettings.get_solo()
    site_settings.email_notifications = 'sales@demoplast.test'
    site_settings.save()

    response = client.post(reverse('lead_form'), data=VALID_DATA)

    assert response.status_code == 200
    assert Lead.objects.filter(name='Иван').exists()
    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == ['sales@demoplast.test']


@pytest.mark.django_db
def test_dispatcher_queues_only_enabled_channels():
    site_settings = SiteSettings.get_solo()
    site_settings.notify_email_enabled = True
    site_settings.notify_telegram_enabled = False
    site_settings.notify_amocrm_enabled = False
    site_settings.save()
    lead = Lead.objects.create(name='Иван', phone='+79001234567', type='order', consent=True)

    with patch('apps.leads.tasks.async_task') as mock_async:
        schedule_lead_notifications(lead.id)

    assert mock_async.call_count == 1
    assert mock_async.call_args.args[0] == 'apps.leads.services.mail.notify_email'


@pytest.mark.django_db
def test_telegram_notification_sent(settings):
    settings.TELEGRAM_BOT_TOKEN = 'TESTTOKEN'
    site_settings = SiteSettings.get_solo()
    site_settings.telegram_chat_id = '12345'
    site_settings.save()
    lead = Lead.objects.create(name='Иван', phone='+79001234567', type='order', consent=True)

    with patch('apps.leads.services.telegram.requests.post') as mock_post:
        notify_telegram(lead.id)

    assert mock_post.called
    _, kwargs = mock_post.call_args
    assert 'TESTTOKEN' in mock_post.call_args[0][0]
    assert kwargs['json']['chat_id'] == '12345'
    assert 'Иван' in kwargs['json']['text']


@pytest.mark.django_db
def test_telegram_skipped_without_config(settings):
    settings.TELEGRAM_BOT_TOKEN = ''
    site_settings = SiteSettings.get_solo()
    site_settings.telegram_chat_id = ''
    site_settings.save()
    lead = Lead.objects.create(name='Иван', phone='+79001234567', type='order', consent=True)

    with patch('apps.leads.services.telegram.requests.post') as mock_post:
        notify_telegram(lead.id)

    assert not mock_post.called

def _resp(json_data):
    response = MagicMock()
    response.raise_for_status.return_value = None
    response.json.return_value = json_data
    return response


@pytest.mark.django_db
def test_amocrm_skipped_without_credentials(settings):
    settings.AMOCRM_BASE_URL = ''
    settings.AMOCRM_CLIENT_ID = ''
    settings.AMOCRM_CLIENT_SECRET = ''
    lead = Lead.objects.create(name='Иван', phone='+79001234567', type='order', consent=True)

    with patch('apps.leads.services.amocrm.requests.post') as mock_post:
        push_lead_to_amocrm(lead.id)

    assert not mock_post.called


@pytest.mark.django_db
def test_amocrm_push_creates_contact_and_lead(settings):
    settings.AMOCRM_BASE_URL = 'https://test.amocrm.ru'
    settings.AMOCRM_CLIENT_ID = 'cid'
    settings.AMOCRM_CLIENT_SECRET = 'secret'
    settings.AMOCRM_PIPELINE_ID = 0
    settings.AMOCRM_STATUS_ID = 0

    auth = AmoCRMAuth.get_solo()
    auth.access_token = 'VALIDTOKEN'
    auth.refresh_token = 'refresh'
    auth.expires_at = timezone.now() + timedelta(hours=1)
    auth.save()

    lead = Lead.objects.create(name='Иван', phone='+79001234567', email='i@x.ru', type='order', consent=True)

    with patch('apps.leads.services.amocrm.requests.post') as mock_post:
        mock_post.side_effect = [
            _resp({'_embedded': {'contacts': [{'id': 111}]}}),
            _resp({'_embedded': {'leads': [{'id': 222}]}}),
        ]
        push_lead_to_amocrm(lead.id)

    assert mock_post.call_count == 2
    contact_call = mock_post.call_args_list[0]
    assert contact_call.args[0].endswith('/api/v4/contacts')
    assert contact_call.kwargs['headers']['Authorization'] == 'Bearer VALIDTOKEN'
    lead_call = mock_post.call_args_list[1]
    assert lead_call.args[0].endswith('/api/v4/leads')
    assert lead_call.kwargs['json'][0]['_embedded']['contacts'][0]['id'] == 111


@pytest.mark.django_db
def test_amocrm_refreshes_expired_token(settings):
    settings.AMOCRM_BASE_URL = 'https://test.amocrm.ru'
    settings.AMOCRM_CLIENT_ID = 'cid'
    settings.AMOCRM_CLIENT_SECRET = 'secret'

    auth = AmoCRMAuth.get_solo()
    auth.access_token = 'OLD'
    auth.refresh_token = 'OLDREFRESH'
    auth.expires_at = timezone.now() - timedelta(minutes=1)
    auth.save()

    lead = Lead.objects.create(name='Иван', phone='+79001234567', type='order', consent=True)

    with patch('apps.leads.services.amocrm.requests.post') as mock_post:
        mock_post.side_effect = [
            _resp({'access_token': 'NEW', 'refresh_token': 'NEWREFRESH', 'expires_in': 86400}),
            _resp({'_embedded': {'contacts': [{'id': 1}]}}),
            _resp({'_embedded': {'leads': [{'id': 2}]}}),
        ]
        push_lead_to_amocrm(lead.id)

    auth.refresh_from_db()
    assert auth.access_token == 'NEW'
    assert auth.refresh_token == 'NEWREFRESH'
    assert mock_post.call_args_list[0].args[0].endswith('/oauth2/access_token')


@pytest.mark.django_db
def test_lead_form_succeeds_even_if_channel_fails(client):
    site_settings = SiteSettings.get_solo()
    site_settings.email_notifications = 'sales@demoplast.test'
    site_settings.save()

    with patch('apps.leads.services.mail.notify_email', side_effect=Exception('boom')):
        response = client.post(reverse('lead_form'), data=VALID_DATA)

    assert response.status_code == 200
    assert Lead.objects.filter(name='Иван').exists()


def test_q_cluster_retry_exceeds_timeout():
    """retry обязан быть строго больше timeout, иначе django-q не стартует."""
    q = settings.Q_CLUSTER
    assert q['retry'] > q['timeout']


def test_q_cluster_has_attempt_cap():
    """max_attempts задан и конечен — иначе упавшая задача повторяется вечно."""
    assert settings.Q_CLUSTER.get('max_attempts', 0) > 0
