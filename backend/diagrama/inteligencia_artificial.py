# diagrama/inteligencia_artificial.py
import os
import tempfile
import base64
import json
import requests
from django.conf import settings
from diagrama.models import Diagrama, Tabla, Atributo
from relacion.models import Relacion
from django.db import transaction

from vosk import Model, KaldiRecognizer
import wave
from pydub import AudioSegment


def procesar_comando_ia(audio_base64=None, texto=None, diagrama_id=None, user=None):
    """
    Función principal que procesa comandos de IA (audio o texto)
    """
    print("=" * 60)
    print("🎯 INICIO procesar_comando_ia")
    print(f"Audio: {bool(audio_base64)}, Texto: {texto}, Diagrama: {diagrama_id}")
    
    try:
        # Paso 1: Obtener texto
        if audio_base64:
            print("🎤 Transcribiendo audio...")
            texto_transcrito = transcribir_audio_base64(audio_base64)
            if not texto_transcrito:
                print("❌ Transcripción falló")
                return {
                    "success": False,
                    "mensaje": "No se pudo transcribir el audio"
                }
            texto_comando = texto_transcrito
            print(f"✅ Transcrito: {texto_comando}")
        elif texto:
            texto_comando = texto
            print(f"📝 Usando texto directo: {texto_comando}")
        else:
            print("❌ No hay audio ni texto")
            return {
                "success": False,
                "mensaje": "Debes proporcionar audio o texto"
            }
        
        # Paso 2: Interpretar con Ollama
        print("🤖 Interpretando con Ollama...")
        comando_interpretado = interpretar_con_ollama(texto_comando)
        
        if not comando_interpretado:
            print("❌ Ollama no devolvió comando válido")
            return {
                "success": False,
                "mensaje": "No se pudo interpretar el comando"
            }
        
        print(f"✅ Comando interpretado: {comando_interpretado}")
        
        # Paso 3: Ejecutar
        print("⚙️ Ejecutando comando...")
        resultado = ejecutar_comando(
            comando=comando_interpretado,
            diagrama_id=diagrama_id,
            user=user
        )
        
        print(f"✅ Resultado: {resultado}")
        print("=" * 60)
        return resultado
        
    except Exception as e:
        print(f"❌ ERROR GENERAL: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        return {
            "success": False,
            "mensaje": f"Error procesando comando: {str(e)}"
        }

def transcribir_audio_base64(audio_base64):
    """
    Convierte audio en base64 a texto usando Vosk
    """
    try:
        audio_data = base64.b64decode(audio_base64)
        
        with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_audio:
            temp_audio.write(audio_data)
            temp_audio_path = temp_audio.name
        
        wav_path = convertir_a_wav(temp_audio_path)
        
        # AJUSTE PARA DOCKER: Ruta del modelo Vosk
        model_path = os.path.join("/app", "vosk-model-small-es-0.42")
        
        if not os.path.exists(model_path):
            raise Exception(f"Modelo Vosk no encontrado en {model_path}")
        
        model = Model(model_path)
        wf = wave.open(wav_path, "rb")
        rec = KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)
        
        texto_completo = ""
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                texto_completo += result.get("text", "") + " "
        
        result = json.loads(rec.FinalResult())
        texto_completo += result.get("text", "")
        
        os.unlink(temp_audio_path)
        os.unlink(wav_path)
        
        return texto_completo.strip()
        
    except Exception as e:
        print(f"Error transcribiendo audio: {e}")
        return None


def convertir_a_wav(audio_path):
    """Convierte cualquier audio a WAV mono 16kHz"""
    try:
        audio = AudioSegment.from_file(audio_path)
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(16000)
        
        wav_path = audio_path.replace(os.path.splitext(audio_path)[1], '.wav')
        audio.export(wav_path, format="wav")
        
        return wav_path
    except Exception as e:
        raise Exception(f"Error convirtiendo audio: {str(e)}")


