import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework.exceptions import ValidationError
from datetime import timezone

class DiagramaConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        from diagrama.models import Diagrama
        
        self.room_group_name = None
        self.editar = False
        self.user = self.scope.get('user')

        print(f"🔹 Connect: Usuario -> {self.user}")
        
        if not self.user or not self.user.is_authenticated:
            print("❌ Connect: Usuario no autenticado, cerrando socket")
            await self.close()
            return

        diagrama_id = self.scope['url_route']['kwargs']['diagrama_id']
        self.diagrama = await self.get_diagrama(diagrama_id)
        if not self.diagrama:
            print(f"❌ Connect: Diagrama {diagrama_id} no encontrado")
            await self.close()
            return

        usuarios_colab = await self.get_colaboradores_ids(diagrama_id)
        diagrama_user_id = await self.get_diagrama_user_id()

        if self.user.id == diagrama_user_id or self.user.id in usuarios_colab:
            self.room_group_name = f"diagrama_{self.diagrama.id}"
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            if self.user.id == diagrama_user_id:
                self.editar = True
            else:
                permisos = await self.get_permisos(self.diagrama.id, self.user.id)
                self.editar = "editar" in permisos

            await self.accept()
            print(f"✅ Usuario {self.user.id} conectado al diagrama {diagrama_id}")
        else:
            print("❌ Usuario sin permisos en este diagrama")
            await self.close()

    async def receive(self, text_data):
        if not getattr(self, 'diagrama', None) or not getattr(self, 'editar', False) or not self.diagrama.estado:
            return

        try:
            data = json.loads(text_data)
            accion = data.get("accion")
            payload = data.get("payload")
        except json.JSONDecodeError:
            await self.send_error("Formato JSON inválido")
            return

        if not accion or payload is None:
            await self.send_error("Formato JSON inválido")
            return

        acciones = {
            "tabla.agregar": self.agregar_tabla,
            "tabla.actualizar": self.actualizar_tabla,
            "tabla.eliminar": self.eliminar_tabla,
            "atributo.agregar": self.agregar_atributo,
            "atributo.actualizar": self.actualizar_atributo,
            "atributo.eliminar": self.eliminar_atributo,
            "relacion.agregar": self.agregar_relacion,
            "relacion.actualizar": self.actualizar_relacion,
            "relacion.eliminar": self.eliminar_relacion,
            "tabla.getAll": self.get_all_tablas,
            "relacion.getAll": self.get_all_relaciones,
            "atributo.getAll": self.get_all_atributos,
            "tabla.getById": self.get_tabla_por_id, 
            "generar.sql": self.generar_sql,           # ← NUEVO
            "generar.springboot": self.generar_springboot,
        }
        print('🔹 Accion recibida:', accion, payload)
        funcion = acciones.get(accion)
        if funcion:
            try:
                result = await funcion(payload)
                if accion == "atributo.getAll":
                    result = {
                        "tabla_id": payload.get("tabla_id"),
                        "atributos": result
                    }
                if accion not in ['tabla.getAll', 'relacion.getAll', 'atributo.getAll', 'tabla.getById','generar.sql', 'generar.springboot']:
                    self.actualizar_diagrama(self.diagrama.id)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "broadcast_message",
                        "accion": accion,
                        "payload": result,
                        "diagrama_id": self.diagrama.id
                    }
                )
                
            except ValidationError as e:
                await self.send_error(e.detail)
            except Exception as e:
                await self.send_error(f"Error inesperado: {str(e)}")
        else:
            await self.send_error(f"Acción desconocida: {accion}")

    async def broadcast_message(self, event):
        await self.send(text_data=json.dumps({
            "accion": event["accion"],
            "payload": event["payload"],
            "diagrama_id": event.get("diagrama_id")
        }))

    async def send_error(self, message):
        await self.send(text_data=json.dumps({"error": message}))

    async def disconnect(self, close_code):
        print(f"🔹 Disconnect: Usuario {self.user} Close code {close_code}")
        if self.room_group_name:
            try:
                await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
                self.room_group_name = None
            except Exception as e:
                print(f"⚠️ Disconnect Error: {e}")

    # ===================== Métodos DB seguros =====================

    @database_sync_to_async
    def get_diagrama_user_id(self):
        return self.diagrama.user_id_id

    @database_sync_to_async
    def get_diagrama(self, diagrama_id):
        from diagrama.models import Diagrama
        try:
            return Diagrama.objects.get(id=diagrama_id)
        except Diagrama.DoesNotExist:
            return None
    
    @database_sync_to_async
    def get_all_tablas(self, payload):
        from diagrama.models import Tabla
        from diagrama.serializers import TablaSerializer
        diagrama_id = payload.get("diagrama_id")
        tablas = Tabla.objects.filter(diagrama_id__id=diagrama_id)
        return TablaSerializer(tablas, many=True).data
    
    @database_sync_to_async
    def get_all_atributos(self, payload):
        from diagrama.models import Atributo
        from diagrama.serializers import AtributoSerializer
        #print(payload)
        tabla_id = payload.get("tabla_id")
        #print(tabla_id)
        atributos = Atributo.objects.filter(tabla_id__id=tabla_id)
        #print(atributos)
        a = AtributoSerializer(atributos, many=True).data
        #print(a)
        return a

    @database_sync_to_async
    def get_permisos(self, diagrama_id, user_id):
        from colaborador.models import Colaborador
        return list(
            Colaborador.objects.filter(diagrama_id=diagrama_id, user_id=user_id)
            .values_list("permiso", flat=True)
        )
        
    @database_sync_to_async
    def get_colaboradores_ids(self, diagrama_id):
        from colaborador.models import Colaborador
        return list(
            Colaborador.objects.filter(diagrama_id=diagrama_id)
            .values_list("user_id", flat=True)
        )


    # ===================== TABLA =====================
    @database_sync_to_async
    def agregar_tabla(self, payload):
        from diagrama.serializers import TablaSerializer
        serializer = TablaSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data

    @database_sync_to_async
    def actualizar_tabla(self, payload):
        from diagrama.models import Tabla
        from diagrama.serializers import TablaSerializer
        try:
            tabla = Tabla.objects.get(id=payload.get("id"))
        except Tabla.DoesNotExist:
            raise ValidationError("La tabla no existe")
        serializer = TablaSerializer(tabla, data=payload, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data

    @database_sync_to_async
    def eliminar_tabla(self, payload):
        from diagrama.models import Tabla
        try:
            tabla = Tabla.objects.get(id=payload.get("id"))
            tabla.delete()
            return {"status": "ok"}
        except Tabla.DoesNotExist:
            raise ValidationError("La tabla no existe")
        
    @database_sync_to_async
    def get_tabla_por_id(self, payload):
        from diagrama.models import Tabla
        from diagrama.serializers import TablaSerializer, AtributoSerializer
        tabla_id = payload.get("id")
        if not tabla_id:
            return None
        try:
            tabla = Tabla.objects.get(id=tabla_id)
            # Serializamos la tabla
            data = TablaSerializer(tabla).data

            # Opcional: incluir atributos en la respuesta para refrescar todo
            from diagrama.models import Atributo
            atributos = Atributo.objects.filter(tabla_id=tabla.id)
            data["atributos"] = AtributoSerializer(atributos, many=True).data

            return data
        except Tabla.DoesNotExist:
            return None

    # ===================== ATRIBUTO =====================
    @database_sync_to_async
    def agregar_atributo(self, payload):
        from diagrama.serializers import AtributoSerializer
        #print("Payload:", payload )
        serializer = AtributoSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        #print("este es el serializer: ", serializer)
        return serializer.data

    @database_sync_to_async
    def actualizar_atributo(self, payload):
        from diagrama.models import Atributo
        from diagrama.serializers import AtributoSerializer
        try:
            atributo = Atributo.objects.get(id=payload.get("id"))
        except Atributo.DoesNotExist:
            raise ValidationError("El atributo no existe")
        serializer = AtributoSerializer(atributo, data=payload, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data

    @database_sync_to_async
    def eliminar_atributo(self, payload):
        from diagrama.models import Atributo
        try:
            atributo = Atributo.objects.get(id=payload.get("id"))
            tabla_id = atributo.tabla_id
            atributo.delete()
            return {"status": "ok", "id": payload.get("id"), "tabla_id": tabla_id.id}
        except Atributo.DoesNotExist:
            raise ValidationError("El atributo no existe")

    # ===================== RELACION =====================
    @database_sync_to_async
    def get_all_relaciones(self, payload):
        from relacion.models import Relacion
        from relacion.serializers import RelacionSerializer
        diagrama_id = payload.get("diagrama_id")
        relaciones = Relacion.objects.filter(diagrama_id__id=diagrama_id)
        #print(atributos)
        a = RelacionSerializer(relaciones, many=True).data
        #print(a)
        return a
            
    @database_sync_to_async
    def agregar_relacion(self, payload):
        from relacion.serializers import RelacionSerializer
        #print("confirmado")
        serializer = RelacionSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        print(serializer)
        return serializer.data

    @database_sync_to_async
    def actualizar_relacion(self, payload):
        from relacion.models import Relacion
        from relacion.serializers import RelacionSerializer
        try:
            relacion = Relacion.objects.get(id=payload.get("id"))
        except Relacion.DoesNotExist:
            raise ValidationError("La relación no existe")
        serializer = RelacionSerializer(relacion, data=payload, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data

    @database_sync_to_async
    def eliminar_relacion(self, payload):
        from relacion.models import Relacion
        try:
            relacion = Relacion.objects.get(id=payload.get("id"))
            relacion.delete()
            return {"status": "ok"}
        except Relacion.DoesNotExist:
            raise ValidationError("La relación no existe")

    @database_sync_to_async
    def actualizar_diagrama(diagrama_id):
        from diagrama.models import Diagrama
        diagrama = Diagrama.objects.get(id=diagrama_id)
        diagrama.save(update_fields=["fecha_modificacion"])
        return None
    
    # ==================== GENERAR SQL ====================
    async def generar_sql(self, payload):
        diagrama_id = payload.get("diagrama_id")
        
        # Llamar a la función SQL de forma síncrona
        sql_content = await self.run_sql_generation(diagrama_id)
        
        return {
            "tipo": "archivo",
            "formato": "sql",
            "contenido": sql_content,
            "nombre_archivo": f"{self.diagrama.nombre}.sql"
        }
    
    @database_sync_to_async
    def run_sql_generation(self, diagrama_id):
        from script.generar_script import sql  # Función auxiliar
        return sql(diagrama_id)

    # ==================== GENERAR SPRING BOOT ====================
    async def generar_springboot(self, payload):
        diagrama_id = payload.get("diagrama_id")
        
        # Generar el ZIP
        zip_data = await self.run_springboot_generation(diagrama_id)
        
        return {
            "tipo": "archivo",
            "formato": "zip",
            "contenido": zip_data,  # Base64 encoded
            "nombre_archivo": f"{self.diagrama.nombre}_springboot.zip"
        }
    
    @database_sync_to_async
    def run_springboot_generation(self, diagrama_id):
        from script.generar_script import spring_boot  # Función auxiliar
        return spring_boot(diagrama_id)