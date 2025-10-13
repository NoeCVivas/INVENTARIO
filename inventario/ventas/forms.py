from django import forms
from django.forms import inlineformset_factory
from ventas.models import Venta, ItemVenta

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['codigo', 'cliente']

ItemVentaFormSet = inlineformset_factory(
    Venta,
    ItemVenta,
    fields=['producto', 'cantidad', 'precio_unitario'],
    extra=1,
    can_delete=False
)
