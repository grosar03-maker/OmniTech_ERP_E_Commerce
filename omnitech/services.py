"""
Services Layer - OmniTech
Lógica de negocio centralizada aplicando SOLID y bajo acoplamiento
"""

import uuid
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db import transaction

from .factories import ProductFactory
from .models import Order, OrderItem, OrderState

# =============================================================================
# ORDER SERVICE - Aplica SRP y reduce acoplamiento
# =============================================================================


class OrderService:
    """
    Servicio encargado de la orquestación de pedidos.
    SRP: Solo maneja la lógica de negocio de pedidos
    DIP: Utiliza dependencias inyectadas o propiedades de los modelos
    """

    @staticmethod
    def crear_pedido(usuario, email_invitado, region, observaciones, costo_envio):
        """Crea un pedido pendiente."""
        numero_pedido = f'OT-{uuid.uuid4().hex[:8].upper()}'
        return Order.objects.create(
            numero_pedido=numero_pedido,
            usuario=usuario,
            email_invitado=email_invitado,
            estado=OrderState.PENDIENTE_PAGO,
            region_envio=region,
            observaciones=observaciones,
            costo_envio=costo_envio,
        )

    @staticmethod
    def procesar_pago(order_id, carrito_temp):
        """
        Procesa el pago exitoso aplicando lógica de dominio.
        OCP: Usa polimorfismo de los productos (procesar_venta)
        """
        try:
            with transaction.atomic():
                order = Order.objects.select_for_update().get(numero_pedido=order_id)

                if order.estado != OrderState.PENDIENTE_PAGO:
                    return None, False, 'Pedido ya procesado o cancelado'

                subtotal = Decimal('0.00')

                for item_data in carrito_temp:
                    producto_id = item_data['producto_id']
                    tipo = item_data['tipo']
                    cantidad = int(item_data['cantidad'])
                    precio = Decimal(str(item_data['precio']))
                    subtotal += precio * cantidad

                    # Factory Method + OCP: polimorfismo vía ProductFactory
                    producto = ProductFactory.obtener_producto_con_lock(tipo, producto_id)
                    producto.procesar_venta(cantidad)

                    OrderItem.objects.create(
                        pedido=order,
                        producto_fisico=producto if ProductFactory.es_tipo_fisico(tipo) else None,
                        licencia=producto if not ProductFactory.es_tipo_fisico(tipo) else None,
                        cantidad=cantidad,
                        precio_unitario=precio,
                    )

                # Actualizar pedido
                order.subtotal = subtotal
                order.total = subtotal + (order.costo_envio or Decimal('0'))
                order.estado = OrderState.PAGADO_PROCESANDO
                from django.utils import timezone

                order.fecha_pago = timezone.now()
                order.save()

                return order, True, None
        except Exception as e:
            return None, False, str(e)

    @staticmethod
    def crear_pedido_para_stripe(request, carrito, email, region, observaciones):
        """
        DIP: Crea un pedido PENDIENTE_PAGO y calcula costo de envío.
        Reemplaza la lógica directa que estaba en views.py.
        """
        import uuid

        from django.conf import settings

        numero_pedido = f'OT-{uuid.uuid4().hex[:8].upper()}'

        peso_total = sum(item.get('peso', 0) * item['cantidad'] for item in carrito if item.get('tipo') == 'fisico')

        costo_envio = Decimal(str(peso_total * 500)) if peso_total > 0 else Decimal('0')

        if region == 'La Araucania':
            subtotal = sum(Decimal(str(item['precio'])) * item['cantidad'] for item in carrito)
            if subtotal > Decimal(str(settings.SUBSIDIO_MONTO)):
                costo_envio = Decimal('0')

        order = Order.objects.create(
            numero_pedido=numero_pedido,
            usuario=request.user if request.user.is_authenticated else None,
            email_invitado=email,
            estado=OrderState.PENDIENTE_PAGO,
            region_envio=region,
            observaciones=observaciones,
            costo_envio=costo_envio,
        )

        request.session['order_id'] = numero_pedido
        request.session['carrito_temp'] = carrito
        request.session.save()

        return order, costo_envio

    @staticmethod
    def calcular_costo_envio(carrito, region):
        """Calcula el costo de envío aplicando RN-04."""
        peso_total = sum(item.get('peso', 0) * item['cantidad'] for item in carrito if item.get('tipo') == 'fisico')

        costo = Decimal(str(peso_total * 500)) if peso_total > 0 else Decimal('0')

        # RN-04: Subsidio La Araucanía
        if region == 'La Araucania':
            subtotal = sum(Decimal(str(item['precio'])) * item['cantidad'] for item in carrito)
            if subtotal > Decimal(str(settings.SUBSIDIO_MONTO)):
                costo = Decimal('0')

        return costo


