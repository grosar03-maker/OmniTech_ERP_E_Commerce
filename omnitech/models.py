"""
OmniTech ERP & E-Commerce - Modelos de Dominio
Arquitectura Hexagonal con Service Layer

Módulo: Catálogo Híbrido y Carrito de Compras
Sistema transaccional híbrido (Hardware + Licencias Digitales)
"""

from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models


def _get_fernet():
    import base64
    import hashlib

    from cryptography.fernet import Fernet

    key = base64.urlsafe_b64encode(hashlib.sha256(settings.SECRET_KEY.encode()).digest())
    return Fernet(key)


def encriptar_clave(clave):
    """Helper para encriptar claves de licencia."""
    f = _get_fernet()
    return f.encrypt(clave.encode()).decode()


class ProductState(models.TextChoices):
    """Estados genéricos para productos."""

    ACTIVO = 'activo', 'Activo'
    INACTIVO = 'inactivo', 'Inactivo'
    AGOTADO = 'agotado', 'Agotado'


class LicenseState(models.TextChoices):
    """Estados del ciclo de vida de licencias digitales (RN-02)."""

    DISPONIBLE = 'disponible', 'Disponible'
    RESERVADA = 'reservada', 'Reservada'
    CONSUMIDA = 'consumida', 'Consumida'


class OrderState(models.TextChoices):
    """Estados del pedido con soporte para bifurcación mixta (RN-01)."""

    PENDIENTE_PAGO = 'pendiente_pago', 'Pendiente de Pago'
    PAGADO_PROCESANDO = 'pagado_procesando', 'Pagado - Procesando'
    COMPLETADO = 'completado', 'Completado'
    CANCELADO = 'cancelado', 'Cancelado'


class Order(models.Model):
    """
    Pedido del sistema - Maneja transacciones ACID.

    Soporta bifurcación mixta (RN-01):
    - Software: despacho inmediato vía email
    - Hardware: encolamiento para empaque físico
    """

    numero_pedido = models.CharField(
        max_length=20, unique=True, editable=False, help_text='Código único de seguimiento'
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='pedidos',
        null=True,
        blank=True,
        help_text='Usuario registrado (null para guest checkout RN-06)',
    )
    email_invitado = models.EmailField(null=True, blank=True, help_text='Email para guest checkout (RN-06)')
    estado = models.CharField(max_length=20, choices=OrderState.choices, default=OrderState.PENDIENTE_PAGO)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    region_envio = models.CharField(
        max_length=100, blank=True, help_text='Región para cálculo de envío subsidiado (RN-04)'
    )
    observaciones = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_pago = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'orders'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['numero_pedido']),
            models.Index(fields=['estado', 'fecha_creacion']),
            models.Index(fields=['usuario', 'fecha_creacion']),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(subtotal__gte=0), name='order_subtotal_positive'),
            models.CheckConstraint(check=models.Q(costo_envio__gte=0), name='order_envio_positive'),
            models.CheckConstraint(check=models.Q(total__gte=0), name='order_total_positive'),
        ]

    def __str__(self):
        return f'Pedido {self.numero_pedido} - {self.get_estado_display()}'

    def calcular_total(self):
        """Calcula el total considerando subsidio regional (RN-04)."""
        self.subtotal = sum(item.precio_unitario * item.cantidad for item in self.items.all())

        tiene_hardware = self.items.filter(producto_fisico__isnull=False).exists()

        if tiene_hardware and self.region_envio == 'La Araucanía' and self.subtotal > settings.SUBSIDIO_MONTO:
            self.costo_envio = Decimal('0.00')
        elif tiene_hardware:
            peso_total = sum(
                item.producto_fisico.peso * item.cantidad for item in self.items.filter(producto_fisico__isnull=False)
            )
            self.costo_envio = Decimal(str(peso_total * 500))

        self.total = self.subtotal + self.costo_envio
        return self.total

    def tiene_software(self):
        return self.items.filter(licencia__isnull=False).exists()

    def tiene_hardware(self):
        return self.items.filter(producto_fisico__isnull=False).exists()


