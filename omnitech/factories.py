"""
Factories - OmniTech
Patrón Factory Method para creación/obtención de productos.
OCP: Agregar un nuevo tipo de producto no requiere modificar views ni services.
"""

from django.shortcuts import get_object_or_404
from .models import PhysicalProduct, DigitalLicense


class ProductFactory:
    """
    Factory Method pattern.
    Centraliza la resolución de modelos de producto por tipo.
    """

    PRODUCT_MAP = {
        'fisico': PhysicalProduct,
        'software': DigitalLicense,
        'digital': DigitalLicense,
    }

    @classmethod
    def obtener_modelo(cls, tipo):
        model = cls.PRODUCT_MAP.get(tipo)
        if not model:
            raise ValueError(f"Tipo de producto desconocido: {tipo}")
        return model

    @classmethod
    def obtener_producto(cls, tipo, producto_id):
        return cls.obtener_modelo(tipo).objects.get(id=producto_id)

    @classmethod
    def obtener_producto_o_404(cls, tipo, producto_id):
        return get_object_or_404(cls.obtener_modelo(tipo), id=producto_id)

    @classmethod
    def obtener_producto_con_lock(cls, tipo, producto_id):
        return cls.obtener_modelo(tipo).objects.select_for_update().get(id=producto_id)

    @classmethod
    def es_tipo_fisico(cls, tipo):
        return tipo == 'fisico'

    @classmethod
    def obtener_nombre_corto(cls, tipo):
        return 'Físico' if tipo == 'fisico' else 'Licencia'
