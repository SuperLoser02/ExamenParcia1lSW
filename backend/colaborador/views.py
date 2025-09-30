from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Colaborador
from .serializers import ColaboradorSerializer
from diagrama.models import Diagrama
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your views here.
# mandar invitacion modo editor y vista
# aceptar invitacion

class ColaboradorViewSet(viewsets.ModelViewSet):
    serializer_class = ColaboradorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Colaborador.objects.all()
    
    @action(detail=False, methods=['POST'])
    def mandar_invitacion(self, request):
        diagrama_id = request.data.get('diagrama_id')
        username = request.data.get('username')
        permiso = request.data.get('permiso')
        user = request.user
        try:
            diagrama = Diagrama.objects.get(id=diagrama_id)
        except:
            return Response(f"El diagrama no exite: {diagrama_id}", status=400)
        if diagrama.user_id != user:
             return Response("Usted no es autor del diagrma", status=400)
        try:
            user_colaborador = User.objects.get(username=username)
        except:
            return Response("El usuario que invita no existe", status=400)
        
        if(permiso not in ['editar','vista']):
            return Response("Debe elegir entre: editar o vista")
        
        Colaborador.objects.get_or_create(
            permiso=permiso,
            diagrama_id=diagrama,         # ojo, pasa la instancia, no el id
            user_id=user_colaborador,     # idem
            estado=False
        )
        return Response("Invitacion ya mandada", status=200)

    
    @action(detail=False, methods=['GET'])
    def mostrar_invitacion(self, request):
        invitaciones = Colaborador.objects.filter(user_id=request.user, estado=False)
    
        data = []
        for invitacion in invitaciones:
            data.append({
                'id': invitacion.id,
                'permiso': invitacion.permiso,
                'estado': invitacion.estado,
                'diagrama_id': invitacion.diagrama_id.id,  # ← .id
                'diagrama_nombre': invitacion.diagrama_id.nombre,  # ← .nombre
                'user_id': invitacion.user_id.id,  # ← .id (IMPORTANTE)
                'user_username': invitacion.user_id.username,  # ← .username (IMPORTANTE)
                'fecha_creacion': invitacion.fecha_creacion,
                'fecha_modificacion': invitacion.fecha_modificacion,
            })
        return Response(data, status=200)
    
    @action(detail=False, methods=['PATCH'])
    def aceptar_invitacion(self, request):
        invitacion_id = request.data.get("invitacion_id")
        user = request.user
        respuesta = request.data.get("respuesta")

        try:
            colaboracion = Colaborador.objects.get(id=invitacion_id)
        except Colaborador.DoesNotExist:
            return Response("La invitación no existe", status=400)

    # Verificar que el usuario sea el destinatario
        if colaboracion.user_id != user:
            return Response("Usted no recibió esta invitación", status=403)

    # Verificar si ya fue aceptada antes
        if colaboracion.estado is True:
            return Response("La invitación ya fue aceptada y no puede modificarse", status=400)

    # Procesar la respuesta
        if respuesta is True:
            colaboracion.estado = True
            colaboracion.save()
            return Response("Invitación aceptada", status=200)
        elif respuesta is False:
            colaboracion.delete()
            return Response("Invitación rechazada", status=200)
        else:
            return Response("La respuesta tiene que ser booleana (true o false)", status=400)
        
    @action(detail=True, methods=['PATCH'])
    def eliminar_colaborador(self, request, pk=None):
        user = request.user
        username = request.data.get("username")
        try:
            colaboracion = self.get_object()
        except:
            return Response({"error": "La colaboracion no existe"}, status=404)
        try:
            user_colaborador = User.objects.get(username=username)
        except:
            return Response({"error": "No existe el usuario que colabora"}, status=403)
        diagrama = colaboracion.diagrama_id
        if(diagrama.user_id != user):
            return Response({"error": "No eres el autor del diagrama"}, status=403)
        if(colaboracion.user_id != user_colaborador):
            return Response({"error": f"{username} no colabora en este diagrama"}, status=403)
        colaboracion.delete()
        return Response("Colaboracion eliminada", status=200)
    
    @action(detail=False, methods=["get"])
    def mis_colaboracion(self, request):
        colaboraciones = Colaborador.objects.filter(user_id=request.user, estado=True)
        serializer = ColaboradorSerializer(colaboraciones, many=True)
        return Response(serializer.data, status=200)
    

        