from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static      
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from ventas.views import generar_factura_pdf, logout_view

urlpatterns = [
    
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('admin/', admin.site.urls),
    path('productos/', include('productos.urls')),
    path('clientes/', include('clientes.urls')),
    path('ventas/', include('ventas.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', logout_view, name='logout'),
    path('accounts/', include('allauth.urls')),
    path('factura/<int:venta_id>/pdf/', generar_factura_pdf, name='factura_pdf'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
