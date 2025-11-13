from django import forms
from django.forms import inlineformset_factory
from .models import Venta, ItemVenta
from productos.models import Producto
from datetime import date

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['cliente', 'medio_pago', 'fecha']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control w-50'}),
            'medio_pago': forms.Select(attrs={
                'class': 'form-control w-25',
                'id': 'id_medio_pago'
            }),
            'fecha': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control w-25'
            }),
        }

class ItemVentaForm(forms.ModelForm):
    class Meta:
        model = ItemVenta
        fields = ['producto', 'cantidad', 'precio_unitario']
        widgets = {
            'producto': forms.Select(attrs={
                'class': 'form-control producto'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control cantidad',
                'min': 1
            }),
            'precio_unitario': forms.NumberInput(attrs={
                'readonly': 'readonly',
                'class': 'form-control precio-unitario'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].queryset = Producto.objects.filter(stock__gt=0)

    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        cantidad = cleaned_data.get('cantidad')

        if not producto:
            raise forms.ValidationError("Debe seleccionar un producto.")
        if not cantidad or cantidad <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor a cero.")
        return cleaned_data

ItemVentaFormSet = inlineformset_factory(
    Venta, ItemVenta,
    form=ItemVentaForm,
    extra=1,
    can_delete=True
)
