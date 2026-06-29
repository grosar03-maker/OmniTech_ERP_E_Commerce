import json
from decimal import Decimal

import pytest
from django.urls import reverse

from omnitech.models import (
    DigitalLicense,
    LicenseState,
    Order,
    OrderState,
    PhysicalProduct,
    ProductState,
)
from omnitech.factories import ProductFactory


@pytest.fixture
def physical_product(db):
    return PhysicalProduct.objects.create(
        nombre='Notebook Pro',
        descripcion='Equipo de alto rendimiento',
        precio=Decimal('120000.00'),
        sku='NB-001',
        categoria='Hardware',
        peso=Decimal('2.50'),
        stock_fisico=10,
        stock_reservado=0,
    )


@pytest.fixture
def digital_license(db):
    return DigitalLicense.objects.create(
        nombre='Antivirus Pro',
        descripcion='Licencia anual',
        precio=Decimal('20000.00'),
        sku='AV-001',
        categoria='Software',
        clave_encriptada='gAAAAABnZmFkZQ==',
        plataforma='Windows',
        duracion_dias=365,
    )


@pytest.mark.django_db
class TestHomeView:
    def test_home_returns_200(self, client):
        response = client.get(reverse('home'))
        assert response.status_code == 200

    def test_home_shows_products(self, client, physical_product, digital_license):
        response = client.get(reverse('home'))
        assert response.status_code == 200
        assert 'Notebook Pro' in str(response.content)


@pytest.mark.django_db
class TestProductosView:
    def test_productos_returns_200(self, client):
        response = client.get(reverse('productos'))
        assert response.status_code == 200

    def test_productos_with_category_filter(self, client, physical_product):
        response = client.get(reverse('productos'), {'categoria': 'Hardware'})
        assert response.status_code == 200

    def test_productos_with_type_filter_hardware(self, client, physical_product, digital_license):
        response = client.get(reverse('productos'), {'tipo': 'hardware'})
        assert response.status_code == 200

    def test_productos_with_type_filter_software(self, client, physical_product, digital_license):
        response = client.get(reverse('productos'), {'tipo': 'software'})
        assert response.status_code == 200

    def test_productos_with_search_query(self, client, physical_product):
        response = client.get(reverse('productos'), {'q': 'Notebook'})
        assert response.status_code == 200

    def test_productos_with_search_no_results(self, client):
        response = client.get(reverse('productos'), {'q': 'ZZZZNONEXISTENT'})
        assert response.status_code == 200


@pytest.mark.django_db
class TestDetalleProducto:
    def test_detalle_producto_fisico(self, client, physical_product):
        url = reverse('detalle_producto', args=['fisico', physical_product.id])
        response = client.get(url)
        assert response.status_code == 200

    def test_detalle_producto_software(self, client, digital_license):
        url = reverse('detalle_producto', args=['software', digital_license.id])
        response = client.get(url)
        assert response.status_code == 200

    def test_detalle_producto_not_found(self, client):
        url = reverse('detalle_producto', args=['fisico', 99999])
        response = client.get(url)
        assert response.status_code == 302


@pytest.mark.django_db
class TestVerCarrito:
    def test_ver_carrito_empty(self, client):
        response = client.get(reverse('ver_carrito'))
        assert response.status_code == 200

    def test_ver_carrito_with_items(self, client, physical_product):
        session = client.session
        session['carrito'] = [{
            'producto_id': physical_product.id, 'tipo': 'fisico',
            'nombre': 'Notebook Pro', 'precio': 120000, 'cantidad': 2,
        }]
        session.save()
        response = client.get(reverse('ver_carrito'))
        assert response.status_code == 200


@pytest.mark.django_db
class TestCheckout:
    def test_checkout_redirects_if_cart_empty(self, client):
        response = client.get(reverse('checkout'))
        assert response.status_code == 302

    def test_checkout_get_with_items(self, client, physical_product, settings):
        settings.SUBSIDIO_MONTO = 100000
        session = client.session
        session['carrito'] = [{
            'producto_id': physical_product.id, 'tipo': 'fisico',
            'nombre': 'Notebook Pro', 'precio': 120000, 'cantidad': 2,
        }]
        session.save()
        response = client.get(reverse('checkout'))
        assert response.status_code == 200

    def test_checkout_post_creates_stripe_session(self, client, physical_product, settings, monkeypatch):
        settings.SUBSIDIO_MONTO = 100000
        settings.STRIPE_PUBLIC_KEY = 'pk_test'
        session = client.session
        session['carrito'] = [{
            'producto_id': physical_product.id, 'tipo': 'fisico',
            'nombre': 'Notebook Pro', 'precio': 120000, 'cantidad': 2,
        }]
        session.save()

        class FakeSession:
            url = 'https://checkout.stripe.com/test'

        monkeypatch.setattr(
            'omnitech.views_cart.crear_checkout_session',
            lambda *a, **kw: FakeSession(),
        )
        response = client.post(reverse('checkout'), {
            'email': 'buyer@test.com', 'region': 'Metropolitana',
        })
        assert response.status_code == 302

    def test_checkout_post_missing_email(self, client, physical_product, settings):
        settings.SUBSIDIO_MONTO = 100000
        session = client.session
        session['carrito'] = [{
            'producto_id': physical_product.id, 'tipo': 'fisico',
            'nombre': 'Notebook Pro', 'precio': 120000, 'cantidad': 2,
        }]
        session.save()
        response = client.post(reverse('checkout'), {'email': '', 'region': ''})
        assert response.status_code == 302


@pytest.mark.django_db
class TestPagoExitoso:
    def test_pago_exitoso_no_session_id(self, client):
        response = client.get(reverse('pago_exitoso'))
        assert response.status_code == 302

    def test_pago_exitoso_no_order_id(self, client):
        response = client.get(reverse('pago_exitoso'), {'session_id': 'cs_test_123'})
        assert response.status_code == 302

    def test_pago_exitoso_with_order(self, client, user, physical_product):
        order = Order.objects.create(
            numero_pedido='OT-SUCCESS-01',
            usuario=user, subtotal=Decimal('120000'), total=Decimal('120000'),
            estado=OrderState.PENDIENTE_PAGO,
        )
        session = client.session
        session['order_id'] = 'OT-SUCCESS-01'
        session['carrito_temp'] = [{
            'producto_id': physical_product.id, 'tipo': 'fisico',
            'precio': 120000, 'cantidad': 1,
        }]
        session.save()

        response = client.get(reverse('pago_exitoso'), {'session_id': 'cs_test_123'})
        assert response.status_code == 200


@pytest.mark.django_db
class TestEmptyCart:
    def test_vaciar_carrito_when_empty(self, client):
        response = client.post(reverse('vaciar_carrito'))
        assert response.json()['success'] is True

    def test_agregar_carrito_con_cantidad_invalida(self, client):
        response = client.post(
            reverse('agregar_carrito'),
            data=json.dumps({'producto_id': 999, 'tipo': 'fisico', 'cantidad': 'abc'}),
            content_type='application/json',
        )
        assert response.json()['success'] is False
