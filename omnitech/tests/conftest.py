from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.test import Client

from omnitech.models import DigitalLicense, Order, PhysicalProduct


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
    return PhysicalProduct.objects.create(
        nombre='Notebook Pro',
        precio=Decimal('120000.00'),
        sku='NB-001',
        categoria='Hardware',
        peso=Decimal('2.50'),
        stock_fisico=10,
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


@pytest.fixture
def order(user):
    return Order.objects.create(
        numero_pedido='OT-TEST-01',
        usuario=user,
        subtotal=Decimal('120000.00'),
        total=Decimal('120000.00'),
    )


@pytest.fixture
def digital_license_reservada(db, digital_license, user):
    from omnitech.models import Order

    order = Order.objects.create(numero_pedido='RES-001', usuario=user, subtotal=80000, total=80000)
    digital_license.reservar(order)
    return digital_license


@pytest.fixture
def digital_license_consumida(db, digital_license_reservada):
    digital_license_reservada.entregar()
    return digital_license_reservada
