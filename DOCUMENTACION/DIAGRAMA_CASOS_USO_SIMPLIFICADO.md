# DIAGRAMA DE CASOS DE USO - OmniTech ERP
## Versión Simple y Compacta

---

## Actores

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ACTORES DEL SISTEMA                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   👤 CLIENTE REGISTRADO                                                      │
│   ├── Puede comprar productos                                                │
│   ├── Gestionar carrito                                                      │
│   ├── Ver sus pedidos y licencias                                            │
│   └── Gestionar su perfil                                                    │
│                                                                             │
│   👤 INVITADO / GUEST                                                        │
│   ├── Navegar catálogo                                                       │
│   ├── Agregar productos al carrito                                           │
│   ├── Checkout sin registro (solo email)                                     │
│   └── Crear cuenta post-compra                                              │
│                                                                             │
│   👨‍💼 ADMINISTRADOR                                                           │
│   ├── Gestionar productos (CRUD)                                            │
│   ├── Gestionar pedidos                                                     │
│   ├── Gestionar licencias                                                    │
│   ├── Ver reportes                                                           │
│   └── Gestionar stock                                                        │
│                                                                             │
│   💳 STRIPE (Sistema Externo)                                                │
│   ├── Procesar pagos                                                         │
│   └── Enviar webhooks                                                        │
│                                                                             │
│   📧 EMAIL SERVICE (Sistema Externo)                                         │
│   └── Enviar boletas                                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Casos de Uso por Paquete

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         PAQUETE: CATÁLOGO                                    ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║   ┌──────────────────┐                                                       ║
║   │ UC-01: Navegar   │                                                       ║
║   │     Catálogo     │                                                       ║
║   └────────┬─────────┘                                                       ║
║            │                                                                  ║
║   ┌────────▼─────────┐                                                       ║
║   │ UC-02: Filtrar   │                                                       ║
║   │     Productos    │                                                       ║
║   │ (tipo/categoría)│                                                       ║
║   └────────┬─────────┘                                                       ║
║            │                                                                  ║
║   ┌────────▼─────────┐                                                       ║
║   │ UC-03: Ver        │                                                       ║
║   │     Detalle       │                                                       ║
║   │     Producto      │                                                       ║
║   └──────────────────┘                                                       ║
║                                                                              ║
║   Actor: Cliente, Invitado                                                   ║
║                                                                              ║
╚═══════════════════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════════════════╗
║                         PAQUETE: CARRITO                                     ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║   ┌──────────────────┐                                                       ║
║   │ UC-05: Agregar    │                                                       ║
║   │     al Carrito   │──┐                                                    ║
║   └──────────────────┘  │  ┌──────────────────┐                               ║
║                        │  │ UC-38: Reservar   │                               ║
║   ┌──────────────────┐ │  │     Stock         │                               ║
║   │ UC-06: Modificar │ │  └──────────────────┘                               ║
║   │     Cantidad     │─┘                                                     ║
║   └──────────────────┘                                                       ║
║                                                                              ║
║   ┌──────────────────┐                                                       ║
║   │ UC-07: Eliminar  │                                                       ║
║   │     del Carrito  │                                                       ║
║   └──────────────────┘                                                       ║
║                                                                              ║
║   ┌──────────────────┐                                                       ║
║   │ UC-09: Ver       │                                                       ║
║   │     Carrito      │                                                       ║
║   └──────────────────┘                                                       ║
║                                                                              ║
║   Actor: Cliente, Invitado                                                   ║
║                                                                              ║
╚═══════════════════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════════════════╗
║                         PAQUETE: CHECKOUT                                     ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║   ┌──────────────────┐                                                       ║
║   │ UC-10: Completar │                                                       ║
║   │     Checkout     │                                                       ║
║   └────────┬─────────┘                                                       ║
║            │                                                                  ║
║   ┌────────▼─────────┐                                                       ║
║   │ UC-11: Ingresar  │                                                       ║
║   │     Datos Envío   │                                                       ║
║   │  (email/región)  │                                                       ║
║   └────────┬─────────┘                                                       ║
║            │                                                                  ║
║   ┌────────▼─────────┐                                                       ║
║   │ UC-14: Proceder  │                                                       ║
║   │     al Pago      │                                                       ║
║   └────────┬─────────┘                                                       ║
║            │                                                                  ║
║   ┌────────▼─────────┐                                                       ║
║   │ UC-15: Procesar   │◄──────────┐                                           ║
║   │     Pago          │           │                                           ║
║   └────────┬─────────┘           │                                           ║
║            │                    │                                           ║
║            ▼                    │                                           ║
║   ┌──────────────────┐  ┌──────────┐                                        ║
║   │ UC-17: Recibir   │  │  💳      │                                        ║
║   │     Notificación │◄─│  STRIPE  │                                        ║
║   └──────────────────┘  └──────────┘                                        ║
║                                                                              ║
║   Actor: Cliente, Invitado                                                    ║
║                                                                              ║
╚═══════════════════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════════════════╗
║                         PAQUETE: PEDIDOS                                      ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║   ┌──────────────────┐                                                       ║
║   │ UC-18: Ver       │                                                       ║
║   │     Mis Pedidos  │                                                       ║
║   └────────┬─────────┘                                                       ║
║            │                                                                  ║
║   ┌────────▼─────────┐                                                       ║
║   │ UC-19: Detalle   │                                                       ║
║   │     de Pedido    │                                                       ║
║   └────────┬─────────┘                                                       ║
║            │                                                                  ║
║   ┌────────▼─────────┐                                                       ║
║   │ UC-20: Estado    │                                                       ║
║   │     de Pedido    │                                                       ║
║   └────────┬─────────┘                                                       ║
║            │                                                                  ║
║   ┌────────▼─────────┐                                                       ║
║   │ UC-21: Cancelar  │                                                       ║
║   │     Pedido       │──┐                                                    ║
║   └──────────────────┘  │                                                    ║
║                        │  ┌──────────────────┐                               ║
║   Actor: Cliente       │  │ UC-40: Liberar   │                               ║
║                        └──│     Reserva      │                               ║
║                          └──────────────────┘                               ║
║                                                                              ║
╚═══════════════════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════════════════╗
║                         PAQUETE: LICENCIAS                                    ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║   ┌──────────────────┐     ┌──────────────────┐                               ║
║   │ UC-22: Ver       │────▶│ UC-23: Ver       │                               ║
║   │     Mis Licencias│     │     Clave        │                               ║
║   └──────────────────┘     └────────┬─────────┘                               ║
║                                     │                                          ║
║                                     ▼                                          ║
║                           ┌──────────────────┐                               ║
║                           │ UC-43: Desencriptar│                               ║
║                           │     Clave         │                               ║
║                           └──────────────────┘                               ║
║                                                                              ║
║   Actor: Cliente                                                            ║
║                                                                              ║
╚═══════════════════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════════════════╗
║                         PAQUETE: USUARIO                                      ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║   ┌──────────────────┐                                                       ║
║   │ UC-24: Registrarse│                                                      ║
║   └────────┬─────────┘                                                       ║
║            │                                                                  ║
║   ┌────────▼─────────┐                                                       ║
║   │ UC-25: Iniciar   │                                                       ║
║   │     Sesión       │                                                       ║
║   └────────┬─────────┘                                                       ║
║            │                                                                  ║
║   ┌────────▼─────────┐                                                       ║
║   │ UC-26: Cerrar    │                                                       ║
║   │     Sesión       │                                                       ║
║   └────────┬─────────┘                                                       ║
║            │                                                                  ║
║   ┌────────▼─────────┐                                                       ║
║   │ UC-27: Ver       │                                                       ║
║   │     Perfil       │                                                       ║
║   └────────┬─────────┘                                                       ║
║            │                                                                  ║
║   ┌────────▼─────────┐                                                       ║
║   │ UC-28: Editar   │                                                       ║
║   │     Perfil      │                                                       ║
║   └──────────────────┘                                                       ║
║                                                                              ║
║   ─── GUEST ONLY ───                                                         ║
║                                                                              ║
║   ┌──────────────────┐                                                       ║
║   │ UC-29: Guest     │                                                       ║
║   │     Checkout    │                                                       ║
║   └────────┬─────────┘                                                       ║
║            │                                                                  ║
║   ┌────────▼─────────┐                                                       ║
║   │ UC-30: Crear     │                                                       ║
║   │     Cuenta Post  │                                                       ║
║   │     Compra       │                                                       ║
║   └──────────────────┘                                                       ║
║                                                                              ║
║   Actor: Cliente, Invitado                                                   ║
║                                                                              ║
╚═══════════════════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════════════════╗
║                         PAQUETE: ADMINISTRACIÓN                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║   ┌──────────────────┐                                                       ║
║   │ UC-31: Gestionar │──┐                                                    ║
║   │     Productos   │  │  ┌──────────────────┐                               ║
║   └──────────────────┘  │  │ UC-42: Encriptar │                               ║
║                          │  │     Clave        │                               ║
║   ┌──────────────────┐  │  └──────────────────┘                               ║
║   │ UC-32: Gestionar │  │                                                    ║
║   │     Pedidos     │──┘                                                    ║
║   └──────────────────┘                                                       ║
║                                                                              ║
║   ┌──────────────────┐                                                       ║
║   │ UC-33: Gestionar │                                                       ║
║   │     Licencias   │                                                       ║
║   └──────────────────┘                                                       ║
║                                                                              ║
║   ┌──────────────────┐                                                       ║
║   │ UC-34: Ver       │                                                       ║
║   │     Reportes    │                                                       ║
║   └──────────────────┘                                                       ║
║                                                                              ║
║   ┌──────────────────┐                                                       ║
║   │ UC-35: Gestionar │                                                       ║
║   │     Stock       │──────┐                                                ║
║   └──────────────────┘       │  ┌──────────────────┐                         ║
║                              │  │ UC-41: Reabaste- │                         ║
║   Actor: Admin              └──│     cimiento    │                         ║
║                               └──────────────────┘                         ║
║                                                                              ║
╚═══════════════════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════════════════╗
║                         PAQUETE: SISTEMA (Background)                        ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║   ┌──────────────────┐     ┌──────────────────┐                               ║
║   │ UC-36: Enviar     │────▶│ UC-37: Generar   │                               ║
║   │     Boleta       │     │     PDF          │                               ║
║   └──────────────────┘     └──────────────────┘                               ║
║            │                                                                  ║
║            ▼                                                                  ║
║   ┌──────────────────┐                                                       ║
║   │ 📧 EMAIL SERVICE  │                                                       ║
║   └──────────────────┘                                                       ║
║                                                                              ║
║   ┌──────────────────┐                                                       ║
║   │ UC-38: Reservar   │◄── UC-05 (Agregar al carrito)                        ║
║   │     Stock        │                                                       ║
║   └────────┬─────────┘                                                       ║
║            │                                                                  ║
║   ┌────────▼─────────┐                                                       ║
║   │ UC-39: Confirmar │◄── UC-15 (Pago exitoso)                               ║
║   │     Reserva      │                                                       ║
║   └────────┬─────────┘                                                       ║
║            │                                                                  ║
║   ┌────────▼─────────┐                                                       ║
║   │ UC-40: Liberar   │◄── UC-16/UC-21 (Cancelar)                            ║
║   │     Reserva      │                                                       ║
║   └──────────────────┘                                                       ║
║                                                                              ║
║   Actor: Sistema (Automático)                                                ║
║                                                                              ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## Diagrama de Herencia de Casos de Uso

