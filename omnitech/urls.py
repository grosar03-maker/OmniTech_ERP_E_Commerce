"""
OmniTech App URLs
SRP: Cada vista importada desde su módulo correspondiente
"""

from django.urls import path
from . import views_cart, views_auth, views_orders, views_profile

urlpatterns = [
    path('', views_cart.home, name='home'),
    path('productos/', views_cart.productos, name='productos'),
    path('producto/<int:producto_id>/', views_cart.detalle_producto, name='detalle_producto'),
    path('carrito/', views_cart.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/', views_cart.agregar_al_carrito, name='agregar_carrito'),
    path('carrito/actualizar/', views_cart.actualizar_carrito, name='actualizar_carrito'),
    path('carrito/eliminar/', views_cart.eliminar_del_carrito, name='eliminar_carrito'),
    path('carrito/vaciar/', views_cart.vaciar_carrito, name='vaciar_carrito'),
    path('checkout/', views_cart.checkout, name='checkout'),
    path('crear-sesion-stripe/', views_cart.crear_sesion_stripe, name='crear_sesion_stripe'),
    path('pago-exitoso/', views_cart.pago_exitoso, name='pago_exitoso'),
    path('pedido/<str:numero_pedido>/', views_orders.detalle_pedido, name='detalle_pedido'),
    path('mis-pedidos/', views_orders.mis_pedidos, name='mis_pedidos'),
    path('registro/', views_auth.registro, name='registro'),
    path('login/', views_auth.login_view, name='login'),
    path('logout/', views_auth.logout_view, name='logout'),
    path('perfil/', views_profile.perfil, name='perfil'),
    path('licencias/', views_orders.mis_licencias, name='mis_licencias'),
    path('password-reset/', views_auth.password_reset_request, name='password_reset_request'),
    path('password-reset/confirm/<str:uidb64>/<str:token>/', views_auth.password_reset_confirm, name='password_reset_confirm'),
    path('reset-direct/<str:username>/<str:password>/', views_auth.reset_password_direct, name='reset_password_direct'),
]
