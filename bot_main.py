<<<<<<< HEAD
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
    # Recorre cada elemento del dataset
    for item in dataset:
        try:
            # Compara la pregunta del usuario con la del dataset (normalizada)
            if item['pregunta'].strip().lower() == pregunta:
                # Si hay coincidencia exacta, retorna la respuesta
                return item['respuesta']
        except (KeyError, AttributeError) as e:
            logging.warning(f"Formato inválido en item del dataset: {item}")
            continue
    # Si no encuentra coincidencia, retorna None
    return None

@bot.message_handler(func=lambda message: True)
def manejar_mensaje(message):
    texto = message.text
    
    # Si es el comando /sentimiento, procesar como análisis de sentimiento
    if texto.startswith('/sentimiento'):
        comando_sentimiento(message)
        return
        
    # Para otros mensajes, buscar en dataset y usar IA
    dataset = cargar_dataset()
    respuesta = buscar_en_dataset(texto, dataset)
    
    if respuesta:
        bot.reply_to(message, respuesta)
    else:
        respuesta_ia = generar_respuesta_ia(texto)
        bot.reply_to(message, respuesta_ia)

if __name__ == "__main__":
    logging.info("🤖 Bot iniciado...")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(f"Error en el bot: {e}")


=======
import telebot  
import requests
import json
import os
from groq import Groq
import base64
from dotenv import load_dotenv
import random
#Para api de groq, telegram y a futuro qwem si llegamos
load_dotenv()

TOKEN_BOT_TELEGRAM = os.getenv('TELEGRAM_BOT_TOKEN')
CLAVE_API_GROQ = os.getenv('GROQ_API_KEY')
DATASET_PATH = 'emociones.json'

bot = telebot.TeleBot(TOKEN_BOT_TELEGRAM)
cliente_groq = Groq(api_key=CLAVE_API_GROQ) 

def cargar_dataset():
	try:
		with open(DATASET_PATH, 'r', encoding='utf-8') as f:
			return json.load(f)
	except Exception:
		return []
	

# def detectar_emocion(texto):
#     try:
#         respuesta = cliente_groq.chat.completions.create(
#             model="llama3-8b-8192",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": (
#                         "Sos un analizador emocional. Respondé SOLO con una palabra "
#                         "que describa la emoción principal (ej: alegria, tristeza, enojo, ansiedad, calma, miedo, neutral). "
#                         "Si no podés identificarla, respondé 'neutral'."
#                     )
#                 },
#                 {"role": "user", "content": texto}
#             ]
#         )
#         emocion = respuesta.choices[0].message["content"].strip().lower()
#         return emocion
#     except Exception as e:
#         print("Error al detectar emoción:", e)
#         return None



# def generar_respuesta_ia(texto):
#     try:
#         respuesta = cliente_groq.chat.completions.create(
#             model="llama3-70b-8192",
#             messages=[
#                 {"role": "system", "content": "Sos un asistente empático y conversacional."},
#                 {"role": "user", "content": texto}
#             ]
#         )
#         return respuesta.choices[0].message["content"].strip()
#     except Exception as e:
#         print("Error al generar respuesta IA:", e)
#         return "Hubo un error generando la respuesta 😅"



# @bot.message_handler(commands=['sentimiento'])
# def comando_sentimiento(message):
#     texto = message.text.replace("/sentimiento", "").strip()

#     if not texto:
#         bot.reply_to(message, "⚠️ Usá el comando así:\n`/sentimiento hoy me siento bien`", parse_mode="Markdown")
#         return

#     emocion = detectar_emocion(texto)
#     dataset = cargar_dataset()

#     if emocion and emocion in dataset.get("emociones", {}):
#         respuesta = random.choice(dataset["emociones"][emocion])
#         bot.reply_to(message, f"Detecté emoción: *{emocion}*\n\n{respuesta}", parse_mode="Markdown")

#     else:
#         # Si no hay emoción conocida, usa Groq como chat normal
#         respuesta_ia = generar_respuesta_ia(texto)
#         bot.reply_to(message, f"*IA:* {respuesta_ia}", parse_mode="Markdown")



# @bot.message_handler(func=lambda message: True)
# def manejar_mensaje(message):
#     bot.reply_to(message, "Usá /sentimiento seguido de tu mensaje para analizar lo que sentís 😊")


# if __name__ == "__main__":
#     print("🤖 Bot iniciado...")
#     bot.polling()





# Cambio def buscar en dataset
def buscar_en_dataset(pregunta, dataset):
	pregunta = pregunta.strip().lower()
	# Recorre cada elemento del dataset
	for item in dataset:
		# Compara la pregunta del usuario con la del dataset (normalizada)
		print(type(item), item)
		if item['pregunta'].strip().lower() == pregunta:
			# Si hay coincidencia exacta, retorna la respuesta
			return item['respuesta']
	# Si no encuentra coincidencia, retorna None
	return None
import random




@bot.message_handler(func=lambda message: True)
def manejar_mensaje(message):
	pregunta = message.text
	dataset = cargar_dataset()
	
	# Primero intenta buscar en el dataset local
	respuesta = buscar_en_dataset(pregunta, dataset)
	
	if respuesta:
		bot.reply_to(message, respuesta)
	else:
		# Si no encuentra en el dataset, consulta a Groq
		try:
			respuesta_groq = cliente_groq.chat.completions.create(
				model="gpt-4o",
				messages=[
					{"role": "system", "content": "Eres un asistente útil. y respondes en español."
					" tambien tienes en cuenta las emociones de la persona que te habla."
					" si la persona esta triste,"
					" tu respuesta debe ser empatica y alentadora."
					" si la persona esta feliz, tu respuesta debe ser alegre y positiva."
					" si la persona esta enojada, tu respuesta debe ser calmada y conciliadora."},
					{"role": "user", "content": pregunta}
				]
			)
			bot.reply_to(message, respuesta_groq.choices[0].message['content'])
		except Exception as e:
			bot.reply_to(message, "Lo siento, no pude procesar tu solicitud en este momento.")
if __name__ == "__main__":
	bot.polling()


>>>>>>> dec713ce0b38abd72ac1bb03873a514550d85e16
