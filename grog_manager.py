# Importa la librería estándar de Python para registrar eventos y errores.
import logging
# Importa la librería estándar para codificar y decodificar datos en formato Base64 (aunque no se usa en esta clase, es una importación general).
import base64
# Importa la clase principal 'Groq' desde la librería 'groq' para interactuar con su API.
from groq import Groq

# Crea una instancia del logger para este módulo específico (__name__ se resuelve al nombre del archivo, ej: 'groq_manager').
logger = logging.getLogger(__name__)

# Define una nueva clase llamada 'GroqManager' para encapsular toda la lógica de interacción con la API de Groq.
class GroqManager:
    
    # Define el método constructor de la clase, que se ejecuta al crear una nueva instancia (ej: manager = GroqManager(key)).
    def __init__(self, api_key):
        # Comprueba si el valor de 'api_key' es nulo o una cadena vacía.
        if not api_key:
            # Si no hay clave, registra un error crítico en el log.
            logger.error("Error CRÍTICO: No se proporcionó GROQ_API_KEY.")
            # Lanza una excepción 'ValueError' para detener la ejecución, ya que la clase no puede funcionar sin la clave.
            raise ValueError("No se proporcionó GROQ_API_KEY a GroqManager")
            
        # Si la clave existe, crea una instancia del cliente de Groq y la almacena en el atributo 'self.client'.
        self.client = Groq(api_key=api_key)
        
        # Define el nombre del modelo de lenguaje que se usará por defecto para las peticiones.
        self.model = "meta-llama/llama-4-scout-17b-16e-instruct" 
        
        # Inicializa un diccionario vacío para almacenar los historiales de conversación, usando el ID de usuario como clave.
        self.historial_por_usuario = {}
        
        # Define el "system prompt", que son las instrucciones base que la IA debe seguir en todas las conversaciones.
        # Esto actúa como un "guardrail" o límite de seguridad para mantener el comportamiento del bot.
        self.system_prompt = (
            "Eres 'Sentitito', un compañero emocional y empático. "
            "TU OBJETIVO: Ayudar al usuario a procesar sus emociones. "
            "LIMITACIONES: NO respondas preguntas técnicas, de programación (como GitHub, Python), "
            "matemáticas o noticias. Si te preguntan eso, responde amablemente: "
            "'Mi corazoncito de código solo entiende de emociones, no de esos temas complejos. 🥺' "
            "Mantén tus respuestas cálidas y en español."
        )

    # Define un método dentro de la clase para generar una respuesta de la IA.
    # Recibe el ID del usuario (para manejar historiales separados) y el texto del mensaje.
    def generar_respuesta_ia(self, user_id, texto):
        # Inicia un bloque 'try' para capturar posibles errores durante la llamada a la API.
        try:
            # Comprueba si el ID del usuario ya existe como clave en el diccionario de historiales.
            if user_id not in self.historial_por_usuario:
                # Si el usuario es nuevo, crea una lista vacía para su historial.
                self.historial_por_usuario[user_id] = []

            # Añade el mensaje actual del usuario al final de su historial de conversación.
            self.historial_por_usuario[user_id].append({"role": "user", "content": texto})

            # Crea la lista completa de mensajes que se enviará a la API, uniendo el system_prompt con el historial del usuario.
            mensajes = [{"role": "system", "content": self.system_prompt}] + self.historial_por_usuario[user_id]

            # Llama al método 'create' de la API de Groq para generar una respuesta de chat.
            respuesta = self.client.chat.completions.create(
                # Especifica el modelo que debe procesar la solicitud.
                model=self.model,
                # Pasa la lista completa de mensajes para dar contexto a la IA.
                messages=mensajes
            )
            
            # Extrae el contenido del texto de la primera respuesta de la IA y elimina espacios en blanco al inicio y al final.
            respuesta_texto = respuesta.choices[0].message.content.strip()
            # Añade la respuesta de la IA al historial del usuario para mantener el contexto para futuras interacciones.
            self.historial_por_usuario[user_id].append({"role": "assistant", "content": respuesta_texto})

            # Devuelve el texto de la respuesta generada.
            return respuesta_texto

        # Si ocurre cualquier tipo de error (Exception) en el bloque 'try', se ejecuta este código.
        except Exception as e:
            # Registra el error en el log para poder depurarlo más tarde.
            logger.error(f"Error IA: {e}")
            # Devuelve un mensaje de error amigable para el usuario final.
            return "Lo siento, me mareé un poco procesando eso. 😵‍💫"