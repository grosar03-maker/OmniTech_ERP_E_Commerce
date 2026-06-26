"""
Views: Perfil de Usuario - OmniTech
SRP: Solo vistas relacionadas con el perfil del usuario
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Order, UserProfile


@login_required
def perfil(request):
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
        'is_admin': request.user.is_staff,
    }
    return render(request, 'perfil.html', context)
