import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from omnitech import models
from omnitech.factories import ProductFactory
from omnitech.models import (
    DigitalLicense,
    LicenseState,
    Order,
    OrderItem,
    OrderState,
    PhysicalProduct,
    ProductState,
    UserProfile,
    encriptar_clave,
)
from omnitech.services import CartService, OrderService


@pytest.mark.django_db
class TestDigitalLicenseLifecycle:
    def test_default_state_is_disponible(self, digital_license):
        assert digital_license.estado_licencia == LicenseState.DISPONIBLE
        assert digital_license.esta_disponible() is True

    def test_reservar_cambia_a_reservada(self, digital_license, user):
        order = Order.objects.create(numero_pedido='ORD-RES', usuario=user, subtotal=100, total=100)
        result = digital_license.reservar(order)
        assert result is True
        digital_license.refresh_from_db()
        assert digital_license.estado_licencia == LicenseState.RESERVADA
        assert digital_license.orden_compra == order

    def test_reservar_licencia_no_disponible_falla(self, digital_license_reservada, user):
        order = Order.objects.create(numero_pedido='ORD-RES2', usuario=user, subtotal=100, total=100)
        result = digital_license_reservada.reservar(order)
        assert result is False

    def test_entregar_desde_disponible(self, digital_license, user):
        order = Order.objects.create(numero_pedido='ORD-ENT', usuario=user, subtotal=100, total=100)
        digital_license.reservar(order)
        result = digital_license.entregar()
        assert result is True
        digital_license.refresh_from_db()
        assert digital_license.estado_licencia == LicenseState.CONSUMIDA
        assert digital_license.fecha_asignacion is not None

    def test_entregar_licencia_ya_consumida_falla(self, digital_license_consumida):
        result = digital_license_consumida.entregar()
        assert result is False

    def test_entregar_desde_disponible_directo(self, digital_license):
        result = digital_license.entregar()
        assert result is True
        digital_license.refresh_from_db()
        assert digital_license.estado_licencia == LicenseState.CONSUMIDA

    def test_encriptacion_roundtrip(self):
        clave_original = 'XXXXX-YYYYY-ZZZZZ-WWWWW'
        encriptada = encriptar_clave(clave_original)
        assert encriptada != clave_original
        licencia = DigitalLicense(
            nombre='Encrypt Test',
            precio=100,
            sku='ENC-001',
            categoria='Test',
            clave_encriptada=encriptada,
            plataforma='Test',
        )
        desencriptada = licencia.desencriptar_clave()
        assert desencriptada == clave_original


@pytest.mark.django_db
class TestDigitalLicenseProcesarVenta:
    def test_procesar_venta_cantidad_uno(self, digital_license, user):
        order = Order.objects.create(numero_pedido='PV-001', usuario=user, subtotal=80000, total=80000)
        digital_license.orden_compra = order
        result = digital_license.procesar_venta(1)
        assert result is True
        digital_license.refresh_from_db()
        assert digital_license.estado_licencia == LicenseState.CONSUMIDA

    def test_procesar_venta_cantidad_cero(self, digital_license):
        result = digital_license.procesar_venta(0)
        assert result is False

    def test_procesar_venta_cantidad_negativa(self, digital_license):
        result = digital_license.procesar_venta(-1)
        assert result is False

    def test_procesar_venta_cantidad_mayor_que_uno_sin_stock_extra(self, digital_license, user):
        order = Order.objects.create(numero_pedido='PV-002', usuario=user, subtotal=160000, total=160000)
        digital_license.orden_compra = order
        with pytest.raises(ValueError, match='Stock insuficiente'):
            digital_license.procesar_venta(2)

    def test_procesar_venta_stock_insuficiente(self, digital_license, user):
        order = Order.objects.create(numero_pedido='PV-003', usuario=user, subtotal=80000, total=80000)
        digital_license.orden_compra = order
        with pytest.raises(ValueError, match='Stock insuficiente'):
            digital_license.procesar_venta(5)

    def test_procesar_venta_licencia_no_disponible(self, digital_license_consumida):
        result = digital_license_consumida.procesar_venta(1)
        assert result is False


