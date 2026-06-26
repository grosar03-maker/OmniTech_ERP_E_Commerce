from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def api_productos(request):
    from .factories import ProductFactory

    fisicos_model = ProductFactory.obtener_modelo('fisico')
    fisicos = list(
        fisicos_model.objects.filter(estado='activo').values(
            'id', 'nombre', 'sku', 'precio', 'categoria', 'peso', 'stock_fisico'
        )
    )
    digitales_model = ProductFactory.obtener_modelo('digital')
    digitales = list(
        digitales_model.objects.filter(estado='activo').values(
            'id', 'nombre', 'sku', 'precio', 'categoria', 'plataforma', 'duracion_dias'
        )
    )
    return Response(
        {
            'count': len(fisicos) + len(digitales),
            'fisicos': fisicos,
            'digitales': digitales,
        }
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_me(request):
    user = request.user
    perfil = getattr(user, 'perfil', None)
    return Response(
        {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_staff': user.is_staff,
            'nombres': f'{user.first_name} {user.last_name}'.strip(),
            'perfil': {
                'rut': perfil.rut if perfil else None,
                'telefono': perfil.telefono if perfil else '',
                'region': perfil.region if perfil else '',
                'ciudad': perfil.ciudad if perfil else '',
            }
            if perfil
            else None,
        }
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_pedidos(request):
    pedidos = request.user.pedidos.all().values('numero_pedido', 'estado', 'total', 'fecha_creacion')
    return Response(
        {
            'count': pedidos.count(),
            'pedidos': list(pedidos),
        }
    )
