from django import forms
from django.forms import inlineformset_factory
from .models import Venta, ItemVenta

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['cliente', 'fecha', 'medio_pago']

    # Campos adicionales para tarjeta
    numero_tarjeta = forms.CharField(
        label="Número de tarjeta",
        max_length=16,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '16 dígitos'})
    )
    codigo_seguridad = forms.CharField(
        label="Código de seguridad",
        max_length=4,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'CVV'})
    )
    fecha_vencimiento = forms.CharField(
        label="Fecha de vencimiento",
        max_length=5,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'MM/AA'})
    )

    def clean(self):
        cleaned_data = super().clean()
        medio_pago = cleaned_data.get("medio_pago")

        # Validación solo si el medio de pago es tarjeta
        if medio_pago in ["credito", "debito"]:
            if not cleaned_data.get("numero_tarjeta"):
                self.add_error("numero_tarjeta", "Debe ingresar el número de tarjeta.")
            if not cleaned_data.get("codigo_seguridad"):
                self.add_error("codigo_seguridad", "Debe ingresar el código de seguridad.")
            if not cleaned_data.get("fecha_vencimiento"):
                self.add_error("fecha_vencimiento", "Debe ingresar la fecha de vencimiento.")

        return cleaned_data


# 👇 Form personalizado para ItemVenta
class ItemVentaForm(forms.ModelForm):
    class Meta:
        model = ItemVenta
        fields = ['producto', 'cantidad', 'precio_unitario', 'subtotal']
        widgets = {
            'producto': forms.Select(attrs={'class': 'producto'}),
            'cantidad': forms.NumberInput(attrs={'class': 'cantidad'}),
            'precio_unitario': forms.TextInput(attrs={'class': 'precio-unitario'}),
            'subtotal': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

# 👇 Formset usando el form personalizado
ItemVentaFormSet = inlineformset_factory(
    Venta,
    ItemVenta,
    form=ItemVentaForm,
    extra=1,
    can_delete=True
)
