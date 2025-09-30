# diagrama/inteligencia_artificial.py
import os
import tempfile
import base64
import json
import requests
from django.conf import settings
from diagrama.models import Diagrama, Tabla, Atributo
from relacion.models import Relacion

from vosk import Model, KaldiRecognizer
import wave
from pydub import AudioSegment


def procesar_comando_ia(audio_base64=None, texto=None, diagrama_id=None, user=None):
    """
    Función principal que procesa comandos de IA (audio o texto)
    """
    try:
        # Paso 1: Obtener texto
        if audio_base64:
            texto_transcrito = transcribir_audio_base64(audio_base64)
            if not texto_transcrito:
                return {
                    "success": False,
                    "mensaje": "No se pudo transcribir el audio"
                }
            texto_comando = texto_transcrito
        elif texto:
            texto_comando = texto
        else:
            return {
                "success": False,
                "mensaje": "Debes proporcionar audio o texto"
            }
        
        # Paso 2: Interpretar con Ollama
        comando_interpretado = interpretar_con_ollama(texto_comando)
        
        if not comando_interpretado:
            return {
                "success": False,
                "mensaje": "No se pudo interpretar el comando"
            }
        
        # Paso 3: Ejecutar
        resultado = ejecutar_comando(
            comando=comando_interpretado,
            diagrama_id=diagrama_id,
            user=user
        )
        
        return resultado
        
    except Exception as e:
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
    AJUSTE PARA DOCKER: URL de Ollama desde variable de entorno
    """
    
    # Obtener URL de Ollama desde settings o variable de entorno
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
- Para relaciones, detectar automáticamente el tipo por el contexto

EJEMPLOS:

"crea tabla usuarios con nombre y email"
→ {
  "accion": "crear_tabla_con_atributos",
  "parametros": {
    "nombre_tabla": "usuarios",
    "atributos": [
      {"nombre": "id", "tipo": "INT"},
      {"nombre": "nombre", "tipo": "VARCHAR(255)"},
      {"nombre": "email", "tipo": "VARCHAR(255)"}
    ]
  }
}

"relaciona usuarios con pedidos uno a muchos"
→ {
  "accion": "crear_relacion",
  "parametros": {
    "tabla_origen": "usuarios",
    "tabla_destino": "pedidos",
    "tipo_relacion": "1:N"
  }
}

Si no entiendes: {"accion": "error", "mensaje": "explicación"}
"""

    try:
        response = requests.post(
            f'{ollama_url}/api/generate',
            json={
                "model": "llama3.2:3b",
                "prompt": f"{system_prompt}\n\nUSUARIO: {texto_usuario}\n\nRESPUESTA JSON:",
                "stream": False,
                "temperature": 0.1,
                "format": "json"
            },
            timeout=60  # Más tiempo para Docker
        )
        
        if response.status_code != 200:
            print(f"Error de Ollama: {response.status_code}")
            return None
        
        resultado = response.json()
        texto_respuesta = resultado.get('response', '').strip()
        comando_json = json.loads(texto_respuesta)
        
        return comando_json
        
    except requests.exceptions.ConnectionError:
        print(f"No se pudo conectar a Ollama en {ollama_url}")
        return None
    except Exception as e:
        print(f"Error interpretando comando: {e}")
        return None


# ... [resto del código de ejecutar_comando igual que antes] ...
def ejecutar_comando(comando, diagrama_id, user):
    # ... [código anterior sin cambios] ...
    pass