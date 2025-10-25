# ventas/forms.py
from django import forms
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import Venta, ItemVenta

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['codigo', 'cliente']

class ItemVentaForm(forms.ModelForm):
    class Meta:
        model = ItemVenta
        fields = ['producto', 'cantidad']

ItemVentaFormSet = inlineformset_factory(
    Venta, ItemVenta,
    form=ItemVentaForm,
    extra=1,
    can_delete=False
)
