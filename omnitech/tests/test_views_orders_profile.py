from decimal import Decimal

import pytest
from django.urls import reverse

from omnitech.models import DigitalLicense, LicenseState, Order, OrderState, PhysicalProduct


@pytest.fixture
def physical_product(db):
    return PhysicalProduct.objects.create(
        nombre='Notebook Pro',
        precio=Decimal('120000.00'),
        sku='NB-001',
        categoria='Hardware',
        peso=Decimal('2.50'),
        stock_fisico=10,
    )


@pytest.fixture
def order(user):
    return Order.objects.create(
        numero_pedido='OT-ORDER-01',
        usuario=user,
        subtotal=Decimal('120000.00'),
        total=Decimal('120000.00'),
    )


@pytest.mark.django_db
class TestDetallePedido:
    def test_detalle_pedido_authenticated_owner(self, client, user, order):
        client.login(username='testuser', password='testpass123')
        response = client.get(reverse('detalle_pedido', args=['OT-ORDER-01']))
        assert response.status_code == 200

    def test_detalle_pedido_authenticated_not_owner(self, client, order):
        from django.contrib.auth.models import User
        other_user = User.objects.create_user(username='other', password='testpass123')
        client.login(username='other', password='testpass123')
        response = client.get(reverse('detalle_pedido', args=['OT-ORDER-01']))
        assert response.status_code == 302

    def test_detalle_pedido_anonymous_for_user_order(self, client, order):
        response = client.get(reverse('detalle_pedido', args=['OT-ORDER-01']))
        assert response.status_code == 302

    def test_detalle_pedido_anonymous_guest_order(self, client):
        guest_order = Order.objects.create(
            numero_pedido='OT-GUEST-01',
            subtotal=Decimal('50000'),
            total=Decimal('50000'),
        )
        response = client.get(reverse('detalle_pedido', args=['OT-GUEST-01']))
        assert response.status_code == 200

    def test_detalle_pedido_not_found(self, client):
        response = client.get(reverse('detalle_pedido', args=['OT-NONEXISTENT']))
        assert response.status_code == 404


@pytest.mark.django_db
class TestMisPedidos:
    def test_mis_pedidos_redirects_anonymous(self, client):
        response = client.get(reverse('mis_pedidos'))
        assert response.status_code == 302

    def test_mis_pedidos_empty(self, client, user):
        client.login(username='testuser', password='testpass123')
        response = client.get(reverse('mis_pedidos'))
        assert response.status_code == 200

    def test_mis_pedidos_with_orders(self, client, user, order):
        client.login(username='testuser', password='testpass123')
        response = client.get(reverse('mis_pedidos'))
        assert response.status_code == 200


@pytest.mark.django_db
class TestMisLicencias:
    def test_mis_licencias_redirects_anonymous(self, client):
        response = client.get(reverse('mis_licencias'))
        assert response.status_code == 302

    def test_mis_licencias_empty(self, client, user):
        client.login(username='testuser', password='testpass123')
        response = client.get(reverse('mis_licencias'))
        assert response.status_code == 200

    def test_mis_licencias_with_licenses(self, client, user, order):
        client.login(username='testuser', password='testpass123')
        DigitalLicense.objects.create(
            nombre='License 1', precio=Decimal('10000'), sku='LIC-001',
            categoria='Software', clave_encriptada='key1',
            plataforma='Windows', duracion_dias=365,
            orden_compra=order, estado_licencia=LicenseState.CONSUMIDA,
        )
        response = client.get(reverse('mis_licencias'))
        assert response.status_code == 200


@pytest.mark.django_db
class TestPerfil:
    def test_perfil_redirects_anonymous(self, client):
        response = client.get(reverse('perfil'))
        assert response.status_code == 302

    def test_perfil_with_existing_profile(self, client, user):
        from omnitech.models import UserProfile
        UserProfile.objects.create(user=user, region='Metropolitana')
        client.login(username='testuser', password='testpass123')
        response = client.get(reverse('perfil'))
        assert response.status_code == 200

    def test_perfil_creates_profile_if_missing(self, client, user):
        client.login(username='testuser', password='testpass123')
        response = client.get(reverse('perfil'))
        assert response.status_code == 200
        assert hasattr(user, 'perfil')

    def test_perfil_shows_admin_flag(self, client, staff_user):
        client.login(username='staffuser', password='staffpass123')
        response = client.get(reverse('perfil'))
        assert response.status_code == 200
