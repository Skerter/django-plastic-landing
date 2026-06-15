import pytest

from apps.core.models import SiteSettings


@pytest.mark.django_db
def test_seed_migration_populated_settings():
    site_settings = SiteSettings.get_solo()
    # по одному полю из каждой группы — миграция засеяла все категории
    assert site_settings.phone_sales        # контакты
    assert site_settings.address            # адрес
    assert site_settings.inn                # реквизиты



def test_tel_property_strips_formatting():
    site_settings = SiteSettings(phone_sales='+7 (495) 000-00-00', phone_accounting='8 800 555 35 35')
    assert site_settings.phone_sales_tel == '+74950000000'
    assert site_settings.phone_accounting_tel == '+88005553535'


@pytest.mark.django_db
def test_context_processor_injects_site_settings(client):
    response = client.get('/')
    assert 'site_settings' in response.context


@pytest.mark.django_db
def test_phone_change_appears_on_page(client):
    site_settings = SiteSettings.get_solo()
    site_settings.phone_sales = '+7 999 000-00-00'
    site_settings.save()

    response = client.get('/kontakty/')
    assert '+7 999 000-00-00' in response.content.decode()


METRIKA_SCRIPT = 'mc.yandex.ru/metrika/tag.js'


@pytest.mark.django_db
def test_metrika_absent_without_consent(client):
    site_settings = SiteSettings.get_solo()
    site_settings.metrika_id = '12345678'
    site_settings.save()

    response = client.get('/')
    assert METRIKA_SCRIPT not in response.content.decode()


@pytest.mark.django_db
def test_metrika_present_with_consent_and_id(client):
    site_settings = SiteSettings.get_solo()
    site_settings.metrika_id = '12345678'
    site_settings.save()

    client.cookies['cookie_consent'] = 'accepted'
    response = client.get('/')
    html = response.content.decode()
    assert METRIKA_SCRIPT in html
    assert 'ym(12345678, "init"' in html


@pytest.mark.django_db
def test_metrika_absent_when_id_empty(client):
    site_settings = SiteSettings.get_solo()
    site_settings.metrika_id = ''
    site_settings.save()

    client.cookies['cookie_consent'] = 'accepted'
    response = client.get('/')
    assert METRIKA_SCRIPT not in response.content.decode()
