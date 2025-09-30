from django.db import models
from django.conf import settings




# Create your models here.
class Diagrama(models.Model):
    nombre = models.CharField(max_length=100)
    estado = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nombre
    
class Tabla(models.Model):
    nombre = models.CharField(max_length=100)
    diagrama_id = models.ForeignKey(Diagrama, on_delete=models.CASCADE)
    pos_x = models.IntegerField(default=0)
    pos_y = models.IntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nombre
    
    def extraer_primary_key(self):
        primary_key = Atributo.objects.filter(tabla_id=self, primary_key=True)
        return primary_key
TIPOS_MYSQL = [
    ("integer", "INT"),
    ("smallint", "SMALLINT"),
    ("bigint", "BIGINT"),
    ("float", "FLOAT"),
    ("decimal", "DECIMAL"),
    ("char", "VARCHAR"),
    ("text", "TEXT"),
    ("boolean", "TINYINT"),
    ("date", "DATE"),
    ("datetime", "DATETIME"),
    ("time", "TIME"),
    ("json", "JSON"),
]

class Atributo(models.Model):
    nombre = models.CharField(max_length=100)
    primary_key = models.BooleanField(default=False)
    is_nullable = models.BooleanField(default=False)
    tipo_dato = models.CharField(max_length=50,choices=TIPOS_MYSQL,default="integer")
    rango = models.CharField(max_length=100, blank=True, null=True)
    tabla_id = models.ForeignKey(Tabla, on_delete=models.CASCADE)
    auto_increment = models.BooleanField(default=False)
    solo_positivo = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    