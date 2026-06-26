"""
Email Template Service - OmniTech
Separación de lógica de presentación aplicando SRP
"""

from django.template.loader import get_template


def renderizar_boleta(pedido, logo_url=''):
    """
    Renderiza la boleta usando templates de Django.
    SRP: Esta función solo maneja la presentación, no la lógica de negocio.
    """
    # Recolectar datos del pedido
    items = pedido.items.all()

    items_list = []
    for item in items:
        if item.producto_fisico:
            items_list.append(
                {
                    'nombre': item.producto_fisico.nombre,
                    'tipo': 'Hardware',
                    'cantidad': item.cantidad,
                    'precio_unitario': float(item.precio_unitario),
                    'subtotal': float(item.precio_unitario * item.cantidad),
                    'imagen': getattr(item.producto_fisico, 'imagen_url', ''),
                }
            )
        else:
            items_list.append(
                {
                    'nombre': item.licencia.nombre,
                    'tipo': 'Software/Licencia',
                    'cantidad': item.cantidad,
                    'precio_unitario': float(item.precio_unitario),
                    'subtotal': float(item.precio_unitario * item.cantidad),
                    'imagen': getattr(item.licencia, 'imagen_url', ''),
                }
            )

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

    items_html = ''
    for item in items_list:
        imagen = item['imagen'] or 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=60&h=60&fit=crop'
        badge_color = '#60a5fa' if item['tipo'] == 'Hardware' else '#a78bfa'
        badge_bg = 'rgba(96,165,250,0.15)' if item['tipo'] == 'Hardware' else 'rgba(167,139,250,0.15)'
        items_html += f'''
        <tr>
            <td style="padding: 14px 12px; border-bottom: 1px solid #1e1e2e;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <img src="{imagen}" alt="{item['nombre']}"
                         style="width: 48px; height: 48px; object-fit: cover; border-radius: 8px; border: 1px solid #2d2d3a; flex-shrink: 0;">
                    <div>
                        <div style="font-weight: 600; color: #f1f1f3; font-size: 13px; margin-bottom: 3px;">{item['nombre']}</div>
                        <span style="display: inline-block; background: {badge_bg}; color: {badge_color}; padding: 2px 7px; border-radius: 20px; font-size: 10px; font-weight: 600; letter-spacing: 0.3px;">{item['tipo']}</span>
                    </div>
                </div>
            </td>
            <td style="padding: 14px 10px; border-bottom: 1px solid #1e1e2e; text-align: center; color: #d4d4d8; font-size: 14px;">{item['cantidad']}</td>
            <td style="padding: 14px 10px; border-bottom: 1px solid #1e1e2e; text-align: right; color: #d4d4d8; font-size: 14px;">${item['precio_unitario']:,.0f}</td>
            <td style="padding: 14px 0 14px 10px; border-bottom: 1px solid #1e1e2e; text-align: right; color: #f1f1f3; font-size: 14px; font-weight: 700;">${item['subtotal']:,.0f}</td>
        </tr>
        '''

    costo_envio_display = 'Gratis ✓' if float(pedido.costo_envio or 0) == 0 else f'${float(pedido.costo_envio):,.0f}'
    costo_color = '#4ade80' if float(pedido.costo_envio or 0) == 0 else '#d4d4d8'

    html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OmniTech - Comprobante de compra</title>
    <!--[if mso]><style>td, th {{ border-collapse: collapse; }}</style><![endif]-->
