# Informe del Proyecto — OmniTech ERP & E-Commerce

---

## 1. Nombre e Integrantes

| Nombre | Rol |
|--------|-----|
| **Nombre del equipo** | OmniTech Dev Team |
| *Integrante 1* | Desarrollo backend (modelos, servicios, APIs) |
| *Integrante 2* | Frontend e integración Stripe |
| *Integrante 3* | Panel administrador, refactorización SOLID, Factory Method, UI/UX |

---

## 2. Problema

Una tienda de tecnología requiere un sistema transaccional híbrido que permita vender **productos físicos (hardware)** y **licencias digitales (software)** bajo un mismo carrito de compras. El sistema debe:

- Gestionar inventario físico con control de stock, reservas temporales y reabastecimiento automático.
- Entregar licencias digitales con claves encriptadas de forma inmediata post-pago.
- Procesar pagos vía Stripe con manejo transaccional ACID.
- Enviar comprobantes y claves por correo electrónico.
- Proveer un panel de administración web para gestionar el catálogo completo.

No existía una solución unificada que manejara ambos tipos de producto con la misma interfaz de carrito, pago y administración.

---

## 3. Avance del Proyecto

### 3.1 Modelo de Datos (100%)

| Modelo | Estado | Descripción |
|--------|--------|-------------|
| `Product` (abstracto) | ✅ Completo | Clase base con nombre, SKU, precio, categoría, estado, imagen |
| `PhysicalProduct` | ✅ Completo | Producto físico con peso, stock, reservas, umbral mínimo |
| `DigitalLicense` | ✅ Completo | Licencia digital con clave encriptada, plataforma, duración, ciclo de vida |
| `Order` | ✅ Completo | Pedido con estados, guest checkout, envío regional |
| `OrderItem` | ✅ Completo | Ítem de pedido con relación polimórfica a físico o licencia |
| `UserProfile` | ✅ Completo | Perfil extendido de usuario con RUT, región, historial |

### 3.2 Backend y Lógica de Negocio (100%)

| Componente | Estado |
|------------|--------|
| `ProductFactory` (Factory Method) | ✅ Implementado |
| `OrderService` (procesar_pago, crear_pedido) | ✅ Implementado |
| `CartService` (carrito, totales) | ✅ Implementado |
| `EmailService` (boletas, claves) | ✅ Implementado |
| `StripeService` (sesiones checkout) | ✅ Implementado |

### 3.3 Frontend (100%)

| Página | Estado |
|--------|--------|
| Home | ✅ Completo |
| Productos con buscador y filtros | ✅ Completo |
| Detalle de producto | ✅ Completo |
| Carrito de compras | ✅ Completo |
| Checkout + Stripe | ✅ Completo |
| Pago exitoso | ✅ Completo |
| Registro / Login | ✅ Completo |
| Perfil de usuario | ✅ Completo |
| Mis pedidos / Mis licencias | ✅ Completo |
| **Panel Administrador Web** | ✅ Completo |

### 3.4 Panel Administrador Web

| Funcionalidad | Estado |
|---------------|--------|
| Dashboard con estadísticas | ✅ Completo |
| CRUD productos físicos | ✅ Completo |
| CRUD licencias digitales | ✅ Completo |
| Agregar claves adicionales a licencias | ✅ Completo |
| Toggle activar/desactivar | ✅ Completo |
| Eliminar con confirmación modal | ✅ Completo |
| Buscador en vivo por SKU, nombre, categoría | ✅ Completo |
| Navegación por tabs (físicos / licencias) | ✅ Completo |

### 3.5 Refactorización SOLID y Patrones (100%)

| Tarea | Estado |
|-------|--------|
| SRP: views.py separado en módulos por dominio | ✅ Completo |
| Factory Method en `factories.py` | ✅ Completo |
| DIP: lógica de negocio en OrderService | ✅ Completo |
| LSP: procesar_venta polimórfico en PhysicalProduct y DigitalLicense | ✅ Completo |
| Unificar CartService (eliminar duplicación) | ✅ Completo |
| OrderItem registrado como admin propio | ✅ Completo |
| Documentación de patrones y SOLID en código | ✅ Completo |

---

## 4. Requerimientos y Reglas de Negocio

