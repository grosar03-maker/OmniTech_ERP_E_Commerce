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


@staff_member_required(login_url='/login/')
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


def _extraer_datos_producto(request):
    nombre = request.POST.get('nombre', '').strip()
    sku = request.POST.get('sku', '').strip().upper()
    return {
        'nombre': nombre,
        'sku': sku,
        'descripcion': request.POST.get('descripcion', '').strip(),
        'categoria': request.POST.get('categoria', '').strip(),
        'precio': Decimal(str(request.POST.get('precio', '0'))),
        'imagen_url': request.POST.get('imagen_url', '').strip(),
    }


def _validar_nombre_sku(nombre, sku):
    return bool(nombre and sku)


def _aplicar_campos_tipo(producto, tipo, datos):
    if tipo == 'fisico':
        producto.peso = Decimal(str(datos.get('peso', '0')))
        producto.stock_fisico = int(datos.get('stock_fisico', 0))
    else:
        producto.plataforma = datos.get('plataforma', '').strip()
        producto.duracion_dias = int(datos.get('duracion_dias', 365))
        clave = datos.get('clave_encriptada', '').strip()
        if clave:
            producto.clave_encriptada = clave


def _extraer_y_validar(request, redirect_url, *url_args):
    datos = _extraer_datos_producto(request)
    if not _validar_nombre_sku(datos['nombre'], datos['sku']):
        messages.error(request, 'Nombre y SKU son requeridos')
        return None, redirect(redirect_url, *url_args)
    return datos, None


@staff_member_required(login_url='/login/')
def editar_producto(request, producto_id, tipo):
    producto = ProductFactory.obtener_producto_o_404(tipo, producto_id)

    if request.method == 'POST':
        try:
            datos, err = _extraer_y_validar(request, 'editar_producto', producto_id, tipo)
            if err:
                return err

            for attr in ('nombre', 'sku', 'descripcion', 'categoria', 'precio', 'imagen_url'):
                setattr(producto, attr, datos[attr])

            _aplicar_campos_tipo(producto, tipo, request.POST)

            producto.save()

            claves_extra = request.POST.getlist('claves_adicionales')
            sku_base = datos['sku']
            contador = 1
            for c in claves_extra:
                c = c.strip()
                if not c:
                    continue
                nuevo_sku = f'{sku_base}-{contador:03d}'
                while DigitalLicense.objects.filter(sku=nuevo_sku).exists():
                    contador += 1
                    nuevo_sku = f'{sku_base}-{contador:03d}'
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


@staff_member_required(login_url='/login/')
def agregar_producto(request, tipo):
    if request.method == 'POST':
        try:
            datos, err = _extraer_y_validar(request, 'agregar_producto', tipo)
            if err:
                return err

            if tipo == 'fisico':
                PhysicalProduct.objects.create(
                    nombre=datos['nombre'],
                    sku=datos['sku'],
                    descripcion=datos['descripcion'],
                    categoria=datos['categoria'],
                    precio=datos['precio'],
                    imagen_url=datos['imagen_url'],
                    peso=Decimal(str(request.POST.get('peso', '0'))),
                    stock_fisico=int(request.POST.get('stock_fisico', 0)),
                )
                messages.success(request, f'Producto físico {datos["nombre"]} creado')
            else:
                DigitalLicense.objects.create(
                    nombre=datos['nombre'],
                    sku=datos['sku'],
                    descripcion=datos['descripcion'],
                    categoria=datos['categoria'],
                    precio=datos['precio'],
                    imagen_url=datos['imagen_url'],
                    clave_encriptada=request.POST.get('clave_encriptada', '').strip(),
                    plataforma=request.POST.get('plataforma', '').strip(),
                    duracion_dias=int(request.POST.get('duracion_dias', 365)),
                    estado_licencia=LicenseState.DISPONIBLE,
                )
                messages.success(request, f'Licencia {datos["nombre"]} creada')

            return redirect('admin_dashboard')

        except Exception as e:
            messages.error(request, f'Error al crear producto: {str(e)}')
            return redirect('agregar_producto', tipo=tipo)

    context = {
        'es_fisico': tipo == 'fisico',
        'es_software': tipo != 'fisico',
    }
    return render(request, 'admin_producto_form.html', context)


@staff_member_required(login_url='/login/')
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


@staff_member_required(login_url='/login/')
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
