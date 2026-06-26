"""
Views: Autenticación - OmniTech
SRP: Solo vistas relacionadas con login, registro y recuperación de contraseña
"""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .models import UserProfile


def registro(request):
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
    logout(request)
    messages.success(request, 'Has cerrado sesión.')
    return redirect('home')


def password_reset_request(request):
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

            reset_url = request.build_absolute_uri(f'/password-reset/confirm/{uid}/{token}/')

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

        messages.success(
            request, 'Te hemos enviado un correo con instrucciones si el usuario existe en nuestro sistema.'
        )
        return redirect('login')

    return render(request, 'password_reset.html')


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('password', '')
            password2 = request.POST.get('password2', '')

            print(f'[DEBUG] Form data: {dict(request.POST)}')
            print(f'[DEBUG] password field: {repr(password)}')
            print(f'[DEBUG] user: {user.username}, pk: {user.pk}')
            print(f'[DEBUG] old hash: {user.password[:40]}...')

            if len(password) < 8:
                messages.error(request, 'La contrasena debe tener al menos 8 caracteres.')
                return render(request, 'password_reset_confirm.html', {'uidb64': uidb64, 'token': token})

            if password != password2:
                messages.error(request, 'Las contrasenas no coinciden.')
                return render(request, 'password_reset_confirm.html', {'uidb64': uidb64, 'token': token})

            from django.contrib.auth.hashers import make_password

            nuevo_hash = make_password(password)

            User.objects.filter(pk=user.pk).update(password=nuevo_hash)

            user = User.objects.get(pk=user.pk)

            print(f'[DEBUG] new hash: {user.password[:40]}...')
            print(f'[DEBUG] verify check_password: {user.check_password(password)}')

            messages.success(request, 'Contrasena restablecida. Intenta iniciar sesion.')
            return redirect('login')

        return render(request, 'password_reset_confirm.html', {'uidb64': uidb64, 'token': token})
    else:
        messages.error(request, 'El enlace de restablecimiento es invalido o ha expirado.')
        return redirect('password_reset_request')


def debug_password(request):
    from django.contrib.auth.hashers import make_password

    if request.method == 'POST':
        username = request.POST.get('username', '')
        new_password = request.POST.get('new_password', '')

        try:
            user = User.objects.get(username=username)
            old_hash = user.password

            nuevo_hash = make_password(new_password)
            user.password = nuevo_hash
            user.save()

            return JsonResponse(
                {
                    'success': True,
                    'username': username,
                    'old_hash': old_hash[:50],
                    'new_hash': nuevo_hash[:50],
                    'verify_after_save': user.check_password(new_password),
                }
            )
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Usuario no existe'})

    return JsonResponse({'error': 'Usa POST con username y new_password'})


def reset_password_direct(request, username, password):
    try:
        user = User.objects.get(username=username)
        from django.contrib.auth.hashers import make_password

        user.password = make_password(password)
        user.save()
        return JsonResponse({'success': True, 'user': username, 'verify': user.check_password(password)})
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'})