@pytest.mark.django_db
class TestPhysicalProductStock:
    def test_stock_disponible_calculo(self, physical_product):
        assert physical_product.stock_disponible == 45

    def test_stock_disponible_nunca_negativo(self, physical_product):
        physical_product.stock_reservado = 999
        assert physical_product.stock_disponible == 0

    def test_reservar_exitosa(self, physical_product):
        result = physical_product.reservar(5)
        assert result is True
        physical_product.refresh_from_db()
        assert physical_product.stock_reservado == 10

    def test_reservar_stock_insuficiente(self, physical_product):
        result = physical_product.reservar(999)
        assert result is False
        physical_product.refresh_from_db()
        assert physical_product.stock_reservado == 5

    def test_liberar_reserva(self, physical_product):
        physical_product.liberar_reserva(3)
        physical_product.refresh_from_db()
        assert physical_product.stock_reservado == 2

    def test_liberar_reserva_nunca_negativo(self, physical_product):
        physical_product.liberar_reserva(999)
        physical_product.refresh_from_db()
        assert physical_product.stock_reservado == 0

    def test_confirmar_reserva(self, physical_product):
        physical_product.confirmar_reserva(5)
        physical_product.refresh_from_db()
        assert physical_product.stock_fisico == 45
        assert physical_product.stock_reservado == 0

    def test_procesar_venta_fisico(self, physical_product):
        result = physical_product.procesar_venta(5)
        assert result is True
        physical_product.refresh_from_db()
        assert physical_product.stock_fisico == 45
        assert physical_product.stock_reservado == 0

    def test_necesita_reabastecimiento_stock_bajo(self, physical_product):
        physical_product.stock_fisico = 1
        physical_product.stock_reservado = 0
        assert physical_product.necesita_reabastecimiento() is True

    def test_necesita_reabastecimiento_stock_normal(self, physical_product):
        physical_product.stock_fisico = 50
        physical_product.stock_reservado = 0
        assert physical_product.necesita_reabastecimiento() is False


@pytest.mark.django_db
class TestOrderCalculation:
    def test_calcular_total_sin_items(self, order):
        order.calcular_total()
        assert order.subtotal == 0
        assert order.costo_envio == 0
        assert order.total == 0

    def test_calcular_total_con_hardware(self, order, physical_product):
        OrderItem.objects.create(
            pedido=order,
            producto_fisico=physical_product,
            cantidad=2,
            precio_unitario=physical_product.precio,
        )
        order.calcular_total()
        peso_total = float(physical_product.peso) * 2
        envio_esperado = Decimal(str(peso_total * 500))
        assert order.costo_envio == envio_esperado
        assert order.total == order.subtotal + order.costo_envio

    def test_calcular_total_subsidio_araucania(self, order, physical_product):
        order.region_envio = 'La Araucanía'
        OrderItem.objects.create(
            pedido=order,
            producto_fisico=physical_product,
            cantidad=10,
            precio_unitario=physical_product.precio,
        )
        order.calcular_total()
        assert order.costo_envio == Decimal('0.00')
        assert order.total == order.subtotal

    def test_calcular_total_subsidio_solo_con_monto_suficiente(self, order, db):
        producto_barato = PhysicalProduct.objects.create(
            nombre='Cable Test', precio=1000, sku='CBL-001',
            categoria='Accesorios', peso=0.5, stock_fisico=50,
        )
        order.region_envio = 'La Araucanía'
        OrderItem.objects.create(
            pedido=order,
            producto_fisico=producto_barato,
            cantidad=1,
            precio_unitario=1000,
        )
        order.calcular_total()
        assert order.costo_envio > 0

    def test_calcular_total_solo_software_sin_envio(self, order, digital_license):
        OrderItem.objects.create(
            pedido=order,
            licencia=digital_license,
            cantidad=1,
            precio_unitario=digital_license.precio,
        )
        order.calcular_total()
        assert order.costo_envio == 0
        assert order.total == order.subtotal

    def test_tiene_hardware_y_software(self, order, physical_product, digital_license):
        OrderItem.objects.create(
            pedido=order, producto_fisico=physical_product, cantidad=1, precio_unitario=100
        )
        OrderItem.objects.create(
            pedido=order, licencia=digital_license, cantidad=1, precio_unitario=100
        )
        assert order.tiene_hardware() is True
        assert order.tiene_software() is True


