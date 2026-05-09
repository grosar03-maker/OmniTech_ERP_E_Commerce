"""
Views: Catálogo y Carrito - OmniTech
SRP: Solo vistas relacionadas con navegación de productos y compras
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings
from decimal import Decimal
import json

from .models import (
    PhysicalProduct, DigitalLicense,
    ProductState, LicenseState, OrderState
)
from .services import (
    enviar_boleta_pedido, OrderService, CartService, enviar_claves_licencia
)
from .stripe_service import crear_checkout_session
from .factories import ProductFactory


def home(request):
    productos_fisicos = PhysicalProduct.objects.filter(
        estado=ProductState.ACTIVO
    ).order_by('-fecha_creacion')[:8]

    licencias = DigitalLicense.objects.filter(
        estado=ProductState.ACTIVO,
        estado_licencia=LicenseState.DISPONIBLE
    ).order_by('-fecha_creacion')[:8]

    context = {
        'productos_destacados': productos_fisicos,
        'licencias_destacadas': licencias,
    }
    return render(request, 'home.html', context)


def productos(request):
    categoria = request.GET.get('categoria', '')
    tipo = request.GET.get('tipo', '')

    productos_fisicos = None
    licencias = None

    if tipo == 'hardware' or tipo == '':
        productos_fisicos = PhysicalProduct.objects.filter(estado=ProductState.ACTIVO)
        if categoria:
            productos_fisicos = productos_fisicos.filter(categoria__icontains=categoria)

    if tipo == 'software' or tipo == '':
        licencias = DigitalLicense.objects.filter(estado=ProductState.ACTIVO)
        if categoria:
            licencias = licencias.filter(categoria__icontains=categoria)

    cats_hardware = PhysicalProduct.objects.values_list('categoria', flat=True).distinct()
    cats_software = DigitalLicense.objects.values_list('categoria', flat=True).distinct()
    categorias = list(set(list(cats_hardware) + list(cats_software)))

    context = {
        'productos_fisicos': productos_fisicos,
        'licencias': licencias,
        'categorias': categorias,
        'categoria_seleccionada': categoria,
        'tipo_seleccionado': tipo,
    }
    return render(request, 'productos.html', context)


def detalle_producto(request, producto_id):
    producto_fisico = None
    licencia = None

    try:
        producto_fisico = PhysicalProduct.objects.get(id=producto_id)
    except PhysicalProduct.DoesNotExist:
        try:
            licencia = DigitalLicense.objects.get(id=producto_id)
        except DigitalLicense.DoesNotExist:
            messages.error(request, 'Producto no encontrado.')
            return redirect('productos')

    context = {
        'producto': producto_fisico or licencia,
        'es_fisico': producto_fisico is not None,
    }
    return render(request, 'detalle_producto.html', context)


@require_POST
def agregar_al_carrito(request):
    try:
        data = json.loads(request.body)
        producto_id = data.get('producto_id')
        tipo = data.get('tipo', 'fisico')
        cantidad = int(data.get('cantidad', 1))

        producto = ProductFactory.obtener_producto_o_404(tipo, producto_id)
        if ProductFactory.es_tipo_fisico(tipo):
            if producto.stock_disponible < cantidad:
                return JsonResponse({'success': False, 'error': 'Stock insuficiente'})
        else:
            if producto.estado_licencia != LicenseState.DISPONIBLE:
                return JsonResponse({'success': False, 'error': 'Licencia no disponible'})
        precio = producto.precio

        carrito = CartService.get_carrito(request)

        item_existente = None
        for i, item in enumerate(carrito):
            if item.get('producto_id') == producto_id and item.get('tipo') == tipo:
                item_existente = i
                break

        if item_existente is not None:
            carrito[item_existente]['cantidad'] += cantidad
        else:
            carrito.append({
                'producto_id': producto_id,
                'tipo': tipo,
                'nombre': producto.nombre,
                'precio': float(precio),
                'cantidad': cantidad,
            })

        CartService.save_carrito(request, carrito)
        totales = CartService.calcular_totales(carrito)

        return JsonResponse({
            'success': True,
            'carrito_count': totales['cantidad_items'],
            'message': f'{producto.nombre} agregado al carrito'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
def actualizar_carrito(request):
    try:
        data = json.loads(request.body)
        producto_id = data.get('producto_id')
        tipo = data.get('tipo')
        cantidad = int(data.get('cantidad', 1))

        carrito = CartService.get_carrito(request)

        for item in carrito:
            if item.get('producto_id') == producto_id and item.get('tipo') == tipo:
                if cantidad <= 0:
                    carrito.remove(item)
                else:
                    if cantidad > 0 and ProductFactory.es_tipo_fisico(tipo):
                        producto = ProductFactory.obtener_producto_o_404(tipo, producto_id)
                        if producto.stock_disponible < cantidad:
                            return JsonResponse({'success': False, 'error': 'Stock insuficiente'})
                    item['cantidad'] = cantidad
                break

        CartService.save_carrito(request, carrito)
        totales = CartService.calcular_totales(carrito)

        return JsonResponse({'success': True, **totales})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
def eliminar_del_carrito(request):
    try:
        data = json.loads(request.body)
        producto_id = data.get('producto_id')
        tipo = data.get('tipo')

        carrito = CartService.get_carrito(request)
        carrito = [item for item in carrito
                   if not (item.get('producto_id') == producto_id and item.get('tipo') == tipo)]

        CartService.save_carrito(request, carrito)
        totales = CartService.calcular_totales(carrito)

        return JsonResponse({'success': True, **totales})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
def vaciar_carrito(request):
    CartService.save_carrito(request, [])
    return JsonResponse({'success': True, 'message': 'Carrito vaciado'})


def ver_carrito(request):
    carrito = CartService.get_carrito(request)
    totales = CartService.calcular_totales(carrito)
    context = {
        'carrito': totales['items'],
        'subtotal': totales['subtotal'],
        'costo_envio': totales['costo_envio'],
        'total': totales['total'],
        'cantidad_items': totales['cantidad_items'],
    }
    return render(request, 'carrito.html', context)


def checkout(request):
    carrito = CartService.get_carrito(request)
    if not carrito:
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('productos')

    if request.method == 'POST':
        return crear_sesion_stripe(request)

    totales = CartService.calcular_totales(carrito)
    region = request.session.get('region_usuario', '')

    if region == 'La Araucanía' and totales['subtotal'] > float(settings.SUBSIDIO_MONTO):
        totales['costo_envio'] = 0
        totales['total'] = totales['subtotal']

    context = {
        'carrito': totales['items'],
        'subtotal': totales['subtotal'],
        'costo_envio': totales['costo_envio'],
        'total': totales['total'],
        'region': region,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'checkout.html', context)


@require_POST
def crear_sesion_stripe(request):
    try:
        carrito = CartService.get_carrito(request)
        if not carrito:
            messages.error(request, 'Tu carrito está vacío')
            return redirect('productos')

        email = request.POST.get('email')
        region = request.POST.get('region', '')
        observaciones = request.POST.get('observaciones', '')

        if not email:
            messages.error(request, 'El correo es requerido')
            return redirect('checkout')

        order, _ = OrderService.crear_pedido_para_stripe(
            request, carrito, email, region, observaciones
        )

        totales = CartService.calcular_totales(carrito)

        success_url = request.build_absolute_uri(f'/pago-exitoso/?session_id={{CHECKOUT_SESSION_ID}}')
        cancel_url = request.build_absolute_uri('/checkout/')

        session = crear_checkout_session(order, totales['items'], success_url, cancel_url)

        return redirect(session.url)

    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('checkout')


def pago_exitoso(request):
    session_id = request.GET.get('session_id')

    if not session_id:
        messages.error(request, 'Sesión no válida')
        return redirect('home')

    try:
        order_id = request.session.pop('order_id', None)
        carrito_temp = request.session.pop('carrito_temp', [])

        if not order_id:
            messages.error(request, 'No se encontró el pedido')
            return redirect('home')

        if not carrito_temp:
            from .models import Order
            order = Order.objects.get(numero_pedido=order_id)
        else:
            order, success, error_msg = OrderService.procesar_pago(order_id, carrito_temp)
            if not success:
                messages.error(request, error_msg or 'Error al procesar el pago')
                return redirect('home')

            enviar_boleta_pedido(order)
            enviar_claves_licencia(order)

        CartService.save_carrito(request, [])

        messages.success(request, f'¡Pago exitoso! Tu número de pedido es {order_id}')
        return render(request, 'pago_exitoso.html', {'pedido': order})

    except Exception as e:
        import traceback
        print(f"Error en pago_exitoso: {e}")
        traceback.print_exc()
        messages.error(request, 'Error al procesar el pago')
        return redirect('home')
