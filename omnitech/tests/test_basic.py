import sys
import pytest
from django.urls import reverse

from omnitech import models

# Saltar tests de templates en Python >= 3.13 por incompatibilidad
# Django 4.2 + Python 3.14. En CI (Python 3.11) funcionan correctamente.
skip_template_tests = pytest.mark.skipif(
    sys.version_info >= (3, 13),
    reason='Template context copy no compatible con Python >= 3.13',
)


@pytest.mark.django_db
class TestModels:
    def test_user_profile_creation(self, user):
        from omnitech.models import UserProfile
        UserProfile.objects.create(user=user)
        assert hasattr(user, 'perfil')

    def test_order_creation(self, user):
        order = models.Order.objects.create(
            numero_pedido='TEST-001',
            usuario=user,
            subtotal=10000,
            total=10000,
        )
        assert order.numero_pedido == 'TEST-001'
        assert order.get_estado_display() == 'Pendiente de Pago'

    def test_physical_product_sku_regex(self):
        product = models.PhysicalProduct(
            nombre='Test',
            precio=10000,
            sku='TEST-001',
            categoria='Componentes',
            peso=1.5,
            stock_fisico=10,
        )
        try:
            product.full_clean()
        except Exception:
            pytest.fail('SKU valido deberia pasar validacion')


@pytest.mark.django_db
@skip_template_tests
class TestViews:
    def test_home_page(self, client):
        url = reverse('home')
        response = client.get(url)
        assert response.status_code == 200

    def test_login_page(self, client):
        url = reverse('login')
        response = client.get(url)
        assert response.status_code == 200

    def test_products_page(self, client):
        url = reverse('productos')
        response = client.get(url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestJWT:
    def test_token_obtain_invalid_credentials(self, client):
        url = reverse('token_obtain_pair')
        response = client.post(
            url,
            {
                'username': 'nonexistent',
                'password': 'wrongpass',
            },
            content_type='application/json',
        )
        assert response.status_code == 401

    def test_token_obtain_valid_credentials(self, client, user):
        url = reverse('token_obtain_pair')
        response = client.post(
            url,
            {
                'username': 'testuser',
                'password': 'testpass123',
            },
            content_type='application/json',
        )
        assert response.status_code == 200
        assert 'access' in response.json()
        assert 'refresh' in response.json()

    def test_token_refresh(self, client, user):
        obtain_url = reverse('token_obtain_pair')
        response = client.post(
            obtain_url,
            {
                'username': 'testuser',
                'password': 'testpass123',
            },
            content_type='application/json',
        )
        refresh_token = response.json()['refresh']

        refresh_url = reverse('token_refresh')
        response = client.post(
            refresh_url,
            {
                'refresh': refresh_token,
            },
            content_type='application/json',
        )
        assert response.status_code == 200
        assert 'access' in response.json()


@pytest.mark.django_db
class TestAPI:
    def test_api_me_unauthenticated(self, client):
        url = reverse('api_me')
        response = client.get(url)
        assert response.status_code == 401

    def test_api_me_authenticated(self, client, user):
        obtain_url = reverse('token_obtain_pair')
        response = client.post(
            obtain_url,
            {
                'username': 'testuser',
                'password': 'testpass123',
            },
            content_type='application/json',
        )
        token = response.json()['access']

        me_url = reverse('api_me')
        response = client.get(
            me_url,
            HTTP_AUTHORIZATION=f'Bearer {token}',
        )
        assert response.status_code == 200
        assert response.json()['username'] == 'testuser'

    def test_api_productos(self, client):
        url = reverse('api_productos')
        response = client.get(url)
        assert response.status_code == 200
        assert 'fisicos' in response.json()
        assert 'digitales' in response.json()