# =============================================================================
# CART SERVICE - Gestión del carrito
# =============================================================================


class CartService:
    """Servicio para gestión del carrito (SRP)."""

    @staticmethod
    def get_carrito(request):
        """Obtiene el carrito de la sesión."""
        return request.session.get(settings.CART_SESSION_KEY, [])

    @staticmethod
    def save_carrito(request, carrito):
        """Guarda el carrito en la sesión."""
        request.session[settings.CART_SESSION_KEY] = carrito
        request.session.modified = True

    @staticmethod
    def calcular_totales(carrito):
        """Calcula subtotales del carrito."""
        subtotal = Decimal('0.00')
        items_data = []

        for item in carrito:
            cantidad = int(item.get('cantidad', 1))
            precio = Decimal(str(item.get('precio', 0)))
            tipo = item.get('tipo', 'fisico')
            producto_id = item.get('producto_id')

            item_subtotal = precio * cantidad
            subtotal += item_subtotal

            try:
                producto = ProductFactory.obtener_producto(tipo, producto_id)
                nombre = producto.nombre
                imagen = producto.imagen_url or (
                    '/static/img/product-placeholder.png'
                    if ProductFactory.es_tipo_fisico(tipo)
                    else '/static/img/license-placeholder.png'
                )
                peso = float(producto.peso) if ProductFactory.es_tipo_fisico(tipo) else 0
            except ObjectDoesNotExist:
                continue

            items_data.append(
                {
                    'id': producto_id,
                    'tipo': tipo,
                    'nombre': nombre,
                    'precio': float(precio),
                    'cantidad': cantidad,
                    'subtotal': float(item_subtotal),
                    'imagen': imagen,
                    'peso': peso,
                }
            )

        peso_total = sum(item['peso'] * item['cantidad'] for item in items_data)
        costo_envio = Decimal(str(peso_total * 500)) if peso_total > 0 else Decimal('0.00')

        return {
            'items': items_data,
            'subtotal': float(subtotal),
            'costo_envio': float(costo_envio),
            'total': float(subtotal + costo_envio),
            'cantidad_items': sum(item['cantidad'] for item in items_data),
        }


# =============================================================================
# EMAIL SERVICE - Envío de correos
# =============================================================================


class EmailService:
    """Servicio para envío de correos (SRP)."""

    @staticmethod
    def _logo_url():
        return f"{settings.SITE_URL}/static/img/logo_web.png"

    @staticmethod
    def enviar_boleta(pedido):
        """Envía la boleta por correo."""
        from .services_template import renderizar_boleta

        email_destino = pedido.email_invitado or (pedido.usuario.email if pedido.usuario else None)

        if not email_destino:
            return False, 'No se encontró email'

        try:
            html_boleta = renderizar_boleta(pedido, logo_url=EmailService._logo_url())

            send_mail(
                subject=f'OmniTech - Comprobante de compra {pedido.numero_pedido}',
                message=f'Tu pedido {pedido.numero_pedido} ha sido confirmado. Total: ${float(pedido.total):,.0f}',
                from_email=settings.EMAIL_FROM,
                recipient_list=[email_destino],
                html_message=html_boleta,
                fail_silently=False,
            )
            return True, f'Boleta enviada a {email_destino}'
        except Exception as e:
            return False, str(e)

    @staticmethod
    def notificar_stock_bajo(producto, cantidad):
        """Notifica cuando el stock está bajo."""
        try:
            send_mail(
                subject=f'Alerta: Stock bajo - {producto.nombre}',
                message=f'El producto tiene stock bajo: {cantidad} unidades.',
                from_email=settings.EMAIL_FROM,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=True,
            )
            return True
        except Exception:
            return False


