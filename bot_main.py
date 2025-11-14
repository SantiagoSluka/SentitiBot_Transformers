# pip install pyTelegramBotAPI
# Esta librería es un wrapper que facilita la interacción con la API de Telegram para crear bots.
import telebot

# 'json' es una librería estándar de Python, no necesita instalación con pip.
# Se utiliza para codificar y decodificar datos en formato JSON.
import json

# 'os' es una librería estándar de Python, no necesita instalación con pip.
# Proporciona funciones para interactuar con el sistema operativo (como leer archivos o variables de entorno).
import os

# 'logging' es una librería estándar de Python, no necesita instalación con pip.
# Permite registrar mensajes y eventos para depurar y monitorear la aplicación.
import logging

# 'random' es una librería estándar de Python, no necesita instalación con pip.
# Se usa para generar números y secuencias aleatorias.
import random

# 'base64' es una librería estándar de Python, no necesita instalación con pip.
# Proporciona funciones para codificar y decodificar datos en formato Base64.
import base64

# 'tempfile' es una librería estándar de Python, no necesita instalación con pip.
# Permite crear archivos y directorios temporales de forma segura.
import tempfile

# pip install groq
# Este es el cliente oficial de Python para interactuar con la API de Groq.
from groq import Groq

# pip install python-dotenv
# Esta librería se utiliza para cargar variables de entorno desde un archivo .env,
# lo cual es útil para manejar claves de API y configuraciones de forma segura.
from dotenv import load_dotenv

# Esto parece ser un módulo local de tu proyecto (un archivo llamado 'conection.py').
# No se instala con pip. Asegúrate de que el archivo esté en la misma carpeta que tu script principal.
from conection import DatabaseManager

# pip install soundfile
# Librería utilizada para leer y escribir archivos de audio en diferentes formatos.
import soundfile as sf

# pip install numpy
# Es una librería fundamental para la computación científica en Python.
# 'soundfile' y muchas otras librerías de procesamiento de datos y audio dependen de ella para manejar arreglos y matrices numéricas.
import numpy as np

# Carga las variables de entorno de un archivo llamado '.env'.
# Esto te permite guardar datos sensibles como tokens de API y claves secretas 
# fuera de tu código fuente principal, lo cual es una buena práctica de seguridad.
load_dotenv()

#------------------------------------------------------------------------------------

# Configura el sistema de registro (logging) de eventos de la aplicación.
# level=logging.INFO: Establece que se registrarán todos los mensajes de nivel INFO y superiores (INFO, WARNING, ERROR, CRITICAL).
# format='...': Define el formato en que se mostrará cada mensaje de registro: 
#   %(asctime)s -> La fecha y hora en que ocurrió el evento.
#   %(levelname)s -> El nivel del mensaje (ej: INFO, ERROR).
#   %(message)s -> El mensaje de registro en sí.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Crea un objeto 'logger' específico para este módulo. 
# Es una práctica recomendada para organizar mejor los registros si tu aplicación crece.
logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------------

# Obtiene el valor de la variable de entorno 'TELEGRAM_BOT_TOKEN' del sistema (cargada previamente por load_dotenv).
# Este token es la "llave" que identifica y autoriza a tu bot para usar la API de Telegram.
TOKEN_BOT_TELEGRAM = os.getenv('TELEGRAM_BOT_TOKEN')

# Obtiene la clave de la API de Groq de las variables de entorno.
# Esta clave es necesaria para autenticar tus solicitudes a los modelos de lenguaje de Groq.
CLAVE_API_GROQ = os.getenv('GROQ_API_KEY')

# Define una constante que contiene el nombre del modelo de lenguaje de Groq que se usará para tareas de chat.
GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct" 

# Define una constante para el modelo que se usaría en tareas de visión (aunque aquí se usa el mismo que el de chat).
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"   

# Define una constante para el modelo que se usará para transcribir audio a texto. 
# "whisper-large-v3" es un modelo de reconocimiento de voz muy potente de OpenAI.
TRANSCRIPTION_MODEL = "whisper-large-v3"

