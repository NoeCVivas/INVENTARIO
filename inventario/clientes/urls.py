from django.urls import path
from .views import (
    ClienteListView,
    ClienteCreateView,
    ClienteUpdateView,
    ClienteDeleteView,
    ClienteDetailView,  # 👈 Asegurate de importar esta vista
)

app_name = 'clientes'

urlpatterns = [
    path('', ClienteListView.as_view(), name='cliente_list'),
    path('nuevo/', ClienteCreateView.as_view(), name='cliente_create'),
    path('<int:pk>/editar/', ClienteUpdateView.as_view(), name='cliente_update'),
    path('<int:pk>/eliminar/', ClienteDeleteView.as_view(), name='cliente_delete'),
    path('<int:pk>/', ClienteDetailView.as_view(), name='cliente_detail'),  # 👈 Esta línea es clave
]