# =============================================================================
# FUNCIONES LEGACY - Mantenidas por compatibilidad
# =============================================================================


def generar_html_boleta(pedido):
    """Función legacy - ahora delegamos al template."""
    from .services_template import renderizar_boleta

    return renderizar_boleta(pedido, logo_url=EmailService._logo_url())


def enviar_boleta_pedido(pedido):
    """Envía la boleta por correo (legacy)."""
    return EmailService.enviar_boleta(pedido)


def enviar_notificacion_stock_bajo(producto, cantidad):
    """Notifica cuando el stock está bajo (legacy)."""
    return EmailService.notificar_stock_bajo(producto, cantidad)


def enviar_claves_licencia(pedido):
    """
    Envía las claves de licencia por correo electrónico.
    Solo envía licencias digitales compradas.
    """
    from django.conf import settings
    from django.core.mail import send_mail

    licencias = pedido.items.filter(licencia__isnull=False)

    if not licencias.exists():
        return False, 'No hay licencias digitales en este pedido'

    email_destino = pedido.email_invitado or (pedido.usuario.email if pedido.usuario else None)

    if not email_destino:
        return False, 'No se encontró email del cliente'

    logo_url = f"{settings.SITE_URL}/static/img/logo_web.png"

    try:
        claves_info = []
        for item in licencias:
            licencia = item.licencia
            try:
                clave = licencia.desencriptar_clave()
            except Exception:
                clave = licencia.clave_encriptada

            claves_info.append(
                {
                    'nombre': licencia.nombre,
                    'plataforma': licencia.plataforma,
                    'clave': clave,
                    'duracion': licencia.duracion_dias,
                }
            )

        html_content = generar_html_claves(claves_info, pedido.numero_pedido)

        send_mail(
            subject=f'OmniTech - Tus claves de licencia #{pedido.numero_pedido}',
            message=f'Tu pedido {pedido.numero_pedido} ha sido confirmado. Aquí están tus claves de licencia.',
            from_email=settings.EMAIL_FROM,
            recipient_list=[email_destino],
            html_message=html_content,
            fail_silently=False,
        )
        return True, f'Claves enviadas a {email_destino}'
    except Exception as e:
        return False, str(e)


def generar_html_claves(claves, numero_pedido):
    """Genera HTML con las claves de licencia — diseño mejorado, compatible con Gmail/Outlook."""
    cards_html = ''
    for item in claves:
        cards_html += f"""
        <tr>
            <td style="padding: 0 0 16px 0;">
                <table width="100%" cellpadding="0" cellspacing="0" style="background:#13131f; border:1px solid #2a2a3e; border-radius:12px; overflow:hidden;">
                    <!-- Card header -->
                    <tr>
                        <td style="padding: 16px 20px; background: linear-gradient(135deg, #1a1a2e 0%, #16162a 100%); border-bottom: 1px solid #2a2a3e;">
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td>
                                        <div style="font-size:15px; font-weight:700; color:#f1f1f3;">{item['nombre']}</div>
                                        <div style="margin-top:5px;">
                                            <span style="display:inline-block; background:rgba(167,139,250,0.15); color:#a78bfa; padding:2px 9px; border-radius:20px; font-size:10px; font-weight:700; letter-spacing:0.5px;">{item['plataforma']}</span>
                                        </div>
                                    </td>
                                    <td align="right">
                                        <div style="font-size:10px; color:#52525b; text-align:right; margin-bottom:3px;">Vigencia</div>
                                        <div style="font-size:16px; color:#4ade80; font-weight:700; text-align:right;">{item['duracion']} días</div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <!-- Clave -->
                    <tr>
                        <td style="padding: 16px 20px;">
                            <div style="font-size:10px; color:#52525b; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;">Tu clave de licencia</div>
                            <div style="background:#09090d; border:1px solid #2a2a3e; border-radius:8px; padding:14px 16px;">
                                <span style="font-family:'Courier New',Courier,monospace; font-size:15px; color:#a78bfa; font-weight:700; letter-spacing:1px; word-break:break-all; line-height:1.5;">{item['clave']}</span>
                            </div>
                            <div style="margin-top:10px; font-size:11px; color:#52525b;">
                                Copia esta clave y pégala al activar tu software.
                            </div>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        """

    html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OmniTech - Tus claves de licencia</title>