#------------------------------------------------------------------------------------

# Crea una instancia del bot de Telegram. 
# Se le pasa el token para que la librería 'telebot' sepa a qué bot controlar.
# A partir de ahora, el objeto 'bot' se usará para enviar mensajes, recibir actualizaciones, etc.
bot = telebot.TeleBot(TOKEN_BOT_TELEGRAM)
db_manager = DatabaseManager()
#------------------------------------------------------------------------------------

# Crea una instancia del cliente de Groq. 
# Se le pasa la clave de la API para que pueda realizar solicitudes autenticadas a los modelos de Groq.
cliente_groq = Groq(api_key=CLAVE_API_GROQ)

# Crea una instancia de tu clase personalizada 'DatabaseManager'. 
# Este objeto se encargará de todas las operaciones con la base de datos (conectar, guardar, leer, etc.).
db_manager = DatabaseManager() 

#------------------------------------------------------------------------------------

# Inicializa una lista vacía llamada 'historial'.
# Esta variable probablemente se usará para almacenar el historial de la conversación con el usuario.
historial = [] 

#------------------------------------------------------------------------------------

# Define una función llamada 'detectar_emocion' que acepta un argumento: 'texto'.
def detectar_emocion(texto):
    # Esta es una cadena de documentación (docstring) que explica lo que hace la función.
    """Detecta la emoción principal (Texto)."""
    # Inicia un bloque 'try'. El código dentro de este bloque se ejecutará,
    # y si ocurre un error, el programa no se detendrá, sino que saltará al bloque 'except'.
    try:
        # Realiza una llamada a la API de Groq para obtener una completación de chat.
        respuesta = cliente_groq.chat.completions.create(
            # Especifica qué modelo de lenguaje debe procesar la solicitud.
            model=GROQ_MODEL,
            # Proporciona los mensajes de la conversación. Es una lista de diccionarios.
            messages=[
                # Mensaje de rol "system": Da instrucciones o contexto al modelo. 
                # Aquí se le dice que actúe como un analizador de sentimientos y que responda con una sola palabra.
                {"role": "system", "content": "Eres un analizador de sentimientos. Responde SOLO con una palabra en español (ej: alegria, tristeza, enojo, ansiedad, calma, miedo, neutral)."},
                # Mensaje de rol "user": Es la entrada del usuario, en este caso, el texto que se quiere analizar.
                {"role": "user", "content": texto}
            ]
        )
        # Extrae el contenido del mensaje de la respuesta de la API.
        # respuesta.choices[0]: La API puede dar varias respuestas, elegimos la primera (la más probable).
        # .message.content: Obtenemos el texto de esa respuesta.
        # .strip(): Elimina espacios en blanco al principio y al final.
        # .lower(): Convierte todo el texto a minúsculas para estandarizarlo.
        emocion = respuesta.choices[0].message.content.strip().lower()
        # La función devuelve la emoción detectada.
        return emocion
    # Si ocurre cualquier tipo de error (Exception) en el bloque 'try', se ejecuta este código.
    # 'as e' guarda la información del error en la variable 'e'.
    except Exception as e:
        # Registra un mensaje de error utilizando el logger que configuramos antes.
        # Esto es muy útil para saber qué salió mal durante la ejecución.
        logging.error(f"Error al detectar emoción: {e}")
        # Si hubo un error, la función devuelve un valor por defecto para no interrumpir el programa.
        return "neutral"

