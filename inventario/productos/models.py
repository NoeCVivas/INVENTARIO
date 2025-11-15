from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from PIL import Image
import os

# Validación de tamaño de imagen
def validate_image_size(image):
    filesize = image.file.size
    megabyte_limit = 5.0
    if filesize > megabyte_limit * 1024 * 1024:
        raise ValidationError(f"El tamaño máximo permitido es de {megabyte_limit} MB")

# Ruta dinámica para guardar imágenes
def get_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.sku}.{ext}"  # Usamos el SKU como nombre de archivo
    return os.path.join("productos", filename)

class Producto(models.Model):
    nombre = models.CharField("Nombre", max_length=50)
    descripcion = models.CharField("Descripción", max_length=200)
    precio = models.DecimalField("Precio", max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField("Stock", default=0)
    stock_minimo = models.IntegerField("Stock Mínimo", default=5)
    sku = models.CharField(
        "SKU",
        max_length=50,
        unique=True,
        blank=False,
        help_text="Debe coincidir con el nombre del archivo de imagen (sin extensión)"
    )
    imagen = models.ImageField(
        "Imagen",
        upload_to=get_image_path,
        validators=[validate_image_size],
        blank=True,
        null=True,
        help_text="Formatos permitidos: jpg, png, gif. Tamaño máximo: 5MB"
    )
    fecha_creacion = models.DateTimeField("Fecha de creación", auto_now_add=True)
    fecha_actualizacion = models.DateTimeField("Fecha de actualización", auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Redimensionar imagen si es muy grande
        if self.imagen and hasattr(self.imagen, 'path'):
            try:
                img = Image.open(self.imagen.path)
                img.verify()  # valida formato
                img = Image.open(self.imagen.path)  # reabrir para modificar
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.imagen.path)
            except Exception as e:
                print(f"Error al procesar la imagen: {e}")

    @property
    def necesita_reposicion(self):
        return self.stock < self.stock_minimo


class MovimientoStock(models.Model):
    TIPO_CHOICES = [
        ("entrada", "Entrada"),
        ("salida", "Salida"),
        ("ajuste", "Ajuste"),
    ]

    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="movimientos",
        verbose_name="Producto"
    )
    tipo = models.CharField("Tipo", max_length=50, choices=TIPO_CHOICES)
    cantidad = models.IntegerField("Cantidad")
    motivo = models.CharField("Motivo", max_length=200, blank=True, null=True)
    fecha = models.DateTimeField("Fecha", default=timezone.now)
    usuario = models.CharField("Usuario", max_length=50)

    class Meta:
        verbose_name = "Movimiento de Stock"
        verbose_name_plural = "Movimientos de Stock"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.producto.nombre} - {self.get_tipo_display()} - {self.cantidad}"
