from django.urls import path
from .views import VentaCreateView, VentaListView, VentaDetailView, generar_factura_pdf

app_name = 'ventas'

urlpatterns = [
    path('', VentaListView.as_view(), name='venta_list'),
    path('nueva/', VentaCreateView.as_view(), name='venta_create'),
    path('<int:pk>/', VentaDetailView.as_view(), name='venta_detail'),
    path('factura/<int:venta_id>/pdf/', generar_factura_pdf, name='generar_factura_pdf'),  # ✅ nueva ruta
]