class OrderItem(models.Model):
    """
    Ítem de pedido - Relación genérica con productos.

    Soporta tanto hardware como software mediante relaciones específicas.
    """

    pedido = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    producto_fisico = models.ForeignKey(
        'PhysicalProduct',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='order_items',
        help_text='Relación para productos físicos',
    )
    licencia = models.ForeignKey(
        'DigitalLicense',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='order_items',
        help_text='Relación para licencias digitales',
    )
    cantidad = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        db_table = 'order_items'
        indexes = [
            models.Index(fields=['pedido']),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(cantidad__gte=1), name='orderitem_cantidad_positive'),
            models.CheckConstraint(
                check=models.Q(models.Q(producto_fisico__isnull=False) | models.Q(licencia__isnull=False)),
                name='orderitem_producto_required',
            ),
            models.CheckConstraint(
                check=models.Q(models.Q(producto_fisico__isnull=True) | models.Q(licencia__isnull=True)),
                name='orderitem_exclusive_product',
            ),
        ]

    def __str__(self):
        producto = self.producto_fisico or self.licencia
        return f'{self.cantidad}x {producto}'

    @property
    def subtotal(self):
        return (self.precio_unitario * self.cantidad) - self.descuento

    def save(self, *args, **kwargs):
        if self.producto_fisico:
            self.precio_unitario = self.producto_fisico.precio
        elif self.licencia:
            self.precio_unitario = self.licencia.precio
        super().save(*args, **kwargs)


class Product(models.Model):
    """
    Clase base abstracta para el catálogo híbrido.

    Define la interfaz común para productos físicos y digitales.
    """

    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    imagen_url = models.URLField(max_length=500, blank=True, help_text='URL de imagen del producto')
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    sku = models.CharField(
        max_length=50,
        unique=True,
        validators=[
            RegexValidator(regex=r'^[A-Z0-9-]+$', message='SKU debe contener solo mayúsculas, números y guiones')
        ],
    )
    categoria = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, choices=ProductState.choices, default=ProductState.ACTIVO)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        abstract = True
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['categoria', 'estado']),
        ]

    def __str__(self):
        return f'{self.sku} - {self.nombre}'


class PhysicalProduct(Product):
    """
    Producto físico - Hardware para venta y gestión de inventario.

    Incluye control de stock con reserva volátil (RN-03) y
    reabastecimiento automático (RN-05).
    """

    peso = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], help_text='Peso en kilogramos'
    )
    stock_fisico = models.PositiveIntegerField(default=0, help_text='Cantidad disponible en bodega')
    stock_reservado = models.PositiveIntegerField(default=0, help_text='Cantidad reservada durante checkout (RN-03)')
    umbral_minimo = models.PositiveIntegerField(default=10, help_text='Nivel que dispara reabastecimiento (RN-05)')
    proveedor = models.CharField(max_length=255, blank=True)
    ubicacion_bodega = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = 'physical_products'
        verbose_name = 'Producto Físico'
        verbose_name_plural = 'Productos Físicos'

    def __str__(self):
        return f'{self.sku} | Stock: {self.stock_disponible}'

    @property
    def stock_disponible(self):
        """Stock real considerando reservas."""
        return max(0, self.stock_fisico - self.stock_reservado)

    def necesita_reabastecimiento(self):
        """Verifica si debe generar borrador de importación (RN-05)."""
        return self.stock_disponible <= (self.umbral_minimo * 0.15)

    def reservar(self, cantidad):
        """
        Reserva stock por 15 minutos (RN-03).
        Retorna True si la reserva fue exitosa.
        """
        if self.stock_disponible >= cantidad:
            self.stock_reservado += cantidad
            self.save(update_fields=['stock_reservado'])
            return True
        return False

    def liberar_reserva(self, cantidad):
        """Libera reserva tras checkout fallido."""
        self.stock_reservado = max(0, self.stock_reservado - cantidad)
        self.save(update_fields=['stock_reservado'])

    def confirmar_reserva(self, cantidad):
        """Convierte reserva en venta efectividad."""
        self.stock_fisico = max(0, self.stock_fisico - cantidad)
        self.stock_reservado = max(0, self.stock_reservado - cantidad)
        self.save(update_fields=['stock_fisico', 'stock_reservado'])

    def procesar_venta(self, cantidad):
        """
        OCP: Método polimórfico para procesar venta.
        Cada subclase sabe cómo procesarse a sí misma.
        """
        self.confirmar_reserva(cantidad)
        return True


