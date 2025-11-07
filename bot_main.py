import telebot  
import json
import os
import logging
import random
from dotenv import load_dotenv
from textblob import TextBlob
from conection import DatabaseManager
from grog_manager import GroqManager
import cv2
from fer import FER
#pip install opencv-python fer
import tempfile

load_dotenv()

logging.basicConfig(level=logging.INFO, 
                format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN_BOT_TELEGRAM = os.getenv('TELEGRAM_BOT_TOKEN')
CLAVE_API_GROQ = os.getenv('GROQ_API_KEY') 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, 'emociones.json')

bot = telebot.TeleBot(TOKEN_BOT_TELEGRAM)

try:
    db_manager = DatabaseManager()
    groq_manager = GroqManager(api_key=CLAVE_API_GROQ) 

except ValueError as e:
    logger.critical(f"Error al iniciar los manejadores: {e}")
    logger.critical("El bot NO se iniciará sin las variables de entorno.")
    exit() 


# Funciones del Bot

def cargar_dataset():
    """Carga el archivo JSON de emociones."""
    try:
        with open(DATASET_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error al cargar {DATASET_PATH}: {e}")
        return {} 
    
def analyze_sentiment(text):
    """Analiza sentimiento usando TextBlob (para la BD)."""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        sentiment = "positive"
    elif polarity < -0.1:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    return sentiment, round(polarity, 3)


# Manejadores de Mensajes

@bot.message_handler(commands=['sentimiento'])
def comando_sentimiento(message):
    """Maneja el comando /sentimiento."""
    user = message.from_user
    texto = message.text.replace("/sentimiento", "").strip()

    if not texto:
        bot.reply_to(message, "⚠️ Usá el comando así:\n`/sentimiento hoy me siento bien`", parse_mode="Markdown")
        return

    #Analizar sentimiento
    emocion, score = analyze_sentiment(texto)
    
    # Guardar en BD usando nuestra clase POO
    username = user.username or user.first_name or "N/A"
    db_manager.save_message_and_user(user.id, username, texto, emocion, score)

    # Buscar respuesta en JSON
    dataset = cargar_dataset()
    respuesta_json = f"Detecté emoción: *{emocion}* (Score: {score})\n\n"
    
    try:
        if emocion == "positive" and "celebracion_logros" in dataset:
            respuesta_json += random.choice(dataset["celebracion_logros"])['texto']
        elif emocion == "negative" and "sentimientos_negativos" in dataset:
            respuesta_json += random.choice(dataset["sentimientos_negativos"]["tristeza"])['texto']
        else:
            respuesta_json += "Gracias por compartir cómo te sientes."
            
        bot.reply_to(message, respuesta_json, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error al buscar respuesta JSON para {emocion}: {e}")
        bot.reply_to(message, f"Detecté: *{emocion}*. (No pude encontrar una respuesta JSON).", parse_mode="Markdown")

@bot.message_handler(content_types=['photo'])
def manejar_imagen(message):
    user = message.from_user

    # Descargar mejor resolución
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded = bot.download_file(file_info.file_path)

    # Guardar la imagen temporalmente
    temp_path = f"temp_{user.id}.jpg"
    with open(temp_path, "wb") as img:
      @bot.message_handler(content_types=['photo'])
def manejar_imagen(message):
    user = message.from_user

    # Descargar imagen
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded = bot.download_file(file_info.file_path)

    temp_path = f"temp_{user.id}.jpg"
    with open(temp_path, "wb") as img:
        img.write(downloaded)

    bot.reply_to(message, "Procesando la imagen... un momento.")

    # --- DETECCIÓN DE CARA + EMOCIÓN ---
    from fer import FER
    import cv2
    detector = FER()

    try:
        img = cv2.imread(temp_path)
        emociones = detector.detect_emotions(img)

        if emociones:
            rostro = emociones[0]
            emocion_predominante = max(rostro["emotions"], key=rostro["emotions"].get)
            intensidad = rostro["emotions"][emocion_predominante]
            texto_emocion = f"🤖 Detecté una emoción predominante: *{emocion_predominante}* (intensidad {round(intensidad, 2)})"
        else:
            texto_emocion = "No pude detectar un rostro claro en la imagen."
    except:
        texto_emocion = "Hubo un problema al analizar la emoción."

    bot.send_message(message.chat.id, texto_emocion, parse_mode="Markdown")
  
    # Respuestas personalizadas según emoción detectada
    respuestas_emocionales = {
        "happy": "Veo una sonrisa ahí. Me alegra mucho eso.",
        "sad": "Parece que estás pasando un momento difícil. Si querés hablar, estoy acá.",
        "angry": "Te noto con enojo. A veces soltar un poco ayuda.",
        "surprise": "Wow, sorpresa! Algo inesperado pasó ahí.",
        "fear": "Parece que hay un poco de miedo. Está bien sentirse así a veces.",
        "neutral": "Veo una expresión bastante neutra. Todo tranqui."
    }

    if emociones:
        if emocion_predominante in respuestas_emocionales:
            bot.send_message(
                message.chat.id,
                respuestas_emocionales[emocion_predominante]
            )
        else:
            bot.send_message(message.chat.id, "Hay una emoción que no pude clasificar bien.")

    # --- ANÁLISIS VISUAL CON GROQ ---
    resultado = groq_manager.analizar_imagen(
        user.id,
        temp_path,
        prompt="Describe la imagen y el contexto emocional."
    )
    bot.send_message(message.chat.id, resultado)

    try:
        os.remove(temp_path)
    except:
        pass

        img.write(downloaded)

    bot.reply_to(message, "Procesando la imagen... un momento.")

    # Usamos Groq para analizar la imagen
    resultado = groq_manager.analizar_imagen(
        user.id,
        temp_path,
        prompt="Explica lo que ves en la imagen con detalles."
    )

    bot.send_message(message.chat.id, resultado)

    # Borrar la imagen temporal
    try:
        os.remove(temp_path)
    except:
        pass

def buscar_en_dataset(pregunta, dataset):
    # Normaliza la pregunta (quita espacios y pasa a minúsculas)
    pregunta = pregunta.strip().lower()
    # Recorre cada elemento del dataset
    for item in dataset:
        # Compara la pregunta del usuario con la del dataset (normalizada)
        if item['pregunta'].strip().lower() == pregunta:
            # Si hay coincidencia exacta, retorna la respuesta
            return item['respuesta']
    # Si no encuentra coincidencia, retorna None
    return None

@bot.message_handler(func=lambda message: True)
def manejar_mensaje(message):
    """Manejador principal para todos los mensajes de texto."""
    texto = message.text
    user = message.from_user
    
    # Analizar y Guardar en BD (para TODOS los mensajes)
    emocion, score = analyze_sentiment(texto)
    username = user.username or user.first_name or "N/A"
    db_manager.save_message_and_user(user.id, username, texto, emocion, score)
        
    # lógica de buscar en dataset
    respuesta_dataset = None
    
    if respuesta_dataset:
        bot.reply_to(message, respuesta_dataset)
    else:
        # user.id para que pueda usar el historial
        respuesta_ia = groq_manager.generar_respuesta_ia(user.id, texto)
        bot.reply_to(message, respuesta_ia)

#Ejecución
if __name__ == "__main__":
    logging.info("🤖 Iniciando Bot...")
    
    # Probar la conexión a la base de datos
    if not db_manager.test_connection():
        logging.critical("CRÍTICO: No se pudo conectar a la base de datos.")
        logging.critical("El bot no se iniciará.")
    else:
        logging.info("Base de datos conectada. Iniciando polling...")
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logging.error(f"Error en el bot: {e}")