# --- NUEVA FUNCIÓN PARA CARGAR EL DATASET ---
# Define una función llamada 'cargar_dataset' que no recibe argumentos.
def cargar_dataset():
    # Es una cadena de documentación (docstring) que explica el propósito de la función.
    """Carga el archivo emociones.json de forma segura."""
    # Inicia un bloque 'try' para manejar posibles errores, como que el archivo no exista.
    try:
        # Abre el archivo 'emociones.json' en modo lectura ('r') y con codificación 'utf-8' (para soportar acentos y caracteres especiales).
        # 'with open(...) as f:' asegura que el archivo se cierre automáticamente al finalizar.
        with open('emociones.json', 'r', encoding='utf-8') as f:
            # Lee el contenido del archivo JSON y lo convierte en un objeto de Python (un diccionario o una lista).
            return json.load(f)
    # Si ocurre cualquier tipo de error (Exception) en el bloque 'try', se ejecuta este código.
    except Exception as e:
        # Registra un mensaje de error detallado usando el logger que configuramos previamente.
        logger.error(f"Error al cargar emociones.json: {e}")
        # Devuelve 'None' para indicar que la carga del dataset falló.
        return None

# --- NUEVA FUNCIÓN PARA BUSCAR EN EL DATASET ---
# Define una función llamada 'buscar_respuesta_en_dataset' que recibe el texto del usuario y el dataset cargado.
def buscar_respuesta_en_dataset(texto, dataset):
    # Docstring que explica la función.
    """
    Busca palabras clave en el texto del usuario para encontrar una respuesta
    predefinida en el dataset. Devuelve una respuesta o None.
    """
    # Si el dataset no se pudo cargar (es None), la función termina inmediatamente.
    if not dataset:
        return None

    # Convierte el texto del usuario a minúsculas para hacer la búsqueda insensible a mayúsculas/minúsculas.
    texto_lower = texto.lower()

    # Crea un diccionario para mapear categorías de intención (claves) con una tupla de palabras clave (valores).
    # Esto permite identificar la intención del usuario de forma sencilla.
    keyword_map = {
        'saludos': ('hola', 'buenas', 'hey'),
        'tristeza': ('triste', 'deprimido', 'mal', 'llorando'),
        'ansiedad': ('ansiedad', 'nervioso', 'preocupado', 'miedo'),
        'estres': ('estrés', 'estresado', 'cansado', 'agotado'),
        'falta_de_motivacion': ('motivado', 'sin ganas', 'no quiero'),
        'autoestima_baja': ('autoestima', 'siento feo', 'no sirvo'),
        'celebracion_logros': ('logré', 'conseguí', 'feliz por', 'gran día'),
        'despedidas': ('chau', 'adiós', 'nos vemos', 'hasta luego')
    }
    
    # Inicia un bucle que recorre cada par (categoría, lista de palabras clave) en 'keyword_map'.
    for categoria_principal, keywords in keyword_map.items():
        # Inicia un segundo bucle que recorre cada palabra clave dentro de la lista actual.
        for keyword in keywords:
            # Comprueba si la palabra clave actual está presente en el texto del usuario (en minúsculas).
            if keyword in texto_lower:
                # Si encuentra una coincidencia, inicializa una lista vacía para guardar las posibles respuestas.
                respuestas_list = []
                # Revisa si la categoría existe directamente en el nivel principal del dataset.
                if categoria_principal in dataset:
                    # Si existe, asigna la lista de respuestas de esa categoría.
                    respuestas_list = dataset[categoria_principal]
                # Si no, revisa si la categoría existe dentro de 'sentimientos_negativos'.
                elif categoria_principal in dataset.get('sentimientos_negativos', {}):
                    # Si existe, asigna la lista de respuestas de esa subcategoría.
                    respuestas_list = dataset['sentimientos_negativos'][categoria_principal]
                
                # Si se encontró una lista de respuestas (no está vacía).
                if respuestas_list:
                    # Elige un objeto de respuesta al azar de la lista.
                    respuesta_obj = random.choice(respuestas_list)
                    # Devuelve el valor asociado a la clave 'texto' de ese objeto de respuesta.
                    return respuesta_obj.get('texto')
    
    # Si después de revisar todas las palabras clave no se encontró ninguna coincidencia, devuelve None.
    return None

