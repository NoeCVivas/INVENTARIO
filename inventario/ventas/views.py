from django.views.generic import CreateView, ListView, DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.db.models import Sum, F
import json
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import logout

from .models import Venta, ItemVenta
from .forms import VentaForm, ItemVentaFormSet
from productos.models import Producto, MovimientoStock


class VentaCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Venta
    form_class = VentaForm
    template_name = 'venta/venta_form.html'
    permission_required = 'ventas.add_venta'

    def get_context_data_custom(self, form, formset):
        productos = Producto.objects.filter(stock__gt=0)
        precios = {str(p.id): float(p.precio) for p in productos}
        stocks = {str(p.id): p.stock for p in productos}
        return {
            'form': form,
            'formset': formset,
            'precios_json': json.dumps(precios, cls=DjangoJSONEncoder),
            'stocks_json': json.dumps(stocks, cls=DjangoJSONEncoder),
        }

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        formset = ItemVentaFormSet(prefix='form')
        context = self.get_context_data_custom(form, formset)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        formset = ItemVentaFormSet(request.POST, prefix='form')

        if form.is_valid() and formset.is_valid():

            medio_pago = form.cleaned_data['medio_pago'].lower()

            # ► Validación extra de tarjeta
            if medio_pago in ["credito", "debito"]:
                numero = request.POST.get('numero_tarjeta', '').strip()
                vencimiento = request.POST.get('fecha_vencimiento', '').strip()
                cvv = request.POST.get('codigo_seguridad', '').strip()

                if not numero or not vencimiento or not cvv:
                    messages.error(request, "Completá todos los datos de la tarjeta.")
                    context = self.get_context_data_custom(form, formset)
                    return render(request, self.template_name, context)

            with transaction.atomic():
                venta = form.save(commit=False)
                venta.codigo = f"V-{Venta.objects.count() + 1:04d}"
                venta.total = 0
                venta.save()

                # ► Procesar ítems correctamente
                for item_form in formset.forms:

                    if not item_form.cleaned_data:
                        continue

                    producto = item_form.cleaned_data.get("producto")
                    cantidad = item_form.cleaned_data.get("cantidad")

                    if not producto or not cantidad:
                        continue

                    # Bloquear el producto para evitar condiciones de carrera
                    producto_bloqueado = Producto.objects.select_for_update().get(id=producto.id)

                    # Validación de stock
                    if producto_bloqueado.stock < cantidad:
                        messages.error(request, f"Stock insuficiente para {producto_bloqueado.nombre}")
                        raise transaction.TransactionManagementError()

                    precio = producto_bloqueado.precio
                    subtotal = precio * cantidad

                    # Crear item
                    ItemVenta.objects.create(
                        venta=venta,
                        producto=producto_bloqueado,
                        cantidad=cantidad,
                        precio_unitario=precio,
                        subtotal=subtotal
                    )

                    # Actualizar stock seguro con F()
                    Producto.objects.filter(id=producto_bloqueado.id).update(stock=F('stock') - cantidad)

                    # Registrar movimiento de salida
                    MovimientoStock.objects.create(
                        producto=producto_bloqueado,
                        tipo='salida',
                        cantidad=cantidad,
                        motivo=f"Venta {venta.codigo}",
                        usuario=request.user.username
                    )

                    # Sumar al total
                    venta.total += subtotal

                venta.save()

                messages.success(request, "Venta registrada correctamente.")
                return redirect('ventas:venta_detail', pk=venta.pk)

        # Si algo falla
        context = self.get_context_data_custom(form, formset)
        return render(request, self.template_name, context)


class VentaListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Venta
    template_name = 'venta/venta_list.html'
    context_object_name = 'ventas'
    permission_required = 'ventas.view_venta'


class VentaDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Venta
    template_name = 'venta/venta_detail.html'
    context_object_name = 'venta'
    permission_required = 'ventas.view_venta'


@login_required
@permission_required('ventas.view_venta', raise_exception=True)
def generar_factura_pdf(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    items = venta.items.all()

    template = get_template('venta/factura_pdf.html')
    html = template.render({'venta': venta, 'items': items})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="factura_{venta.codigo}.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response


@login_required
@permission_required('ventas.view_venta', raise_exception=True)
def ventas_por_dia_json(request):
    datos = (
        Venta.objects
        .values('fecha')
        .annotate(total_dia=Sum('total'))
        .order_by('fecha')
    )
    fechas = [str(d['fecha']) for d in datos]
    totales = [float(d['total_dia']) for d in datos]
    return JsonResponse({'labels': fechas, 'data': totales})


@login_required
@permission_required('ventas.view_venta', raise_exception=True)
def ventas_por_dia(request):
    return render(request, 'venta/ventas_por_dia.html')


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect('login')
