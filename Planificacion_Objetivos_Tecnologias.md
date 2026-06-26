# Planificación de Objetivos y Tecnologías

## OmniTech ERP & E-Commerce

---

## 1. Resumen del Proyecto

### 1.1 Identificación del Problema

OmniTech es una tienda de tecnología que comercializa simultáneamente dos tipos de producto radicalmente distintos:

- **Productos Físicos (Hardware):** Componentes de PC, periféricos, equipos de cómputo, accesorios. Requieren gestión de inventario físico, control de stock, reserva temporal durante el checkout, cálculo de costos de envío por peso, y despacho físico con seguimiento de estado.
- **Licencias Digitales (Software):** Claves de activación, códigos de licencia, suscripciones digitales. Son productos intangibles que requieren almacenamiento encriptado, ciclo de vida controlado (disponible → reservada → consumida), y entrega inmediata post-pago vía email.

Operar ambos tipos de producto por separado genera los siguientes problemas:

1. **Duplicación de sistemas:** Catálogos separados, carritos separados, procesos de venta diferentes.
2. **Pérdida de ventas:** Un cliente que quiere comprar un mouse y una licencia de Office en la misma transacción no puede hacerlo.
3. **Gestión manual:** Las licencias se entregan manualmente, sin trazabilidad ni automatización.
4. **Cálculo de envío inexacto:** No existe un sistema que calcule automáticamente el costo de envío basado en el peso real de los productos.
5. **Sin reserva de stock:** Los productos físicos pueden ser comprados por múltiples clientes simultáneamente sin control de inventario en tiempo real.
6. **Autenticación limitada:** Solo se permite registro con usuario y contraseña tradicional, sin opción a utilizar cuentas de Google, GitHub u otras redes sociales.
7. **Sin comprobante digital:** No se genera un comprobante PDF descargable de la compra realizada.
8. **Sin sistema de reseñas:** Los clientes no pueden calificar ni comentar los productos adquiridos.

### 1.2 Solución Propuesta

OmniTech ERP & E-Commerce es un **sistema transaccional híbrido** integrado en una sola plataforma web que unifica la venta de productos físicos y digitales bajo un mismo carrito de compras, con un proceso de checkout unificado y comportamientos post-pago diferenciados según el tipo de producto.

**Características principales de la solución:**

| Aspecto | Implementación |
|---|---|
| **Catálogo unificado** | Un solo catálogo web que muestra ambos tipos de producto con búsqueda, filtros por categoría y tipo. |
| **Carrito híbrido** | El cliente puede agregar hardware y licencias al mismo carrito. El sistema maneja las diferencias de forma transparente. |
| **Checkout único** | Un solo formulario de checkout que captura datos de envío (para hardware) y email (para licencias). |
| **Pago integrado** | Pago con tarjeta de crédito/débito vía Stripe Checkout en pesos chilenos (CLP). |
| **Bifurcación post-pago** | Las licencias se entregan inmediatamente vía email; el hardware se encola para empaque y despacho físico. |
| **Reserva de stock (15 min)** | El stock se reserva durante el checkout y se libera si el pago no se completa. |
| **Envío subsidiado** | Descuento automático en envío para compras >$100,000 CLP en la Región de La Araucanía. |
| **Licencias encriptadas** | Las claves se almacenan encriptadas (Fernet + SHA256) y se entregan automáticamente post-pago. |
| **Autenticación social** | Inicio de sesión y registro con Google y GitHub mediante OAuth 2.0. |
| **Comprobante PDF** | Generación de boleta PDF descargable desde la página de pago exitoso e historial de pedidos. |
| **Reseñas y valoraciones** | Sistema de calificación (1-5 estrellas) y comentarios para productos adquiridos. |

### 1.3 Reglas de Negocio

| Código | Regla de Negocio | Descripción |
|---|---|---|
| **RN-01** | Bifurcación mixta de despacho | Software se entrega inmediatamente vía email; hardware se encola para empaque físico y despacho. |
| **RN-02** | Ciclo de vida de licencias | DISPONIBLE → RESERVADA → CONSUMIDA. Una vez consumida, la licencia es inmutable. |
| **RN-03** | Reserva volátil de stock | El stock físico se reserva por 15 minutos durante el checkout. Si no se completa el pago, la reserva se libera. |
| **RN-04** | Subsidio de envío | Envío gratis para compras >$100,000 CLP con destino a la Región de La Araucanía. |
| **RN-05** | Reabastecimiento automático | Cuando el stock disponible cae al 15% del umbral mínimo, se genera alerta de reabastecimiento. |
| **RN-06** | Guest checkout | Clientes pueden comprar sin registrarse, solo proporcionando su email. Los datos del guest se fusionan si se registra después. |

---

## 2. Alcance a Cubrir

### 2.1 Actores del Sistema

