import telebot
import json
import os
import logging
from groq import Groq
from dotenv import load_dotenv
import random

# Cargar variables de entorno
load_dotenv()

# --- CAMBIO 1: Definir el logger para poder usar la variable "logger" ---
# Configuración de logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
# Creamos una variable logger para usarla consistentemente
logger = logging.getLogger(__name__)


# --- Configuración de variables globales ---
TOKEN_BOT_TELEGRAM = os.getenv('TELEGRAM_BOT_TOKEN')
CLAVE_API_GROQ = os.getenv('GROQ_API_KEY')
DATASET_PATH = 'emociones.json'
GROQ_MODEL = "llama-3.1-8b-instant"

# --- Inicialización de clientes ---
bot = telebot.TeleBot(TOKEN_BOT_TELEGRAM)
cliente_groq = Groq(api_key=CLAVE_API_GROQ)


# --- Base de datos en memoria para el historial (simplificado) ---
# Un diccionario para guardar el historial de cada usuario por separado
historial_por_usuario = {}

def cargar_dataset():
    try:
        with open(DATASET_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"No se pudo cargar el dataset de emociones: {e}")
        return {} # Devolver un diccionario vacío para evitar errores

def detectar_emocion(texto):
    try:
        respuesta = cliente_groq.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Sos un analizador emocional. Respondé SOLO con una palabra "
                        "que describa la emoción principal (ej: alegria, tristeza, enojo, ansiedad, calma, miedo, neutral). "
                        "Si no podés identificarla, respondé 'neutral'."
                    )
                },
                {"role": "user", "content": texto}
            ]
        )
        emocion = respuesta.choices[0].message.content.strip().lower()
        return emocion
    except Exception as e:
        logger.error(f"Error al detectar emoción: {e}")
        return "neutral" # Devolver 'neutral' en caso de error

def generar_respuesta_ia(user_id, texto):
    try:
        # Obtener el historial del usuario, o crear uno nuevo si no existe
        if user_id not in historial_por_usuario:
            historial_por_usuario[user_id] = []
        
        historial = historial_por_usuario[user_id]
        
        # Agregás el mensaje del usuario al historial
        historial.append({"role": "user", "content": texto})

        # Limitar el historial para no exceder el límite de tokens (opcional pero recomendado)
        if len(historial) > 10:
            historial = historial[-10:] # Mantiene solo los últimos 10 mensajes

        # Crear el prompt para la API
        prompt = [
            {
                "role": "system",
                "content": (
                    "Eres un asistente útil y respondes en español. "
                    "Debes responder lo justo y necesario para ayudar a la persona que te habla. "
                    "También tienes en cuenta las emociones de la persona. "
                    "Si la persona está triste, tu respuesta debe ser empática y alentadora. "
                    "Si está feliz, sé alegre y positivo. "
                    "Si está enojada, responde de forma calmada y conciliadora."
                ),
            },
            *historial
        ]

        respuesta = cliente_groq.chat.completions.create(
            model=GROQ_MODEL,
            messages=prompt
        )

        respuesta_texto = respuesta.choices[0].message.content.strip()
        # Guardás la respuesta del asistente en el historial
        historial.append({"role": "assistant", "content": respuesta_texto})
        
        # Actualizar el historial del usuario
        historial_por_usuario[user_id] = historial

        return respuesta_texto

    except Exception as e:
        logger.error(f"Error al generar respuesta IA: {e}")
        return "Lo siento, hubo un problema al procesar tu mensaje. ¿Podrías intentarlo de nuevo? 🥺"

# --- CAMBIO 2: Lógica de manejadores corregida ---

# MANEJADOR PARA EL COMANDO /sentimiento
@bot.message_handler(commands=['sentimiento'])
def comando_sentimiento(message):
    texto = message.text.replace("/sentimiento", "").strip()

    if not texto:
        bot.reply_to(message, "⚠️ Usá el comando así:\n`/sentimiento hoy me siento bien`", parse_mode="Markdown")
        return

    emocion = detectar_emocion(texto)

    rol_base = (
        "Eres un asistente empático que responde en español. "
        "Tu tarea es responder brevemente, pero de forma emocionalmente adecuada. "
        "Primero, confirma la emoción que detectaste y luego responde al mensaje del usuario."
    )

    try:
        mensajes = [
            {"role": "system", "content": rol_base},
            {"role": "user", "content": f"Emoción detectada: {emocion}. Mensaje del usuario: '{texto}'"}
        ]

        respuesta = cliente_groq.chat.completions.create(
            model=GROQ_MODEL,
            messages=mensajes
        )
        respuesta_texto = respuesta.choices[0].message.content.strip()

        bot.reply_to(
            message,
            f"🧠 *Emoción detectada:* `{emocion}`\n\n💬 *Respuesta IA:* {respuesta_texto}",
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.error(f"Error en comando_sentimiento: {e}")
        bot.reply_to(message, "⚠️ Hubo un problema procesando tu emoción, intentá de nuevo más tarde.")

# MANEJADOR PARA TODOS LOS DEMÁS MENSAJES DE TEXTO
# --- CAMBIO 3: Este manejador ahora va al final ---
@bot.message_handler(content_types=['text'])
def manejar_mensajes_de_texto(message):
    user_id = message.from_user.id
    respuesta_ia = generar_respuesta_ia(user_id, message.text)
    bot.reply_to(message, respuesta_ia)


# --- 4. EJECUCIÓN DEL BOT ---
if __name__ == "__main__":
    logger.info("🤖 Iniciando Bot...")
    
    # --- CAMBIO 4: Eliminada la comprobación de la base de datos ---
    # Ya que no se está usando en este script, se quita la llamada a db_manager
    # para evitar el error de variable no definida.
    
    logger.info("✅ Bot listo para recibir mensajes.")

    try:
        logger.info("🚀 Iniciando polling del bot...")
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        logger.critical(f"Error fatal que detuvo el bot: {e}")