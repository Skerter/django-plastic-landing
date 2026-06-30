import pytest

from apps.pages.models import Certificate
from tests.factories import CertificateFactory


@pytest.mark.django_db
def test_home_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_lead_form_returns_200(client):
    response = client.get("/lead/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_lead_form_post_without_consent_returns_200_with_errors(client):
    response = client.post(
        "/lead/",
        {
            "name": "Иван",
            "phone": "+79001234567",
            "type": "order",
            "consent": False,
        },
    )
    assert response.status_code == 200
    assert "consent" in response.content.decode().lower()


def test_certificate_str_returns_title():
    cert = Certificate(title="ГОСТ 12345")
    assert str(cert) == "ГОСТ 12345"


@pytest.mark.django_db
def test_active_certificate_shown_on_about(client):
    cert = CertificateFactory(is_active=True)
    response = client.get("/o-kompanii/")
    assert cert.title in response.content.decode()


@pytest.mark.django_db
def test_certificates_section_hidden_when_empty(client):
    response = client.get("/o-kompanii/")
    assert "Сертификаты" not in response.content.decode()
