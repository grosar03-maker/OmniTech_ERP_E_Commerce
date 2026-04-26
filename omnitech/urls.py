"""
OmniTech App URLs
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('productos/', views.productos, name='productos'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/', views.agregar_al_carrito, name='agregar_carrito'),
    path('carrito/actualizar/', views.actualizar_carrito, name='actualizar_carrito'),
    path('carrito/eliminar/', views.eliminar_del_carrito, name='eliminar_carrito'),
    path('carrito/vaciar/', views.vaciar_carrito, name='vaciar_carrito'),
    path('checkout/', views.checkout, name='checkout'),
    path('crear-sesion-stripe/', views.crear_sesion_stripe, name='crear_sesion_stripe'),
    path('pago-exitoso/', views.pago_exitoso, name='pago_exitoso'),
    path('pedido/<str:numero_pedido>/', views.detalle_pedido, name='detalle_pedido'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    path('licencias/', views.mis_licencias, name='mis_licencias'),
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/confirm/<str:uidb64>/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('reset-direct/<str:username>/<str:password>/', views.reset_password_direct, name='reset_password_direct'),
]