### RN-01 — Bifurcación Mixta de Despacho
- **Software**: despacho inmediato vía email con las claves de licencia.
- **Hardware**: encolamiento para empaque físico y cálculo de costo de envío por peso.
- Implementado en `OrderService.procesar_pago()` y `enviar_claves_licencia()`.

### RN-02 — Ciclo de Vida de Licencias
- Las licencias digitales siguen el ciclo: `DISPONIBLE → RESERVADA → CONSUMIDA`.
- Una vez consumida, la licencia es inmutable.
- Implementado en `DigitalLicense.entregar()`.

### RN-03 — Reserva Volátil de Stock (15 min)
- El stock se reserva durante el checkout por 15 minutos.
- Si el pago no se completa, la reserva se libera automáticamente.
- Implementado en `PhysicalProduct.reservar()` y `liberar_reserva()`.

### RN-04 — Subsidio de Envío Región de La Araucanía
- Pedidos con subtotal > $100.000 y región "La Araucanía" tienen envío gratuito.
- Implementado en `Order.calcular_total()`.

### RN-05 — Reabastecimiento Automático
- Cuando el stock disponible cae al 15% del umbral mínimo, se dispara una alerta de reabastecimiento.
- Implementado en `PhysicalProduct.necesita_reabastecimiento()`.

### RN-06 — Guest Checkout
- Usuarios no registrados pueden comprar ingresando solo su email.
- La orden se asocia al email, no a un usuario.
- Implementado en `Order.email_invitado`.

---

## 5. Principios SOLID (Diagramas)

### 5.1 Single Responsibility Principle (SRP)

```
┌─────────────────────────────────────────────────────┐
│                    views.py                          │
├─────────────────┬──────────────┬───────────────────┤
│   views_cart.py │ views_auth.py│  views_orders.py  │
│   (carrito,     │ (login,      │  (pedidos,        │
│    checkout,     │  registro,    │   detalle)        │
│    pago)        │  password)   │                   │
├─────────────────┼──────────────┼───────────────────┤
│ views_profile.py│ views_admin.py                   │
│ (perfil,        │ (panel admin, CRUD productos)    │
│  licencias)     │                                   │
└─────────────────┴───────────────────────────────────┘
```

**Explicación**: Cada archivo de vistas tiene una única responsabilidad temática. `views.py` original fue separado en 5 archivos independientes.

```
┌─────────────────────────────────────────────────────┐
│                   services.py                        │
├─────────────────┬──────────────┬───────────────────┤
│  OrderService   │ CartService  │  EmailService     │
│  (pedidos,      │ (carrito,    │  (correos,        │
│   pagos)        │  totales)    │   notificaciones) │
└─────────────────┴──────────────┴───────────────────┘
```

### 5.2 Open/Closed Principle (OCP)

```
         ┌──────────────────┐
         │   Product         │ (clase base abstracta)
         │ procesar_venta()  │
         └─────────┬────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
┌───────▼─────────┐  ┌───────▼──────────┐
│ PhysicalProduct  │  │ DigitalLicense   │
│ procesar_venta() │  │ procesar_venta() │
│ → confirmar_     │  │ → buscar claves  │
│   reserva()      │  │   disponibles    │
└─────────────────┘  └──────────────────┘
```

**Explicación**: Agregar un nuevo tipo de producto no requiere modificar `services.py` ni `views.py`. Solo se crea una nueva subclase de `Product` con su propio `procesar_venta()`.

### 5.3 Liskov Substitution Principle (LSP)

```python
# Ambos se usan de forma intercambiable:
producto = ProductFactory.obtener_producto(tipo, id)
producto.procesar_venta(cantidad)  # ← polimórfico

# PhysicalProduct: descuenta stock
# DigitalLicense:   consume claves disponibles
```

**Explicación**: `PhysicalProduct.procesar_venta(5)` y `DigitalLicense.procesar_venta(5)` son intercambiables. Ambos aceptan el mismo parámetro `cantidad` y procesan exactamente esa cantidad.

### 5.4 Interface Segregation Principle (ISP)

Las interfaces (clases base/métodos públicos) están segregadas por dominio:

