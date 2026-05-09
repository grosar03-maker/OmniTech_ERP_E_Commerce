"""
Services Layer - OmniTech
Lógica de negocio centralizada aplicando SOLID y bajo acoplamiento
"""

from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from decimal import Decimal
import uuid

from .models import (
    Order, OrderItem, OrderState, LicenseState
)
from .factories import ProductFactory


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
                    return None, False, "Pedido ya procesado o cancelado"

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

        peso_total = sum(
            item.get('peso', 0) * item['cantidad']
            for item in carrito
            if item.get('tipo') == 'fisico'
        )

        costo_envio = Decimal(str(peso_total * 500)) if peso_total > 0 else Decimal('0')

        if region == 'La Araucanía':
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
        peso_total = sum(
            item.get('peso', 0) * item['cantidad'] 
            for item in carrito
            if item.get('tipo') == 'fisico'
        )
        
        costo = Decimal(str(peso_total * 500)) if peso_total > 0 else Decimal('0')
        
        # RN-04: Subsidio La Araucanía
        if region == 'La Araucanía':
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
                    '/static/img/product-placeholder.png' if ProductFactory.es_tipo_fisico(tipo)
                    else '/static/img/license-placeholder.png'
                )
                peso = float(producto.peso) if ProductFactory.es_tipo_fisico(tipo) else 0
            except ObjectDoesNotExist:
                continue
            
            items_data.append({
                'id': producto_id,
                'tipo': tipo,
                'nombre': nombre,
                'precio': float(precio),
                'cantidad': cantidad,
                'subtotal': float(item_subtotal),
                'imagen': imagen,
                'peso': peso,
            })
        
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
    def enviar_boleta(pedido):
        """Envía la boleta por correo."""
        from .services_template import renderizar_boleta
        email_destino = pedido.email_invitado or (pedido.usuario.email if pedido.usuario else None)
        
        if not email_destino:
            return False, 'No se encontró email'
        
        try:
            html_boleta = renderizar_boleta(pedido)
            
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
    return renderizar_boleta(pedido)

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
    from django.core.mail import send_mail
    from django.conf import settings
    
    licencias = pedido.items.filter(licencia__isnull=False)
    
    if not licencias.exists():
        return False, 'No hay licencias digitales en este pedido'
    
    email_destino = pedido.email_invitado or (pedido.usuario.email if pedido.usuario else None)
    
    if not email_destino:
        return False, 'No se encontró email del cliente'
    
    try:
        claves_info = []
        for item in licencias:
            licencia = item.licencia
            try:
                clave = licencia.desencriptar_clave()
            except Exception:
                clave = licencia.clave_encriptada
            
            claves_info.append({
                'nombre': licencia.nombre,
                'plataforma': licencia.plataforma,
                'clave': clave,
                'duracion': licencia.duracion_dias,
            })
        
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
    """Genera HTML con las claves de licencia."""
    cards_html = ''
    for idx, item in enumerate(claves):
        card_id = f"license-{idx}"
        cards_html += f'''
        <div style="background: linear-gradient(135deg, #1a1a24 0%, #0f0f14 100%); border: 1px solid #2d2d3a; border-radius: 16px; padding: 20px; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
                <div>
                    <div style="font-size: 16px; font-weight: 700; color: #ffffff; margin-bottom: 4px;">{item['nombre']}</div>
                    <div style="font-size: 12px; color: #86868b;">
                        <span style="display: inline-block; background: rgba(102, 126, 234, 0.2); color: #a78bfa; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 600;">{item['plataforma']}</span>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 10px; color: #86868b; margin-bottom: 2px;">Vigencia</div>
                    <div style="font-size: 14px; color: #4ade80; font-weight: 600;">{item['duracion']} dias</div>
                </div>
            </div>
            <div style="background: #0a0a0f; border-radius: 8px; padding: 12px;">
                <div style="font-size: 10px; color: #86868b; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px;">Tu clave de licencia</div>
                <div style="font-family: 'Courier New', monospace; font-size: 14px; color: #a78bfa; font-weight: 600; word-break: break-all; line-height: 1.5;" id="{card_id}">{item['clave']}</div>
            </div>
            <button onclick="navigator.clipboard.writeText(document.getElementById('{card_id}').innerText)" style="margin-top: 12px; background: rgba(102, 126, 234, 0.2); border: none; color: #a78bfa; padding: 8px 16px; border-radius: 8px; font-size: 12px; font-weight: 600; cursor: pointer; width: 100%; transition: background 0.2s;" onmouseover="this.style.background='rgba(102,126,234,0.3)'" onmouseout="this.style.background='rgba(102,126,234,0.2)'">
                Copiar clave
            </button>
        </div>
        '''
    
    html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OmniTech - Tus claves de licencia</title>
</head>
<body style="margin: 0; padding: 0; background: #000000; font-family: 'Segoe UI', -apple-system, sans-serif;">
    <div style="max-width: 520px; margin: 0 auto; background: #0a0a0f; padding: 32px 24px;">
        <!-- Header -->
        <div style="text-align: center; padding-bottom: 24px; border-bottom: 1px solid #2d2d3a;">
            <h1 style="margin: 0 0 6px 0; font-size: 24px; font-weight: 700; color: #ffffff;">
                <span style="background: linear-gradient(135deg, #ffffff 0%, #a78bfa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">OmniTech</span>
            </h1>
            <p style="margin: 0; font-size: 12px; color: #86868b;">Tus claves de licencia</p>
        </div>
        
        <!-- Info -->
        <div style="padding: 24px 0; border-bottom: 1px solid #2d2d3a;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="font-size: 11px; color: #86868b;">Numero de pedido</div>
                    <div style="font-size: 18px; font-weight: 700; color: #a78bfa;">{numero_pedido}</div>
                </div>
                <div style="display: inline-block; background: rgba(74, 222, 128, 0.15); color: #4ade80; padding: 6px 12px; border-radius: 16px; font-size: 11px; font-weight: 600;">
                    Pago confirmado
                </div>
            </div>
        </div>
        
        <!-- titulo -->
        <div style="padding: 24px 0 12px 0;">
            <h3 style="font-size: 12px; color: #86868b; margin: 0; text-transform: uppercase; letter-spacing: 0.5px;">Tus licencias adquiridas</h3>
        </div>
        
        <!-- Licencias -->
        <div style="padding-bottom: 24px;">
            {cards_html}
        </div>
        
        <!-- Instrucciones -->
        <div style="padding: 20px; background: linear-gradient(135deg, #1e1e32 0%, #16162a 100%); border-radius: 12px; border: 1px solid #2d2d3a;">
            <p style="font-size: 13px; color: #ffffff; margin: 0 0 12px 0; font-weight: 600;">Como activar tu licencia:</p>
            <ol style="font-size: 12px; color: #a1a1aa; margin: 0; padding-left: 16px; line-height: 1.8;">
                <li>Copia la clave de licencia haciendo clic en el boton "Copiar clave"</li>
                <li>Abre la aplicacion o plataforma del software</li>
                <li>Busca la opcion "Activar licencia" o "Ingresar clave"</li>
                <li>Pega la clave y confirma la activación</li>
            </ol>
        </div>
        
        <!-- Footer -->
        <div style="padding-top: 24px; text-align: center; border-top: 1px solid #1a1a24;">
            <p style="font-size: 11px; color: #52525a; margin: 0;">
                OmniTech 2026 - Soporte: soporte@omnitech.cl
            </p>
        </div>
    </div>
</body>
</html>
    '''
    return html