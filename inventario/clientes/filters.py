# clientes/filters.py
import django_filters
from django.db import models as dj_models
from .models import Cliente

class ClienteFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='filter_q', label='Buscar')

    def filter_q(self, queryset, name, value):
        value = (value or "").strip()
        if not value:
            return queryset
        return queryset.filter(
            dj_models.Q(documento__icontains=value) |
            dj_models.Q(nombre__icontains=value) |
            dj_models.Q(apellido__icontains=value)
        )

    class Meta:
        model = Cliente
        fields = ['q', 'documento']
