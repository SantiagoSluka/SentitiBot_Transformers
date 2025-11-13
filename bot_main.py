# import telebot  
# import json
# import os
# import logging
# import random
# from dotenv import load_dotenv
# from textblob import TextBlob
# from conection import DatabaseManager
# from grog_manager import GroqManager
# import tempfile
# import ffmpeg
# import openai
# from dotenv import load_dotenv
# from telegram import Update
# from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# load_dotenv()

# logging.basicConfig(level=logging.INFO, 
#                 format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# TOKEN_BOT_TELEGRAM = os.getenv('TELEGRAM_BOT_TOKEN')
# CLAVE_API_GROQ = os.getenv('GROQ_API_KEY') 
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DATASET_PATH = os.path.join(BASE_DIR, 'emociones.json')
# openai.api_key= os.getenv("OPENAI_API_KEY")
# bot = telebot.TeleBot(TOKEN_BOT_TELEGRAM)

# try:
#     db_manager = DatabaseManager()
#     groq_manager = GroqManager(api_key=CLAVE_API_GROQ) 

# except ValueError as e:
#     logger.critical(f"Error al iniciar los manejadores: {e}")
#     logger.critical("El bot NO se iniciará sin las variables de entorno.")
#     exit() 


# # Funciones del Bot

# def cargar_dataset():
#     """Carga el archivo JSON de emociones."""
#     try:
#         with open(DATASET_PATH, 'r', encoding='utf-8') as f:
#             return json.load(f)
#     except Exception as e:
#         logger.error(f"Error al cargar {DATASET_PATH}: {e}")
#         return {} 
    
# def analyze_sentiment(text):
#     """Analiza sentimiento usando TextBlob (para la BD)."""
#     blob = TextBlob(text)
#     polarity = blob.sentiment.polarity
#     if polarity > 0.1:
#         sentiment = "positive"
#     elif polarity < -0.1:
#         sentiment = "negative"
#     else:
#         sentiment = "neutral"
#     return sentiment, round(polarity, 3)

# @bot.message_handler(func=lambda message: True)
# def manejar_mensajes_de_texto(message):
#     respuesta_ia = generar_respuesta_ia(message.text)
#     bot.reply_to(message, respuesta_ia)

# # Manejadores de Mensajes

# @bot.message_handler(commands=['sentimiento'])
# def comando_sentimiento(message):
#     """Maneja el comando /sentimiento."""
#     user = message.from_user
#     texto = message.text.replace("/sentimiento", "").strip()

#     if not texto:
#         bot.reply_to(message, "⚠️ Usá el comando así:\n`/sentimiento hoy me siento bien`", parse_mode="Markdown")
#         return

#     #Analizar sentimiento
#     emocion, score = analyze_sentiment(texto)
    
#     # Guardar en BD usando nuestra clase POO
#     username = user.username or user.first_name or "N/A"
#     db_manager.save_message_and_user(user.id, username, texto, emocion, score)

#     # Buscar respuesta en JSON
#     dataset = cargar_dataset()
#     respuesta_json = f"Detecté emoción: *{emocion}* (Score: {score})\n\n"
    
#     try:
#         if emocion == "positive" and "celebracion_logros" in dataset:
#             respuesta_json += random.choice(dataset["celebracion_logros"])['texto']
#         elif emocion == "negative" and "sentimientos_negativos" in dataset:
#             respuesta_json += random.choice(dataset["sentimientos_negativos"]["tristeza"])['texto']
#         else:
#             respuesta_json += "Gracias por compartir cómo te sientes."
            
#         bot.reply_to(message, respuesta_json, parse_mode="Markdown")
        
#     except Exception as e:
#         logger.error(f"Error al buscar respuesta JSON para {emocion}: {e}")
#         bot.reply_to(message, f"Detecté: *{emocion}*. (No pude encontrar una respuesta JSON).", parse_mode="Markdown")


