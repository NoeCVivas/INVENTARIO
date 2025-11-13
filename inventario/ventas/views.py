from django.views.generic import CreateView, ListView, DetailView
from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import json

from .models import Venta, ItemVenta
from .forms import VentaForm, ItemVentaFormSet
from productos.models import Producto

class VentaCreateView(CreateView):
    model = Venta
    form_class = VentaForm
    template_name = 'venta/venta_form.html'

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
        formset = ItemVentaFormSet()
        context = self.get_context_data_custom(form, formset)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        formset = ItemVentaFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                venta = form.save(commit=False)
                venta.codigo = f"V-{Venta.objects.count() + 1:04d}"
                venta.total = 0
                venta.medio_pago = form.cleaned_data['medio_pago']
                venta.fecha = form.cleaned_data['fecha']
                venta.save()

                for item_form in formset:
                    item = item_form.save(commit=False)
                    item.venta = venta

                    # ✅ Validación: producto obligatorio
                    if not item.producto:
                        messages.error(request, "Falta seleccionar un producto en uno de los ítems.")
                        transaction.set_rollback(True)
                        context = self.get_context_data_custom(form, formset)
                        return render(request, self.template_name, context)

                    item.precio_unitario = item.producto.precio
                    item.subtotal = item.precio_unitario * item.cantidad

                    producto = item.producto
                    if producto.stock < item.cantidad:
                        messages.error(request, f"Stock insuficiente para {producto.nombre}")
                        transaction.set_rollback(True)
                        context = self.get_context_data_custom(form, formset)
                        return render(request, self.template_name, context)

                    producto.stock -= item.cantidad
                    producto.save()
                    item.save()
                    venta.total += item.subtotal

                venta.save()
                messages.success(request, "Venta registrada correctamente.")
                return redirect('ventas:venta_detail', pk=venta.pk)

        context = self.get_context_data_custom(form, formset)
        return render(request, self.template_name, context)


class VentaListView(ListView):
    model = Venta
    template_name = 'venta/venta_list.html'
    context_object_name = 'ventas'


class VentaDetailView(DetailView):
    model = Venta
    template_name = 'venta/venta_detail.html'
    context_object_name = 'venta'


def generar_factura_pdf(request, venta_id):
    venta = Venta.objects.get(id=venta_id)
    items = venta.itemventa_set.all()
    template = get_template('venta/factura_pdf.html')
    html = template.render({'venta': venta, 'items': items})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="factura_{venta.codigo}.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response
