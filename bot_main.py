import telebot  
import requests
import json
import os
from groq import Groq
import base64
from dotenv import load_dotenv
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
		return [print("susto")]