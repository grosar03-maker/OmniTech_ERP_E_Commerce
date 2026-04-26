"""
Script para poblar la base de datos con datos de ejemplo
OmniTech ERP & E-Commerce
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'omnitech.settings')
django.setup()

from django.contrib.auth.models import User
from omnitech.models import (
    PhysicalProduct, DigitalLicense, 
    ProductState, LicenseState
)
from decimal import Decimal

def populate_database():
    print("=" * 50)
    print("OmniTech - Poblando Base de Datos")
    print("=" * 50)
    
    print("\n[1/4] Creando usuario administrador...")
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@omnitech.cl',
            password='admin123'
        )
        print(f"  ✓ Admin creado: admin / admin123")
    else:
        print("  - Admin ya existe")
    
    print("\n[2/4] Creando productos físicos (Hardware)...")
    
    hardware_products = [
        {
            'nombre': 'MacBook Pro 14" M3 Pro',
            'sku': 'HW-MAC-M3P-001',
            'descripcion': 'Chip M3 Pro con CPU de 12 núcleos, GPU de 18 núcleos y Neural Engine de 16 núcleos. 18GB de memoria unificada. SSD de 512GB.',
            'precio': Decimal('2499900'),
            'categoria': 'Portátiles',
            'imagen_url': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&h=600&fit=crop',
            'peso': Decimal('1.55'),
            'stock_fisico': 15,
            'stock_reservado': 0,
            'umbral_minimo': 5,
            'proveedor': 'Apple Chile',
            'ubicacion_bodega': 'A-12-03'
        },
        {
            'nombre': 'iPhone 15 Pro Max',
            'sku': 'HW-IPH-15PM-001',
            'descripcion': 'Titanio de grado aeroespacial. Chip A17 Pro. Cámara gran angular de 48 MP. USB-C con USB 3.',
            'precio': Decimal('1699900'),
            'categoria': 'Smartphones',
            'imagen_url': 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=800&h=600&fit=crop',
            'peso': Decimal('0.221'),
            'stock_fisico': 25,
            'stock_reservado': 0,
            'umbral_minimo': 8,
            'proveedor': 'Apple Chile',
            'ubicacion_bodega': 'A-15-01'
        },
        {
            'nombre': 'Sony WH-1000XM5',
            'sku': 'HW-SNY-XM5-001',
            'descripcion': 'Auriculares inalámbricos con Noise Cancelling líder en la industria. 30 horas de batería. LDAC.',
            'precio': Decimal('499990'),
            'categoria': 'Audio',
            'imagen_url': 'https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=800&h=600&fit=crop',
            'peso': Decimal('0.250'),
            'stock_fisico': 30,
            'stock_reservado': 0,
            'umbral_minimo': 10,
            'proveedor': 'Sony Chile',
            'ubicacion_bodega': 'B-05-02'
        },
        {
            'nombre': 'Samsung Monitor Odyssey G9',
            'sku': 'HW-SAM-G9-001',
            'descripcion': 'Monitor gaming curvo 49" DQHD. 240Hz. 1ms Response Time. Quantum Matrix Technology.',
            'precio': Decimal('1899900'),
            'categoria': 'Monitores',
            'imagen_url': 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&h=600&fit=crop',
            'peso': Decimal('14.5'),
            'stock_fisico': 8,
            'stock_reservado': 0,
            'umbral_minimo': 3,
            'proveedor': 'Samsung Chile',
            'ubicacion_bodega': 'C-01-01'
        },
        {
            'nombre': 'Teclado Mecánico Keychron Q1 Pro',
            'sku': 'HW-KEY-Q1P-001',
            'descripcion': 'Teclado 75% QMK/VIA. switches Gateron G Pro. CNC aluminum body. Conectividad Bluetooth/USB-C.',
            'precio': Decimal('189990'),
            'categoria': 'Periféricos',
            'imagen_url': 'https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?w=800&h=600&fit=crop',
            'peso': Decimal('1.65'),
            'stock_fisico': 45,
            'stock_reservado': 0,
            'umbral_minimo': 15,
            'proveedor': 'Keychron',
            'ubicacion_bodega': 'B-08-04'
        },
        {
            'nombre': 'Mouse Logitech MX Master 3S',
            'sku': 'HW-LOG-MX3S-001',
            'descripcion': 'Ratón ergonómico premium. Scroll MagSpeed electromagnético. 8K DPI. Silent Clicks.',
            'precio': Decimal('149990'),
            'categoria': 'Periféricos',
            'imagen_url': 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=800&h=600&fit=crop',
            'peso': Decimal('0.141'),
            'stock_fisico': 60,
            'stock_reservado': 0,
            'umbral_minimo': 20,
            'proveedor': 'Logitech',
            'ubicacion_bodega': 'B-08-05'
        },
        {
            'nombre': 'Webcam Logitech Brio 4K',
            'sku': 'HW-LOG-BR4K-001',
            'descripcion': 'Cámara web 4K Ultra HD. HDR con RightLight 3. Campo de visión 90°. Windows Hello.',
            'precio': Decimal('299990'),
            'categoria': 'Periféricos',
            'imagen_url': 'https://images.unsplash.com/photo-1587826080692-f439cd0b70da?w=800&h=600&fit=crop',
            'peso': Decimal('0.236'),
            'stock_fisico': 35,
            'stock_reservado': 0,
            'umbral_minimo': 10,
            'proveedor': 'Logitech',
            'ubicacion_bodega': 'B-08-06'
        },
        {
            'nombre': 'NVIDIA RTX 4090 Founders Edition',
            'sku': 'HW-NVI-4090-001',
            'descripcion': 'GPU flagships con 24GB GDDR6X. Arquitectura Ada Lovelace. DLSS 3. Ray Tracing de 3ª generación.',
            'precio': Decimal('2999900'),
            'categoria': 'Componentes',
            'imagen_url': 'https://images.unsplash.com/photo-1591488320449-011701bb6704?w=800&h=600&fit=crop',
            'peso': Decimal('2.4'),
            'stock_fisico': 5,
            'stock_reservado': 0,
            'umbral_minimo': 2,
            'proveedor': 'NVIDIA Chile',
            'ubicacion_bodega': 'D-02-01'
        },
    ]
    
    for product_data in hardware_products:
        product, created = PhysicalProduct.objects.get_or_create(
            sku=product_data['sku'],
            defaults=product_data
        )
        if created:
            print(f"  ✓ {product.nombre}")
        else:
            print(f"  - {product.nombre} (ya existe)")
    
    print("\n[3/4] Creando licencias digitales (Software)...")
    
    def encriptar_clave(clave):
        from cryptography.fernet import Fernet
        import base64
        import hashlib
        from django.conf import settings
        
        key = base64.urlsafe_b64encode(
            hashlib.sha256(settings.SECRET_KEY.encode()).digest()
        )
        f = Fernet(key)
        return f.encrypt(clave.encode()).decode()
    
    software_licenses = [
        {
            'nombre': 'Microsoft 365 Family (1 Año)',
            'sku': 'SW-MS-365F-001',
            'descripcion': 'Suscripción para hasta 6 personas. Incluye Word, Excel, PowerPoint, Outlook. 1TB OneDrive por persona.',
            'precio': Decimal('149990'),
            'categoria': 'Productividad',
            'imagen_url': 'https://images.unsplash.com/photo-1633419461186-7d40a38105ec?w=800&h=600&fit=crop',
            'clave_encriptada': encriptar_clave('MS365-FAMILY-xxxx-YYYY-ZZZZ'),
            'plataforma': 'Microsoft',
            'duracion_dias': 365,
            'estado_licencia': LicenseState.DISPONIBLE,
        },
        {
            'nombre': 'Adobe Creative Cloud (1 Año)',
            'sku': 'SW-ADB-CC-001',
            'descripcion': 'Acceso a todas las apps de Adobe: Photoshop, Illustrator, Premiere Pro, After Effects y más.',
            'precio': Decimal('899990'),
            'categoria': 'Diseño',
            'imagen_url': 'https://images.unsplash.com/photo-1626785774573-4b799315345d?w=800&h=600&fit=crop',
            'clave_encriptada': encriptar_clave('ADB-CC-xxxx-YYYY'),
            'plataforma': 'Adobe',
            'duracion_dias': 365,
            'estado_licencia': LicenseState.DISPONIBLE,
        },
        {
            'nombre': 'Windows 11 Pro (Licencia Perpetua)',
            'sku': 'SW-MS-W11P-001',
            'descripcion': 'Sistema operativo Windows 11 Professional. Licencia permanente. Actualizaciones de por vida.',
            'precio': Decimal('199990'),
            'categoria': 'Sistemas Operativos',
            'imagen_url': 'https://images.unsplash.com/photo-1587831990711-23ca6441447b?w=800&h=600&fit=crop',
            'clave_encriptada': encriptar_clave('WIN11-PRO-xxxx-YYYY-ZZZZ-AAAA'),
            'plataforma': 'Microsoft',
            'duracion_dias': 0,
            'estado_licencia': LicenseState.DISPONIBLE,
        },
        {
            'nombre': 'Antivirus Kaspersky Total Security',
            'sku': 'SW-KAS-TS-001',
            'descripcion': 'Protección completa para PC, Mac y móviles. VPN ilimitada. Gestor de contraseñas. Control parental.',
            'precio': Decimal('79990'),
            'categoria': 'Seguridad',
            'imagen_url': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?w=800&h=600&fit=crop',
            'clave_encriptada': encriptar_clave('KTS-xxxx-YYYY-ZZZZ'),
            'plataforma': 'Kaspersky',
            'duracion_dias': 365,
            'estado_licencia': LicenseState.DISPONIBLE,
        },
        {
            'nombre': 'NordVPN (2 Años)',
            'sku': 'SW-NRD-VPN-001',
            'descripcion': 'VPN ultrarrápida. Más de 5000 servidores. Protección contra malware y tracker. Threat Protection.',
            'precio': Decimal('79990'),
            'categoria': 'Seguridad',
            'imagen_url': 'https://images.unsplash.com/photo-1614064641938-3bbee52942c7?w=800&h=600&fit=crop',
            'clave_encriptada': encriptar_clave('NORDVPN-xxxx-YYYY'),
            'plataforma': 'NordVPN',
            'duracion_dias': 730,
            'estado_licencia': LicenseState.DISPONIBLE,
        },
        {
            'nombre': 'AutoCAD 2024 (1 Año)',
            'sku': 'SW-ADT-AC24-001',
            'descripcion': 'Software de diseño CAD. Creación de planos 2D y modelos 3D. Herramientas específicas para arquitectura e ingeniería.',
            'precio': Decimal('499990'),
            'categoria': 'Ingeniería',
            'imagen_url': 'https://images.unsplash.com/photo-1503387762-592deb58ef4e?w=800&h=600&fit=crop',
            'clave_encriptada': encriptar_clave('AUTOCAD-xxxx-YYYY'),
            'plataforma': 'Autodesk',
            'duracion_dias': 365,
            'estado_licencia': LicenseState.DISPONIBLE,
        },
        {
            'nombre': 'Zoom Pro (1 Año)',
            'sku': 'SW-ZOM-PRO-001',
            'descripcion': 'Videoconferencias HD. Hasta 100 participantes. Grabación en la nube. Administración de usuarios.',
            'precio': Decimal('159990'),
            'categoria': 'Comunicación',
            'imagen_url': 'https://images.unsplash.com/photo-1587825140708-dfaf72ae4b04?w=800&h=600&fit=crop',
            'clave_encriptada': encriptar_clave('ZOOM-PRO-xxxx'),
            'plataforma': 'Zoom',
            'duracion_dias': 365,
            'estado_licencia': LicenseState.DISPONIBLE,
        },
        {
            'nombre': 'Spotify Premium (6 Meses)',
            'sku': 'SW-SPF-PR6-001',
            'descripcion': 'Música sin anuncios. Descarga offline. Acceso a más de 100 millones de canciones. Podcasts exclusivos.',
            'precio': Decimal('29990'),
            'categoria': 'Entretenimiento',
            'imagen_url': 'https://images.unsplash.com/photo-1614680376408-81e91ffe3db7?w=800&h=600&fit=crop',
            'clave_encriptada': encriptar_clave('SPOTIFY-PRE-xxxx'),
            'plataforma': 'Spotify',
            'duracion_dias': 180,
            'estado_licencia': LicenseState.DISPONIBLE,
        },
    ]
    
    for license_data in software_licenses:
        license_obj, created = DigitalLicense.objects.get_or_create(
            sku=license_data['sku'],
            defaults=license_data
        )
        if created:
            print(f"  ✓ {license_obj.nombre}")
        else:
            print(f"  - {license_obj.nombre} (ya existe)")
    
    print("\n[4/4] Creando usuarios de prueba...")
    
    test_users = [
        {'username': 'cliente1', 'email': 'cliente1@test.cl', 'password': 'cliente123'},
        {'username': 'gustavo', 'email': 'gustavo@test.cl', 'password': 'gustavo123'},
    ]
    
    for user_data in test_users:
        if not User.objects.filter(username=user_data['username']).exists():
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password']
            )
            print(f"  ✓ Usuario: {user_data['username']}")
        else:
            print(f"  - Usuario: {user_data['username']} (ya existe)")
    
    print("\n" + "=" * 50)
    print("¡Base de datos poblada exitosamente!")
    print("=" * 50)
    print("\nCredenciales de acceso:")
    print("  Admin: admin / admin123")
    print("  Cliente: cliente1 / cliente123")
    print("\nPara ejecutar el servidor:")
    print("  python manage.py runserver")
    print("=" * 50)

if __name__ == '__main__':
    populate_database()
