import pytest

from django.core.files.uploadedfile import SimpleUploadedFile

from apps.pages.models import Certificate


@pytest.mark.django_db
def test_home_returns_200(client):
    response = client.get('/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_lead_form_returns_200(client):
    response = client.get('/lead/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_lead_form_post_without_consent_returns_200_with_errors(client):
    response = client.post('/lead/', {
        'name': 'Иван',
        'phone': '+79001234567',
        'type': 'order',
        'consent': False,
    })
    assert response.status_code == 200
    assert 'consent' in response.content.decode().lower()


# минимальный валидный 1x1 GIF — чтобы ImageField принял файл как картинку
ONE_PX_GIF = (
    b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!'
    b'\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
)


def make_image(name='cert.gif'):
    return SimpleUploadedFile(name, ONE_PX_GIF, content_type='image/gif')


def test_certificate_str_returns_title():
    cert = Certificate(title='ГОСТ 12345')
    assert str(cert) == 'ГОСТ 12345'


@pytest.mark.django_db
def test_active_certificate_shown_on_about(client):
    Certificate.objects.create(title='ГОСТ 12345', image=make_image(), is_active=True)
    response = client.get('/o-kompanii/')
    assert 'ГОСТ 12345' in response.content.decode()


@pytest.mark.django_db
def test_certificates_section_hidden_when_empty(client):
    response = client.get('/o-kompanii/')
    assert 'Сертификаты' not in response.content.decode()
