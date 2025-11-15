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


# 👇 Formset para manejar múltiples productos en una venta
ItemVentaFormSet = inlineformset_factory(
    Venta,
    ItemVenta,
    fields=['producto', 'cantidad', 'precio_unitario', 'subtotal'],
    extra=1,          # cantidad de formularios vacíos adicionales
    can_delete=True   # permite eliminar filas
)