# def buscar_en_dataset(pregunta, dataset):
#     # Normaliza la pregunta (quita espacios y pasa a minúsculas)
#     pregunta = pregunta.strip().lower()
#     # Recorre cada elemento del dataset
#     for item in dataset:
#         # Compara la pregunta del usuario con la del dataset (normalizada)
#         if item['pregunta'].strip().lower() == pregunta:
#             # Si hay coincidencia exacta, retorna la respuesta
#             return item['respuesta']
#     # Si no encuentra coincidencia, retorna None
#     return None

# @bot.message_handler(func=lambda message: True)
# def manejar_mensaje(message):
#     """Manejador principal para todos los mensajes de texto."""
#     texto = message.text
#     user = message.from_user
    
#     # Analizar y Guardar en BD (para TODOS los mensajes)
#     emocion, score = analyze_sentiment(texto)
#     username = user.username or user.first_name or "N/A"
#     db_manager.save_message_and_user(user.id, username, texto, emocion, score)
        
#     # lógica de buscar en dataset
#     respuesta_dataset = None
    
#     if respuesta_dataset:
#         bot.reply_to(message, respuesta_dataset)
#     else:
#         # user.id para que pueda usar el historial
#         respuesta_ia = groq_manager.generar_respuesta_ia(user.id, texto)
#         bot.reply_to(message, respuesta_ia)


# """
# Kevin
# """
# #Función para convertir el audio OGG a WAV (que Whisper puede leer)
# @bot.message_handler(content_types=['audio', 'voice'])
# def convert_to_wav(input_path):
#     output_path = input_path.replace(".oga", ".wav")
#     ffmpeg.input(input_path).output(output_path).run(quiet=True, overwrite_output=True)
#     return output_path

#  # función para transcribir usando Whisper de OpenAI

# def transcribir_audio(audio_path):
#     with open(audio_path, "rb") as audio_file:
#         transcript = openai.Audio.transcriptions.create(
#             model="whisper-1",
#             file=audio_file,
#             response_format="text"
#         )
#     return transcript.strip()

# # Handler principal de audio
# async def audio_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     file = await update.message.voice.get_file() if update.message.voice else await update.message.audio.get_file()

#     # Crear un archivo temporal
#     with tempfile.TemporaryDirectory() as tmpdir:
#         input_path = os.path.join(tmpdir, "audio.oga")
#         await file.download_to_drive(custom_path=input_path)

#         # Convertir a WAV
#         wav_path = convert_to_wav(input_path)
# #transcribir
#         await update.message.reply_text(" Transcribiendo tu audio, por favor espera...")
#         texto = transcribir_audio(wav_path)

#         # Responder con el texto
#         await update.message.reply_text(f" Transcripción:\n\n{texto}")

# #Inicializar el bot
# async def main():
#     app = ApplicationBuilder().token(TOKEN_BOT_TELEGRAM).build()





# #Ejecución
# if __name__ == "__main__":
#     logging.info("🤖 Iniciando Bot...")
    
#     # Probar la conexión a la base de datos
#     if not db_manager.test_connection():
#         logging.critical("CRÍTICO: No se pudo conectar a la base de datos.")
#         logging.critical("El bot no se iniciará.")
#     else:
#         logging.info("Base de datos conectada. Iniciando polling...")
#         try:
#             bot.polling(none_stop=True)
#         except Exception as e:
#             logging.error(f"Error en el bot: {e}")





import telebot
import json
import os
import logging
import random
import tempfile
import ffmpeg  # Se requiere 'ffmpeg-python' (pip install ffmpeg-python)
from dotenv import load_dotenv
from textblob import TextBlob
from conection import DatabaseManager
from grog_manager import GroqManager
from groq import Groq
from pydub import AudioSegment
# --- 1. CONFIGURACIÓN INICIAL ---
load_dotenv()

