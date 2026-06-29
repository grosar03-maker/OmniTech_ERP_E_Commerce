import pytest
from django.contrib.auth.models import User
from django.test import Client


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
    )


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        username='staffuser',
        email='staff@example.com',
        password='staffpass123',
        is_staff=True,
    )


@pytest.fixture
def authenticated_client(client, user):
    client.login(username='testuser', password='testpass123')
    return client


@pytest.fixture
def physical_product(db):
    from omnitech.models import PhysicalProduct

    return PhysicalProduct.objects.create(
        nombre='Procesador Test',
        precio=150000,
        sku='CPU-001',
        categoria='Componentes',
        peso=0.5,
        stock_fisico=50,
        stock_reservado=5,
        umbral_minimo=10,
    )


@pytest.fixture
def digital_license(db):
    from omnitech.models import DigitalLicense, LicenseState
    from omnitech.models import encriptar_clave

    return DigitalLicense.objects.create(
        nombre='Windows Pro',
        precio=80000,
        sku='WIN-PRO-001',
        categoria='Sistemas Operativos',
        clave_encriptada=encriptar_clave('AAAAA-BBBBB-CCCCC-DDDDD'),
        plataforma='Windows',
        duracion_dias=365,
        estado_licencia=LicenseState.DISPONIBLE,
    )


@pytest.fixture
def digital_license_reservada(db, digital_license, user):
    from omnitech.models import Order, OrderState

    order = Order.objects.create(numero_pedido='RES-001', usuario=user, subtotal=80000, total=80000)
    digital_license.reservar(order)
    return digital_license


@pytest.fixture
def digital_license_consumida(db, digital_license_reservada):
    digital_license_reservada.entregar()
    return digital_license_reservada


@pytest.fixture
def order(db, user):
    from omnitech.models import Order

    return Order.objects.create(
        numero_pedido='ORD-TEST-001',
        usuario=user,
        subtotal=150000,
        total=150000,
        region_envio='Santiago',
    )
