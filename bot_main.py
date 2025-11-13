import telebot  
import json
import os
import logging
import base64  
from groq import Groq
from dotenv import load_dotenv
from conection import DatabaseManager 

load_dotenv()

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN_BOT_TELEGRAM = os.getenv('TELEGRAM_BOT_TOKEN')
CLAVE_API_GROQ = os.getenv('GROQ_API_KEY')
GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct" 
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"   

bot = telebot.TeleBot(TOKEN_BOT_TELEGRAM)
cliente_groq = Groq(api_key=CLAVE_API_GROQ)
db_manager = DatabaseManager() 

historial = [] 

def detectar_emocion(texto):
    """Detecta la emoción principal (Texto)."""
    try:
        respuesta = cliente_groq.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "Eres un analizador de sentimientos. Responde SOLO con una palabra en español (ej: alegria, tristeza, enojo, ansiedad, calma, miedo, neutral)."},
                {"role": "user", "content": texto}
            ]
        )
        emocion = respuesta.choices[0].message.content.strip().lower()
        return emocion
    except Exception as e:
        logging.error(f"Error al detectar emoción: {e}")
        return "neutral"

def generar_respuesta_ia(texto):
    """Genera respuesta de TEXTO con Guardrails."""
    try:
        historial.append({"role": "user", "content": texto})
        
        # --- GUARDRAILS (CANDADO DE SEGURIDAD) ---
        system_prompt = (
            "Eres 'Sentitito', un compañero emocional. "
            "TU MISIÓN: Hablar de sentimientos, bienestar y empatía. "
            "PROHIBICIONES: NO respondas preguntas sobre programación, GitHub, código, matemáticas, "
            "política o datos técnicos complejos. "
            "SI TE PREGUNTAN ESO: Responde amablemente 'Lo siento, mi corazoncito solo entiende de emociones, no de tecnología. ¿Cómo te sientes hoy?'."
        )

        respuesta = cliente_groq.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                *historial 
            ]
        )
        respuesta_texto = respuesta.choices[0].message.content.strip()
        historial.append({"role": "assistant", "content": respuesta_texto})
        return respuesta_texto
    except Exception as e:
        logging.error(f"Error IA (Texto): {e}")
        return "Me quedé pensando... ¿podrías repetirlo? 🥺"

# --- 2. FUNCIÓN DE VISIÓN CORREGIDA (sin 'self') ---
def analizar_imagen_local(image_path, prompt="Describe la emoción de esta imagen."):
    """Analiza una imagen guardada localmente."""
    try:
        with open(image_path, "rb") as img:
            encoded = base64.b64encode(img.read()).decode("utf-8")

        respuesta = cliente_groq.chat.completions.create( # Usamos el cliente global
            model=VISION_MODEL, # Usamos el modelo de visión estable
            messages=[
                {"role": "system", "content": "Eres un experto analizando emociones en imágenes. Responde en español."},
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
        return "No pude ver bien la imagen. 🙈"

# --- COMANDOS ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "¡Hola! Soy Sentitito 💖. Háblame de tu día o envíame una foto para ver cómo te sientes.")

@bot.message_handler(commands=['sentimiento'])
def comando_sentimiento(message):
    texto = message.text.replace("/sentimiento", "").strip()
    if not texto:
        bot.reply_to(message, "⚠️ Usá: `/sentimiento hoy me siento...`", parse_mode="Markdown")
        return
    emocion = detectar_emocion(texto)
    bot.reply_to(message, f"🧠 *Emoción detectada:* `{emocion}`", parse_mode="Markdown")

@bot.message_handler(commands=['diario'])
def comando_diario(message):
    user_id = message.from_user.id
    registros = db_manager.obtener_historial_reciente(user_id, limite=5)
    
    if not registros:
        bot.reply_to(message, "📓 Tu diario está vacío. ¡Escríbeme algo!")
        return

    txt = "📓 **Tu Diario Emocional:**\n\n"
    for item in registros:
        texto_msg = item[0]; senti = item[1]
        emoji = "✨"
        if "alegr" in senti: emoji = "😊"
        elif "trist" in senti: emoji = "😢"
        elif "enojo" in senti: emoji = "😠"
        elif "ansied" in senti: emoji = "😰"
        elif "calma" in senti: emoji = "😌"
        txt += f"{emoji} *{senti.upper()}*: \"{texto_msg}\"\n"
    
    bot.reply_to(message, txt, parse_mode="Markdown")


# --- MANEJADORES DE CONTENIDO (Texto e Imagen) ---

@bot.message_handler(content_types=['text'])
def manejar_mensajes_de_texto(message):
    user_id = message.from_user.id
    username = message.from_user.username or "Anonimo"
    texto = message.text

    # 1. Detectar emoción del texto
    emocion = detectar_emocion(texto)

    # 2. Guardar en BD
    db_manager.save_message_and_user(user_id, username, texto, emocion, 0.0)

    # 3. Responder (con filtro anti-tech)
    respuesta = generar_respuesta_ia(texto)
    bot.reply_to(message, respuesta)

# --- 4. MANEJADOR DE FOTOS (¡El que faltaba!) ---
@bot.message_handler(content_types=['photo'])
def manejar_fotos(message):
    bot.reply_to(message, "Viendo tu foto... 📸 Dame un segundo.")
    
    try:
        # 1. Descargar la foto
        file_id = message.photo[-1].file_id # [-1] es la de mayor calidad
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # 2. Guardar temporalmente
        temp_path = f"temp_{file_id}.jpg"
        with open(temp_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        # 3. Analizar la foto
        # (Si el usuario escribió un pie de foto (caption), lo usamos como prompt)
        prompt = message.caption if message.caption else "Qué emoción transmite esta imagen?"
        
        analisis = analizar_imagen_local(temp_path, prompt)
        
        # 4. Responder
        bot.reply_to(message, f"👁️ *Análisis de la foto:*\n{analisis}")

        # 5. Limpiar
        os.remove(temp_path)

    except Exception as e:
        logger.error(f"Error procesando foto: {e}")
        bot.reply_to(message, "¡Ups! No pude analizar esa imagen. Intenta con otra.")


if __name__ == "__main__":
    logger.info("🤖 Iniciando Sentitito Bot...")
    if db_manager.test_connection():
        logger.info("✅ Base de datos conectada.")
    else:
        logger.warning("⚠️ SIN BASE DE DATOS.")
    
    bot.polling(none_stop=True)
