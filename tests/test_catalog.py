import pytest
from apps.catalog.models import Category, Product


@pytest.mark.django_db
def test_inactive_category_not_shown(client):
    Category.objects.create(name='Скрытая', slug='skrytaya', is_active=False)
    response = client.get('/catalog/')
    assert 'Скрытая' not in response.content.decode()


# Слаги намеренно НЕ из сид-миграции (0004_seed_catalog) — иначе UNIQUE-конфликт:
# сид наполняет тестовую БД kanistry/kryshki, поэтому тесты берут свои слаги.
@pytest.mark.django_db
def test_active_category_shown(client):
    Category.objects.create(name='Тест-канистры', slug='test-kanistry', is_active=True)
    response = client.get('/catalog/')
    assert 'Тест-канистры' in response.content.decode()


@pytest.mark.django_db
def test_product_detail_returns_200(client):
    category = Category.objects.create(name='Тест-канистры', slug='test-kanistry', is_active=True)
    Product.objects.create(name='Канистра 10л', slug='test-kanistra-10l', category=category, is_active=True)
    response = client.get('/catalog/test-kanistry/test-kanistra-10l/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_inactive_product_returns_404(client):
    category = Category.objects.create(name='Тест-канистры', slug='test-kanistry', is_active=True)
    Product.objects.create(name='Канистра 10л', slug='test-kanistra-10l', category=category, is_active=False)
    response = client.get('/catalog/test-kanistry/test-kanistra-10l/')
    assert response.status_code == 404