```
                              ┌─────────────────┐
                              │   COMPRAR       │
                              │   (extends)     │
                              └────────┬────────┘
                                       │
           ┌───────────────────────────┼───────────────────────────┐
           │                           │                           │
           ▼                           ▼                           ▼
    ┌─────────────┐            ┌─────────────┐            ┌─────────────┐
    │ COMPRAR    │            │ COMPRAR     │            │ GUEST       │
    │ COMO       │            │ COMO        │            │ CHECKOUT    │
    │ CLIENTE    │            │ INVITADO    │            │ (UC-29)     │
    └─────────────┘            └─────────────┘            └─────────────┘
           │                           │
           ▼                           ▼
    ┌─────────────┐            ┌─────────────┐
    │ • Login     │            │ • Ingresar  │
    │ • Ver carro │            │   email     │
    │ • Checkout  │            │ • Checkout  │
    │ • Pagar     │            │ • Pagar     │
    └─────────────┘            │ • Ofrecer   │
                                │   registro  │
                                └─────────────┘
```

---

## Tabla de Casos de Uso

| ID | Nombre | Actor | Descripción |
|----|--------|-------|-------------|
| **Catálogo** |
| UC-01 | Navegar Catálogo | Cliente, Invitado | Ver lista de productos |
| UC-02 | Filtrar Productos | Cliente, Invitado | Filtrar por tipo/categoría |
| UC-03 | Ver Detalle Producto | Cliente, Invitado | Ver información detallada |
| UC-04 | Buscar Producto | Cliente | Buscar por término |
| **Carrito** |
| UC-05 | Agregar al Carrito | Cliente, Invitado | Añadir producto |
| UC-06 | Modificar Cantidad | Cliente | Cambiar cantidad |
| UC-07 | Eliminar del Carrito | Cliente | Quitar producto |
| UC-08 | Vaciar Carrito | Cliente | Limpiar carrito |
| UC-09 | Ver Carrito | Cliente, Invitado | Ver contenido y totales |
| **Checkout** |
| UC-10 | Completar Checkout | Cliente, Invitado | Proceso de compra |
| UC-11 | Ingresar Datos Envío | Cliente, Invitado | Formulario envío |
| UC-12 | Seleccionar Ciudad | Cliente, Invitado | Ciudad según región |
| UC-13 | Revisar Resumen | Cliente, Invitado | Ver totales |
| UC-14 | Proceder al Pago | Cliente, Invitado | Ir a Stripe |
| **Pagos** |
| UC-15 | Procesar Pago | Cliente, Invitado | Pago con Stripe |
| UC-16 | Cancelar Pago | Cliente | Cancelar checkout |
| UC-17 | Recibir Notificación | Sistema | Webhook Stripe |
| **Pedidos** |
| UC-18 | Ver Mis Pedidos | Cliente | Lista de pedidos |
| UC-19 | Detalle de Pedido | Cliente | Info completa |
| UC-20 | Estado de Pedido | Cliente | Seguimiento |
| UC-21 | Cancelar Pedido | Cliente | Anular pedido |
| **Licencias** |
| UC-22 | Ver Mis Licencias | Cliente | Lista licencias |
| UC-23 | Ver Clave | Cliente | Ver clave desencriptada |
| **Usuario** |
| UC-24 | Registrarse | Cliente | Crear cuenta |
| UC-25 | Iniciar Sesión | Cliente | Login |
| UC-26 | Cerrar Sesión | Cliente | Logout |
| UC-27 | Ver Perfil | Cliente | Ver perfil |
| UC-28 | Editar Perfil | Cliente | Modificar datos |
| UC-29 | Guest Checkout | Invitado | Comprar sin registro |
| UC-30 | Crear Cuenta Post-Compra | Invitado | Registro después |
| **Administración** |
| UC-31 | Gestionar Productos | Admin | CRUD productos |
| UC-32 | Gestionar Pedidos | Admin | Ver/modificar pedidos |
| UC-33 | Gestionar Licencias | Admin | CRUD licencias |
| UC-34 | Ver Reportes | Admin | Estadísticas |
| UC-35 | Gestionar Stock | Admin | Control inventario |
| **Sistema** |
| UC-36 | Enviar Boleta | Sistema | Email con boleta |
| UC-37 | Generar PDF | Sistema | Crear documento |
| UC-38 | Reservar Stock | Sistema | Bloquear stock |
| UC-39 | Confirmar Reserva | Sistema | Convertir en venta |
| UC-40 | Liberar Reserva | Sistema | Devolver stock |
| UC-41 | Reabastecimiento | Sistema | Orden de compra |
| UC-42 | Encriptar Clave | Sistema | Cifrar licencia |
| UC-43 | Desencriptar Clave | Sistema | Descifrar licencia |
