from rest_framework import serializers
from .models import Diagrama, Tabla, Atributo

class DiagramaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diagrama
        fields = '__all__'
        
class TablaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tabla
        fields = '__all__'
        
class AtributoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Atributo
        fields = '__all__'