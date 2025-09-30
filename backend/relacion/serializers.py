from rest_framework import serializers
from .models import Relacion

class RelacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relacion
        fields = '__all__'
        