| Actor | Descripción | Privilegios |
|---|---|---|
| **Visitante (no autenticado)** | Usuario que navega el sitio sin haber iniciado sesión | Navegar catálogo, ver detalle de productos, buscar productos, agregar al carrito, realizar checkout como invitado (guest), iniciar sesión o registrarse con email o redes sociales |
| **Cliente (autenticado)** | Usuario que ha iniciado sesión (email o red social) | Todo lo del visitante más: acceder a historial de pedidos, ver detalle de pedidos, descargar boletas PDF, ver licencias adquiridas con sus claves, gestionar perfil (RUT, teléfono, dirección), calificar y reseñar productos comprados, cerrar sesión |
| **Administrador / Staff** | Usuario con permisos de staff de Django | Todo lo anterior más: acceder al panel de administración web, ver dashboard con estadísticas (ventas, productos, pedidos), CRUD completo de productos físicos y licencias digitales, activar/desactivar productos, eliminar productos, exportar pedidos a CSV/Excel |

### 2.2 Funcionalidades por Actor

#### Visitante / Cliente

| Módulo | Funcionalidad | Descripción |
|---|---|---|
| **Catálogo** | Navegación home | Ver productos destacados, ofertas y novedades en la página principal |
| **Catálogo** | Listado de productos | Ver todos los productos con paginación, filtros por categoría y tipo (físico/digital) |
| **Catálogo** | Búsqueda | Buscar productos por nombre, SKU o categoría mediante campo de búsqueda en navbar y página de productos |
| **Catálogo** | Detalle de producto | Ver información completa: nombre, precio, descripción, imagen, categoría, stock disponible, reseñas |
| **Carrito** | Agregar al carrito | Agregar productos físicos y digitales al mismo carrito desde cualquier página |
| **Carrito** | Ver carrito | Visualizar resumen del carrito con productos, cantidades, subtotales, costo de envío y total |
| **Carrito** | Actualizar cantidades | Modificar cantidad de productos físicos en el carrito |
| **Carrito** | Eliminar items | Quitar productos específicos del carrito |
| **Carrito** | Vaciar carrito | Eliminar todos los productos del carrito |
| **Carrito** | Persistencia | El carrito persiste durante la sesión del navegador |
| **Checkout** | Formulario de envío | Ingresar dirección de envío, región, ciudad, teléfono y observaciones |
| **Checkout** | Cálculo de envío | Cálculo automático del costo de envío basado en el peso total de los productos físicos |
| **Checkout** | Guest checkout | Completar la compra sin registrarse, solo con email (RN-06) |
| **Pago** | Stripe Checkout | Redirección a Stripe para pago con tarjeta de crédito/débito en CLP |
| **Pago** | Pago exitoso | Página de confirmación con resumen del pedido, número de seguimiento y enlace para descargar boleta PDF |
| **Pago** | Pago fallido | Manejo de errores de pago con mensaje al usuario y liberación de stock reservado |
| **Pedidos** | Historial | Lista de todos los pedidos realizados con estado, fecha, monto total |
| **Pedidos** | Detalle | Ver items del pedido, cantidades, precios, estado actual, costo de envío, observaciones |
| **Pedidos** | Descargar boleta | Descargar comprobante PDF del pedido |
| **Licencias** | Mis licencias | Lista de licencias digitales adquiridas con nombre, plataforma, clave desencriptada, duración |
| **Autenticación** | Registro con email | Crear cuenta con nombre de usuario, email y contraseña |
| **Autenticación** | Registro con Google | Crear cuenta usando cuenta de Google (OAuth 2.0) |
| **Autenticación** | Registro con GitHub | Crear cuenta usando cuenta de GitHub (OAuth 2.0) |
| **Autenticación** | Inicio de sesión | Iniciar sesión con email/usuario y contraseña, o con Google/GitHub |
| **Autenticación** | Recuperar contraseña | Solicitar restablecimiento de contraseña vía email |
| **Autenticación** | Cerrar sesión | Finalizar la sesión activa |
| **Perfil** | Ver perfil | Visualizar datos personales (RUT, teléfono, región, ciudad, dirección) |
| **Perfil** | Editar perfil | Actualizar datos personales y preferencias |
| **Productos** | Reseñas | Calificar productos comprados (1-5 estrellas) y escribir comentarios |
| **Productos** | Ver reseñas | Leer reseñas de otros clientes en la página de detalle del producto |

#### Administrador / Staff

