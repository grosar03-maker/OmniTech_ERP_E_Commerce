"""
Email Template Service - OmniTech
Separación de lógica de presentación aplicando SRP
"""

from django.template import Template, Context
from django.template.loader import get_template


def renderizar_boleta(pedido):
    """
    Renderiza la boleta usando templates de Django.
    SRP: Esta función solo maneja la presentación, no la lógica de negocio.
    """
    # Recolectar datos del pedido
    items = pedido.items.all()
    
    items_list = []
    for item in items:
        if item.producto_fisico:
            items_list.append({
                'nombre': item.producto_fisico.nombre,
                'tipo': 'Hardware',
                'cantidad': item.cantidad,
                'precio_unitario': float(item.precio_unitario),
                'subtotal': float(item.precio_unitario * item.cantidad),
                'imagen': getattr(item.producto_fisico, 'imagen_url', ''),
            })
        else:
            items_list.append({
                'nombre': item.licencia.nombre,
                'tipo': 'Software/Licencia',
                'cantidad': item.cantidad,
                'precio_unitario': float(item.precio_unitario),
                'subtotal': float(item.precio_unitario * item.cantidad),
                'imagen': getattr(item.licencia, 'imagen_url', ''),
            })
    
    # Datos del cliente
    email_destino = pedido.email_invitado or (pedido.usuario.email if pedido.usuario else '')
    cliente_nombre = pedido.usuario.username if pedido.usuario else 'Cliente Invitado'
    fecha_formato = pedido.fecha_creacion.strftime('%d de %B de %Y, %H:%M')
    
    # Intentar usar template externo o generar HTML
    try:
        template = get_template('email/boleta.html')
        context = {
            'pedido': pedido,
            'items': items_list,
            'cliente': cliente_nombre,
            'email': email_destino,
            'fecha': fecha_formato,
        }
        return template.render(context)
    except Exception:
        # Fallback: generar HTML directamente si el template no existe
        return generar_html_fallback(pedido, items_list, cliente_nombre, email_destino, fecha_formato)


def generar_html_fallback(pedido, items_list, cliente_nombre, email_destino, fecha):
    """Genera HTML de fallback si el template no existe."""
    from django.conf import settings
    
    items_html = ''
    for item in items_list:
        imagen = item['imagen'] or 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=60&h=60&fit=crop'
        items_html += f'''
        <tr>
            <td style="padding: 16px 12px; border-bottom: 1px solid #2d2d3a;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <img src="{imagen}" alt="{item['nombre']}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 6px; display: block;">
                    <div style="min-width: 0;">
                        <div style="font-weight: 600; color: #ffffff; margin-bottom: 2px; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{item['nombre']}</div>
                        <div style="font-size: 11px; color: #86868b;">{item['tipo']}</div>
                    </div>
                </div>
            </td>
            <td style="padding: 16px 8px; border-bottom: 1px solid #2d2d3a; text-align: center; color: #ffffff; font-size: 14px;">{item['cantidad']}</td>
            <td style="padding: 16px 8px; border-bottom: 1px solid #2d2d3a; text-align: right; color: #ffffff; font-size: 14px;">${item['precio_unitario']:,.0f}</td>
            <td style="padding: 16px 0 16px 8px; border-bottom: 1px solid #2d2d3a; text-align: right; color: #ffffff; font-size: 14px; font-weight: 600;">${item['subtotal']:,.0f}</td>
        </tr>
        '''
    
    costo_envio_display = "Gratis" if float(pedido.costo_envio or 0) == 0 else f"${float(pedido.costo_envio):,.0f}"
    
    html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OmniTech - Comprobante de compra</title>
    <style>
        @media only screen and (max-width: 480px) {{
            .ticket-table {{ width: 100% !important; }}
            .ticket-container {{ padding: 20px 16px !important; }}
            .ticket-product-cell {{ display: block !important; }}
            .ticket-product-img {{ width: 40px !important; height: 40px !important; }}
            .ticket-row {{ display: block !important; text-align: left !important; }}
            .ticket-row td {{ display: block !important; padding: 8px 0 !important; text-align: left !important; }}
            .ticket-header {{ text-align: left !important; }}
            .ticket-total-row {{ flex-direction: column !important; align-items: flex-start !important; }}
            .ticket-total-label {{ text-align: left !important; margin-bottom: 4px; }}
            .ticket-total-value {{ text-align: left !important; }}
        }}
    </style>
