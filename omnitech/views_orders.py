"""
Views: Pedidos y Licencias - OmniTech
SRP: Solo vistas relacionadas con pedidos y licencias del usuario
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Order, DigitalLicense


def detalle_pedido(request, numero_pedido):
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
    pedidos = Order.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    context = {'pedidos': pedidos}
    return render(request, 'mis_pedidos.html', context)


@login_required
def mis_licencias(request):
    licencias = DigitalLicense.objects.filter(
        orden_compra__usuario=request.user
    ).order_by('-fecha_asignacion')
    context = {'licencias': licencias}
    return render(request, 'mis_licencias.html', context)
