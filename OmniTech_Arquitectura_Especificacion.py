from weasyprint import HTML

# Content for the PDF document
html_content = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>
        @page {
            size: A4;
            margin: 20mm;
            background-color: #f4f7f9;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #333;
            line-height: 1.6;
            background-color: #f4f7f9;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 800px;
            margin: auto;
        }
        header {
            text-align: center;
            border-bottom: 3px solid #2c3e50;
            margin-bottom: 30px;
            padding-bottom: 20px;
        }
        h1 { color: #2c3e50; font-size: 24pt; margin-bottom: 5pt; }
        h2 { color: #2980b9; font-size: 18pt; margin-top: 25pt; border-left: 5px solid #2980b9; padding-left: 10px; }
        h3 { color: #34495e; font-size: 14pt; margin-top: 15pt; }
        p, li { font-size: 11pt; }
        .section-box {
            background-color: #ffffff;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .highlight {
            color: #e67e22;
            font-weight: bold;
        }
        .prompt-box {
            background-color: #2c3e50;
            color: #ecf0f1;
            padding: 20px;
            border-radius: 5px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 10pt;
            white-space: pre-wrap;
            border: 1px solid #1a252f;
        }
        .footer {
            text-align: center;
            font-size: 9pt;
            color: #7f8c8d;
            margin-top: 40px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        th, td {
            text-align: left;
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }
        th { background-color: #2980b9; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Documento de Arquitectura y Especificación de Sistema</h1>
            <p><strong>Proyecto:</strong> OmniTech ERP & E-Commerce</p>
            <p>Universidad Católica de Temuco | Ingeniería Civil en Informática</p>
            <p><strong>Estudiante:</strong> Gustavo Rosa | <strong>Fecha:</strong> Abril 2026</p>
        </header>

        <section class="section-box">
            <h2>1. Descripción General</h2>
            <p>OmniTech es un sistema transaccional híbrido diseñado para el retail tecnológico. Unifica la venta B2C de hardware y licencias digitales con un módulo ERP para la gestión de importaciones internacionales y logística local.</p>
            <p>El enfoque principal es el <strong>modelado arquitectónico</strong> bajo principios de Arquitectura Hexagonal, utilizando simuladores (Mocks/Stubs) para las integraciones externas.</p>
        </section>

        <section class="section-box">
            <h2>2. Objetivos Arquitectónicos</h2>
            <ul>
                <li><strong>Arquitectura Hexagonal:</strong> Aislamiento del dominio de la infraestructura externa.</li>
                <li><strong>Capa de Servicios:</strong> Motor transaccional centralizado para orquestar la lógica.</li>
                <li><strong>Propiedades ACID:</strong> Garantizar integridad de datos y evitar sobreventas concurrentes.</li>
            </ul>
        </section>

        <section class="section-box">
            <h2>3. Lógica y Reglas de Negocio Estrictas</h2>
            <p>Políticas automatizadas que rigen el comportamiento del sistema:</p>
            <ul>
                <li><span class="highlight">RN-01. Bifurcación de Pedido Mixto:</span> Despacho inmediato de software vía email y encolamiento de hardware para empaque físico tras pago exitoso.</li>
                <li><span class="highlight">RN-02. Inmutabilidad de Licencias:</span> Las licencias enviadas pasan a estado "Consumida" y no admiten devoluciones ni reasignaciones.</li>
                <li><span class="highlight">RN-03. Reserva Volátil (Mutex):</span> Bloqueo de stock físico por 15 minutos durante el checkout; liberación automática en caso de fallo.</li>
                <li><span class="highlight">RN-04. Subsidio Regional:</span> Envío gratis para compras > $100.000 CLP con destino a la Región de La Araucanía.</li>
                <li><span class="highlight">RN-05. Reabastecimiento Automático:</span> Generación de borrador de importación cuando el stock cae al 15% del umbral mínimo.</li>
                <li><span class="highlight">RN-06. Guest Checkout:</span> Permite compras indicando solo un correo para seguimiento, sin necesidad de registro previo.</li>
            </ul>
        </section>

        <section class="section-box">
            <h2>4. Requisitos Funcionales (Resumen)</h2>
            <table>
                <tr><th>Categoría</th><th>Requisitos Clave</th></tr>
                <tr><td>Usuarios</td><td>Registro, Login, Perfil, Recuperación de contraseña.</td></tr>
                <tr><td>E-Commerce</td><td>Catálogo con filtros, Carrito híbrido, Compra invitados.</td></tr>
                <tr><td>Digital</td><td>Venta y entrega automática de licencias, Visualización de claves.</td></tr>
                <tr><td>Pagos/Logística</td><td>Validación de pagos, Tracking de pedidos, Comprobantes.</td></tr>
                <tr><td>Administración</td><td>Gestión de stock, Reportes de ventas, Control de importaciones.</td></tr>
            </table>
        </section>

        <section class="section-box">
            <h2>5. Requisitos No Funcionales</h2>
            <ul>
                <li><strong>Rendimiento:</strong> Tiempo de respuesta < 3 segundos.</li>
                <li><strong>Seguridad:</strong> Cifrado de contraseñas y datos sensibles; autenticación segura.</li>
                <li><strong>Escalabilidad:</strong> Código modular preparado para crecimiento sin degradación de rendimiento.</li>
                <li><strong>Disponibilidad:</strong> Operación 24/7 con respaldos automáticos de base de datos.</li>
            </ul>
        </section>

        <section class="section-box">
            <h2>6. Patrones de Diseño a Implementar</h2>
            <ul>
                <li><strong>Strategy:</strong> Cálculo de envíos dinámico (Gratis vs Peso).</li>
                <li><strong>Observer:</strong> Desencadenar acciones post-pago (email vs logística) de forma asíncrona.</li>
                <li><strong>State:</strong> Gestión de ciclos de vida (Licencias e Importaciones).</li>
                <li><strong>Adapter:</strong> Conexión con simuladores de pago y couriers.</li>
                <li><strong>Factory Method:</strong> Instanciación dinámica de ítems en el carrito.</li>
            </ul>
        </section>

        <section class="section-box">
            <h2>7. MASTER PROMPT PARA ASISTENTE DE CÓDIGO</h2>
            <p>Copia y pega este bloque en tu herramienta de IA para iniciar el desarrollo:</p>
            <div class="prompt-box">
Actúa como Arquitecto de Software Senior experto en Django. Construiremos el MVP de "OmniTech ERP & E-Commerce".

CONTEXTO:
Sistema híbrido (Hardware + Licencias Digitales) con Arquitectura Hexagonal y Service Layer (services.py). Prohibido "Fat Views" o "Fat Models". Integraciones externas mediante Adaptadores (Mocks).

TAREA 1: GENERAR models.py
1. Herencia: Clase base abstracta 'Product'. 'PhysicalProduct' (peso, stock, umbral) y 'DigitalLicense' (clave_encriptada) heredan de ella.
2. Patrón State: Usar TextChoices para DigitalLicense (DISPONIBLE, RESERVADA, CONSUMIDA) y Order (PENDIENTE_PAGO, PAGADO, COMPLETADO, CANCELADO).
3. Transaccional: Modelos Order y OrderItem con ForeignKeys claras. Implementar Meta constraints para asegurar integridad ACID.
4. Notificaciones/Perfil: Modelo UserProfile extendido para trazabilidad.

Genera el código limpio y profesional para models.py.
            </div>
        </section>

        <div class="footer">
            <p>Documento Generado para el Proyecto de Arquitectura de Software - UCT 2026</p>
        </div>
    </div>
</body>
</html>
"""

# Save to PDF
output_path = "OmniTech_Arquitectura_Especificacion.pdf"
HTML(string=html_content).write_pdf(output_path)