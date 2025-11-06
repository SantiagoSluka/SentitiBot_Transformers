import mysql.connector
from mysql.connector import Error
from textblob import TextBlob
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler
import os
import logging
from dotenv import load_dotenv

# --- 1. Cargar el .env PRIMERO ---
# Esto lee tu archivo .env
load_dotenv()

# --- 2. Configuración de Logging ---
# Esto nos ayuda a ver errores
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- 3. Leer TODAS las variables de entorno ---
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
# Usamos el nombre de variable correcto que me mostraste
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') 

# --- 4. Funciones de Base de Datos CORREGIDAS ---

def test_connection():
    """
    Prueba la conexión y la cierra.
    Solo se usa al inicio para ver si la BD está viva.
    """
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        if connection.is_connected():
            logger.info("✅ Conexión de prueba a la base de datos exitosa.")
            connection.close()
            return True
    except Error as e:
        logger.error(f"❌ Error al probar la conexión: {e}")
        return False

def create_connection():
    """
    Crea y DEVUELVE una nueva conexión.
    NO la cierra. La usaremos para guardar datos.
    """
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        if connection.is_connected():
            return connection
    except Error as e:
        logger.error(f"❌ Error al crear una nueva conexión: {e}")
        return None

# --- 5. Tu función de Sentimiento (sin cambios) ---

def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity

    if polarity > 0.1:
        sentiment = "positive"
    elif polarity < -0.1:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return sentiment, round(polarity, 3)

# --- 6. Manejadores de Telegram ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /start."""
    await update.message.reply_text("¡Hola! Soy tu bot analizador de sentimientos. Mándame un mensaje.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    ¡LA PARTE MÁS IMPORTANTE!
    Se ejecuta CADA VEZ que un usuario envía un mensaje.
    """
    
    # 1. Obtenemos las variables que SÍ existen aquí
    user = update.effective_user
    text = update.message.text

    if not user or not text:
        return

    # 2. Analizamos el sentimiento
    sentiment, score = analyze_sentiment(text)
    response = f"🧠 Sentimiento: {sentiment.upper()} (puntaje: {score})"

    # 3. Respondemos al usuario (quitado parse_mode, no es necesario)
    await update.message.reply_text(response)

    # 4. --- LÓGICA DE BASE DE DATOS (EL LUGAR CORRECTO) ---
    # Todo el código que tenías suelto, ahora va aquí.
    conn = None
    cursor = None
    try:
        # Usamos la nueva función que SÍ devuelve una conexión
        conn = create_connection() 
        
        if conn:
            cursor = conn.cursor()
            
            # Revisamos si el usuario existe (usando user.id)
            cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user.id,))
            
            if cursor.fetchone() is None:
                # Si no existe, lo creamos.
                # (Aquí definimos 'username', que también faltaba)
                username = user.username or user.full_name or "N/A"
                cursor.execute(
                    "INSERT INTO users (user_id, username) VALUES (%s, %s)",
                    (user.id, username) # Usamos las variables correctas
                )
            
            # Insertamos el mensaje
            cursor.execute(
                """
                INSERT INTO messages (user_id, text, sentiment, score)
                VALUES (%s, %s, %s, %s)
                """,
                (user.id, text, sentiment, score) # Usamos las variables correctas
            )
            
            conn.commit() # Confirmamos los cambios
            logger.info(f"Mensaje de {user.id} guardado en la BD.")

        else:
            logger.error("No se pudo conectar a la BD para guardar el mensaje.")

    except Error as e:
        logger.error(f"Error de base de datos en handle_message: {e}")
        if conn:
            conn.rollback() # Revertir cambios si algo salió mal
    finally:
        # Esto es MUY importante: siempre cerrar la conexión y el cursor
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
            logger.info("🔒 Conexión de mensaje cerrada.")
    # --- FIN DE LÓGICA DE BASE DE DATOS ---


# --- 7. Función Principal (main) CORREGIDA ---

def main():
    """Configura y corre el bot."""
    
    # Verificamos que las variables de entorno se cargaron
    if not TELEGRAM_TOKEN:
        logger.error("Error CRÍTICO: No se encontró la variable de entorno TELEGRAM_BOT_TOKEN.")
        logger.error("Asegúrate de que tu archivo .env está bien configurado y se llama '.env'")
        return
        
    if not DB_HOST or not DB_USER or not DB_PASSWORD or not DB_NAME:
        logger.error("Error CRÍTICO: Faltan variables de entorno de la base de datos (DB_HOST, DB_USER, etc.).")
        return

    # Primero, probamos la conexión ANTES de arrancar el bot
    if not test_connection():
        logger.error("El bot no se iniciará hasta que la conexión a la base de datos funcione.")
        return # Salir del script si no hay BD

    # Usamos la variable TELEGRAM_TOKEN leída del .env
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Añadir manejadores
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🤖 Bot en marcha... Ctrl+C para detenerlo.")
    app.run_polling()


# --- 8. El inicio del script (sin cambios) ---

if __name__ == "__main__":
    main()