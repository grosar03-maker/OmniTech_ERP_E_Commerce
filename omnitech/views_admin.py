"""
Views: Administración Web - OmniTech
SRP: Solo vistas para administración de productos desde la web
"""

from decimal import Decimal

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import ProtectedError
from django.shortcuts import redirect, render

from .factories import ProductFactory
from .models import DigitalLicense, LicenseState, PhysicalProduct, ProductState


@staff_member_required
def dashboard(request):
    productos_fisicos = PhysicalProduct.objects.all().order_by('-fecha_creacion')
    licencias = DigitalLicense.objects.all().order_by('-fecha_creacion')

    context = {
        'productos_fisicos': productos_fisicos,
        'licencias': licencias,
        'total_fisicos': productos_fisicos.count(),
        'total_licencias': licencias.count(),
        'stock_bajo': PhysicalProduct.objects.filter(estado=ProductState.ACTIVO).count(),
    }
    return render(request, 'admin_dashboard.html', context)


@staff_member_required
def editar_producto(request, producto_id, tipo):
    producto = ProductFactory.obtener_producto_o_404(tipo, producto_id)

    if request.method == 'POST':
        try:
            producto.nombre = request.POST.get('nombre', '').strip()
            sku = request.POST.get('sku', '').strip().upper()
            producto.descripcion = request.POST.get('descripcion', '').strip()
            producto.categoria = request.POST.get('categoria', '').strip()
            producto.precio = Decimal(str(request.POST.get('precio', '0')))
            producto.imagen_url = request.POST.get('imagen_url', '').strip()

            if not producto.nombre or not sku:
                messages.error(request, 'Nombre y SKU son requeridos')
                return redirect('editar_producto', producto_id=producto_id, tipo=tipo)

            producto.sku = sku

            if tipo == 'fisico':
                producto.peso = Decimal(str(request.POST.get('peso', '0')))
                producto.stock_fisico = int(request.POST.get('stock_fisico', 0))
            else:
                producto.plataforma = request.POST.get('plataforma', '').strip()
                producto.duracion_dias = int(request.POST.get('duracion_dias', 365))
                clave = request.POST.get('clave_encriptada', '').strip()
                if clave:
                    producto.clave_encriptada = clave

            producto.save()

            claves_extra = request.POST.getlist('claves_adicionales')
            contador = 1
            for c in claves_extra:
                c = c.strip()
                if not c:
                    continue
                nuevo_sku = f'{sku}-{contador:03d}'
                while DigitalLicense.objects.filter(sku=nuevo_sku).exists():
                    contador += 1
                    nuevo_sku = f'{sku}-{contador:03d}'
                DigitalLicense.objects.create(
                    nombre=producto.nombre,
                    sku=nuevo_sku,
                    descripcion=producto.descripcion,
                    categoria=producto.categoria,
                    precio=producto.precio,
                    imagen_url=producto.imagen_url,
                    plataforma=producto.plataforma,
                    duracion_dias=producto.duracion_dias,
                    clave_encriptada=c,
                    estado_licencia=LicenseState.DISPONIBLE,
                )
                contador += 1
            if claves_extra:
                messages.success(request, f'{len(claves_extra)} clave(s) adicional(es) creada(s)')

            messages.success(request, f'{producto.nombre} actualizado')
        except Exception as e:
            messages.error(request, f'Error al actualizar: {str(e)}')
        return redirect('admin_dashboard')

    es_fisico = tipo == 'fisico'
    context = {
        'producto': producto,
        'precio_actual': str(int(producto.precio)) if producto.precio else '',
        'peso_actual': str(producto.peso) if es_fisico and producto.peso else '',
        'es_fisico': es_fisico,
        'es_software': not es_fisico,
        'editando': True,
    }
    return render(request, 'admin_producto_form.html', context)


@staff_member_required
def agregar_producto(request, tipo):
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre', '').strip()
            sku = request.POST.get('sku', '').strip().upper()
            descripcion = request.POST.get('descripcion', '').strip()
            categoria = request.POST.get('categoria', '').strip()
            precio = request.POST.get('precio', '0')
            imagen_url = request.POST.get('imagen_url', '').strip()

            if not nombre or not sku:
                messages.error(request, 'Nombre y SKU son requeridos')
                return redirect('agregar_producto', tipo=tipo)

            precio_dec = Decimal(str(precio))

            if tipo == 'fisico':
                peso = request.POST.get('peso', '0')
                stock_fisico = int(request.POST.get('stock_fisico', 0))
                PhysicalProduct.objects.create(
                    nombre=nombre,
                    sku=sku,
                    descripcion=descripcion,
                    categoria=categoria,
                    precio=precio_dec,
                    imagen_url=imagen_url,
                    peso=Decimal(str(peso)),
                    stock_fisico=stock_fisico,
                )
                messages.success(request, f'Producto físico {nombre} creado')
            else:
                clave_encriptada = request.POST.get('clave_encriptada', '').strip()
                plataforma = request.POST.get('plataforma', '').strip()
                duracion_dias = int(request.POST.get('duracion_dias', 365))
                DigitalLicense.objects.create(
                    nombre=nombre,
                    sku=sku,
                    descripcion=descripcion,
                    categoria=categoria,
                    precio=precio_dec,
                    imagen_url=imagen_url,
                    clave_encriptada=clave_encriptada,
                    plataforma=plataforma,
                    duracion_dias=duracion_dias,
                    estado_licencia=LicenseState.DISPONIBLE,
                )
                messages.success(request, f'Licencia {nombre} creada')

            return redirect('admin_dashboard')

        except Exception as e:
            messages.error(request, f'Error al crear producto: {str(e)}')
            return redirect('agregar_producto', tipo=tipo)

    context = {
        'es_fisico': tipo == 'fisico',
        'es_software': tipo != 'fisico',
    }
    return render(request, 'admin_producto_form.html', context)


@staff_member_required
def toggle_estado(request, producto_id, tipo):
    try:
        producto = ProductFactory.obtener_producto(tipo, producto_id)
        if producto.estado == ProductState.ACTIVO:
            producto.estado = ProductState.INACTIVO
            messages.info(request, f'{producto.nombre} desactivado')
        else:
            producto.estado = ProductState.ACTIVO
            messages.success(request, f'{producto.nombre} activado')
        producto.save(update_fields=['estado'])
    except Exception:
        messages.error(request, 'Producto no encontrado')
    return redirect('admin_dashboard')


@staff_member_required
def eliminar_producto(request, producto_id, tipo):
    try:
        producto = ProductFactory.obtener_producto_o_404(tipo, producto_id)
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f'"{nombre}" eliminado permanentemente')
    except ProtectedError:
        messages.error(request, 'No se puede eliminar: tiene pedidos asociados')
    except Exception as e:
        messages.error(request, f'Error al eliminar: {str(e)}')
    return redirect('admin_dashboard')
