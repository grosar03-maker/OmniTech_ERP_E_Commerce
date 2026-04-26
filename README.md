# OmniTech ERP & E-Commerce

Sistema transaccional híbrido de venta de hardware y licencias digitales con Arquitectura Hexagonal y diseño Apple Liquid Glass.

## Características

- **Catálogo Híbrido**: Hardware + Licencias Digitales
- **Carrito de Compras**: Carrito híbrido con gestión de stock
- **Sistema de Pedidos**: Con bifurcación para software y hardware
- **Diseño Moderno**: Apple Liquid Glass UI/UX
- **Arquitectura Hexagonal**: Service Layer con Django

## Reglas de Negocio Implementadas

- RN-01: Bifurcación de pedido mixto
- RN-02: Inmutabilidad de licencias
- RN-03: Reserva volátil de stock
- RN-04: Subsidio regional (La Araucanía)
- RN-05: Reabastecimiento automático
- RN-06: Guest checkout

## Instalación

1. **Crear entorno virtual**:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

3. **Aplicar migraciones**:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. **Poblar base de datos** (opcional):
```bash
python populate_db.py
```

5. **Ejecutar servidor**:
```bash
python manage.py runserver
```

## Credenciales

### Admin
- Usuario: `admin`
- Contraseña: `admin123`
- URL: http://localhost:8000/admin/

### Cliente
- Usuario: `cliente1`
- Contraseña: `cliente123`

## Estructura del Proyecto

```
proyecto/
├── omnitech/              # App principal
│   ├── models.py          # Modelos de dominio
│   ├── views.py           # Vistas y lógica de negocio
│   ├── urls.py            # URLs de la app
│   ├── forms.py           # Formularios
│   └── admin.py           # Panel de administración
├── templates/             # Templates HTML
│   ├── base.html
│   ├── home.html
│   ├── productos.html
│   ├── carrito.html
│   ├── checkout.html
│   └── ...
├── static/
│   ├── css/style.css      # Estilos Liquid Glass
│   └── js/carrito.js      # JavaScript del carrito
├── manage.py
├── settings.py
└── populate_db.py
```

## API Endpoints

| Método | URL | Descripción |
|--------|-----|-------------|
| GET | `/` | Página principal |
| GET | `/productos/` | Catálogo de productos |
| GET | `/producto/<id>/` | Detalle de producto |
| GET | `/carrito/` | Ver carrito |
| POST | `/carrito/agregar/` | Agregar al carrito |
| POST | `/carrito/actualizar/` | Actualizar cantidad |
| POST | `/carrito/eliminar/` | Eliminar del carrito |
| GET | `/checkout/` | Página de checkout |
| POST | `/procesar-pago/` | Procesar pago |
| GET | `/mis-pedidos/` | Pedidos del usuario |
| GET | `/mis-licencias/` | Licencias del usuario |

## Tecnologías

- Django 4.2+
- SQLite (desarrollo)
- HTML5/CSS3
- JavaScript ES6+
- Docker (próximamente)