# Define una función para generar una respuesta usando la IA de Groq.
def generar_respuesta_ia(texto):
    # Docstring que explica la función.
    """Genera respuesta de TEXTO con Guardrails."""
    # Inicia un bloque 'try' para manejar posibles errores de la API.
    try:
        # Añade el mensaje del usuario al historial de la conversación.
        historial.append({"role": "user", "content": texto})
        
        # Define el "system prompt", que son las instrucciones y reglas que la IA debe seguir.
        # Esto actúa como un "candado de seguridad" (Guardrail) para mantener a la IA en su tema.
        system_prompt = (
            "Eres 'Sentitito', un compañero emocional. "
            "TU MISIÓN: Hablar de sentimientos, bienestar y empatía. "
            "PROHIBICIONES: NO respondas preguntas sobre programación, GitHub, código, matemáticas, "
            "política o datos técnicos complejos. "
            "SI TE PREGUNTAN ESO: Responde amablemente 'Lo siento, mi corazoncito solo entiende de emociones, no de tecnología. ¿Cómo te sientes hoy?'."
        )

        # Realiza la llamada a la API de Groq para obtener una respuesta del chat.
        respuesta = cliente_groq.chat.completions.create(
            # Especifica el modelo de lenguaje a utilizar.
            model=GROQ_MODEL,
            # Envía los mensajes: primero el prompt del sistema y luego todo el historial de la conversación.
            # El asterisco (*) desempaqueta la lista 'historial'.
            messages=[
                {"role": "system", "content": system_prompt},
                *historial 
            ]
        )
        # Extrae el contenido del texto de la primera respuesta generada por la IA.
        # .strip() elimina espacios en blanco al inicio y al final.
        respuesta_texto = respuesta.choices[0].message.content.strip()
        # Añade la respuesta de la IA al historial para mantener el contexto de la conversación.
        historial.append({"role": "assistant", "content": respuesta_texto})
        # Devuelve el texto de la respuesta.
        return respuesta_texto
    # Si ocurre un error durante la llamada a la API.
    except Exception as e:
        # Registra el error.
        logging.error(f"Error IA (Texto): {e}")
        # Devuelve un mensaje de error amigable para el usuario.
        return "Me quedé pensando... ¿podrías repetirlo? 🥺"

    
# --- 2. FUNCIÓN DE VISIÓN CORREGIDA (sin 'self') ---
# Define una función para analizar una imagen que está guardada en el disco.
def analizar_imagen_local(image_path, prompt="Describe la emoción de esta imagen."):
    # Docstring que explica la función.
    """Analiza una imagen guardada localmente."""
    # Inicia un bloque 'try' para manejar errores de archivo o de la API.
    try:
        # Abre el archivo de la imagen en modo lectura binaria ('rb').
        with open(image_path, "rb") as img:
            # Lee el contenido binario de la imagen y lo codifica en formato Base64.
            # .decode("utf-8") convierte los bytes de base64 en una cadena de texto.
            encoded = base64.b64encode(img.read()).decode("utf-8")

        # Realiza la llamada a la API de Groq para el análisis de la imagen.
        respuesta = cliente_groq.chat.completions.create( # Usamos el cliente global
            # Especifica el modelo de visión a utilizar.
            model=VISION_MODEL, # Usamos el modelo de visión estable
            # Construye la lista de mensajes para la API.
            messages=[
                # Prompt del sistema que le da un rol al modelo.
                {"role": "system", "content": "Eres un experto analizando emociones en imágenes. Responde en español."},
                {
                    # Mensaje del usuario, que contiene dos partes.
                    "role": "user",
                    "content": [
                        # La primera parte es el texto del prompt.
                        {"type": "text", "text": prompt},
                        # La segunda parte es la URL de la imagen en formato de datos (data URL).
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded}"}}
                    ]
                }
            ]
        )
        # Extrae y devuelve el texto de la respuesta del modelo.
        return respuesta.choices[0].message.content.strip()
    # Si ocurre un error.
    except Exception as e:
        # Registra el error.
        logger.error(f"Error analizando imagen: {e}")
        # Devuelve un mensaje de error amigable.
        return "No pude ver bien la imagen. 🙈"