def interpretar_con_ollama(texto_usuario):
    """
    Interpreta el comando usando Ollama
    """
    ollama_url = os.getenv('OLLAMA_URL', 'http://ollama:11434')
    
    system_prompt = """Eres un asistente experto en crear diagramas de bases de datos.

Analiza el texto del usuario y responde SOLO con un JSON válido:

{
  "accion": "tipo_de_accion",
  "parametros": {...}
}

ACCIONES DISPONIBLES:

1. crear_tabla_con_atributos
   parametros: {
     "nombre_tabla": "string",
     "atributos": [
       {"nombre": "id", "tipo": "INT"},
       {"nombre": "email", "tipo": "VARCHAR(255)"}
     ]
   }

2. crear_relacion
   parametros: {
     "tabla_origen": "string",
     "tabla_destino": "string",
     "tipo_relacion": "1:1" | "1:N" | "N:M"
   }

3. eliminar_tabla
   parametros: {"tabla_nombre": "string"}

4. eliminar_relacion
   parametros: {
     "tabla_origen": "string",
     "tabla_destino": "string"
   }

REGLAS:
- SIEMPRE incluir atributo "id" de tipo INT como primer atributo
- Tipos válidos: INT, VARCHAR(n), TEXT, DATE, DATETIME, BOOLEAN, DECIMAL(n,m)
- Si el usuario no especifica tipo, usar VARCHAR(255)

Si no entiendes: {"accion": "error", "mensaje": "explicación"}
"""

    try:
        print(f"🤖 Enviando a Ollama: {texto_usuario}")
        
        response = requests.post(
            f'{ollama_url}/api/generate',
            json={
                "model": "llama3.2:3b",
                "prompt": f"{system_prompt}\n\nUSUARIO: {texto_usuario}\n\nRESPUESTA JSON:",
                "stream": False,
                "temperature": 0.1,
                "format": "json"
            },
            timeout=60
        )
        
        print(f"📡 Status Ollama: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Error de Ollama: {response.text}")
            return None
        
        resultado = response.json()
        print(f"📦 Respuesta completa de Ollama: {json.dumps(resultado, indent=2)}")
        
        texto_respuesta = resultado.get('response', '').strip()
        print(f"📝 Texto extraído: {texto_respuesta}")
        
        if not texto_respuesta:
            print("⚠️ Ollama no devolvió texto")
            return None
        
        comando_json = json.loads(texto_respuesta)
        print(f"✅ JSON interpretado: {comando_json}")
        
        return comando_json
        
    except requests.exceptions.ConnectionError:
        print(f"❌ No se pudo conectar a Ollama en {ollama_url}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error decodificando JSON: {e}")
        print(f"Texto recibido: {texto_respuesta}")
        return None
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return None