class DigitalLicense(Product):
    """
    Licencia digital - Producto intangible con clave encriptada.

    Ciclo de vida: DISPONIBLE -> RESERVADA -> CONSUMIDA (RN-02).
    Las licencias consumidas son inmutables.
    """

    clave_encriptada = models.CharField(max_length=500, help_text='Clave almacenada encriptada')
    plataforma = models.CharField(max_length=100, help_text='Plataforma o servicio asociado')
    duracion_dias = models.PositiveIntegerField(default=365, help_text='Vigencia en días (0 = indefinida)')
    estado_licencia = models.CharField(max_length=20, choices=LicenseState.choices, default=LicenseState.DISPONIBLE)
    orden_compra = models.ForeignKey(
        Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='licencias_entregadas'
    )
    fecha_asignacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'digital_licenses'
        verbose_name = 'Licencia Digital'
        verbose_name_plural = 'Licencias Digitales'
        indexes = [
            models.Index(fields=['estado_licencia']),
            models.Index(fields=['plataforma']),
        ]

    def __str__(self):
        return f'{self.sku} | {self.get_estado_licencia_display()}'

    def esta_disponible(self):
        return self.estado_licencia == LicenseState.DISPONIBLE

    def reservar(self, orden):
        """Reserva la licencia para una orden."""
        if self.esta_disponible():
            self.estado_licencia = LicenseState.RESERVADA
            self.orden_compra = orden
            self.save(update_fields=['estado_licencia', 'orden_compra'])
            return True
        return False

    def entregar(self):
        """
        Entrega la licencia al cliente.
        Una vez consumida, es inmutable (RN-02).
        Acepta DISPONIBLE y RESERVADA para soportar flujo directo de compra.
        """
        from django.utils import timezone

        if self.estado_licencia in (LicenseState.DISPONIBLE, LicenseState.RESERVADA):
            self.estado_licencia = LicenseState.CONSUMIDA
            self.fecha_asignacion = timezone.now()
            self.save(update_fields=['estado_licencia', 'fecha_asignacion'])
            return True
        return False

    def desencriptar_clave(self):
        """
        Desencripta la clave para visualización.
        En producción usar AWS KMS o similar.
        """
        f = _get_fernet()
        return f.decrypt(self.clave_encriptada.encode()).decode()

    def procesar_venta(self, cantidad):
        """
        OCP: Método polimórfico para procesar venta.
        LSP: Respeta el parámetro cantidad.
        Si cantidad > 1, busca licencias disponibles adicionales del mismo SKU.
        """
        if cantidad <= 0:
            return False
        if not self.entregar():
            return False
        if cantidad > 1:
            licencias_extra = DigitalLicense.objects.filter(
                sku=self.sku, estado_licencia=LicenseState.DISPONIBLE
            ).select_for_update(skip_locked=True)[: cantidad - 1]
            for lic in licencias_extra:
                lic.orden_compra = self.orden_compra
                lic.entregar()
            if licencias_extra.count() < cantidad - 1:
                raise ValueError(
                    f'Stock insuficiente de licencias para {self.nombre}. '
                    f'Se necesitan {cantidad}, disponibles: {licencias_extra.count() + 1}'
                )
        return True


class UserProfile(models.Model):
    """
    Perfil extendido de usuario para trazabilidad y preferencias.

    Soporta guest checkout (RN-06) mediante registro posterior.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rut = models.CharField(
        max_length=12,
        blank=True,
        null=True,
        validators=[RegexValidator(regex=r'^\d{7,8}-[\dkK]$', message='RUT debe tener formato XX.XXX.XXX-X')],
    )
    telefono = models.CharField(max_length=20, blank=True)
    region = models.CharField(max_length=100, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    direccion = models.TextField(blank=True)
    newsletter = models.BooleanField(default=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    ultima_compra = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'

    def __str__(self):
        return f'Perfil de {self.user.username}'

    @property
    def es_de_araucania(self):
        return self.region == 'La Araucanía'

    def calcular_total_compras(self):
        from django.db.models import Sum

        total = self.user.pedidos.filter(estado=OrderState.COMPLETADO).aggregate(total=Sum('total'))[
            'total'
        ] or Decimal('0.00')
        return total