| Módulo | Funcionalidad | Descripción |
|---|---|---|
| **Dashboard** | Estadísticas | Ver total de productos, pedidos, ingresos, productos con stock bajo |
| **Dashboard** | Navegación por tabs | Alternar entre vista de productos físicos y licencias digitales |
| **Productos Físicos** | Listar | Ver todos los productos físicos con SKU, nombre, precio, stock, estado |
| **Productos Físicos** | Crear | Agregar nuevo producto físico con nombre, SKU, precio, peso, stock, categoría, imagen |
| **Productos Físicos** | Editar | Modificar cualquier campo de un producto físico existente |
| **Productos Físicos** | Activar/Desactivar | Cambiar el estado del producto entre activo e inactivo |
| **Productos Físicos** | Eliminar | Eliminar un producto físico con confirmación modal |
| **Licencias Digitales** | Listar | Ver todas las licencias con SKU, nombre, plataforma, estado, duración |
| **Licencias Digitales** | Crear | Agregar nueva licencia con nombre, SKU, clave encriptada, plataforma, duración |
| **Licencias Digitales** | Editar | Modificar campos de una licencia existente |
| **Licencias Digitales** | Activar/Desactivar | Cambiar estado de la licencia |
| **Licencias Digitales** | Eliminar | Eliminar licencia con confirmación |
| **Pedidos** | Ver pedidos | Listar todos los pedidos del sistema con filtros por estado |
| **Pedidos** | Actualizar estado | Cambiar estado del pedido (procesando, completado, cancelado) |
| **Pedidos** | Exportar | Exportar pedidos a archivo CSV/Excel |
| **Notificaciones** | Stock bajo | Recibir alertas visuales de productos que necesitan reabastecimiento (RN-05) |

### 2.3 Fuera del Alcance (Primera Entrega)

| Funcionalidad | Motivo |
|---|---|
| Aplicación móvil nativa (iOS/Android) | El proyecto se limita a web responsive. Una app nativa requeriría desarrollo separado y API más robusta. |
| Integración con servicios de despacho externo (Starken, Chilexpress) | Requiere convenios comerciales y APIs de terceros. Se simula el proceso de despacho con estados manuales. |
| Facturación electrónica SII | Requiere certificación ante el Servicio de Impuestos Internos de Chile. Se entrega comprobante interno (boleta) no tributario. |
| Múltiples bodegas o sucursales | El sistema asume una sola bodega central. |
| Pasarela de pago Webpay Plus | Stripe cubre el requerimiento de pago con tarjeta. Webpay queda como mejora futura (Objetivo O8). |
| Cupones de descuento | Se implementará en una fase posterior (Objetivo O7). |
| Chat en vivo / soporte ticket | El soporte se maneja por email. |

---

## 3. Objetivos

### 3.1 Objetivos del Sistema

| N° | Objetivo | Prioridad | Funcionalidad asociada | Código |
|---|---|---|---|---|
| **O1** | Implementar autenticación mediante redes sociales | Alta | Login con Google OAuth 2.0 y GitHub OAuth usando django-allauth, permitiendo registro e inicio de sesión con un solo clic | `OAUTH` |
| **O2** | Migrar sistema de correos a proveedor compatible con Render | Alta | Reemplazar SMTP de Gmail por SendGrid (Add-On nativo de Render) o Mailgun. Garantizar entrega de boletas, claves de licencia y notificaciones de stock bajo | `EMAIL` |
| **O3** | Integrar sistema de reseñas y valoraciones de productos | Alta | Permitir que clientes registrados califiquen productos (1-5 estrellas) y dejen comentarios visibles en la página de detalle | `REVIEWS` |
| **O4** | Implementar generación de comprobantes PDF | Media | Generar boleta PDF descargable desde la página de pago exitoso, detalle de pedido e historial de pedidos | `PDF` |
| **O5** | Exponer API REST para productos y pedidos | Media | Crear endpoints RESTful con Django REST Framework para consultar catálogo, productos por tipo, detalle de producto y estado de pedidos | `API` |
| **O6** | Implementar dashboard administrativo con exportación de datos | Media | Agregar exportación de pedidos y productos a CSV/Excel desde el panel de administración | `EXPORT` |
| **O7** | Agregar sistema de cupones de descuento | Media | Crear modelos y lógica para cupones con descuento porcentual o fijo, aplicables en el checkout | `COUPONS` |
| **O8** | Integrar Webpay Plus como medio de pago alternativo | Media | Agregar soporte para Webpay Plus (Transbank) como método de pago local chileno | `WEBPAY` |
| **O9** | Mejorar seguimiento de pedidos físicos | Baja | Agregar estados intermedios (en preparación, despachado, en tránsito, entregado) con notificación al cliente por email | `TRACKING` |
| **O10** | Implementar notificaciones en tiempo real al administrador | Baja | Usar WebSockets o polling para notificar al administrador sobre nuevos pedidos y stock bajo sin recargar la página | `REALTIME` |

### 3.2 Justificación de Objetivos

#### O1 — Autenticación con redes sociales (Prioridad: Alta)

**Justificación:** Actualmente el sistema solo permite registro con formulario tradicional (usuario, email, contraseña). Esto representa una barrera de entrada para usuarios que prefieren utilizar cuentas existentes. La integración con Google y GitHub mediante OAuth 2.0 reduce la fricción en el registro, aumenta la tasa de conversión y mejora la experiencia de usuario. Además, elimina la necesidad de recordar una contraseña adicional.