</head>
<body style="margin:0; padding:0; background:#09090d; font-family:'Segoe UI',Helvetica,Arial,sans-serif; -webkit-font-smoothing:antialiased;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#09090d; padding: 32px 16px;">
<tr><td align="center">
<table role="presentation" width="520" cellpadding="0" cellspacing="0" style="background:#111118; border:1px solid #1e1e2e; border-radius:16px; overflow:hidden; max-width:520px; width:100%;">

    <!-- HEADER -->
    <tr>
        <td style="background:linear-gradient(135deg,#18182a 0%,#0f0f1a 60%,#1a0f2e 100%); padding:30px 32px 26px; border-bottom:1px solid #1e1e2e;">
            <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                    <td>
                        <img src="{logo_url}" alt="OmniTech" style="max-width: 140px; height: auto; border-radius: 8px;">
                        <div style="font-size:11px; color:#6b7280; margin-top:8px; letter-spacing:1px; text-transform:uppercase;">Tus claves de licencia</div>
                    </td>
                    <td align="right">
                        <div style="display:inline-block; background:rgba(74,222,128,0.12); border:1px solid rgba(74,222,128,0.3); color:#4ade80; padding:6px 14px; border-radius:20px; font-size:12px; font-weight:700;">
                            ✓ Pago confirmado
                        </div>
                    </td>
                </tr>
            </table>
        </td>
    </tr>

    <!-- PEDIDO INFO -->
    <tr>
        <td style="padding: 20px 32px; border-bottom:1px solid #1e1e2e; background:#0e0e18;">
            <div style="font-size:11px; color:#52525b; margin-bottom:4px;">Número de pedido</div>
            <div style="font-size:22px; font-weight:800; color:#a78bfa; letter-spacing:-0.3px;">{numero_pedido}</div>
        </td>
    </tr>

    <!-- TITULO LICENCIAS -->
    <tr>
        <td style="padding: 22px 32px 8px;">
            <div style="font-size:10px; color:#52525b; text-transform:uppercase; letter-spacing:1px;">Licencias adquiridas</div>
        </td>
    </tr>

    <!-- LICENCIAS -->
    <tr>
        <td style="padding: 4px 32px 8px;">
            <table width="100%" cellpadding="0" cellspacing="0">
                {cards_html}
            </table>
        </td>
    </tr>

    <!-- INSTRUCCIONES -->
    <tr>
        <td style="padding: 0 32px 24px;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background:linear-gradient(135deg,#1a1a2e,#16162a); border:1px solid #2a2a3e; border-radius:12px;">
                <tr>
                    <td style="padding: 18px 20px;">
                        <div style="font-size:13px; color:#f1f1f3; font-weight:700; margin-bottom:12px;">Cómo activar tu licencia</div>
                        <table cellpadding="0" cellspacing="0">
                            <tr><td style="padding:3px 0; font-size:12px; color:#a1a1aa; line-height:1.7;">1. &nbsp;Copia la clave de licencia que ves arriba.</td></tr>
                            <tr><td style="padding:3px 0; font-size:12px; color:#a1a1aa; line-height:1.7;">2. &nbsp;Abre la aplicación o plataforma del software.</td></tr>
                            <tr><td style="padding:3px 0; font-size:12px; color:#a1a1aa; line-height:1.7;">3. &nbsp;Busca la opción "Activar licencia" o "Ingresar clave".</td></tr>
                            <tr><td style="padding:3px 0; font-size:12px; color:#a1a1aa; line-height:1.7;">4. &nbsp;Pega la clave y confirma la activación.</td></tr>
                        </table>
                    </td>
                </tr>
            </table>
        </td>
    </tr>

    <!-- FOOTER -->
    <tr>
        <td style="padding: 18px 32px 26px; border-top:1px solid #1e1e2e; text-align:center; background:#0e0e18;">
            <p style="font-size:11px; color:#3f3f46; margin:0;">
                OmniTech © 2026 · <a href="mailto:soporte@omnitech.cl" style="color:#a78bfa; text-decoration:none;">soporte@omnitech.cl</a>
            </p>
        </td>
    </tr>

</table>
</td></tr>
</table>
</body>
</html>
    """
    return html
