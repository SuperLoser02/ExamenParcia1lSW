from django.db import models
from diagrama.models import Diagrama
from django.conf import settings

# Create your models here.

class Colaborador(models.Model):
    permiso = models.CharField(max_length=50)
    estado = models.BooleanField(default=False)
    diagrama_id = models.ForeignKey(Diagrama, on_delete=models.CASCADE)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user_id.username} - {self.diagrama_id.nombre} - {self.permiso}"
    
    

