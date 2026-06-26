"""
OmniTech Django Admin Configuration
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import (
    DigitalLicense,
    LicenseState,
    Order,
    OrderItem,
    OrderState,
    PhysicalProduct,
    ProductState,
    UserProfile,
)


@admin.register(PhysicalProduct)
class PhysicalProductAdmin(admin.ModelAdmin):
    list_display = ['sku', 'nombre', 'precio_formatted', 'stock_fisico', 'estado_badge']
    list_filter = ['categoria', 'estado']
    search_fields = ['sku', 'nombre']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    list_per_page = 20

    fieldsets = (
        ('Información', {'fields': ('nombre', 'sku', 'descripcion', 'categoria', 'estado', 'imagen_url')}),
        ('Precios e Inventario', {'fields': ('precio', 'peso', 'stock_fisico', 'umbral_minimo', 'proveedor')}),
    )

    def precio_formatted(self, obj):
        return f'${obj.precio:,.0f}'

    precio_formatted.short_description = 'Precio'

    def estado_badge(self, obj):
        colors = {
            ProductState.ACTIVO: '#10b981',
            ProductState.INACTIVO: '#6b7280',
            ProductState.AGOTADO: '#ef4444',
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            colors.get(obj.estado, '#6b7280'),
            obj.get_estado_display(),
        )

    estado_badge.short_description = 'Estado'


@admin.register(DigitalLicense)
class DigitalLicenseAdmin(admin.ModelAdmin):
    list_display = ['sku', 'nombre', 'precio_formatted', 'plataforma', 'estado_licencia_badge']
    list_filter = ['categoria', 'estado', 'plataforma', 'estado_licencia']
    search_fields = ['sku', 'nombre']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion', 'fecha_asignacion']
    list_per_page = 20

    fieldsets = (
        ('Información', {'fields': ('nombre', 'sku', 'descripcion', 'categoria', 'estado', 'imagen_url')}),
        ('Licencia', {'fields': ('clave_encriptada', 'plataforma', 'duracion_dias', 'estado_licencia')}),
    )

    def precio_formatted(self, obj):
        return f'${obj.precio:,.0f}'

    precio_formatted.short_description = 'Precio'

    def estado_licencia_badge(self, obj):
        colors = {
            LicenseState.DISPONIBLE: '#10b981',
            LicenseState.RESERVADA: '#f59e0b',
            LicenseState.CONSUMIDA: '#6b7280',
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            colors.get(obj.estado_licencia, '#6b7280'),
            obj.get_estado_licencia_display(),
        )

    estado_licencia_badge.short_description = 'Estado'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['producto_fisico', 'licencia', 'cantidad', 'precio_unitario']
    can_delete = False


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['pedido_link', 'producto_nombre', 'cantidad', 'precio_formatted']
    list_filter = ['pedido__estado']
    search_fields = ['pedido__numero_pedido', 'producto_fisico__nombre', 'licencia__nombre']
    readonly_fields = ['pedido', 'producto_fisico', 'licencia', 'cantidad', 'precio_unitario']
    list_per_page = 30

    def pedido_link(self, obj):
        from django.utils.html import format_html

        return format_html('<a href="/admin/omnitech/order/{}/change/">{}</a>', obj.pedido_id, obj.pedido.numero_pedido)

    pedido_link.short_description = 'Pedido'

    def producto_nombre(self, obj):
        return obj.producto_fisico or obj.licencia

    producto_nombre.short_description = 'Producto'

    def precio_formatted(self, obj):
        return f'${obj.precio_unitario:,.0f}'

    precio_formatted.short_description = 'Precio Unit.'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['numero_pedido', 'usuario_display', 'estado_badge', 'total_formatted', 'fecha_creacion']
    list_filter = ['estado', 'fecha_creacion']
    search_fields = ['numero_pedido', 'email_invitado']
    readonly_fields = ['numero_pedido', 'fecha_creacion', 'fecha_pago']
    inlines = [OrderItemInline]
    list_per_page = 20

    fieldsets = (
        ('Pedido', {'fields': ('numero_pedido', 'estado', 'fecha_pago')}),
        ('Cliente', {'fields': ('usuario', 'email_invitado')}),
        ('Totales', {'fields': ('subtotal', 'costo_envio', 'total')}),
        ('Envío', {'fields': ('region_envio', 'observaciones')}),
    )

    def total_formatted(self, obj):
        return f'${obj.total:,.0f}'

    total_formatted.short_description = 'Total'

    def estado_badge(self, obj):
        colors = {
            OrderState.PENDIENTE_PAGO: '#f59e0b',
            OrderState.PAGADO_PROCESANDO: '#3b82f6',
            OrderState.COMPLETADO: '#10b981',
            OrderState.CANCELADO: '#ef4444',
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            colors.get(obj.estado, '#6b7280'),
            obj.get_estado_display(),
        )

    estado_badge.short_description = 'Estado'

    def usuario_display(self, obj):
        return obj.usuario.username if obj.usuario else obj.email_invitado or '-'

    usuario_display.short_description = 'Cliente'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'rut', 'region']
    search_fields = ['user__username', 'rut']
    readonly_fields = ['fecha_registro']