# ... [resto del código de ejecutar_comando igual que antes] ...
def ejecutar_comando(comando, diagrama_id, user):
    """
    Ejecuta el comando interpretado por la IA
    """
    # Mapeo de tipos SQL a tipos Django
    TIPO_MAPPING = {
        'INT': 'integer',
        'SMALLINT': 'smallint',
        'BIGINT': 'bigint',
        'FLOAT': 'float',
        'DECIMAL': 'decimal',
        'VARCHAR': 'char',
        'CHAR': 'char',
        'TEXT': 'text',
        'TINYINT': 'boolean',
        'BOOLEAN': 'boolean',
        'DATE': 'date',
        'DATETIME': 'datetime',
        'TIME': 'time',
        'JSON': 'json',
    }
    
    try:
        accion = comando.get('accion')
        parametros = comando.get('parametros', {})
        
        print(accion, parametros)
        
        if accion == 'error':
            return {
                "success": False,
                "mensaje": parametros.get('mensaje', 'No se entendió el comando')
            }
        
        diagrama = Diagrama.objects.get(id=diagrama_id)
        
        # CREAR TABLA CON ATRIBUTOS
        if accion == 'crear_tabla_con_atributos':
            nombre_tabla = parametros.get('nombre_tabla')
            atributos = parametros.get('atributos', [])
            
            if not nombre_tabla:
                return {
                    "success": False,
                    "mensaje": "No se especificó el nombre de la tabla"
                }
            
            tabla = Tabla.objects.create(
                nombre=nombre_tabla,
                diagrama_id_id=diagrama_id
            )
            
            atributos_creados = []
            for atributo_data in atributos:
                nombre_attr = atributo_data.get('nombre')
                tipo_sql = atributo_data.get('tipo', 'VARCHAR(255)')
                
                # Extraer tipo base (sin paréntesis)
                tipo_base = tipo_sql.split('(')[0].strip().upper()
                
                # Mapear a tipo Django
                tipo_django = TIPO_MAPPING.get(tipo_base, 'char')
                
                # Extraer rango si existe
                rango = None
                if '(' in tipo_sql:
                    rango = tipo_sql.split('(')[1].split(')')[0]
                
                # Detectar primary key
                is_primary = nombre_attr.lower() in ['id', 'pk']
                
                atributo = Atributo.objects.create(
                    nombre=nombre_attr,
                    tipo_dato=tipo_django,
                    rango=rango,
                    tabla_id_id=tabla.id,
                    primary_key=is_primary,
                    auto_increment=is_primary,
                    is_nullable=not is_primary
                )
                atributos_creados.append(atributo.nombre)
            
            return {
                "success": True,
                "mensaje": f"Tabla '{nombre_tabla}' creada con {len(atributos_creados)} atributos",
                "cambios": {
                    "tipo": "crear_tabla",
                    "tabla_id": tabla.id,
                    "tabla_nombre": nombre_tabla,
                    "atributos": atributos_creados
                }
            }
        
        # CREAR RELACIÓN
        elif accion == 'crear_relacion':
            tabla_origen_nombre = parametros.get('tabla_origen')
            tabla_destino_nombre = parametros.get('tabla_destino')
            tipo_relacion = parametros.get('tipo_relacion', '1:N')
            
            try:
                tabla_origen = Tabla.objects.get(
                    nombre__iexact=tabla_origen_nombre,
                    diagrama_id_id=diagrama_id
                )
                tabla_destino = Tabla.objects.get(
                    nombre__iexact=tabla_destino_nombre,
                    diagrama_id_id=diagrama_id
                )
            except Tabla.DoesNotExist:
                return {
                    "success": False,
                    "mensaje": f"No se encontraron las tablas '{tabla_origen_nombre}' o '{tabla_destino_nombre}'"
                }
            
            relacion = Relacion.objects.create(
                tabla_origen_id=tabla_origen.id,
                tabla_destino_id=tabla_destino.id,
                tipo_relacion=tipo_relacion,
                diagrama_id_id=diagrama_id
            )
            
            return {
                "success": True,
                "mensaje": f"Relación {tipo_relacion} creada entre '{tabla_origen_nombre}' y '{tabla_destino_nombre}'",
                "cambios": {
                    "tipo": "crear_relacion",
                    "relacion_id": relacion.id,
                    "tabla_origen": tabla_origen_nombre,
                    "tabla_destino": tabla_destino_nombre,
                    "tipo_relacion": tipo_relacion
                }
            }
        
        # ELIMINAR TABLA
        elif accion == 'eliminar_tabla':
            tabla_nombre = parametros.get('tabla_nombre')
            
            try:
                tabla = Tabla.objects.get(
                    nombre__iexact=tabla_nombre,
                    diagrama_id_id=diagrama_id
                )
                tabla_id = tabla.id
                tabla.delete()
                
                return {
                    "success": True,
                    "mensaje": f"Tabla '{tabla_nombre}' eliminada",
                    "cambios": {
                        "tipo": "eliminar_tabla",
                        "tabla_id": tabla_id,
                        "tabla_nombre": tabla_nombre
                    }
                }
            except Tabla.DoesNotExist:
                return {
                    "success": False,
                    "mensaje": f"No se encontró la tabla '{tabla_nombre}'"
                }
        
        # ELIMINAR RELACIÓN
        elif accion == 'eliminar_relacion':
            tabla_origen_nombre = parametros.get('tabla_origen')
            tabla_destino_nombre = parametros.get('tabla_destino')
            
            try:
                tabla_origen = Tabla.objects.get(
                    nombre__iexact=tabla_origen_nombre,
                    diagrama_id_id=diagrama_id
                )
                tabla_destino = Tabla.objects.get(
                    nombre__iexact=tabla_destino_nombre,
                    diagrama_id_id=diagrama_id
                )
                
                relacion = Relacion.objects.get(
                    tabla_origen_id=tabla_origen.id,
                    tabla_destino_id=tabla_destino.id,
                    diagrama_id_id=diagrama_id
                )
                
                relacion_id = relacion.id
                relacion.delete()
                
                return {
                    "success": True,
                    "mensaje": f"Relación eliminada entre '{tabla_origen_nombre}' y '{tabla_destino_nombre}'",
                    "cambios": {
                        "tipo": "eliminar_relacion",
                        "relacion_id": relacion_id
                    }
                }
            except (Tabla.DoesNotExist, Relacion.DoesNotExist):
                return {
                    "success": False,
                    "mensaje": "No se encontró la relación especificada"
                }
        
        else:
            return {
                "success": False,
                "mensaje": f"Acción desconocida: {accion}"
            }
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "mensaje": f"Error ejecutando comando: {str(e)}"
        }
        
