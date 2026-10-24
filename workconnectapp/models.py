from django.db import models

# Create your models here.
class Alumno(models.Model):
    nombre = models.CharField(max_length=100)
    rol = models.CharField(max_length=11)
    fecha_ingreso = models.DateField()

    def __str__(self):
        return self.nombre