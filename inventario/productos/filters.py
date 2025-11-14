# productos/filters.py
import django_filters
from django.db import models as dj_models
from .models import Producto

class ProductoFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='filter_q', label='Buscar')
    stock_bajo = django_filters.BooleanFilter(method='filter_stock_bajo', label='Stock bajo')

    def filter_q(self, queryset, name, value):
        value = (value or "").strip()
        if not value:
            return queryset
        return queryset.filter(
            dj_models.Q(nombre__icontains=value) |
            dj_models.Q(descripcion__icontains=value) |
            dj_models.Q(sku__icontains=value)
        )

    def filter_stock_bajo(self, queryset, name, value):
        if value:
            return queryset.filter(stock__lt=dj_models.F('stock_minimo'))
        return queryset

    class Meta:
        model = Producto
        fields = ['q', 'stock_bajo']
