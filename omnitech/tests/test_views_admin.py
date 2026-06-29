import pytest
from django.urls import reverse

from omnitech.models import DigitalLicense, PhysicalProduct, ProductState


@pytest.mark.django_db
class TestDashboard:
    def test_dashboard_redirects_anonymous(self, client):
        response = client.get(reverse('admin_dashboard'))
        assert response.status_code == 302

    def test_dashboard_returns_200_for_staff(self, client, staff_user):
        client.login(username='staffuser', password='staffpass123')
        response = client.get(reverse('admin_dashboard'))
        assert response.status_code == 200

    def test_dashboard_shows_products(self, client, staff_user, physical_product, digital_license):
        client.login(username='staffuser', password='staffpass123')
        response = client.get(reverse('admin_dashboard'))
        assert response.status_code == 200


@pytest.mark.django_db
class TestEditarProducto:
    def test_editar_producto_redirects_anonymous(self, client, physical_product):
        response = client.get(reverse('editar_producto', args=[physical_product.id, 'fisico']))
        assert response.status_code == 302

    def test_editar_producto_get_fisico(self, client, staff_user, physical_product):
        client.login(username='staffuser', password='staffpass123')
        response = client.get(reverse('editar_producto', args=[physical_product.id, 'fisico']))
        assert response.status_code == 200

    def test_editar_producto_get_software(self, client, staff_user, digital_license):
        client.login(username='staffuser', password='staffpass123')
        response = client.get(reverse('editar_producto', args=[digital_license.id, 'software']))
        assert response.status_code == 200

    def test_editar_producto_post_fisico(self, client, staff_user, physical_product):
        client.login(username='staffuser', password='staffpass123')
        response = client.post(
            reverse('editar_producto', args=[physical_product.id, 'fisico']),
            {
                'nombre': 'Updated',
                'sku': 'NB-001',
                'precio': '150000',
                'categoria': 'Hardware',
                'peso': '3.0',
                'stock_fisico': '5',
            },
        )
        assert response.status_code == 302
        physical_product.refresh_from_db()
        assert physical_product.nombre == 'Updated'

    def test_editar_producto_post_software(self, client, staff_user, digital_license):
        client.login(username='staffuser', password='staffpass123')
        response = client.post(
            reverse('editar_producto', args=[digital_license.id, 'software']),
            {
                'nombre': 'Lic Updated',
                'sku': 'AV-001',
                'precio': '25000',
                'categoria': 'Software',
                'plataforma': 'Mac',
                'duracion_dias': '180',
            },
        )
        assert response.status_code == 302
        digital_license.refresh_from_db()
        assert digital_license.nombre == 'Lic Updated'

    def test_editar_producto_missing_name(self, client, staff_user, physical_product):
        client.login(username='staffuser', password='staffpass123')
        response = client.post(
            reverse('editar_producto', args=[physical_product.id, 'fisico']),
            {'nombre': '', 'sku': '', 'precio': '0', 'categoria': ''},
        )
        assert response.status_code == 302

    def test_editar_producto_with_extra_licenses(self, client, staff_user, digital_license):
        client.login(username='staffuser', password='staffpass123')
        response = client.post(
            reverse('editar_producto', args=[digital_license.id, 'software']),
            {
                'nombre': 'Lic',
                'sku': 'AV-001',
                'precio': '25000',
                'categoria': 'Software',
                'plataforma': 'Mac',
                'duracion_dias': '180',
                'claves_adicionales': ['NEW-KEY-001', 'NEW-KEY-002'],
            },
        )
        assert response.status_code == 302
        assert DigitalLicense.objects.filter(sku='AV-001-001').exists()