- `Product` → métodos de catálogo (nombre, sku, precio, estado)
- `PhysicalProduct` → gestión de stock (reservar, liberar, reabastecer)
- `DigitalLicense` → ciclo de vida de licencia (entregar, desencriptar)
- `Order` → gestión de pedidos (calcular_total, tiene_hardware, tiene_software)

### 5.5 Dependency Inversion Principle (DIP)

```
┌──────────┐    ┌──────────────────┐    ┌──────────────┐
│  Views    │───▶│  OrderService    │───▶│  Modelos     │
│          │    │  (abstracción)   │    │  (concretos)  │
└──────────┘    └──────────────────┘    └──────────────┘
                      │
                      ▼
               ┌──────────────┐
               │  ProductFactory│
               │  (Factory)    │
               └──────────────┘
```

**Explicación**: Las vistas no crean modelos directamente. Toda la lógica de negocio pasa por `OrderService` y `CartService`. La resolución de modelos se delega a `ProductFactory`.

---

## 6. Patrones de Diseño (Diagramas)

### 6.1 Factory Method — Creación de Productos

```
┌─────────────────────────────────────────────┐
│              ProductFactory                  │
├─────────────────────────────────────────────┤
│  PRODUCT_MAP = {                            │
│    'fisico': PhysicalProduct,               │
│    'software': DigitalLicense,              │
│    'digital': DigitalLicense                │
│  }                                          │
├─────────────────────────────────────────────┤
│  + obtener_modelo(tipo) → Model             │
│  + obtener_producto(tipo, id) → Product     │
│  + obtener_producto_o_404(tipo, id) → Product│
│  + obtener_producto_con_lock(tipo, id)      │
│  + es_tipo_fisico(tipo) → bool              │
└─────────────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
┌───────────────┐         ┌──────────────────┐
│ PhysicalProduct│        │  DigitalLicense   │
│ (fisico)      │         │  (software)       │
└───────────────┘         └──────────────────┘
```

**Criterio de aceptación cumplido**: No existen `if tipo == 'fisico'` para resolver qué modelo usar. Agregar un nuevo tipo de producto solo requiere agregarlo al `PRODUCT_MAP`.

### 6.2 Strategy Pattern — Procesamiento de Ventas

```
┌──────────────┐
│   Cliente    │
│ (OrderService│
│ .procesar_   │
│  pago)       │
└──────┬───────┘
       │ llama
       ▼
┌──────────────────────┐
│  producto.procesar_  │  ← Interfaz común
│  venta(cantidad)     │
└──────────┬───────────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌────────┐  ┌──────────┐
│ Físico │  │ Digital  │
│(descon-│  │(consumir │
│ tar    │  │ claves)  │
│ stock) │  │          │
└────────┘  └──────────┘
```

### 6.3 Service Layer Pattern

```
┌────────────────────────────────────────────────────────┐
│                   Service Layer                         │
├──────────────┬──────────────┬───────────┬─────────────┤
│ OrderService │ CartService  │ EmailSvc  │ StripeSvc   │
│ .procesar_   │ .calcular_   │ .enviar_  │ .crear_     │
│  pago()      │  totales()   │  boleta() │  checkout() │
└──────┬───────┴──────┬───────┴─────┬─────┴──────┬──────┘
       │              │             │            │
       ▼              ▼             ▼            ▼
   ┌────────┐  ┌──────────┐  ┌────────┐  ┌──────────┐
   │ Modelos │  │ Session  │  │ Email  │  │ Stripe   │
   │ (DB)    │  │ (Cart)   │  │ (SMTP) │  │ (API)    │
   └────────┘  └──────────┘  └────────┘  └──────────┘
```

### 6.4 Template Method — Procesar Venta

```
┌─────────────────────────────────────┐
│      procesar_venta(cantidad)        │
│  (método plantilla en subclases)     │
├─────────────────────────────────────┤
│ PhysicalProduct:                     │
│   1. confirmar_reserva(cantidad)    │
│   2. return True                     │
├─────────────────────────────────────┤
│ DigitalLicense:                      │
│   1. Buscar N claves DISPONIBLES    │
│   2. Si insuficientes → error       │
│   3. Marcar como CONSUMIDAS         │
│   4. Asignar orden_compra           │
│   5. return True                     │
└─────────────────────────────────────┘
```

---

## 7. APIs

### 7.1 Stripe API — Procesamiento de Pagos