def normalizar_diagrama(diagrama_id):
    """
    Analiza el diagrama y aplica normalización automática con IA
    """
    try:
        # Obtener todas las tablas del diagrama
        tablas = Tabla.objects.filter(diagrama_id_id=diagrama_id)
        
        if not tablas.exists():
            return {
                "success": False,
                "mensaje": "No hay tablas en el diagrama para normalizar"
            }
        
        # Construir contexto para la IA
        diagrama_info = []
        for tabla in tablas:
            atributos = Atributo.objects.filter(tabla_id=tabla.id)
            attrs_info = []
            for attr in atributos:
                attrs_info.append({
                    "nombre": attr.nombre,
                    "tipo": attr.tipo_dato,
                    "primary_key": attr.primary_key,
                    "is_nullable": attr.is_nullable
                })
            diagrama_info.append({
                "tabla": tabla.nombre,
                "atributos": attrs_info
            })
        
        # Prompt para la IA
        prompt = f"""Analiza este diagrama de base de datos y aplica normalización hasta 3FN.

DIAGRAMA ACTUAL:
{json.dumps(diagrama_info, indent=2, ensure_ascii=False)}

INSTRUCCIONES:
1. Identifica dependencias funcionales
2. Detecta violaciones de 1FN, 2FN, 3FN
3. Propón SOLO nuevas tablas necesarias
4. NO modifiques tablas ya normalizadas

REGLAS:
- Crea tablas solo si hay violaciones claras
- Usa tipos: INT, VARCHAR(255), DATE, etc.
- Para relaciones: "1:N" o "N:M"

Responde SOLO JSON válido:
{{
  "analisis": "análisis breve",
  "violaciones": ["problema1", "problema2"],
  "comandos": [
    {{
      "accion": "crear_tabla_con_atributos",
      "parametros": {{
        "nombre_tabla": "nueva_tabla",
        "atributos": [
          {{"nombre": "id", "tipo": "INT"}},
          {{"nombre": "campo", "tipo": "VARCHAR(255)"}}
        ]
      }}
    }},
    {{
      "accion": "crear_relacion",
      "parametros": {{
        "tabla_origen": "tabla1",
        "tabla_destino": "tabla2",
        "tipo_relacion": "1:N"
      }}
    }}
  ]
}}

Si está normalizado: comandos: []"""

        # Llamar a Ollama
        response = requests.post(
            'http://ollama:11434/api/generate',
            json={
                'model': 'llama3.2:3b',
                'prompt': prompt,
                'stream': False,
                'format': 'json'
            },
            timeout=90
        )
        
        if response.status_code != 200:
            return {
                "success": False,
                "mensaje": "Error al comunicarse con el servicio de IA"
            }
        
        respuesta_ia = response.json()['response']
        
        # Limpiar respuesta
        respuesta_ia = respuesta_ia.strip()
        if respuesta_ia.startswith('```json'):
            respuesta_ia = respuesta_ia[7:]
        if respuesta_ia.endswith('```'):
            respuesta_ia = respuesta_ia[:-3]
        respuesta_ia = respuesta_ia.strip()
        
        resultado = json.loads(respuesta_ia)
        
        # Si no hay comandos, ya está normalizado
        if not resultado.get('comandos'):
            return {
                "success": True,
                "mensaje": "El diagrama ya está normalizado correctamente",
                "analisis": resultado.get('analisis', ''),
                "violaciones": [],
                "cambios_realizados": 0
            }
        
        # Ejecutar comandos en transacción
        resultados_comandos = []
        with transaction.atomic():
            for comando in resultado.get('comandos', []):
                resultado_cmd = ejecutar_comando(comando, diagrama_id, None)
                resultados_comandos.append(resultado_cmd)
        
        # Contar cambios exitosos
        cambios_exitosos = sum(1 for r in resultados_comandos if r.get('success'))
        
        return {
            "success": True,
            "mensaje": f"Normalización completada. Se realizaron {cambios_exitosos} cambios.",
            "analisis": resultado.get('analisis', ''),
            "violaciones": resultado.get('violaciones', []),
            "cambios_realizados": cambios_exitosos,
            "detalles": resultados_comandos
        }
        
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "mensaje": f"Error al interpretar respuesta de IA: {str(e)}"
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "mensaje": f"Error en normalización: {str(e)}"
        }