# Define una función para convertir un archivo de audio a formato WAV.
def convertir_audio_con_soundfile(input_path):
    # Docstring que explica la función y sus ventajas (no requiere ffmpeg).
    """
    Convierte un archivo de audio (ej: .oga de Telegram) a formato WAV
    usando la librería soundfile. NO requiere ffmpeg.
    """
    # Genera el nombre del archivo de salida, cambiando la extensión a .wav.
    output_path = input_path.rsplit('.', 1)[0] + ".wav"
    # Inicia un bloque 'try' para manejar errores de conversión.
    try:
        # 1. Lee el archivo de audio de entrada, obteniendo los datos de audio y la frecuencia de muestreo.
        data, samplerate = sf.read(input_path)
        
        # 2. Escribe los datos leídos en un nuevo archivo con el formato WAV y el subtipo PCM de 16 bits.
        sf.write(output_path, data, samplerate, format='WAV', subtype='PCM_16')
        
        # Registra un mensaje informativo de que la conversión fue exitosa.
        logger.info(f"Audio convertido de {input_path} a {output_path} usando soundfile.")
        # Devuelve la ruta del nuevo archivo .wav.
        return output_path
    # Si ocurre un error.
    except Exception as e:
        # Registra el error.
        logger.error(f"Error al convertir audio con soundfile: {e}")
        # Devuelve None para indicar que la conversión falló.
        return None
    
# Define una función para transcribir un archivo de audio usando la API de Groq.
def transcribir_audio_groq(audio_path):
    # Docstring que explica la función.
    """
    Envía un archivo de audio a la API de Groq para transcribirlo.
    """
    # Inicia un bloque 'try' para manejar errores de la API.
    try:
        # Abre el archivo de audio en modo lectura binaria ('rb').
        with open(audio_path, "rb") as audio_file:
            # Llama al endpoint de transcripciones de audio de la API de Groq.
            transcription = cliente_groq.audio.transcriptions.create(
                # Especifica el modelo de transcripción a usar (Whisper).
                model=TRANSCRIPTION_MODEL,
                # Pasa el archivo de audio abierto.
                file=audio_file,
                # Solicita que la respuesta sea solo el texto plano.
                response_format="text"
            )
        # Devuelve el texto transcrito, eliminando espacios en blanco extra.
        return transcription.strip()
    # Si ocurre un error.
    except Exception as e:
        # Registra el error.
        logger.error(f"Error al transcribir audio con Groq: {e}")
        # Devuelve un mensaje de error amigable.
        return "No pude entender lo que dijiste en el audio. 🎤"
    

# --- COMANDOS ---

# Este decorador le dice a la librería 'telebot' que la función 'send_welcome' debe ejecutarse
# cuando un usuario envía los comandos /start o /help.
@bot.message_handler(commands=['start',])
def send_welcome(message):
    # El bot responde al mensaje original con un texto de bienvenida.
    bot.reply_to(message, "🤖 ¡Bienvenido a Sentitito Bot!🤖\nSentitito Bot es un asistente emocional diseñado para ayudarte a entender mejor tus sentimientos y emociones.\n ✨ ¿Qué podés hacer ahora?Probá enviar un mensaje, una foto o un audio.Y si querés ver más comandos, usá /help")

@bot.message_handler(commands=['help'])
def send_welcome(message):
    # El bot responde al mensaje original con un texto de bienvenida.
    bot.reply_to(message, "👋 ¡Hola! Soy sentitito, tu bot asistente.🤖\nPuedo ayudarte con varias cosas:\n💬 Responder mensajes comunes\nEscribime lo que quieras y te contesto al toque.\n🧠 Analizar sentimientos\nUsá el comando:\n/sentimiento <mensaje>\nTe digo si el texto transmite alegría, tristeza, enojo, sorpresa, etc.\n📘 Registro de emociones\nCon el comando:\n/diario\nPodés llevar un registro de tus estados emocionales y ver cómo fuiste sintiéndote con el tiempo.\n🖼️ Analizar imágenes\nMandame una foto y te cuento qué veo en ella.\n🎧 Responder audios\n" \
    "Enviame un audio y lo transcribo o te respondo según lo que digas.")