@pytest.mark.django_db
class TestOrderItemConstraints:
    def test_item_requiere_producto_o_licencia(self, order):
        with pytest.raises(IntegrityError):
            OrderItem.objects.create(
                pedido=order,
                cantidad=1,
                precio_unitario=100,
            )

    def test_item_no_puede_tener_ambos(self, order, physical_product, digital_license):
        with pytest.raises(IntegrityError):
            OrderItem.objects.create(
                pedido=order,
                producto_fisico=physical_product,
                licencia=digital_license,
                cantidad=1,
                precio_unitario=100,
            )

    def test_item_asigna_precio_desde_producto_fisico(self, order, physical_product):
        item = OrderItem.objects.create(
            pedido=order,
            producto_fisico=physical_product,
            cantidad=1,
            precio_unitario=0,
        )
        assert item.precio_unitario == physical_product.precio

    def test_item_asigna_precio_desde_licencia(self, order, digital_license):
        item = OrderItem.objects.create(
            pedido=order,
            licencia=digital_license,
            cantidad=1,
            precio_unitario=0,
        )
        assert item.precio_unitario == digital_license.precio

    def test_item_subtotal_property(self, order, physical_product):
        item = OrderItem.objects.create(
            pedido=order,
            producto_fisico=physical_product,
            cantidad=3,
            precio_unitario=physical_product.precio,
        )
        assert item.subtotal == physical_product.precio * 3


@pytest.mark.django_db
class TestProductFactory:
    def test_obtener_modelo_fisico(self):
        model = ProductFactory.obtener_modelo('fisico')
        assert model == PhysicalProduct

    def test_obtener_modelo_digital(self):
        model = ProductFactory.obtener_modelo('digital')
        assert model == DigitalLicense

    def test_obtener_modelo_software(self):
        model = ProductFactory.obtener_modelo('software')
        assert model == DigitalLicense

    def test_obtener_modelo_invalido(self):
        with pytest.raises(ValueError, match='Tipo de producto desconocido'):
            ProductFactory.obtener_modelo('invalido')

    def test_es_tipo_fisico_true(self):
        assert ProductFactory.es_tipo_fisico('fisico') is True

    def test_es_tipo_fisico_false(self):
        assert ProductFactory.es_tipo_fisico('digital') is False
        assert ProductFactory.es_tipo_fisico('software') is False

    def test_obtener_nombre_corto(self):
        assert ProductFactory.obtener_nombre_corto('fisico') == 'Físico'
        assert ProductFactory.obtener_nombre_corto('digital') == 'Licencia'

    def test_obtener_producto(self, physical_product):
        producto = ProductFactory.obtener_producto('fisico', physical_product.id)
        assert producto == physical_product

    def test_obtener_producto_o_404_existente(self, physical_product):
        producto = ProductFactory.obtener_producto_o_404('fisico', physical_product.id)
        assert producto == physical_product

    def test_obtener_producto_o_404_inexistente(self):
        from django.http import Http404

        with pytest.raises(Http404):
            ProductFactory.obtener_producto_o_404('fisico', 99999)


@pytest.mark.django_db
class TestOrderService:
    def test_crear_pedido_con_usuario(self, user):
        order = OrderService.crear_pedido(
            usuario=user,
            email_invitado=None,
            region='Santiago',
            observaciones='Test',
            costo_envio=Decimal('5000'),
        )
        assert order.usuario == user
        assert order.email_invitado is None
        assert order.estado == OrderState.PENDIENTE_PAGO
        assert order.numero_pedido.startswith('OT-')
        assert order.region_envio == 'Santiago'

    def test_crear_pedido_con_email_invitado(self):
        order = OrderService.crear_pedido(
            usuario=None,
            email_invitado='guest@test.com',
            region='Valparaíso',
            observaciones='',
            costo_envio=Decimal('0'),
        )
        assert order.usuario is None
        assert order.email_invitado == 'guest@test.com'
        assert order.numero_pedido.startswith('OT-')

    def test_calcular_costo_envio_sin_fisicos(self):
        carrito = [{'tipo': 'software', 'precio': 50000, 'cantidad': 1, 'peso': 0}]
        costo = OrderService.calcular_costo_envio(carrito, 'Santiago')
        assert costo == Decimal('0')

    def test_calcular_costo_envio_con_fisicos(self):
        carrito = [{'tipo': 'fisico', 'precio': 50000, 'cantidad': 2, 'peso': 1.5}]
        costo = OrderService.calcular_costo_envio(carrito, 'Santiago')
        assert costo == Decimal('1500')

    def test_calcular_costo_envio_subsidio_araucania(self):
        carrito = [{'tipo': 'fisico', 'precio': 120000, 'cantidad': 1, 'peso': 2}]
        costo = OrderService.calcular_costo_envio(carrito, 'La Araucania')
        assert costo == Decimal('0')

    def test_calcular_costo_envio_subsidio_araucania_monto_insuficiente(self):
        carrito = [{'tipo': 'fisico', 'precio': 50000, 'cantidad': 1, 'peso': 2}]
        costo = OrderService.calcular_costo_envio(carrito, 'La Araucania')
        assert costo > Decimal('0')

    def test_procesar_pago_pedido_ya_procesado(self, order):
        order.estado = OrderState.PAGADO_PROCESANDO
        order.save()
        result, success, error_msg = OrderService.procesar_pago(order.numero_pedido, [])
        assert success is False
        assert error_msg == 'Pedido ya procesado o cancelado'


