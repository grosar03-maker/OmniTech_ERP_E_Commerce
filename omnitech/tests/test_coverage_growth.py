import json
from decimal import Decimal

import pytest
from django.contrib.sessions.middleware import SessionMiddleware

from omnitech.factories import ProductFactory
from omnitech.forms import CheckoutForm, LoginForm, UserProfileForm, UserRegistrationForm
from omnitech.models import (
    DigitalLicense,
    LicenseState,
    Order,
    OrderItem,
    OrderState,
    PhysicalProduct,
    UserProfile,
    encriptar_clave,
)
from omnitech.services import CartService, EmailService, OrderService, enviar_notificacion_stock_bajo


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
        stock_reservado=2,
        umbral_minimo=10,
    )


@pytest.fixture
def digital_license(db):
    return DigitalLicense.objects.create(
        nombre='Antivirus Pro',
        descripcion='Licencia anual',
        precio=Decimal('20000.00'),
        sku='AV-001',
        categoria='Software',
        clave_encriptada=encriptar_clave('ABC-123-XYZ'),
        plataforma='Windows',
        duracion_dias=365,
    )


@pytest.fixture
def order(user):
    return Order.objects.create(
        numero_pedido='OT-TEST-01',
        usuario=user,
        subtotal=Decimal('0.00'),
        costo_envio=Decimal('0.00'),
        total=Decimal('0.00'),
        region_envio='La Araucania',
    )


def attach_session(request):
    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)
    request.session.save()
    return request


@pytest.mark.django_db
class TestDomainModelsCoverage:
    def test_physical_product_stock_reservation_lifecycle(self, physical_product):
        assert physical_product.stock_disponible == 8
        assert not physical_product.necesita_reabastecimiento()

        assert physical_product.reservar(3) is True
        physical_product.refresh_from_db()
        assert physical_product.stock_reservado == 5
        assert physical_product.stock_disponible == 5

        assert physical_product.reservar(99) is False

        physical_product.liberar_reserva(2)
        physical_product.refresh_from_db()
        assert physical_product.stock_reservado == 3

        assert physical_product.procesar_venta(2) is True
        physical_product.refresh_from_db()
        assert physical_product.stock_fisico == 8
        assert physical_product.stock_reservado == 1

    def test_physical_product_needs_restock_when_available_stock_is_low(self, physical_product):
        physical_product.stock_fisico = 1
        physical_product.stock_reservado = 0
        assert physical_product.necesita_reabastecimiento() is True
        assert str(physical_product) == 'NB-001 | Stock: 1'

    def test_digital_license_lifecycle_and_decryption(self, digital_license, order):
        assert digital_license.esta_disponible() is True
        assert digital_license.desencriptar_clave() == 'ABC-123-XYZ'
        assert digital_license.reservar(order) is True

        digital_license.refresh_from_db()
        assert digital_license.estado_licencia == LicenseState.RESERVADA
        assert digital_license.orden_compra == order
        assert digital_license.entregar() is True

        digital_license.refresh_from_db()
        assert digital_license.estado_licencia == LicenseState.CONSUMIDA
        assert digital_license.fecha_asignacion is not None
        assert digital_license.entregar() is False
        assert str(digital_license) == 'AV-001 | Consumida'

    def test_order_item_subtotal_and_save_sets_price(self, order, physical_product, digital_license):
        item = OrderItem.objects.create(
            pedido=order,
            producto_fisico=physical_product,
            cantidad=2,
            precio_unitario=Decimal('1.00'),
            descuento=Decimal('5000.00'),
        )
        assert item.precio_unitario == physical_product.precio
        assert item.subtotal == Decimal('235000.00')
        assert str(item) == f'2x {physical_product}'

        license_item = OrderItem.objects.create(
            pedido=order,
            licencia=digital_license,
            cantidad=1,
            precio_unitario=Decimal('1.00'),
        )
        assert license_item.precio_unitario == digital_license.precio
        assert license_item.subtotal == digital_license.precio

    def test_order_total_and_type_helpers(self, order, physical_product, digital_license):
        OrderItem.objects.create(pedido=order, producto_fisico=physical_product, cantidad=1, precio_unitario=Decimal('1'))
        OrderItem.objects.create(pedido=order, licencia=digital_license, cantidad=1, precio_unitario=Decimal('1'))

        assert order.tiene_hardware() is True
        assert order.tiene_software() is True
        assert order.calcular_total() == Decimal('141250.00')
        assert order.costo_envio == Decimal('1250.00')
        assert str(order) == 'Pedido OT-TEST-01 - Pendiente de Pago'

    def test_user_profile_helpers(self, user):
        profile = UserProfile.objects.create(user=user, region='La Araucania')
        Order.objects.create(numero_pedido='OT-DONE', usuario=user, estado=OrderState.COMPLETADO, total=Decimal('1500'))
        Order.objects.create(numero_pedido='OT-PENDING', usuario=user, estado=OrderState.PENDIENTE_PAGO, total=Decimal('999'))

        assert profile.es_de_araucania is False
        assert profile.calcular_total_compras() == Decimal('1500')
        assert str(profile) == f'Perfil de {user.username}'