# Decorador que activa la función 'comando_sentimiento' con el comando /sentimiento.
@bot.message_handler(commands=['sentimiento'])
def comando_sentimiento(message):
    # Obtiene el texto del mensaje y elimina el comando "/sentimiento" y espacios extra.
    texto = message.text.replace("/sentimiento", "").strip()
    # Si no queda texto después de limpiar el comando.
    if not texto:
        # Responde con instrucciones sobre cómo usar el comando. 'parse_mode="Markdown"' permite usar formato.
        bot.reply_to(message, "⚠️ Usá: `/sentimiento hoy me siento...`", parse_mode="Markdown")
        # Termina la ejecución de la función.
        return
    # Llama a la función para detectar la emoción en el texto proporcionado.
    emocion = detectar_emocion(texto)
    # Responde al usuario con la emoción detectada, usando formato Markdown para resaltar.
    bot.reply_to(message, f"🧠 *Emoción detectada:* `{emocion}`", parse_mode="Markdown")

# Decorador que activa la función 'comando_diario' con el comando /diario.
@bot.message_handler(commands=['diario'])
def comando_diario(message):
    # Obtiene el ID único del usuario que envió el mensaje.
    user_id = message.from_user.id
    # Llama a la función del gestor de base de datos para obtener los 5 registros más recientes de ese usuario.
    registros = db_manager.obtener_historial_reciente(user_id, limite=5)
    
    # Si la consulta a la base de datos no devuelve ningún registro.
    if not registros:
        # Responde que el diario está vacío.
        bot.reply_to(message, "📓 Tu diario está vacío. ¡Escríbeme algo!")
        # Termina la ejecución de la función.
        return

    # Inicializa una cadena de texto con el título del diario.
    txt = "📓 **Tu Diario Emocional:**\n\n"

# Itera sobre cada registro (fila) devuelto por la base de datos.
    for item in registros:
        # Desempaqueta la tupla (ahora con 3 elementos)
        texto_msg = item[0]
        senti = item[1]
        source = item[2] # 'telegram', 'audio', 'foto', etc.

        # Establece un emoji basado primero en el 'source'
        emoji = "✨" # Emoji por defecto (para texto)
        
        if source == 'audio':
            emoji = "🎙️"
        elif source == 'foto':
            emoji = "📸"
        else:
            # Si es texto (o 'telegram'), usa la lógica de emoción
            if "alegr" in senti: emoji = "😊"
            elif "trist" in senti: emoji = "😢"
            elif "enojo" in senti: emoji = "😠"
            elif "ansied" in senti: emoji = "😰"
            elif "calma" in senti: emoji = "😌"
        
        # Añade una línea formateada al texto de respuesta.
        txt += f"{emoji} *{senti.upper()}*: \"{texto_msg}\"\n"
    
    # Envía el texto completo del diario al usuario.
    bot.reply_to(message, txt, parse_mode="Markdown")