**Implementación:** Usar `django-allauth` que proporciona:
- Vistas preconstruidas para login social
- Manejo de tokens OAuth con refresh automático
- Vinculación de cuentas sociales a usuarios existentes
- Callbacks seguros con CSRF protection

**Flujo:**
1. El usuario hace clic en "Iniciar sesión con Google" o "Iniciar sesión con GitHub"
2. Es redirigido al provedor OAuth para autorizar
3. Al autorizar, es redirigido de vuelta al sistema
4. django-allauth verifica el token, crea o vincula la cuenta, e inicia sesión

#### O2 — Migrar sistema de correos (Prioridad: Alta)

**Justificación:** Render bloquea las conexiones SMTP salientes a Gmail (puertos 587 y 465), como se evidenció en el error `[Errno 101] Network is unreachable`. El sistema actual no puede enviar boletas ni claves de licencia en producción. SendGrid es el Add-On oficial de Render para correos transaccionales, con 100 emails/día gratis y sin restricciones de red.

**Implementación:**
- Agregar SendGrid como Add-On en Render Dashboard
- Usar las credenciales (API Key) que Render inyecta automáticamente como variable de entorno
- Configurar Django con el backend SMTP de SendGrid:
  - `EMAIL_HOST = 'smtp.sendgrid.net'`
  - `EMAIL_PORT = 587`
  - `EMAIL_HOST_USER = 'apikey'`
  - `EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_API_KEY')`

#### O3 — Sistema de reseñas (Prioridad: Alta)

**Justificación:** Las reseñas y valoraciones son un factor crítico en la decisión de compra en tiendas online. Permiten que los clientes compartan su experiencia, aumentan la confianza en los productos y mejoran el SEO del sitio. Además, proporcionan retroalimentación valiosa al administrador sobre la calidad de los productos.

**Implementación:**
- Nuevo modelo `Review` con campos: producto (FK genérico), usuario (FK), puntuación (1-5), comentario, fecha, estado (aprobado/pendiente)
- Vista para crear reseña (solo usuarios autenticados que hayan comprado el producto)
- Vista para mostrar reseñas en la página de detalle del producto
- Moderación por parte del administrador
- Cálculo de puntuación promedio por producto

#### O4 — Comprobantes PDF (Prioridad: Media)

**Justificación:** Los clientes necesitan un comprobante descargable de su compra para respaldo personal, reembolsos o garantías. Actualmente solo se envía una boleta HTML por email que no siempre llega o no es fácil de guardar.

**Implementación:**
- Usar `WeasyPrint` o `xhtml2pdf` para convertir templates HTML a PDF
- Generar el PDF en tiempo real cuando el usuario solicita descargar
- Almacenar en la nube (opcional) para consultas futuras
- Botón "Descargar boleta" en:
  - Página de pago exitoso
  - Detalle del pedido
  - Historial de pedidos

#### O5 — API REST (Prioridad: Media)

**Justificación:** Django REST Framework ya está instalado en el proyecto pero no se utiliza. Exponer una API REST permite:
- Consumir datos del catálogo desde un frontend JavaScript más interactivo
- Preparar el terreno para una futura aplicación móvil
- Integraciones con terceros (ej. sistema de despacho, facturación)
- Cache de consultas frecuentes

**Implementación:**
- Serializers para Product, PhysicalProduct, DigitalLicense, Order
- ViewSets con permisos y autenticación
- Endpoints:
  - `GET /api/productos/` — Catálogo completo con filtros
  - `GET /api/productos/<tipo>/<id>/` — Detalle de producto
  - `GET /api/pedidos/` — Pedidos del usuario autenticado
  - `GET /api/categorias/` — Lista de categorías disponibles

#### O6 — Exportación de datos (Prioridad: Media)

**Justificación:** El administrador necesita exportar pedidos y productos para análisis, contabilidad o reportes. La exportación manual desde el panel de Django admin o la base de datos es tediosa y propensa a errores.

**Implementación:**
- Botón "Exportar CSV" y "Exportar Excel" en el dashboard admin
- Generación del archivo con `csv` nativo de Python y `openpyxl` para Excel
- Filtros por rango de fechas y estado del pedido
- Columnas incluidas: número pedido, fecha, cliente, items, subtotal, envío, total, estado

#### O7 — Cupones de descuento (Prioridad: Media)

**Justificación:** Los cupones son una herramienta de marketing esencial para promociones, descuentos por temporada, fidelización de clientes y captación de nuevos usuarios.

**Implementación:**
- Modelo `Coupon` con: código (único), tipo (porcentaje/monto fijo), valor, fecha expiración, uso máximo, usos actuales, monto mínimo de compra
- Validación del cupón en el checkout
- Aplicación del descuento al subtotal antes de calcular el total
- Mostrar descuento aplicado en el resumen del carrito