@pytest.mark.django_db
class TestFactoriesAndFormsCoverage:
    def test_product_factory_resolves_models_and_names(self, physical_product, digital_license):
        assert ProductFactory.obtener_modelo('fisico') is PhysicalProduct
        assert ProductFactory.obtener_modelo('software') is DigitalLicense
        assert ProductFactory.obtener_modelo('digital') is DigitalLicense
        assert ProductFactory.obtener_producto('fisico', physical_product.id) == physical_product
        assert ProductFactory.obtener_producto_o_404('software', digital_license.id) == digital_license
        assert ProductFactory.es_tipo_fisico('fisico') is True
        assert ProductFactory.es_tipo_fisico('software') is False
        assert ProductFactory.obtener_nombre_corto('fisico') != 'Licencia'
        assert ProductFactory.obtener_nombre_corto('software') == 'Licencia'

    def test_product_factory_rejects_unknown_type(self):
        with pytest.raises(ValueError):
            ProductFactory.obtener_modelo('otro')

    def test_registration_form_validations(self, user):
        duplicate = UserRegistrationForm(
            data={
                'username': user.username,
                'email': 'new@example.com',
                'password': 'testpass123',
                'password2': 'testpass123',
            }
        )
        assert duplicate.is_valid() is False
        assert 'username' in duplicate.errors

        mismatch = UserRegistrationForm(
            data={
                'username': 'newuser',
                'email': 'new@example.com',
                'password': 'testpass123',
                'password2': 'different123',
            }
        )
        assert mismatch.is_valid() is False
        assert '__all__' in mismatch.errors

    def test_basic_forms_are_valid(self, user):
        assert LoginForm(data={'username': 'any', 'password': 'secret'}).is_valid()
        assert CheckoutForm(data={'email': 'buyer@example.com', 'region': 'Metropolitana'}).is_valid()

        profile = UserProfile(user=user)
        form = UserProfileForm(
            data={
                'rut': '12345678-9',
                'telefono': '+56912345678',
                'region': 'La Araucania',
                'ciudad': 'Temuco',
                'direccion': 'Calle 123',
                'newsletter': 'on',
            },
            instance=profile,
        )
        assert form.is_valid()