@pytest.mark.django_db
class TestAgregarProducto:
    def test_agregar_producto_redirects_anonymous(self, client):
        response = client.get(reverse('agregar_producto', args=['fisico']))
        assert response.status_code == 302

    def test_agregar_producto_get_fisico(self, client, staff_user):
        client.login(username='staffuser', password='staffpass123')
        response = client.get(reverse('agregar_producto', args=['fisico']))
        assert response.status_code == 200

    def test_agregar_producto_get_software(self, client, staff_user):
        client.login(username='staffuser', password='staffpass123')
        response = client.get(reverse('agregar_producto', args=['software']))
        assert response.status_code == 200

    def test_agregar_producto_post_fisico(self, client, staff_user):
        client.login(username='staffuser', password='staffpass123')
        response = client.post(
            reverse('agregar_producto', args=['fisico']),
            {
                'nombre': 'New Product',
                'sku': 'NEW-001',
                'precio': '50000',
                'categoria': 'Hardware',
                'peso': '1.0',
                'stock_fisico': '20',
            },
        )
        assert response.status_code == 302
        assert PhysicalProduct.objects.filter(sku='NEW-001').exists()

    def test_agregar_producto_post_software(self, client, staff_user):
        client.login(username='staffuser', password='staffpass123')
        response = client.post(
            reverse('agregar_producto', args=['software']),
            {
                'nombre': 'New License',
                'sku': 'LIC-001',
                'precio': '30000',
                'categoria': 'Software',
                'clave_encriptada': 'TEST-KEY',
                'plataforma': 'Windows',
                'duracion_dias': '365',
            },
        )
        assert response.status_code == 302
        assert DigitalLicense.objects.filter(sku='LIC-001').exists()

    def test_agregar_producto_missing_name(self, client, staff_user):
        client.login(username='staffuser', password='staffpass123')
        response = client.post(
            reverse('agregar_producto', args=['fisico']),
            {'nombre': '', 'sku': '', 'precio': '0', 'categoria': ''},
        )
        assert response.status_code == 302


@pytest.mark.django_db
class TestToggleEstado:
    def test_toggle_estado_redirects_anonymous(self, client, physical_product):
        response = client.post(reverse('toggle_estado', args=[physical_product.id, 'fisico']))
        assert response.status_code == 302

    def test_toggle_estado_activo_to_inactivo(self, client, staff_user, physical_product):
        client.login(username='staffuser', password='staffpass123')
        assert physical_product.estado == ProductState.ACTIVO
        response = client.post(reverse('toggle_estado', args=[physical_product.id, 'fisico']))
        assert response.status_code == 302
        physical_product.refresh_from_db()
        assert physical_product.estado == ProductState.INACTIVO

    def test_toggle_estado_inactivo_to_activo(self, client, staff_user, physical_product):
        client.login(username='staffuser', password='staffpass123')
        physical_product.estado = ProductState.INACTIVO
        physical_product.save(update_fields=['estado'])
        response = client.post(reverse('toggle_estado', args=[physical_product.id, 'fisico']))
        assert response.status_code == 302
        physical_product.refresh_from_db()
        assert physical_product.estado == ProductState.ACTIVO

    def test_toggle_estado_not_found(self, client, staff_user):
        client.login(username='staffuser', password='staffpass123')
        response = client.post(reverse('toggle_estado', args=[99999, 'fisico']))
        assert response.status_code == 302


@pytest.mark.django_db
class TestEliminarProducto:
    def test_eliminar_producto_redirects_anonymous(self, client, physical_product):
        response = client.post(reverse('eliminar_producto', args=[physical_product.id, 'fisico']))
        assert response.status_code == 302

    def test_eliminar_producto_fisico(self, client, staff_user, physical_product):
        client.login(username='staffuser', password='staffpass123')
        response = client.post(reverse('eliminar_producto', args=[physical_product.id, 'fisico']))
        assert response.status_code == 302
        assert not PhysicalProduct.objects.filter(id=physical_product.id).exists()

    def test_eliminar_producto_not_found(self, client, staff_user):
        client.login(username='staffuser', password='staffpass123')
        response = client.post(reverse('eliminar_producto', args=[99999, 'fisico']))
        assert response.status_code == 302