#### O8 — Webpay Plus (Prioridad: Media)

**Justificación:** Stripe es una pasarela internacional que funciona con tarjetas de crédito/débito. Webpay Plus de Transbank es el medio de pago online más usado en Chile, soporta RedCompra y transferencias bancarias. Agregarlo permite llegar a clientes que no tienen tarjetas internacionales.

**Implementación:**
- Integración con SDK `transbank-sdk` de Transbank
- Flujo: iniciar transacción → redirigir a Webpay → confirmar en callback
- Manejo de respuestas: éxito, rechazo, cancelación
- Modo ambiente de prueba (integración) primero, luego producción

#### O9 — Seguimiento de pedidos (Prioridad: Baja)

**Justificación:** Actualmente los pedidos físicos solo tienen estados binarios (pagado_procesando → completado). Agregar estados intermedios mejora la experiencia del cliente al poder rastrear su compra.

**Implementación:**
- Nuevos estados: `EN_PREPARACION`, `DESPACHADO`, `EN_TRANSITO`, `ENTREGADO`
- Notificación automática por email en cada cambio de estado
- Vista visual tipo timeline en el detalle del pedido

#### O10 — Notificaciones en tiempo real (Prioridad: Baja)

**Justificación:** El administrador debe recargar la página para ver nuevos pedidos o alertas de stock bajo. Las notificaciones en tiempo real mejoran la capacidad de respuesta.

**Implementación:**
- Django Channels con WebSockets para:
  - Notificación de nuevo pedido
  - Alerta de stock bajo
  - Pedido completado
- Alternativa simplificada: polling con JavaScript cada 30 segundos

### 3.3 Mapa de Objetivos vs. Reglas de Negocio

| Objetivo | RN-01 | RN-02 | RN-03 | RN-04 | RN-05 | RN-06 |
|---|---|---|---|---|---|---|
| O1 — Auth social | — | — | — | — | — | ✅ |
| O2 — Email | ✅ | ✅ | — | — | ✅ | — |
| O3 — Reseñas | — | — | — | — | — | — |
| O4 — PDF | ✅ | — | — | — | — | — |
| O5 — API REST | — | — | ✅ | ✅ | — | — |
| O6 — Exportación | — | — | — | — | ✅ | — |
| O7 — Cupones | — | — | — | ✅ | — | — |
| O8 — Webpay | ✅ | ✅ | ✅ | — | — | ✅ |
| O9 — Tracking | ✅ | — | — | — | — | — |
| O10 — Tiempo real | — | — | — | — | ✅ | — |

---

## 4. Definición de Tecnologías

### 4.1 Stack Tecnológico Completo

