import pytest

from tests.factories import CategoryFactory, ProductFactory


@pytest.mark.django_db
def test_inactive_category_not_shown(client):
    CategoryFactory(name="Скрытая категория", is_active=False)
    response = client.get("/catalog/")
    assert "Скрытая категория" not in response.content.decode()


@pytest.mark.django_db
def test_active_category_shown(client):
    category = CategoryFactory(is_active=True)
    response = client.get("/catalog/")
    assert category.name in response.content.decode()


@pytest.mark.django_db
def test_product_detail_returns_200(client):
    product = ProductFactory(is_active=True)
    url = f"/catalog/{product.category.slug}/{product.slug}/"
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_inactive_product_returns_404(client):
    product = ProductFactory(is_active=False)
    url = f"/catalog/{product.category.slug}/{product.slug}/"
    response = client.get(url)
    assert response.status_code == 404
