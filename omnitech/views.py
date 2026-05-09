"""
OmniTech Views - Service Layer Implementation
Arquitectura Hexagonal: Lógica de negocio en capa de servicios
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.conf import settings
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from decimal import Decimal
import uuid
import json

from .models import (
    PhysicalProduct, DigitalLicense,
    Order, OrderItem, UserProfile, ProductState,
    LicenseState, OrderState
)
from .services import enviar_boleta_pedido, OrderService, CartService, EmailService, enviar_claves_licencia
from .stripe_service import crear_checkout_session, verificar_pago
from .factories import ProductFactory


def home(request):
    """Página principal con productos destacados."""
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
    """Catálogo completo con filtros."""
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
    """Detalle de producto individual."""
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
    """Agrega un producto al carrito."""
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
    """Actualiza cantidad de un producto en el carrito."""
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
    """Elimina un producto del carrito."""
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
    """Vacía completamente el carrito."""
    CartService.save_carrito(request, [])
    return JsonResponse({'success': True, 'message': 'Carrito vaciado'})


def ver_carrito(request):
    """Vista del carrito de compras."""
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
    """Página de checkout con información del pedido."""
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
    """DIP: Delega la creación del pedido a OrderService."""
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
    """DIP: Delega el procesamiento del pedido a OrderService."""
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


def detalle_pedido(request, numero_pedido):
    """Detalle de un pedido específico."""
    order = get_object_or_404(Order, numero_pedido=numero_pedido)
    
    if request.user.is_authenticated:
        if order.usuario != request.user:
            messages.error(request, 'No tienes permiso para ver este pedido.')
            return redirect('mis_pedidos')
    else:
        if order.usuario is not None:
            messages.error(request, 'Debes iniciar sesión para ver este pedido.')
            return redirect('login')
    
    context = {'pedido': order}
    return render(request, 'detalle_pedido.html', context)


@login_required
def mis_pedidos(request):
    """Lista de pedidos del usuario."""
    pedidos = Order.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    context = {'pedidos': pedidos}
    return render(request, 'mis_pedidos.html', context)


@login_required
def mis_licencias(request):
    """Lista de licencias del usuario."""
    licencias = DigitalLicense.objects.filter(
        orden_compra__usuario=request.user
    ).order_by('-fecha_asignacion')
    context = {'licencias': licencias}
    return render(request, 'mis_licencias.html', context)


def registro(request):
    """Registro de nuevos usuarios."""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        
        if not username or not email or not password:
            messages.error(request, 'Todos los campos son requeridos.')
            return redirect('registro')
        
        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('registro')
        
        if len(password) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            return redirect('registro')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe.')
            return redirect('registro')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'El correo electrónico ya está registrado.')
            return redirect('registro')
        
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            UserProfile.objects.create(user=user)
            
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f'Bienvenido {username}!')
                return redirect('home')
        except Exception as e:
            messages.error(request, f'Error al crear usuario: {str(e)}')
            return redirect('registro')
    
    return render(request, 'registro.html')


def login_view(request):
    """Inicio de sesion."""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        try:
            user = User.objects.get(username=username)
            
            if user.check_password(password):
                login(request, user)
                messages.success(request, f'Bienvenido {username}!')
                return redirect(request.GET.get('next', 'home'))
            else:
                messages.error(request, 'Contrasena incorrecta')
                return render(request, 'login.html')
        except User.DoesNotExist:
            messages.error(request, 'Usuario no existe')
            return render(request, 'login.html')
    
    return render(request, 'login.html')


def logout_view(request):
    """Cierre de sesión."""
    logout(request)
    messages.success(request, 'Has cerrado sesión.')
    return redirect('home')


@login_required
def perfil(request):
    """Perfil del usuario."""
    try:
        user_profile = request.user.perfil
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
    
    total_compras = user_profile.calcular_total_compras()
    pedidos_count = Order.objects.filter(usuario=request.user).count()
    
    context = {
        'perfil': user_profile,
        'total_compras': total_compras,
        'pedidos_count': pedidos_count,
    }
    return render(request, 'perfil.html', context)


def password_reset_request(request):
    """Solicita restablecer contraseña."""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        if not email:
            messages.error(request, 'El correo electronico es requerido.')
            return redirect('password_reset_request')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=email)
            except User.DoesNotExist:
                user = None
        
        if user is not None:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            reset_url = request.build_absolute_uri(
                f'/password-reset/confirm/{uid}/{token}/'
            )
            
            html_message = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background: #000; font-family: 'Segoe UI', -apple-system, sans-serif;">
    <div style="max-width: 480px; margin: 0 auto; background: #0a0a0f; padding: 32px 24px;">
        <div style="text-align: center; padding-bottom: 24px; border-bottom: 1px solid #2d2d3a;">
            <h1 style="margin: 0 0 6px 0; font-size: 24px; font-weight: 700; color: #fff;">
                <span style="background: linear-gradient(135deg, #fff 0%, #a78bfa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">OmniTech</span>
            </h1>
            <p style="margin: 0; font-size: 12px; color: #86868b;">Restablecer contrasena</p>
        </div>
        
        <div style="padding: 24px 0;">
            <p style="font-size: 14px; color: #fff; margin: 0 0 16px 0; line-height: 1.5;">Hola <strong>{user.username}</strong>,</p>
            <p style="font-size: 14px; color: #a1a1aa; margin: 0 0 16px 0; line-height: 1.5;">Recibimos una solicitud para restablecer tu contrasena.</p>
            <div style="text-align: center; margin: 24px 0;"><a href="{reset_url}" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; padding: 14px 28px; border-radius: 12px; font-size: 14px; font-weight: 600; text-decoration: none;">Restablecer contrasena</a></div>
            <p style="font-size: 12px; color: #52525a; margin: 0; line-height: 1.5;">Este enlace expira en 24 horas. Si no solicitaste este cambio, puedes ignorar este correo.</p>
        </div>
        
        <div style="padding-top: 24px; text-align: center; border-top: 1px solid #1a1a24;">
            <p style="font-size: 11px; color: #52525a; margin: 0;">
                OmniTech 2026 - Soporte: soporte@omnitech.cl
            </p>
        </div>
    </div>
</body>
</html>
            '''
            
            send_mail(
                subject='OmniTech - Restablecer contrasena',
                message=f'Recibe este correo porque solicitaste restablecer tu contrasena en OmniTech. Abre este enlace: {reset_url}',
                from_email=settings.EMAIL_FROM,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
        
        messages.success(request, 'Te hemos enviado un correo con instrucciones si el usuario existe en nuestro sistema.')
        return redirect('login')
    
    return render(request, 'password_reset.html')


def password_reset_confirm(request, uidb64, token):
    """Pagina para establecer nueva contrasena."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('password', '')
            password2 = request.POST.get('password2', '')
            
            print(f"[DEBUG] Form data: {dict(request.POST)}")
            print(f"[DEBUG] password field: {repr(password)}")
            print(f"[DEBUG] user: {user.username}, pk: {user.pk}")
            print(f"[DEBUG] old hash: {user.password[:40]}...")
            
            if len(password) < 8:
                messages.error(request, 'La contrasena debe tener al menos 8 caracteres.')
                return render(request, 'password_reset_confirm.html', {'uidb64': uidb64, 'token': token})
            
            if password != password2:
                messages.error(request, 'Las contrasenas no coinciden.')
                return render(request, 'password_reset_confirm.html', {'uidb64': uidb64, 'token': token})
            
            # FORzar update directo a la base de datos
            from django.contrib.auth.hashers import make_password
            nuevo_hash = make_password(password)
            
            User.objects.filter(pk=user.pk).update(password=nuevo_hash)
            
            # Obtener usuario fresco de la base de datos
            user = User.objects.get(pk=user.pk)
            
            print(f"[DEBUG] new hash: {user.password[:40]}...")
            print(f"[DEBUG] verify check_password: {user.check_password(password)}")
            
            messages.success(request, 'Contrasena restablecida. Intenta iniciar sesion.')
            return redirect('login')
        
        return render(request, 'password_reset_confirm.html', {'uidb64': uidb64, 'token': token})
    else:
        messages.error(request, 'El enlace de restablecimiento es invalido o ha expirado.')
        return redirect('password_reset_request')


def debug_password(request):
    """Endpoint de debug para verificar contrasenas."""
    from django.contrib.auth.hashers import make_password
    
    if request.method == 'POST':
        username = request.POST.get('username', '')
        new_password = request.POST.get('new_password', '')
        
        try:
            user = User.objects.get(username=username)
            old_hash = user.password
            
            # Generar nuevo hash
            nuevo_hash = make_password(new_password)
            user.password = nuevo_hash
            user.save()
            
            return JsonResponse({
                'success': True,
                'username': username,
                'old_hash': old_hash[:50],
                'new_hash': nuevo_hash[:50],
                'verify_after_save': user.check_password(new_password),
            })
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Usuario no existe'})
    
    return JsonResponse({'error': 'Usa POST con username y new_password'})


def reset_password_direct(request, username, password):
    """Reset directo sin token."""
    try:
        user = User.objects.get(username=username)
        from django.contrib.auth.hashers import make_password
        user.password = make_password(password)
        user.save()
        return JsonResponse({
            'success': True, 
            'user': username,
            'verify': user.check_password(password)
        })
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'})