| N° | Tecnología | Versión | Categoría | Necesidad que cubre |
|---|---|---|---|---|
| **T1** | **Python** | 3.11+ | Lenguaje de programación | Lenguaje principal del backend. Elegido por su legibilidad, amplio ecosistema de bibliotecas para desarrollo web, seguridad y criptografía. Compatible con todos los frameworks y herramientas del stack. |
| **T2** | **Django** | 4.2 LTS | Framework web full-stack | Framework principal del proyecto. Proporciona: ORM para base de datos, sistema de autenticación, panel de administración, manejo de sesiones, formularios con validación, middleware de seguridad (CSRF, XSS, SQL injection), sistema de templates, manejo de archivos estáticos y emails. |
| **T3** | **Django REST Framework (DRF)** | 3.14+ | Framework API REST | Creación de API REST para consumo externo. Proporciona serializers, view sets, autenticación por token, paginación, navegación automática de API, y documentación navegable. Ya instalado en el proyecto. |
| **T4** | **django-allauth** | Última estable | Autenticación social | Integración unificada de autenticación local y con redes sociales (Google, GitHub). Maneja registro, inicio de sesión, cierre de sesión, verificación de email, conexión de múltiples cuentas sociales a un mismo usuario, y tokens OAuth. |
| **T5** | **SQLite** | 3.x | Base de datos (desarrollo) | Base de datos relacional ligera para desarrollo local. No requiere servidor, archivo único, ideal para entornos de desarrollo. |
| **T6** | **PostgreSQL** | 16.x | Base de datos (producción) | Base de datos relacional robusta para producción en Render. Soporta transacciones ACID, índices avanzados, consultas concurrentes y es la base de datos recomendada por Render para aplicaciones Django. |
| **T7** | **Stripe SDK** | 7.0+ | Pasarela de pago | Procesamiento de pagos con tarjeta de crédito/débito internacional. Proporciona: Stripe Checkout (página de pago alojada), creación de sesiones de pago en CLP, manejo de webhooks para confirmación, reembolsos, y dashboard de transacciones. |
| **T8** | **Transbank SDK** | Última estable | Pasarela de pago local | Integración con Webpay Plus de Transbank para pagos con tarjetas chilenas (RedCompra, crédito). Medio de pago más usado en Chile, requerido para alcance nacional. |
| **T9** | **SendGrid** | — | Servicio de correo transaccional | Envío de correos electrónicos desde Render. Add-On nativo de Render que proporciona API key automática como variable de entorno. Entrega garantizada de boletas de compra, claves de licencia y notificaciones. 100 emails/día gratis. |
| **T10** | **WeasyPrint** | Última estable | Generación de PDF | Convierte templates HTML + CSS a PDF. Permite generar comprobantes de compra con el mismo diseño responsivo de los correos. Soporta CSS moderno, imágenes, tablas y estilos complejos. |
| **T11** | **Cryptography (Fernet)** | 41.0+ | Encriptación | Biblioteca de criptografía simétrica para encriptar/desencriptar claves de licencia. Usa AES en modo CBC con HMAC. Clave derivada de SECRET_KEY de Django mediante SHA256. |
| **T12** | **WhiteNoise** | 6.0+ | Servicio de estáticos | Sirve archivos estáticos (CSS, JS, imágenes) en producción sin necesidad de Nginx. Comprime y cachea automáticamente. Integrado con Django y Gunicorn. |
| **T13** | **Gunicorn** | 21.0+ | Servidor WSGI | Servidor web para producción. Maneja peticiones HTTP concurrentes con múltiples workers. Configurado en el Procfile de Render. |
| **T14** | **JavaScript (ES6+)** | — | Frontend interactivo | Lenguaje de programación del lado del cliente. Proporciona interactividad: operaciones AJAX del carrito (agregar, actualizar, eliminar sin recargar), filtros en vivo del catálogo, validación de formularios, animaciones y actualización dinámica de interfaces. |
| **T15** | **CSS3 (Liquid Glass)** | — | Diseño y estilos | Framework de estilos propio con diseño moderno tipo Apple Liquid Glass. Incluye: glassmorphism, animaciones CSS, transiciones suaves, diseño responsivo, sistema de cuadrícula flexible, tipografía personalizada, sombras, modales y efectos hover. |
| **T16** | **HTML5** | — | Estructura web | Lenguaje de marcado para las plantillas Django. Semántico, accesible, compatible con navegadores modernos. |
| **T17** | **Render** | — | Plataforma de despliegue | Plataforma cloud PaaS para alojar la aplicación. Proporciona: despliegue automático desde GitHub, PostgreSQL gestionado, Add-On SendGrid, SSL gratuito, DNS personalizado, logs en tiempo real y escalado automático. |
| **T18** | **Git / GitHub** | — | Control de versiones | Control de versiones del código fuente. Permite trabajo colaborativo, revisión de código, despliegue continuo a Render desde rama develop, y backup del proyecto. |
| **T19** | **django-widget-tweaks** | 1.5+ | Utilidad de templates | Permite modificar atributos HTML de los widgets de formularios Django directamente en las templates. Útil para agregar clases CSS, placeholders y atributos data. |