@pytest.mark.django_db
class TestCartService:
    def test_calcular_totales_carrito_vacio(self):
        result = CartService.calcular_totales([])
        assert result['subtotal'] == 0
        assert result['costo_envio'] == 0
        assert result['total'] == 0
        assert result['cantidad_items'] == 0
        assert result['items'] == []

    def test_calcular_totales_carrito_con_items(self, physical_product, digital_license):
        carrito = [
            {'producto_id': physical_product.id, 'tipo': 'fisico', 'nombre': physical_product.nombre,
             'precio': float(physical_product.precio), 'cantidad': 2, 'peso': float(physical_product.peso)},
            {'producto_id': digital_license.id, 'tipo': 'software', 'nombre': digital_license.nombre,
             'precio': float(digital_license.precio), 'cantidad': 1, 'peso': 0},
        ]
        result = CartService.calcular_totales(carrito)
        assert result['cantidad_items'] == 3
        subtotal_esperado = float(physical_product.precio) * 2 + float(digital_license.precio) * 1
        assert result['subtotal'] == subtotal_esperado
        assert result['costo_envio'] > 0
        assert result['total'] == result['subtotal'] + result['costo_envio']

    def test_get_carrito_session_vacia(self, client):
        request = type('Req', (), {'session': {}})()
        carrito = CartService.get_carrito(request)
        assert carrito == []

    def test_save_carrito_y_get_carrito(self, client):
        from django.conf import settings
        from django.contrib.sessions.backends.base import SessionBase

        session = SessionBase()
        request = type('Req', (), {'session': session})()

        CartService.save_carrito(request, [{'test': 'data'}])
        assert request.session[settings.CART_SESSION_KEY] == [{'test': 'data'}]
        assert request.session.modified is True


@pytest.mark.django_db
class TestUserProfile:
    def test_es_de_araucania_true(self, user):
        perfil = UserProfile.objects.create(user=user, region='La Araucanía')
        assert perfil.es_de_araucania is True

    def test_es_de_araucania_false(self, user):
        perfil = UserProfile.objects.create(user=user, region='Santiago')
        assert perfil.es_de_araucania is False

    def test_calcular_total_compras_sin_pedidos(self, user):
        perfil = UserProfile.objects.create(user=user)
        assert perfil.calcular_total_compras() == Decimal('0.00')

    def test_calcular_total_compras_con_pedidos(self, user):
        perfil = UserProfile.objects.create(user=user)
        Order.objects.create(
            numero_pedido='ORD-001', usuario=user, subtotal=50000, total=55000,
            estado=OrderState.COMPLETADO,
        )
        Order.objects.create(
            numero_pedido='ORD-002', usuario=user, subtotal=30000, total=33000,
            estado=OrderState.COMPLETADO,
        )
        assert perfil.calcular_total_compras() == Decimal('88000')

    def test_calcular_total_compras_solo_pedidos_completados(self, user):
        perfil = UserProfile.objects.create(user=user)
        Order.objects.create(
            numero_pedido='ORD-003', usuario=user, subtotal=50000, total=55000,
            estado=OrderState.PENDIENTE_PAGO,
        )
        assert perfil.calcular_total_compras() == Decimal('0.00')

    def test_rut_valido_pasa_validacion(self, user):
        perfil = UserProfile(user=user, rut='12345678-5')
        perfil.full_clean()

    def test_rut_invalido_falla_validacion(self, user):
        perfil = UserProfile(user=user, rut='invalid')
        with pytest.raises(ValidationError):
            perfil.full_clean()
