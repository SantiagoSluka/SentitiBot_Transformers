import logging
import base64
from groq import Groq

logger = logging.getLogger(__name__)

class GroqManager:
    
    def __init__(self, api_key):
        if not api_key:
            logger.error("Error CRÍTICO: No se proporcionó GROQ_API_KEY.")
            raise ValueError("No se proporcionó GROQ_API_KEY a GroqManager")
            
        self.client = Groq(api_key=api_key)
        
        # Modelo estándar y rápido de Groq
        self.model = "llama-3.1-8b-instant" 
        
        self.historial_por_usuario = {}
        
        # --- PROMPT LIMITADO (GUARDRAILS) ---
        self.system_prompt = (
            "Eres 'Sentitito', un compañero emocional y empático. "
            "TU OBJETIVO: Ayudar al usuario a procesar sus emociones. "
            "LIMITACIONES: NO respondas preguntas técnicas, de programación (como GitHub, Python), "
            "matemáticas o noticias. Si te preguntan eso, responde amablemente: "
            "'Mi corazoncito de código solo entiende de emociones, no de esos temas complejos. 🥺' "
            "Mantén tus respuestas cálidas y en español."
        )

    def generar_respuesta_ia(self, user_id, texto):
        try:
            if user_id not in self.historial_por_usuario:
                self.historial_por_usuario[user_id] = []

            self.historial_por_usuario[user_id].append({"role": "user", "content": texto})

            mensajes = [{"role": "system", "content": self.system_prompt}] + self.historial_por_usuario[user_id]

            respuesta = self.client.chat.completions.create(
                model=self.model,
                messages=mensajes
            )
            
            respuesta_texto = respuesta.choices[0].message.content.strip()
            self.historial_por_usuario[user_id].append({"role": "assistant", "content": respuesta_texto})

            return respuesta_texto

        except Exception as e:
            logger.error(f"Error IA: {e}")
            return "Lo siento, me mareé un poco procesando eso. 😵‍💫"

