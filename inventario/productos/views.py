from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, F
from django.utils import timezone
from .models import Producto, MovimientoStock
from .forms import ProductoForm, MovimientoStockForm, AjusteStockForm

# Listado general con filtros y paginación
class ProductoListView(ListView):
    model = Producto
    template_name = 'producto/producto_list.html'
    context_object_name = 'productos'
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        nombre = self.request.GET.get('nombre')
        stock_bajo = self.request.GET.get('stock_bajo')
        if nombre:
            queryset = queryset.filter(nombre__icontains=nombre)
        if stock_bajo:
            queryset = queryset.filter(stock__lt=F('stock_minimo'))
        return queryset.order_by('nombre')

# Detalle de producto con últimos movimientos y formulario de ajuste
class ProductoDetailView(DetailView):
    model = Producto
    template_name = 'producto/producto_detail.html'
    context_object_name = 'producto'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movimientos'] = MovimientoStock.objects.filter(producto=self.object).order_by('-fecha')[:10]
        context['form_ajuste'] = AjusteStockForm()
        return context

# Crear producto con movimiento inicial si hay stock
class ProductoCreateView(CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'producto/producto_form.html'
    success_url = reverse_lazy('productos:producto_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.cleaned_data['stock'] > 0:
            MovimientoStock.objects.create(
                producto=self.object,
                tipo="Entrada",
                cantidad=form.cleaned_data['stock'],
                motivo="Stock inicial",
                fecha=timezone.now(),
                usuario=self.request.user.username if self.request.user.is_authenticated else 'Sistema'
            )
        messages.success(self.request, 'Producto creado exitosamente.')
        return response

# Actualizar producto
class ProductoUpdateView(UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'producto/producto_form.html'
    success_url = reverse_lazy('productos:producto_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Producto actualizado exitosamente.')
        return response

# Eliminar producto
class ProductoDeleteView(DeleteView):
    model = Producto
    template_name = 'producto/producto_confirm_delete.html'
    success_url = reverse_lazy('productos:producto_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Producto eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)

# Registrar movimiento de stock (entrada/salida)
class MovimientoStockCreateView(CreateView):
    model = MovimientoStock
    form_class = MovimientoStockForm
    template_name = 'producto/movimiento_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['producto'] = get_object_or_404(Producto, pk=self.kwargs['pk'])
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['producto'] = get_object_or_404(Producto, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        movimiento = form.save(commit=False)
        producto = get_object_or_404(Producto, pk=self.kwargs['pk'])
        movimiento.producto = producto
        movimiento.usuario = self.request.user.username if self.request.user.is_authenticated else 'Sistema'

        if movimiento.tipo == 'Entrada':
            producto.stock += movimiento.cantidad
        elif movimiento.tipo == 'Salida':
            if producto.stock >= movimiento.cantidad:
                producto.stock -= movimiento.cantidad
            else:
                form.add_error('cantidad', 'No hay suficiente stock para realizar esta salida.')
                return self.form_invalid(form)

        producto.save()
        movimiento.save()
        messages.success(self.request, 'Movimiento de stock registrado exitosamente.')
        return redirect('productos:producto_detail', pk=producto.pk)

# Ajuste manual de stock
class AjusteStockView(FormView):
    form_class = AjusteStockForm
    template_name = 'producto/ajuste_stock_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['producto'] = get_object_or_404(Producto, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        producto = get_object_or_404(Producto, pk=self.kwargs['pk'])
        nueva_cantidad = form.cleaned_data['nueva_cantidad']
        motivo = form.cleaned_data['motivo'] or 'Ajuste de stock'
        diferencia = nueva_cantidad - producto.stock

        if diferencia != 0:
            tipo = 'Entrada' if diferencia > 0 else 'Salida'
            MovimientoStock.objects.create(
                producto=producto,
                tipo=tipo,
                cantidad=abs(diferencia),
                motivo=motivo,
                fecha=timezone.now(),
                usuario=self.request.user.username if self.request.user.is_authenticated else 'Sistema'
            )
            producto.stock = nueva_cantidad
            producto.save()
            messages.success(self.request, 'Ajuste de stock realizado exitosamente.')
        else:
            messages.info(self.request, 'No se realizó ningún ajuste ya que la cantidad es la misma.')

        return redirect('productos:producto_detail', pk=producto.pk)

# Listado de productos con stock bajo + paginación
class StockBajoListView(ListView):
    model = Producto
    template_name = 'producto/stock_bajo_list.html'
    context_object_name = 'productos'
    paginate_by = 5  # 👈 Paginación activa

    def get_queryset(self):
        return Producto.objects.filter(stock__lt=F('stock_minimo')).order_by('stock')