</head>
<body style="margin: 0; padding: 0; background: #000000; font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;">
    <div class="ticket-container" style="max-width: 520px; margin: 0 auto; background: #0a0a0f; padding: 32px 24px;">
        <!-- Header -->
        <div style="text-align: center; padding-bottom: 24px; border-bottom: 1px solid #2d2d3a;">
            <h1 style="margin: 0 0 6px 0; font-size: 28px; font-weight: 700; color: #ffffff;">
                <span style="background: linear-gradient(135deg, #ffffff 0%, #a78bfa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">OmniTech</span>
            </h1>
            <p style="margin: 0; font-size: 12px; color: #86868b;">ERP & E-Commerce - Tu tienda de tecnología</p>
        </div>
        
        <!-- Orden Info -->
        <div style="padding: 24px 0; border-bottom: 1px solid #2d2d3a;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
                <div>
                    <div style="font-size: 11px; color: #86868b; margin-bottom: 2px;">Número de pedido</div>
                    <div style="font-size: 18px; font-weight: 700; color: #a78bfa;">{pedido.numero_pedido}</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 11px; color: #86868b; margin-bottom: 2px;">Fecha</div>
                    <div style="font-size: 13px; color: #ffffff;">{fecha}</div>
                </div>
            </div>
            <div style="display: inline-block; background: rgba(74, 222, 128, 0.15); color: #4ade80; padding: 6px 12px; border-radius: 16px; font-size: 11px; font-weight: 600; margin-top: 12px;">
                ✓ Confirmado
            </div>
        </div>
        
        <!-- Cliente -->
        <div style="padding: 24px 0; border-bottom: 1px solid #2d2d3a;">
            <h3 style="font-size: 12px; color: #86868b; margin: 0 0 12px 0; text-transform: uppercase; letter-spacing: 0.5px;">Datos del cliente</h3>
            <div style="display: flex; gap: 24px; flex-wrap: wrap;">
                <div>
                    <div style="font-size: 11px; color: #86868b;">Cliente</div>
                    <div style="color: #ffffff; font-size: 14px;">{cliente_nombre}</div>
                </div>
                <div>
                    <div style="font-size: 11px; color: #86868b;">Email</div>
                    <div style="color: #ffffff; font-size: 14px;">{email_destino}</div>
                </div>
            </div>
        </div>
        
        <!-- Productos -->
        <div style="padding: 24px 0; border-bottom: 1px solid #2d2d3a;">
            <h3 style="font-size: 12px; color: #86868b; margin: 0 0 12px 0; text-transform: uppercase; letter-spacing: 0.5px;">Productos</h3>
            <table class="ticket-table" style="width: 100%; border-collapse: collapse; min-width: 300px;">
                <thead>
                    <tr>
                        <th style="padding: 6px 12px; text-align: left; color: #86868b; font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 500;">Producto</th>
                        <th style="padding: 6px 8px; text-align: center; color: #86868b; font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 500;">Cant.</th>
                        <th style="padding: 6px 8px; text-align: right; color: #86868b; font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 500;">Precio</th>
                        <th style="padding: 6px 0 6px 8px; text-align: right; color: #86868b; font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 500;">Subtotal</th>
                    </tr>
                </thead>
                <tbody>
                {items_html}
                </tbody>
            </table>
        </div>
        
        <!-- Totales -->
        <div style="padding: 24px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #1a1a24;">
                <span style="color: #a1a1aa; font-size: 14px;">Subtotal</span>
                <span style="color: #ffffff; font-size: 14px;">${float(pedido.subtotal):,.0f}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #1a1a24;">
                <span style="color: #a1a1aa; font-size: 14px;">Envío</span>
                <span style="color: #4ade80; font-size: 14px; font-weight: 500;">{costo_envio_display}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 16px 0 0 0; margin-top: 8px;">
                <span style="color: #ffffff; font-size: 16px; font-weight: 700;">Total</span>
                <span style="color: #a78bfa; font-size: 22px; font-weight: 700;">${float(pedido.total):,.0f}</span>
            </div>
        </div>
        
        <!-- Footer -->
        <div style="padding-top: 24px; text-align: center; border-top: 1px solid #1a1a24;">
            <p style="font-size: 13px; color: #86868b; margin: 0 0 12px 0; line-height: 1.5;">
                Gracias por tu compra. Tu pedido será procesado en 24-48 horas hábiles.
            </p>
            <p style="font-size: 11px; color: #52525a; margin: 0;">
                OmniTech © 2026 - Para soporte: soporte@omnitech.cl
            </p>
        </div>
    </div>
</body>
</html>
    '''
    return html