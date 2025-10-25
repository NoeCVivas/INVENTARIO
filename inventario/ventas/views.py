from django.views.generic import CreateView, ListView, DetailView
from django.shortcuts import render, redirect
from django.db import transaction
from ventas.models import Venta, ItemVenta
from ventas.forms import VentaForm, ItemVentaFormSet
from productos.models import Producto

class VentaCreateView(CreateView):
    model = Venta
    form_class = VentaForm
    template_name = 'venta/venta_form.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        formset = ItemVentaFormSet()
        return render(request, self.template_name, {'form': form, 'formset': formset})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        formset = ItemVentaFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                venta = form.save(commit=False)
                venta.total = 0
                venta.save()

                for item_form in formset:
                    item = item_form.save(commit=False)
                    item.venta = venta
                    item.subtotal = item.cantidad * item.precio_unitario
                    item.save()

                    venta.total += item.subtotal

                    producto = item.producto
                    producto.stock -= item.cantidad
                    producto.save()

                venta.save()
            return redirect('ventas:venta_list')

        return render(request, self.template_name, {'form': form, 'formset': formset})

class VentaListView(ListView):
    model = Venta
    template_name = 'venta/venta_list.html'
    context_object_name = 'ventas'

class VentaDetailView(DetailView):
    model = Venta
    template_name = 'venta/venta_detail.html'
    context_object_name = 'venta'