</head>
<body style="margin:0; padding:0; background:#09090d; font-family:'Segoe UI',Helvetica,Arial,sans-serif; -webkit-font-smoothing:antialiased;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#09090d; padding: 32px 16px;">
<tr><td align="center">
<table role="presentation" width="520" cellpadding="0" cellspacing="0" style="background:#111118; border:1px solid #1e1e2e; border-radius:16px; overflow:hidden; max-width:520px; width:100%;">

    <!-- HEADER GRADIENT -->
    <tr>
        <td style="background: linear-gradient(135deg, #18182a 0%, #0f0f1a 60%, #1a0f2e 100%); padding: 32px 32px 28px; border-bottom: 1px solid #1e1e2e;">
            <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                    <td>
                        <img src="{logo_url}" alt="OmniTech" style="max-width: 140px; height: auto; border-radius: 8px;">
                        <div style="font-size: 11px; color: #6b7280; margin-top: 8px; letter-spacing: 1px; text-transform: uppercase;">Comprobante de compra</div>
                    </td>
                    <td align="right">
                        <div style="display:inline-block; background:rgba(74,222,128,0.12); border:1px solid rgba(74,222,128,0.3); color:#4ade80; padding:6px 14px; border-radius:20px; font-size:12px; font-weight:700; letter-spacing:0.3px;">
                            ✓ Pago confirmado
                        </div>
                    </td>
                </tr>
            </table>
        </td>
    </tr>

    <!-- ORDER INFO -->
    <tr>
        <td style="padding: 24px 32px; border-bottom: 1px solid #1e1e2e; background:#0e0e18;">
            <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                    <td style="width:50%;">
                        <div style="font-size:10px; color:#52525b; text-transform:uppercase; letter-spacing:1px; margin-bottom:5px;">Número de pedido</div>
                        <div style="font-size:20px; font-weight:800; color:#a78bfa; letter-spacing:-0.3px;">{pedido.numero_pedido}</div>
                    </td>
                    <td align="right">
                        <div style="font-size:10px; color:#52525b; text-transform:uppercase; letter-spacing:1px; margin-bottom:5px; text-align:right;">Fecha</div>
                        <div style="font-size:13px; color:#d4d4d8; text-align:right;">{fecha}</div>
                    </td>
                </tr>
            </table>
        </td>
    </tr>

    <!-- CLIENTE -->
    <tr>
        <td style="padding: 20px 32px; border-bottom: 1px solid #1e1e2e;">
            <div style="font-size:10px; color:#52525b; text-transform:uppercase; letter-spacing:1px; margin-bottom:12px;">Datos del cliente</div>
            <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                    <td style="width:50%;">
                        <div style="font-size:11px; color:#71717a; margin-bottom:3px;">Cliente</div>
                        <div style="font-size:14px; color:#f1f1f3; font-weight:600;">{cliente_nombre}</div>
                    </td>
                    <td>
                        <div style="font-size:11px; color:#71717a; margin-bottom:3px;">Email</div>
                        <div style="font-size:13px; color:#a78bfa;">{email_destino}</div>
                    </td>
                </tr>
            </table>
        </td>
    </tr>

    <!-- PRODUCTOS HEADER -->
    <tr>
        <td style="padding: 20px 32px 0;">
            <div style="font-size:10px; color:#52525b; text-transform:uppercase; letter-spacing:1px; margin-bottom:12px;">Productos</div>
        </td>
    </tr>

    <!-- TABLA PRODUCTOS -->
    <tr>
        <td style="padding: 0 32px;">
            <table width="100%" cellpadding="0" cellspacing="0">
                <thead>
                    <tr>
                        <th style="padding:8px 12px 8px; text-align:left; color:#52525b; font-size:10px; text-transform:uppercase; letter-spacing:0.8px; font-weight:600; border-bottom: 1px solid #1e1e2e;">Producto</th>
                        <th style="padding:8px 10px; text-align:center; color:#52525b; font-size:10px; text-transform:uppercase; letter-spacing:0.8px; font-weight:600; border-bottom: 1px solid #1e1e2e;">Cant.</th>
                        <th style="padding:8px 10px; text-align:right; color:#52525b; font-size:10px; text-transform:uppercase; letter-spacing:0.8px; font-weight:600; border-bottom: 1px solid #1e1e2e;">Precio</th>
                        <th style="padding:8px 0 8px 10px; text-align:right; color:#52525b; font-size:10px; text-transform:uppercase; letter-spacing:0.8px; font-weight:600; border-bottom: 1px solid #1e1e2e;">Subtotal</th>
                    </tr>
                </thead>
                <tbody>
                    {items_html}
                </tbody>
            </table>
        </td>
    </tr>

    <!-- TOTALES -->
    <tr>
        <td style="padding: 20px 32px; border-top: 1px solid #1e1e2e;">
            <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                    <td style="padding: 7px 0; color:#71717a; font-size:13px;">Subtotal</td>
                    <td style="padding: 7px 0; text-align:right; color:#d4d4d8; font-size:13px;">${float(pedido.subtotal):,.0f}</td>
                </tr>
                <tr>
                    <td style="padding: 7px 0; color:#71717a; font-size:13px; border-bottom: 1px solid #1e1e2e; padding-bottom:14px;">Envío</td>
                    <td style="padding: 7px 0; text-align:right; color:{costo_color}; font-size:13px; font-weight:600; border-bottom: 1px solid #1e1e2e; padding-bottom:14px;">{costo_envio_display}</td>
                </tr>
                <tr>
                    <td style="padding: 16px 0 0; color:#f1f1f3; font-size:17px; font-weight:700;">Total</td>
                    <td style="padding: 16px 0 0; text-align:right; color:#a78bfa; font-size:24px; font-weight:800;">${float(pedido.total):,.0f}</td>
                </tr>
            </table>
        </td>
    </tr>

    <!-- FOOTER -->
    <tr>
        <td style="padding: 20px 32px 28px; border-top: 1px solid #1e1e2e; text-align:center; background:#0e0e18;">
            <p style="font-size:12px; color:#71717a; margin:0 0 6px; line-height:1.6;">
                Gracias por tu compra. Tu pedido será procesado en 24-48 horas hábiles.
            </p>
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