# --- MANEJADORES DE CONTENIDO (Texto e Imagen) --- 
# Este decorador activa la función cuando el bot recibe cualquier mensaje de tipo 'texto' que no sea un comando.
@bot.message_handler(content_types=['text'])
def manejar_mensajes_de_texto(message):
    # Obtiene el ID del usuario.
    user_id = message.from_user.id
    # Obtiene el nombre de usuario o usa "Anonimo" si no tiene uno.
    username = message.from_user.username or "Anonimo"
    # Obtiene el texto del mensaje.
    texto = message.text

    # Llama a la función para detectar la emoción en el texto.
    emocion = detectar_emocion(texto)
    # Guarda el mensaje, usuario, texto y emoción en la base de datos.
    db_manager.save_message_and_user(user_id, username, texto, emocion, 0.0)

    # Carga el dataset de respuestas predefinidas desde el archivo JSON.
    dataset = cargar_dataset()
    # Busca una respuesta predefinida en el dataset usando el texto del usuario.
    respuesta_dataset = buscar_respuesta_en_dataset(texto, dataset)

    # Si se encontró una respuesta en el dataset.
    if respuesta_dataset:
        # Registra en la consola que se usó el dataset.
        logger.info("Respuesta encontrada en el dataset.")
        # La respuesta final será la del dataset.
        respuesta_final = respuesta_dataset
    # Si no se encontró una respuesta en el dataset.
    else:
        # Registra que se va a usar la IA.
        logger.info("No se encontró respuesta en el dataset. Usando la IA.")
        # Genera una respuesta usando el modelo de lenguaje de Groq.
        respuesta_final = generar_respuesta_ia(texto)
    
    # Envía la respuesta final (ya sea del dataset o de la IA) al usuario.
    bot.reply_to(message, respuesta_final)

# --- 4. MANEJADOR DE FOTOS (¡El que faltaba!) ---
# Decorador que activa esta función cuando el usuario envía una foto.
@bot.message_handler(content_types=['photo'])
def manejar_fotos(message):
    # Envía un mensaje inmediato para que el usuario sepa que se está procesando la foto.
    bot.reply_to(message, "Viendo tu foto... 📸 Dame un segundo.")
    
    # Inicia un bloque 'try' para manejar cualquier error durante el proceso.
    try:
        # 1. Obtiene el ID del archivo de la foto. message.photo[-1] se refiere a la foto de mayor resolución.
        file_id = message.photo[-1].file_id 
        # Obtiene la información del archivo, incluyendo la ruta para descargarlo.
        file_info = bot.get_file(file_id)
        # Descarga el archivo de la foto desde los servidores de Telegram.
        downloaded_file = bot.download_file(file_info.file_path)

        # 2. Define un nombre temporal para el archivo de la foto.
        temp_path = f"temp_{file_id}.jpg"
        # Abre el archivo temporal en modo escritura binaria ('wb').
        with open(temp_path, 'wb') as new_file:
            # Escribe los datos de la foto descargada en el archivo temporal.
            new_file.write(downloaded_file)

        # 3. Determina el prompt para la IA. Si la foto tiene un pie de foto (caption), lo usa. Si no, usa uno por defecto.
        prompt = message.caption if message.caption else "Qué emoción transmite esta imagen?"
        
        # Llama a la función que analiza la imagen local usando la API de Groq.
        analisis = analizar_imagen_local(temp_path, prompt)
        
        # 4. Responde al usuario con el análisis de la imagen.
        bot.reply_to(message, f"👁️ *Análisis de la foto:*\n{analisis}")

        # Para guardar en Diario:
        try:
            logger.info("Guardando análisis de foto en el diario...")
            # Detectamos la emoción general del texto de análisis
            emocion_foto = detectar_emocion(analisis)
            user_id = message.from_user.id
            username = message.from_user.username or "Anonimo"
            # Creamos un texto descriptivo para el diario
            texto_para_guardar = f"[Foto] {analisis}"
            
            # Guardamos en la BD usando el nuevo parámetro 'source'
            db_manager.save_message_and_user(
                user_id, username, texto_para_guardar, emocion_foto, 0.0, source='foto'
            )
        except Exception as e:
            logger.error(f"Error al guardar foto en diario: {e}")

        # 5. Elimina el archivo de imagen temporal del disco para limpiar.
        os.remove(temp_path)

    # Si ocurre algún error en el proceso.
    except Exception as e:
        # Registra el error.
        logger.error(f"Error procesando foto: {e}")
        # Envía un mensaje de error al usuario.
        bot.reply_to(message, "¡Ups! No pude analizar esa imagen. Intenta con otra.")

