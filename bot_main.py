import telebot  
import requests
import json
import os
import logging
from groq import Groq
import base64
from dotenv import load_dotenv
import random
import mysql.connector

# Para api de groq, telegram y a futuro qwem si llegamos
load_dotenv()

# Configuración de logging
logging.basicConfig(level=logging.INFO, 
                format='%(asctime)s - %(levelname)s - %(message)s')

TOKEN_BOT_TELEGRAM = os.getenv('TELEGRAM_BOT_TOKEN')
CLAVE_API_GROQ = os.getenv('GROQ_API_KEY')
DATASET_PATH = 'emociones.json'

# Modelo de Groq a utilizar
GROQ_MODEL = "llama-3.1-8b-instant"  # Este es el modelo estable actual de Groq

bot = telebot.TeleBot(TOKEN_BOT_TELEGRAM)
cliente_groq = Groq(api_key=CLAVE_API_GROQ)

def cargar_dataset():
	try:
		with open(DATASET_PATH, 'r', encoding='utf-8') as f:
			return json.load(f)
	except Exception:
		return []
	

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
        logging.error(f"Error al detectar emoción: {e}")
        return None



historial = []  # lista global o guardada por usuario

def generar_respuesta_ia(texto):
    try:
        # Agregás el mensaje del usuario al historial
        historial.append({"role": "user", "content": texto})

        respuesta = cliente_groq.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un asistente útil y respondes en español. "
                        "Debes responder lo justo y necesario para ayudar a la persona que te habla. "
                        "También tienes en cuenta las emociones de la persona que te habla. "
                        "Si la persona está triste, tu respuesta debe ser empática y alentadora. "
                        "Si la persona está feliz, tu respuesta debe ser alegre y positiva. "
                        "Si la persona está enojada, tu respuesta debe ser calmada y conciliadora."
                    ),
                },
                *historial  # ← acá se pasa todo el historial completo
            ]
        )

        # Guardás la respuesta del asistente en el historial
        respuesta_texto = respuesta.choices[0].message.content.strip()
        historial.append({"role": "assistant", "content": respuesta_texto})

        return respuesta_texto

    except Exception as e:
        logging.error(f"Error al generar respuesta IA: {e}")
        return "Lo siento, hubo un problema al procesar tu mensaje. ¿Podrías intentarlo de nuevo? 🥺"



@bot.message_handler(commands=['sentimiento'])
def comando_sentimiento(message):
    texto = message.text.replace("/sentimiento", "").strip()

    if not texto:
        bot.reply_to(message, "⚠️ Usá el comando así:\n`/sentimiento hoy me siento bien`", parse_mode="Markdown")
        return

    emocion = detectar_emocion(texto)
    dataset = cargar_dataset()

    if emocion and emocion in dataset.get("emociones", {}):
        respuesta = random.choice(dataset["emociones"][emocion])
        bot.reply_to(message, f"Detecté emoción: *{emocion}*\n\n{respuesta}", parse_mode="Markdown")

    else:
        # Si no hay emoción conocida, usa Groq como chat normal
        respuesta_ia = generar_respuesta_ia(texto)
        bot.reply_to(message, f"*IA:* {respuesta_ia}", parse_mode="Markdown")


def buscar_en_dataset(pregunta, dataset):
    pregunta = pregunta.strip().lower()

    # Si el dataset tiene una estructura tipo {"emociones": {...}}, no sirve para esta búsqueda
    if not isinstance(dataset, list):
        logging.warning(f"Formato inesperado de dataset: {type(dataset)}. Se esperaba una lista.")
        return None

    for item in dataset:
        try:
            if isinstance(item, dict) and 'pregunta' in item and 'respuesta' in item:
                if item['pregunta'].strip().lower() == pregunta:
                    return item['respuesta']
        except Exception as e:
            logging.warning(f"Error procesando item {item}: {e}")
            continue

    return None



if __name__ == "__main__":
    logging.info("🤖 Bot iniciado...")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(f"Error en el bot: {e}")