### 4.2 Arquitectura de Tecnologías

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLIENTE (Navegador)                          │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    FRONTEND (HTML5 + CSS3 + JS)               │   │
│  │  • Liquid Glass Design (glassmorphism, animaciones)          │   │
│  │  • Fetch API (AJAX para carrito, búsqueda en vivo)           │   │
│  │  • Stripe Checkout (redirección a Stripe)                    │   │
│  │  • django-widget-tweaks (formularios personalizados)         │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                   SERVIDOR (Render - Gunicorn)               │   │
│  │                                                              │   │
│  │  ┌────────────────────────────────────────────────────────┐  │   │
│  │  │              DJANGO 4.2 LTS (Full-Stack)               │  │   │
│  │  │                                                        │  │   │
│  │  │  ┌─────────────┐  ┌──────────┐  ┌──────────────────┐  │  │   │
│  │  │  │  Views /    │  │  Django  │  │  django-allauth  │  │  │   │
│  │  │  │  Templates  │  │  Admin   │  │  (OAuth social)  │  │  │   │
│  │  │  └──────┬──────┘  └──────────┘  └──────────────────┘  │  │   │
│  │  │         │                                              │  │   │
│  │  │  ┌──────┴──────────────────────────────────────────┐   │  │   │
│  │  │  │           SERVICE LAYER (Services)               │   │  │   │
│  │  │  │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │   │  │   │
│  │  │  │  │ Order    │ │ Cart     │ │ EmailService     │ │   │  │   │
│  │  │  │  │ Service  │ │ Service  │ │ (SendGrid)      │ │   │  │   │
│  │  │  │  └──────────┘ └──────────┘ └──────────────────┘ │   │  │   │
│  │  │  │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │   │  │   │
│  │  │  │  │ Stripe   │ │ Webpay   │ │ ProductFactory   │ │   │  │   │
│  │  │  │  │ Service  │ │ Service  │ │ (Factory Method) │ │   │  │   │
│  │  │  │  └──────────┘ └──────────┘ └──────────────────┘ │   │  │   │
│  │  │  └──────────────────────────────────────────────────┘   │  │   │
│  │  │                                                        │  │   │
│  │  │  ┌──────────────────────────────────────────────────┐   │  │   │
│  │  │  │              ORM (Modelos Django)                │   │  │   │
│  │  │  │  ┌────────────┐ ┌──────────────┐ ┌────────────┐ │   │  │   │
│  │  │  │  │ Product    │ │ Physical     │ │ Digital    │ │   │  │   │
│  │  │  │  │ (Abstracto)│ │ Product      │ │ License    │ │   │  │   │
│  │  │  │  └────────────┘ └──────────────┘ └────────────┘ │   │  │   │
│  │  │  │  ┌────────────┐ ┌──────────────┐ ┌────────────┐ │   │  │   │
│  │  │  │  │ Order      │ │ OrderItem    │ │ UserProfile│ │   │  │   │
│  │  │  │  └────────────┘ └──────────────┘ └────────────┘ │   │  │   │
│  │  │  └──────────────────────────────────────────────────┘   │  │   │
│  │  └────────────────────────────────────────────────────────┘  │   │
│  │                        │                                      │
│  │                        ▼                                      │
│  │  ┌────────────────────────────────────────────────────────┐  │   │
│  │  │              SERVIDORES EXTERNOS                        │  │   │
│  │  │                                                        │  │   │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐             │  │   │
│  │  │  │ Stripe   │  │ Webpay   │  │ SendGrid │             │  │   │
│  │  │  │ (Pagos)  │  │ (Pagos)  │  │ (Email)  │             │  │   │
│  │  │  └──────────┘  └──────────┘  └──────────┘             │  │   │
│  │  │                                                        │  │   │
│  │  │  ┌──────────┐  ┌──────────┐                            │  │   │
│  │  │  │ Google   │  │ GitHub   │                            │  │   │
│  │  │  │ OAuth    │  │ OAuth    │                            │  │   │
│  │  │  └──────────┘  └──────────┘                            │  │   │
│  │  └────────────────────────────────────────────────────────┘  │   │
│  │                        │                                      │
│  │                        ▼                                      │
│  │  ┌────────────────────────────────────────────────────────┐  │   │
│  │  │                BASE DE DATOS (PostgreSQL)               │  │   │
│  │  │  Tablas: products, physical_products, digital_licenses, │  │   │
│  │  │          orders, order_items, user_profiles, reviews,   │  │   │
│  │  │          coupons, social_accounts (allauth)             │  │   │
│  │  └────────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.3 Patrones y Principios de Diseño

| Patrón | Tecnología / Implementación | Descripción |
|---|---|---|
| **Factory Method** | `ProductFactory` en `factories.py` | Crea instancias de `PhysicalProduct` o `DigitalLicense` según el tipo. Encapsula la lógica de creación y permite agregar nuevos tipos sin modificar el código existente. |
| **Strategy** | `procesar_venta()` polimórfico en modelos | Cada tipo de producto implementa `procesar_venta()` de forma diferente: `PhysicalProduct` confirma reserva de stock; `DigitalLicense` entrega la licencia y la marca como consumida. |
| **Service Layer** | `services.py` (OrderService, CartService, EmailService, StripeService) | Separa la lógica de negocio de las vistas. Los servicios orquestan operaciones complejas manteniendo las vistas delgadas (thin views) y facilitando pruebas unitarias. |
| **Template Method** | `procesar_pago()` en `OrderService` + `procesar_venta()` en productos | Define el esqueleto del proceso de pago: crear pedido → procesar items individualmente según su tipo → enviar confirmaciones. Las subclases implementan los pasos variables. |
| **OCP (Open/Closed)** | Modelos `Product` abstracto + `procesar_venta()` | Las clases están abiertas para extensión (nuevos tipos de producto) pero cerradas para modificación. Agregar un nuevo tipo solo requiere crear una subclase que implemente `procesar_venta()`. |
| **SRP (Single Responsibility)** | Separación en módulos de vistas | Cada módulo de vista tiene una responsabilidad única: `views_cart.py` (catálogo, carrito, checkout), `views_auth.py` (autenticación), `views_orders.py` (pedidos), `views_profile.py` (perfil), `views_admin.py` (admin). |
| **DIP (Dependency Inversion)** | Service Layer inyectado | Las vistas dependen de abstracciones (servicios) en lugar de implementaciones concretas. Ejemplo: `pago_exitoso` llama a `enviar_boleta_pedido()` sin conocer si usa SMTP, SendGrid o consola. |

### 4.4 Base de Datos: Modelo de Datos

#### Tablas Actuales

