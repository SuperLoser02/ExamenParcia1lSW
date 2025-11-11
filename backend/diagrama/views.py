# diagrama/views.py
from urllib import response
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Diagrama
from .serializers import DiagramaSerializer
from colaborador.models import Colaborador
from django.http import HttpResponse

class DiagramaViewSet(viewsets.ModelViewSet):
    serializer_class = DiagramaSerializer
    permission_classes = [IsAuthenticated]
    queryset = Diagrama.objects.all()

    # Endpoint para obtener solo los diagramas del usuario
    @action(detail=False, methods=['GET'])
    def get_mis_diagramas(self, request):
        user = request.user
        diagramas = Diagrama.objects.filter(user_id=user)
        serializer = DiagramaSerializer(diagramas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def ultimos_5_diagramas_modificados(self, request):
        user = request.user
        diagramas = Diagrama.objects.filter(user_id=user)
        colaboraciones = Colaborador.objects.filter(user_id=user).values_list("diagrama_id", flat=True)
        mis_colaboraciones = Diagrama.objects.filter(id__in=colaboraciones)
        diagramas_todo = diagramas.union(mis_colaboraciones)
        ultimos_5 = diagramas_todo.order_by('-fecha_modificacion')[:5]
        serializer = DiagramaSerializer(ultimos_5, many=True)
        return Response(serializer.data)


    # Endpoint para crear un diagrama
    @action(detail=False, methods=['POST'])
    def crear_diagrama(self, request):
        user = request.user
        nombre = request.data.get('nombre')
        if not nombre:
            return Response({"error": "El nombre es obligatorio"}, status=400)
        diagrama = Diagrama.objects.create(nombre=nombre, user_id=user)
        serializer = DiagramaSerializer(diagrama)
        return Response(serializer.data, status=201)

    # Endpoint para eliminar un diagrama
    @action(detail=True, methods=['DELETE'])
    def delete_diagrama(self, request, pk=None):
        user = request.user
        try:
            diagrama = self.get_object()
        except Diagrama.DoesNotExist:
            return Response({"error": "El diagrama no existe"}, status=404)
        if diagrama.user_id != user:
            return Response({"error": "No eres el autor del diagrama"}, status=403)
        diagrama.delete()
        return Response({"success": "Diagrama eliminado"}, status=200)

    # Endpoint para cambiar el nombre de un diagrama
    @action(detail=True, methods=['PATCH'])
    def cambiar_nombre(self, request, pk=None):
        nuevo_nombre = request.data.get('nuevo_nombre')
        user = request.user
        try:
            diagrama = self.get_object()
        except Diagrama.DoesNotExist:
            return Response({"error": "El diagrama no existe"}, status=404)
        if diagrama.user_id != user:
            return Response({"error": "No eres el autor del diagrama"}, status=403)
        diagrama.nombre = nuevo_nombre
        diagrama.save()
        return Response({"success": "Nombre cambiado"}, status=200)

    # Endpoint para cambiar el estado
    @action(detail=True, methods=['PATCH'])
    def cambiar_estado(self, request, pk=None):
        nuevo_estado = request.data.get('nuevo_estado')
        user = request.user
        try:
            diagrama = self.get_object()
        except Diagrama.DoesNotExist:
            return Response({"error": "El diagrama no existe"}, status=404)
        if diagrama.user_id != user:
            return Response({"error": "No eres el autor del diagrama"}, status=403)
        if not isinstance(nuevo_estado, bool):
            return Response({"error": "El estado debe ser booleano"}, status=400)
        diagrama.estado = nuevo_estado
        diagrama.save()
        return Response({"success": "Estado cambiado"}, status=200)


    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def quien_soy(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
        })
    
    
    # Endpoint para obtener diagramas donde el usuario es colaborador
    @action(detail=False, methods=['GET'])
    def diagramas_donde_soy_colaborador(self, request):
        user = request.user
        colaboraciones = Colaborador.objects.filter(user_id=user, estado=True).values_list("diagrama_id", flat=True)
        diagramas = Diagrama.objects.filter(id__in=colaboraciones)
        serializer = DiagramaSerializer(diagramas, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['GET'])
    def colaborares_de_un_diagrama(self, request, pk=None):
        try:
            diagrama = self.get_object()
        except:
            return Response({"error": "El diagrama no existe"}, status=404)
    
    # Obtener todos los colaboradores de ese diagrama
        colaboradores = Colaborador.objects.filter(diagrama_id=diagrama)
    
    # Extraer los usernames
        usernames = [c.user_id.username for c in colaboradores]
    
        return Response({"usernames": usernames})
    @action(detail=False, methods=["GET"])
    def mis_diagramas_todos(self, request):
        user = request.user

        # Diagramas creados por mí
        mis_diagramas = Diagrama.objects.filter(user_id=user)

        # Diagramas donde colaboro
        colaboraciones = Colaborador.objects.filter(user_id=user).values_list("diagrama_id", flat=True)
        mis_colaboraciones = Diagrama.objects.filter(id__in=colaboraciones)

        # Unimos ambos
        diagramas = mis_diagramas.union(mis_colaboraciones)

        # Si hay parámetro de búsqueda, filtramos por nombre

        serializer = self.get_serializer(diagramas, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=["PATCH"])
    def get_script(self, request, pk=None):
        from script.generar_script import sql
        try:
            diagrama = self.get_object()
        except:
            return Response({"error": "El diagrama no existe"}, status=404)
        
        script_sql = sql(diagrama.id)
        return Response({"script_sql": script_sql})

    @action(detail=True, methods=["PATCH"])
    def get_estructura(self, request, pk=None):
        from script.generar_script import generar_estructura, sql
        try:
            diagrama = self.get_object()
        except:
            return Response({"error": "El diagrama no existe"}, status=404)
        script_sql = generar_estructura(diagrama.id)
        sql = sql(script_sql)
        return Response({"estructura": sql})
    
    @action(detail=True, methods=["get"])
    def springboot(self, request, pk=None):
        from script.generar_script import spring_boot
        try:
            diagrama = self.get_object()
        except:
            return Response({"error": "El diagrama no existe"}, status=404)
        zip = spring_boot(diagrama.id)
        response = HttpResponse(zip, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=demo.zip'
        return response




# Testeo de estructuras para el backend y frontend
    @action(detail=True, methods=["GET"])
    def test_estructura_backend(self, request, pk=None):
        from script.generar_script import generar_estructura
        try:
            diagrama = self.get_object()
        except:
            return Response({"error": "El diagrama no existe"}, status=404)
        estructura = generar_estructura(diagrama.id)
        return Response({"estructura": estructura})
    
    @action(detail=True, methods=["GET"])
    def test_spring_boot_backend(self, request, pk=None):
        from script.generar_script import spring_boot
        try:
            diagrama = self.get_object()
        except:
            return Response({"error": "El diagrama no existe"}, status=404)
        zip = spring_boot(diagrama.id)
        response = HttpResponse(zip, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=demo.zip'
        return response
    
    @action(detail=True, methods=["GET"])
    def test_flutter_frontend(self, request, pk=None):
        from flutter.craer_flutter import flutter
        try:
            Diagrama = self.get_object()
        except:
            return Response({"error": "El diagrama no existe"}, status=404)
        zip = flutter(Diagrama.id)
        response = HttpResponse(zip, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=flutter_app.zip'
        return response
    
    @action(detail=True, methods=["GET"])
    def json_backend(self,request, pk=None):
        from script.generar_script import generar_json_backend
        try:
            diagrama = self.get_object()
        except:
            return Response({"error": "El diagrama no existe"}, status=404)
        json_estructura = generar_json_backend(diagrama.id)
        response = HttpResponse(json_estructura, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="json_backend_{diagrama.id}.txt"'
        return response