@pytest.mark.django_db
class TestServicesCoverage:
    def test_cart_service_session_and_totals(self, rf, physical_product, digital_license):
        request = attach_session(rf.get('/'))
        carrito = [
            {'producto_id': physical_product.id, 'tipo': 'fisico', 'precio': 120000, 'cantidad': 2},
            {'producto_id': digital_license.id, 'tipo': 'software', 'precio': 20000, 'cantidad': 1},
            {'producto_id': 999999, 'tipo': 'fisico', 'precio': 10, 'cantidad': 1},
        ]

        CartService.save_carrito(request, carrito)
        assert CartService.get_carrito(request) == carrito

        totales = CartService.calcular_totales(carrito)
        assert totales['cantidad_items'] == 3
        assert totales['subtotal'] == 260010.0
        assert len(totales['items']) == 2
        assert totales['costo_envio'] == 2500.0
        assert totales['total'] == 262510.0

    def test_order_service_shipping_costs(self, settings):
        settings.SUBSIDIO_MONTO = 100000
        carrito = [
            {'tipo': 'fisico', 'peso': 2.5, 'precio': 120000, 'cantidad': 1},
            {'tipo': 'software', 'peso': 0, 'precio': 20000, 'cantidad': 1},
        ]
        assert OrderService.calcular_costo_envio(carrito, 'Metropolitana') == Decimal('1250.0')
        assert OrderService.calcular_costo_envio(carrito, 'La Araucania') == Decimal('0')
        assert OrderService.calcular_costo_envio([{'tipo': 'software', 'precio': 1000, 'cantidad': 1}], '') == Decimal('0')

    def test_order_service_crear_pedido(self, user):
        order = OrderService.crear_pedido(user, '', 'Metropolitana', 'Sin observaciones', Decimal('1500'))
        assert order.numero_pedido.startswith('OT-')
        assert order.usuario == user
        assert order.estado == OrderState.PENDIENTE_PAGO
        assert order.costo_envio == Decimal('1500')

    def test_order_service_crear_pedido_para_stripe(self, rf, user, settings):
        settings.SUBSIDIO_MONTO = 100000
        request = attach_session(rf.post('/checkout/'))
        request.user = user
        carrito = [{'tipo': 'fisico', 'peso': 1.5, 'precio': 50000, 'cantidad': 2}]

        order, shipping = OrderService.crear_pedido_para_stripe(
            request, carrito, 'buyer@example.com', 'Metropolitana', 'Rapido'
        )

        assert order.numero_pedido == request.session['order_id']
        assert request.session['carrito_temp'] == carrito
        assert shipping == Decimal('1500.0')
        assert order.usuario == user

    def test_order_service_procesar_pago_success(self, order, physical_product):
        carrito = [{'producto_id': physical_product.id, 'tipo': 'fisico', 'precio': 120000, 'cantidad': 2}]

        processed, success, error = OrderService.procesar_pago(order.numero_pedido, carrito)

        assert success is True
        assert error is None
        assert processed.estado == OrderState.PAGADO_PROCESANDO
        assert processed.items.count() == 1
        physical_product.refresh_from_db()
        assert physical_product.stock_fisico == 8

    def test_order_service_procesar_pago_rejects_processed_order(self, order):
        order.estado = OrderState.COMPLETADO
        order.save(update_fields=['estado'])

        processed, success, error = OrderService.procesar_pago(order.numero_pedido, [])

        assert processed is None
        assert success is False
        assert error == 'Pedido ya procesado o cancelado'

    def test_email_services_with_monkeypatched_send_mail(self, monkeypatch, order, user, physical_product):
        OrderItem.objects.create(pedido=order, producto_fisico=physical_product, cantidad=1, precio_unitario=physical_product.precio)
        calls = []

        def fake_send_mail(**kwargs):
            calls.append(kwargs)
            return 1

        monkeypatch.setattr('omnitech.services.send_mail', fake_send_mail)
        ok, message = EmailService.enviar_boleta(order)
        assert ok is True
        assert user.email in message

        assert EmailService.notificar_stock_bajo(physical_product, 1) is True
        assert enviar_notificacion_stock_bajo(physical_product, 1) is True
        assert len(calls) >= 3

    def test_email_service_without_destination(self):
        order = Order.objects.create(numero_pedido='OT-NOEMAIL')
        ok, message = EmailService.enviar_boleta(order)
        assert ok is False
        assert 'email' in message


@pytest.mark.django_db
class TestCartViewsCoverage:
    def test_cart_json_lifecycle(self, client, physical_product):
        response = client.post(
            '/carrito/agregar/',
            data=json.dumps({'producto_id': physical_product.id, 'tipo': 'fisico', 'cantidad': 2}),
            content_type='application/json',
        )
        assert response.status_code == 200
        assert response.json()['success'] is True
        assert response.json()['carrito_count'] == 2

        response = client.post(
            '/carrito/actualizar/',
            data=json.dumps({'producto_id': physical_product.id, 'tipo': 'fisico', 'cantidad': 3}),
            content_type='application/json',
        )
        assert response.json()['success'] is True
        assert response.json()['cantidad_items'] == 3

        response = client.post(
            '/carrito/eliminar/',
            data=json.dumps({'producto_id': physical_product.id, 'tipo': 'fisico'}),
            content_type='application/json',
        )
        assert response.json()['success'] is True
        assert response.json()['cantidad_items'] == 0

    def test_cart_rejects_insufficient_stock_and_unavailable_license(self, client, physical_product, digital_license):
        response = client.post(
            '/carrito/agregar/',
            data=json.dumps({'producto_id': physical_product.id, 'tipo': 'fisico', 'cantidad': 99}),
            content_type='application/json',
        )
        assert response.json() == {'success': False, 'error': 'Stock insuficiente'}

        digital_license.estado_licencia = LicenseState.CONSUMIDA
        digital_license.save(update_fields=['estado_licencia'])
        response = client.post(
            '/carrito/agregar/',
            data=json.dumps({'producto_id': digital_license.id, 'tipo': 'software', 'cantidad': 1}),
            content_type='application/json',
        )
        assert response.json() == {'success': False, 'error': 'Licencia no disponible'}

    def test_vaciar_carrito(self, client, physical_product):
        session = client.session
        session['carrito'] = [{'producto_id': physical_product.id, 'tipo': 'fisico', 'cantidad': 1, 'precio': 120000}]
        session.save()

        response = client.post('/carrito/vaciar/')
        assert response.json()['success'] is True
        assert client.session['carrito'] == []