# --- AÑADE ESTAS LÍNEAS ---
# Reemplaza la ruta con la ubicación EXACTA de tu ffmpeg.exe
# Ojo con las dobles barras invertidas (\\) en Windows.
AudioSegment.converter = "C:\ffmpeg\bin\ffmpeg.exe"
AudioSegment.ffprobe = "C:\ffmpeg\bin\ffprobe.exe"



logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cargar variables de entorno
TOKEN_BOT_TELEGRAM = os.getenv('TELEGRAM_BOT_TOKEN')
CLAVE_API_GROQ = os.getenv('GROQ_API_KEY')


# Validar que las variables de entorno existan
if not all([TOKEN_BOT_TELEGRAM, CLAVE_API_GROQ]):
    logger.critical("ERROR CRÍTICO: Una o más variables de entorno (TELEGRAM_BOT_TOKEN, GROQ_API_KEY) no están definidas.")
    exit()

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, 'emociones.json')

# Instanciación de los objetos principales
bot = telebot.TeleBot(TOKEN_BOT_TELEGRAM)
db_manager = DatabaseManager()
groq_manager = GroqManager(api_key=CLAVE_API_GROQ)


# --- 2. FUNCIONES AUXILIARES ---

def cargar_dataset():
    """Carga el archivo JSON de emociones."""
    try:
        with open(DATASET_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error al cargar {DATASET_PATH}: {e}")
        return {}

def analyze_sentiment(text):
    """Analiza el sentimiento de un texto usando TextBlob."""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        sentiment = "positive"
    elif polarity < -0.1:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    return sentiment, round(polarity, 3)

# def convert_oga_to_wav(oga_path):   no se utilizxa se puede borrar
#     """Convierte un archivo de audio .oga a .wav usando ffmpeg."""
#     wav_path = oga_path.replace(".oga", ".wav")
#     try:
#         (
#             ffmpeg
#             .input(oga_path)
#             .output(wav_path, acodec='pcm_s16le', ac=1, ar='16000') # Formato estándar para muchos modelos de transcripción
#             .run(quiet=True, overwrite_output=True)
#         )
#         return wav_path
#     except ffmpeg.Error as e:
#         logger.error(f"Error de FFmpeg al convertir audio: {e}")
#         return None

def convert_audio_with_pydub(input_path):
    """
    Convierte un archivo de audio a formato WAV usando pydub.
    Devuelve la ruta al nuevo archivo.
    """
    output_path = input_path.replace(".oga", ".wav")
    try:
        # Carga el audio, especificando que es un formato 'ogg'
        audio = AudioSegment.from_file(input_path, format="ogg")
        # Exporta el audio a formato 'wav'
        audio.export(output_path, format="wav")
        logger.info(f"Audio convertido de {input_path} a {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error al convertir audio con pydub: {e}")
        return None

def transcribir_audio(audio_path):
    """
    Transcribe un archivo de audio usando la API de Groq con el modelo Whisper.
    """
    try:
        # 1. Inicializa el cliente de Groq. 
        #    Usa la clave de API que ya cargaste desde las variables de entorno.
        client = Groq(api_key=CLAVE_API_GROQ)

        # 2. Abre el archivo de audio en modo de lectura binaria ('rb').
        with open(audio_path, "rb") as audio_file:
            
            # 3. Llama a la API de transcripciones de Groq.
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",  # Este es el modelo recomendado por Groq para transcripción.
                file=audio_file,
                response_format="text"    # Pedimos que la respuesta sea solo el texto plano.
            )
        
        # 4. La variable 'transcription' contiene directamente el texto.
        #    Usamos .strip() para eliminar cualquier espacio en blanco al inicio o al final.
        return transcription.strip()

    except Exception as e:
        logger.error(f"Error al transcribir con Groq: {e}")
        return "Lo siento, no pude procesar el audio en este momento."

# --- 3. MANEJADORES DE MENSAJES DE TELEGRAM ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Manejador para los comandos /start y /help."""
    bot.reply_to(message, "¡Hola! Soy tu bot asistente. Envíame un mensaje de texto o una nota de voz y te responderé. También puedes usar el comando /sentimiento.")

