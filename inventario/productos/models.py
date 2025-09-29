from django.db import models
import os
import uuid
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from PIL import Image   
from django.utils import timezone

def validate_image_size(image):
    filesize = image.file.size
    megabyte_limit = 5.0
    if filesize > megabyte_limit * 1024 * 1024:
        raise ValidationError(f"El tamaño máximo de la imagen es {megabyte_limit}MB")
    
def get_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('productos/', filename)    

class Producto(models.Model):

    nombre = models.CharField("Nombre", max_length=50)
    descripcion = models.CharField("Descripcion", max_length=200)
    precio = models.DecimalField("Precio", max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    stock = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=5, verbose_name="Stock Minimo")
    imagen = models.ImageField (
        "Imagen",
        upload_to=get_image_path, 
        validators=[validate_image_size],
        blank=True,
        null=True,      
        help_text="Formatos permitidos: jpg, png, gif.Tamaño maximo: 5MB."

    )

    fecha_creacion = models.DateTimeField("Fecha DE Creacion", auto_now=True, auto_now_add=True)
    fecha_creacion = models.DateTimeField("Fecha DE Creacion", auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']
      
    def __str__(self):
        return self.nombre  

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.imagen:
            try:
                img = Image.open(self.imagen.path)
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.imagen.path)
            except Exception as e:
                print(f"Error al procesar la imagen: {e}")


    @property
    def necesita_reposicion(self):
        return self.stock <= self.stock_minimo  

    class movimiento(models.TextChoices):

        TIPO_CHOICES = [
            ('ENTRADA', 'Entrada'),
            ('SALIDA', 'Salida'),
            ('AJUSTE', 'Ajuste'),
        ]          

        producto = models.ForeignKey('Producto', on_delete=models.CASCADE, related_name='movimientos')
        tipo = models.CharField("tipo", max_length=10, choices=TIPO_CHOICES)
        cantidad = models.IntegerField("Cantidad")
        motivo = models.CharField("Motivo", max_length=200, blank=True, null=True)
        fecha = models.DateTimeField("Fecha", default=timezone.now)
        usuario = models.CharField("Usuario", max_length=50)

    class Meta:
        verbose_name = "Movimiento"
        verbose_name_plural = "Movimientos de Stock"
        ordering = ['-fecha']   

    def __str__(self):
        return f"{self.tipo} - {self.producto.nombre} - {self.cantidad}"     