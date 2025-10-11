from django.db import models

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    documento = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    direccion = models.TextField()

    def __str__(self):
        return f"{self.apellido}, {self.nombre} ({self.documento})"
