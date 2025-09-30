from django.db import models
from diagrama.models import Tabla, Diagrama

# Create your models here.

class Relacion(models.Model):
    TIPOS_RELACION = [
        ('herencia', 'Herencia'),
        ('asociacion', 'Asociación'),
        ('agregacion', 'Agregación'),
        ('composicion', 'Composición'),
    ]

    tipo_relacion = models.CharField(max_length=15, choices=TIPOS_RELACION)
    tabla_origen = models.ForeignKey(Tabla, related_name='relaciones_origen', on_delete=models.CASCADE)
    tabla_destino = models.ForeignKey(Tabla, related_name='relaciones_destino', on_delete=models.CASCADE)
    cardinalidad_origen = models.CharField(max_length=10, default='0')
    cardinalidad_destino = models.CharField(max_length=10, default='1')
    diagrama_id = models.ForeignKey(Diagrama, on_delete=models.CASCADE, null=True, default= None)
    tabla_hijo = models.ForeignKey(Tabla, on_delete=models.CASCADE, null=True, blank=True, default=None)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