| Método | Endpoint Interno | Descripción |
|--------|-----------------|-------------|
| `crear_checkout_session()` | `/crear-sesion-stripe/` | Crea sesión de pago Stripe Checkout |
| Webhook (Stripe → app) | `/pago-exitoso/` | Procesa pago exitoso post-redirección |

**Moneda**: CLP (peso chileno)
**Modo**: `payment` (pago único)

### 7.2 APIs Internas (AJAX)

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/carrito/agregar/` | POST (JSON) | Agrega producto al carrito |
| `/carrito/actualizar/` | POST (JSON) | Actualiza cantidad de un ítem |
| `/carrito/eliminar/` | POST (JSON) | Elimina ítem del carrito |
| `/carrito/vaciar/` | POST | Vacía el carrito |

### 7.3 Django Admin (Interfaz interna)

| Modelo | Registrado | Personalización |
|--------|-----------|----------------|
| `PhysicalProduct` | ✅ | fieldsets, list_display, badges de estado |
| `DigitalLicense` | ✅ | fieldsets, list_display, badges de estado |
| `Order` | ✅ | fieldsets, OrderItemInline, badges |
| `OrderItem` | ✅ | Admin propio + Inline en Order |
| `UserProfile` | ✅ | search_fields |

### 7.4 Panel Administrador Web

| URL | Vista | Descripción |
|-----|-------|-------------|
| `/admin-panel/` | `dashboard` | Dashboard con estadísticas y tabs |
| `/admin-panel/agregar/<tipo>/` | `agregar_producto` | Crear producto físico o licencia |
| `/admin-panel/editar/<id>/<tipo>/` | `editar_producto` | Editar producto existente |
| `/admin-panel/toggle-estado/<id>/<tipo>/` | `toggle_estado` | Activar/desactivar producto |
| `/admin-panel/eliminar/<id>/<tipo>/` | `eliminar_producto` | Eliminar producto con protección |

---

## 8. Backlog y Participación del Equipo

### 8.1 Tareas Completadas

| # | Tarea | Prioridad | Estado | Responsable |
|---|-------|-----------|--------|-------------|
| 1 | **Factory Method** — Crear `ProductFactory` en `factories.py` y centralizar resolución de modelos | Alta | ✅ Completo | I3 |
| 2 | **SRP Refactor** — Separar `views.py` en `views_cart.py`, `views_auth.py`, `views_orders.py`, `views_profile.py` | Alta | ✅ Completo | I2 |
| 3 | **DIP / OrderService** — Mover lógica de negocio de vistas a `OrderService` | Alta | ✅ Completo | I2 |
| 4 | **LSP** — Corregir `DigitalLicense.procesar_venta()` para procesar N licencias | Media | ✅ Completo | I2 |
| 5 | **Unificar CartService** — Eliminar duplicación de `calcular_totales` | Media | ✅ Completo | I2 |
| 6 | **Registrar OrderItem en admin.py** | Alta | ✅ Completo | I3 |
| 7 | **Panel Administrador Web** — Dashboard, CRUD productos, modal, buscador | Alta | ✅ Completo | I3 |
| 8 | **UI/UX** — Diseño visual glass, responsividad, animaciones, consistencia | Alta | ✅ Completo | I1 |
| 9 | **Modelos de datos** — Product, PhysicalProduct, DigitalLicense, Order, OrderItem, UserProfile | Alta | ✅ Completo | I2 |
| 10 | **Integración Stripe** — Checkout, webhook, pagos en CLP | Alta | ✅ Completo | I1 |
| 11 | **Autenticación** — Registro, login, password reset, guest checkout | Alta | ✅ Completo | I1 |
| 12 | **Despliegue en Render** | Alta | ✅ Completo | I2 |

### 8.2 Leyenda

- **I1**: Integrante 1 — Backend, modelos, Stripe
- **I2**: Integrante 2 — Frontend, refactorización, servicios
- **I3**: Integrante 3 — Panel administración, Factory Method, UI/UX

### 8.3 Diagrama de Participación

```
I1 ████████████████████  (Modelos, Stripe, Auth)
I2 ████████████████████  (SRP, DIP, LSP, CartService, Frontend)
I3 ████████████████████  (Admin Web, Factory Method, UI/UX)
```