# --- 5. MANEJADOR DE AUDIOS (¡PORFIN!) ---
# Decorador que activa la función si se recibe un audio o una nota de voz.
@bot.message_handler(content_types=['audio', 'voice'])
def manejar_audio(message):
    # Envía un mensaje de espera al usuario.
    bot.reply_to(message, "Escuchando tu audio... 🎙️ Dame un momento.")
    # Inicia un bloque 'try' para manejar errores.
    try:
        # Obtiene el ID del archivo, ya sea una nota de voz (voice) o un archivo de audio (audio).
        file_id = message.voice.file_id if message.voice else message.audio.file_id
        # Obtiene la información del archivo para la descarga.
        file_info = bot.get_file(file_id)
        # Descarga el archivo de audio.
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Crea un directorio temporal que se eliminará automáticamente al salir de este bloque.
        with tempfile.TemporaryDirectory() as tmpdir:
            # Crea la ruta completa para el archivo de entrada dentro del directorio temporal.
            input_path = os.path.join(tmpdir, "audio.oga")
            # Abre el archivo temporal en modo escritura binaria.
            with open(input_path, 'wb') as new_file:
                # Escribe los datos del audio descargado.
                new_file.write(downloaded_file)

            # Llama a la función para convertir el archivo .oga a .wav.
            wav_path = convertir_audio_con_soundfile(input_path)
            # Si la conversión falla (devuelve None).
            if not wav_path:
                # Informa al usuario y termina la función.
                bot.reply_to(message, "No pude procesar el formato de tu audio. 😥")
                return

            # Ahora transcribe el archivo .wav convertido.
            texto_transcrito = transcribir_audio_groq(wav_path)
            
            # Si la transcripción devuelve el mensaje de error de la función.
            if "No pude entender" in texto_transcrito:
                # Envía ese error al usuario y termina la función.
                bot.reply_to(message, texto_transcrito)
                return

            # Responde al usuario con el texto que se entendió del audio.
            bot.reply_to(message, f"📜 *Entendí esto:*\n\n> _{texto_transcrito}_", parse_mode="Markdown")

            # Para guardar en Diario:
            try:
                logger.info("Guardando transcripción de audio en el diario...")
                # Detectamos la emoción del texto transcrito
                emocion_audio = detectar_emocion(texto_transcrito)
                user_id = message.from_user.id
                username = message.from_user.username or "Anonimo"
                
                # Guardamos en la BD usando el nuevo parámetro 'source'
                db_manager.save_message_and_user(
                    user_id, username, texto_transcrito, emocion_audio, 0.0, source='audio'
                )
            except Exception as e:
                logger.error(f"Error al guardar audio en diario: {e}")

            # Usa el texto transcrito para generar una respuesta conversacional con la IA.
            respuesta_final_ia = generar_respuesta_ia(texto_transcrito)
            # Envía la respuesta de la IA al usuario.
            bot.reply_to(message, respuesta_final_ia)

    # Si ocurre cualquier error en el proceso de audio.
    except Exception as e:
        # Registra el error.
        logger.error(f"Error procesando audio: {e}")
        # Envía un mensaje de error genérico al usuario.
        bot.reply_to(message, "¡Vaya! Hubo un problema con tu audio. ¿Puedes intentar de nuevo?")



# Este bloque de código se ejecuta solo si el script es ejecutado directamente (no si es importado como un módulo).
if __name__ == "__main__":
    # Registra un mensaje indicando que el bot se está iniciando.
    logger.info("🤖 Iniciando Sentitito Bot...")
    # Llama a un método para probar la conexión con la base de datos.
    if db_manager.test_connection():
        # Si la conexión es exitosa, lo registra.
        logger.info("✅ Base de datos conectada.")
    else:
        # Si la conexión falla, registra una advertencia.
        logger.warning("⚠️ SIN BASE DE DATOS.")
    
    # Inicia el bot. bot.polling() hace que el bot esté constantemente preguntando a Telegram si hay nuevos mensajes.
    # none_stop=True asegura que el bot continúe funcionando incluso si ocurre un error menor.
    bot.polling(none_stop=True)
    