@bot.message_handler(commands=['sentimiento'])
def comando_sentimiento(message):
    """Maneja el comando /sentimiento para analizar una frase."""
    user = message.from_user
    texto = message.text.replace("/sentimiento", "").strip()

    if not texto:
        bot.reply_to(message, "⚠️ Usá el comando así:\n`/sentimiento hoy me siento bien`", parse_mode="Markdown")
        return

    # Analizar sentimiento y guardar en BD
    emocion, score = analyze_sentiment(texto)
    username = user.username or user.first_name or "N/A"
    db_manager.save_message_and_user(user.id, username, texto, emocion, score)

    # Buscar respuesta en el dataset de emociones
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

@bot.message_handler(content_types=['audio', 'voice'])
def handle_audio_messages(message):
    """Manejador para mensajes de audio y notas de voz (con pydub)."""
    user = message.from_user
    bot.reply_to(message, "🎙️ Recibido. Procesando tu audio, por favor espera...")

    try:
        file_id = message.voice.file_id if message.voice else message.audio.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        with tempfile.TemporaryDirectory() as tmpdir:
            input_oga_path = os.path.join(tmpdir, "audio.oga")
            
            with open(input_oga_path, 'wb') as new_file:
                new_file.write(downloaded_file)

            # --- NUEVA LÓGICA DE CONVERSIÓN ---
            # Convertir el archivo .oga a .wav usando pydub
            output_wav_path = convert_audio_with_pydub(input_oga_path)

            if not output_wav_path:
                bot.reply_to(message, "Hubo un error al preparar tu audio. Inténtalo de nuevo.")
                return

            # Transcribir el archivo .wav convertido
            texto_transcrito = transcribir_audio(output_wav_path)
            # --- FIN DE LA NUEVA LÓGICA ---
            
            bot.reply_to(message, f"📜 *Transcripción:*\n\n_{texto_transcrito}_", parse_mode="Markdown")

            bot.send_chat_action(message.chat.id, 'typing')
            respuesta_ia = groq_manager.generar_respuesta_ia(user.id, texto_transcrito)
            bot.reply_to(message, respuesta_ia)

    except Exception as e:
        logger.error(f"Error general en el manejador de audio: {e}")
        bot.reply_to(message, "Lo siento, ocurrió un error inesperado al procesar tu audio.")


@bot.message_handler(content_types=['text'])
def handle_text_messages(message):
    """Manejador principal para todos los mensajes de texto que no son comandos."""
    texto = message.text
    user = message.from_user

    # 1. Analizar y Guardar en BD
    emocion, score = analyze_sentiment(texto)
    username = user.username or user.first_name or "N/A"
    db_manager.save_message_and_user(user.id, username, texto, emocion, score)

    # 2. Indicar que el bot está "escribiendo..."
    bot.send_chat_action(message.chat.id, 'typing')

    # 3. Generar y enviar respuesta de la IA (Groq)
    # Se pasa el user.id para que la IA pueda usar el historial de conversación
    respuesta_ia = groq_manager.generar_respuesta_ia(user.id, texto)
    bot.reply_to(message, respuesta_ia)

# --- 4. EJECUCIÓN DEL BOT (VERSIÓN MODIFICADA) ---
if __name__ == "__main__":
    logger.info("🤖 Iniciando Bot...")
    
    # Intentamos conectar, pero no detenemos el bot si falla.
    if not db_manager.test_connection():
        # Cambiamos el log de CRITICAL a WARNING para indicar que es un problema, pero no detiene el bot.
        logger.warning("AVISO: No se pudo conectar a la base de datos. El bot se iniciará, pero no podrá guardar mensajes.")
    else:
        logger.info("✅ Base de datos conectada correctamente.")

    # El bot se inicia SIEMPRE, sin importar el estado de la base de datos.
    try:
        logger.info("🚀 Iniciando polling del bot...")
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        logger.critical(f"Error fatal que detuvo el bot: {e}")