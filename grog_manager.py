import logging
from groq import Groq

# Configurar logger para este módulo
logger = logging.getLogger(__name__)

class GroqManager:
    """
    Maneja toda la lógica de la API de Groq y el historial
    de conversaciones (la "memoria" del bot).
    """
    
    def __init__(self, api_key):
        """Inicializa el cliente de Groq y el historial."""
        if not api_key:
            logger.error("Error CRÍTICO: No se proporcionó GROQ_API_KEY.")
            raise ValueError("No se proporcionó GROQ_API_KEY a GroqManager")
            
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"
        
        # Un diccionario para guardar el historial de cada usuario.
        # La clave será user_id, el valor será una lista de mensajes.
        self.historial_por_usuario = {}
        
        # El prompt del sistema es constante
        self.system_prompt = (
            "Eres un asistente útil y respondes en español. "
            "Debes responder lo justo y necesario para ayudar a la persona que te habla. "
            "Tienes en cuenta las emociones de la persona que te habla. "
            "Recuerda las cosas que el usuario te dice (como su nombre) para usarlas en futuras respuestas."
        )

    def generar_respuesta_ia(self, user_id, texto):
        """
        Genera una respuesta de IA usando Groq y mantiene el historial.
        """
        try:
            # Recuperar o crear el historial del usuario
            if user_id not in self.historial_por_usuario:
                self.historial_por_usuario[user_id] = []

    def analizar_imagen(self, user_id, image_path, prompt="Describe la imagen."):
        """
        Envía una imagen a Groq Vision para analizarla y responder en español.
        """
        import base64

        try:
            with open(image_path, "rb") as img:
                encoded = base64.b64encode(img.read()).decode("utf-8")

            respuesta = self.client.chat.completions.create(
                model="llama-vision",
                messages=[
                    {"role": "system", "content": "Eres un analizador visual y respondes en español."},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded}"}}
                        ]
                    }
                ]
            )

            return respuesta.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error analizando imagen: {e}")
            return "No pude analizar la imagen."
         
            # Añadir el nuevo mensaje del usuario al historial
            self.historial_por_usuario[user_id].append({"role": "user", "content": texto})


            # Construir la lista de mensajes para la API
            mensajes = [
                {"role": "system", "content": self.system_prompt}
            ] + self.historial_por_usuario[user_id]

            # Llamar a la API de Groq
            respuesta = self.client.chat.completions.create(
                model=self.model,
                messages=mensajes
            )
            
            respuesta_texto = respuesta.choices[0].message.content.strip()

            # Guardar la respuesta del bot en el historial
            self.historial_por_usuario[user_id].append({"role": "assistant", "content": respuesta_texto})

            return respuesta_texto

        except Exception as e:
            logger.error(f"Error al generar respuesta IA para {user_id}: {e}")
            return "Lo siento, hubo un problema al procesar tu mensaje. 🥺"
