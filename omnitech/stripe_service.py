"""
Stripe Service - OmniTech
Integración con Stripe API para procesamiento de pagos
"""

import stripe
from django.conf import settings
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY


def crear_checkout_session(order, items, success_url, cancel_url):
    """Crea una sesión de pago de Stripe Checkout."""
    
    line_items = []
    moneda = settings.STRIPE_CURRENCY
    
    for item in items:
        if item.get('tipo') == 'fisico':
            nombre = item['nombre']
        else:
            nombre = f"Licencia: {item['nombre']}"
        
        if moneda == 'clp':
            unit_amount = int(float(item['precio']))
        else:
            unit_amount = int(float(item['precio']) * 100)
        
        line_items.append({
            'price_data': {
                'currency': moneda,
                'product_data': {
                    'name': nombre,
                },
                'unit_amount': unit_amount,
            },
            'quantity': item['cantidad'],
        })
    
    costo_envio = float(order.costo_envio) if order.costo_envio else 0
    if costo_envio > 0:
        if moneda == 'clp':
            envio_amount = int(costo_envio)
        else:
            envio_amount = int(costo_envio * 100)
        
        line_items.append({
            'price_data': {
                'currency': moneda,
                'product_data': {
                    'name': 'Envío',
                },
                'unit_amount': envio_amount,
            },
            'quantity': 1,
        })
    
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
        customer_email=order.email_invitado or (order.usuario.email if order.usuario else None),
        metadata={
            'order_id': order.numero_pedido,
        },
    )
    
    return checkout_session


def verificar_pago(session_id):
    """Verifica si un pago fue exitoso."""
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return session.payment_status == 'paid'
    except Exception:
        return False


def obtener_session(session_id):
    """Obtiene una sesión de Stripe por ID."""
    return stripe.checkout.Session.retrieve(session_id)