| Tabla | Columnas principales | Propósito |
|---|---|---|
| `products` (abstracta) | id, nombre, descripción, imagen_url, precio, sku, categoría, estado, fechas | Clase base para el catálogo híbrido. No tiene tabla física. |
| `physical_products` | Hereda de Product + peso, stock_físico, stock_reservado, umbral_mínimo, proveedor, ubicación_bodega | Productos físicos con gestión de inventario y reserva. |
| `digital_licenses` | Hereda de Product + clave_encriptada, plataforma, duración_días, estado_licencia, orden_compra (FK), fecha_asignación | Licencias digitales con ciclo de vida y claves encriptadas. |
| `orders` | numero_pedido (único), usuario (FK nullable), email_invitado, estado, subtotal, costo_envío, total, región_envío, observaciones, fechas | Pedidos del sistema con soporte para guest checkout. |
| `order_items` | pedido (FK), producto_físico (FK nullable), licencia (FK nullable), cantidad, precio_unitario, descuento | Items del pedido con constraint exclusivo (solo físico o solo licencia). |
| `user_profiles` | user (OneToOne), rut, teléfono, región, ciudad, dirección, newsletter, fechas | Perfil extendido de usuario. |
| `auth_user` (Django) | username, email, password, first_name, last_name, is_staff, is_active, date_joined | Usuarios del sistema (Django built-in). |

#### Nuevas Tablas Propuestas (Objetivos O1, O3, O7)

| Tabla | Columnas principales | Objetivo |
|---|---|---|
| `reviews` | id, producto_físico (FK nullable), licencia (FK nullable), usuario (FK), puntuación (1-5), comentario, fecha, estado (aprobado/pendiente) | O3 — Reseñas y valoraciones de productos |
| `coupons` | id, código (único), tipo (porcentaje/monto fijo), valor, fecha_expiracion, uso_máximo, usos_actuales, monto_mínimo, activo | O7 — Cupones de descuento |
| `social_account` (allauth) | user (FK), provider, uid, extra_data | O1 — Cuentas sociales vinculadas |
| `social_token` (allauth) | account (FK), token, token_secret, expires_at | O1 — Tokens de acceso OAuth |

### 4.5 Infraestructura de Despliegue

```
                    ┌──────────────────────────────┐
                    │      GitHub Repository        │
                    │  (grosar03-maker/OmniTech...) │
                    └──────────┬───────────────────┘
                               │ push (rama develop)
                               ▼
                    ┌──────────────────────────────┐
                    │        Render.com             │
                    │                               │
                    │  ┌─────────────────────────┐  │
                    │  │ Web Service (Gunicorn)   │  │
                    │  │ - Django 4.2            │  │
                    │  │ - WhiteNoise estáticos  │  │
                    │  │ - Python 3.11           │  │
                    │  └────────┬────────────────┘  │
                    │           │                    │
                    │  ┌────────┴────────────────┐  │
                    │  │ PostgreSQL (Base Datos)  │  │
                    │  └─────────────────────────┘  │
                    │           │                    │
                    │  ┌────────┴────────────────┐  │
                    │  │ SendGrid Add-On (Email)  │  │
                    │  │ SENDGRID_API_KEY env var │  │
                    │  └─────────────────────────┘  │
                    └──────────────────────────────┘
```

---

## 5. Resumen de Cambios Propuestos

### 5.1 Cambios Inmediatos (Prioridad Alta)

| Cambio | Archivos afectados | Descripción |
|---|---|---|
| Agregar django-allauth | `settings.py`, `urls.py`, templates | Autenticación con Google y GitHub |
| Configurar SendGrid | `settings.py` | Reemplazar SMTP Gmail por SendGrid SMTP |
| Agregar modelo Review | `models.py`, admin, templates | Sistema de reseñas y valoraciones |

### 5.2 Cambios a Mediano Plazo (Prioridad Media)

| Cambio | Archivos afectados | Descripción |
|---|---|---|
| Generación de PDF | `services.py`, nueva vista, template | Comprobantes PDF descargables |
| API REST | `serializers.py`, `views_api.py`, `urls.py` | Endpoints RESTful |
| Exportación CSV/Excel | `views_admin.py`, templates admin | Exportar datos desde dashboard |
| Cupones de descuento | `models.py`, `services.py`, checkout | Sistema de cupones |
| Webpay Plus | `services.py`, nueva vista, `urls.py` | Pasarela de pago chilena |

### 5.3 Mejoras Futuras (Prioridad Baja)

| Cambio | Descripción |
|---|---|
| Tracking de pedidos físicos | Estados intermedios con notificaciones por email |
| Notificaciones en tiempo real | WebSockets con Django Channels para nuevas órdenes y stock bajo |
| Soporte multibodega | Múltiples ubicaciones de inventario |
| Facturación electrónica SII | Integración con Servicio de Impuestos Internos de Chile |
| Aplicación móvil | App nativa con React Native o Flutter consumiendo la API REST |

---

*Documento generado para la actividad "Planificación de Objetivos y Tecnologías"*
