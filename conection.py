import mysql.connector
from mysql.connector import Error
from textblob import TextBlob
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

def test_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root', 
            password='@MtGIoPcpixel423',
            database='sentitito_bot'
        )

        if connection.is_connected():
            print("✅ Conexión exitosa a la base de datos MySQL")
            connection.close()
            return True

    except Error as e:
        print(f"❌ Error al conectar: {e}")
        return False
if __name__ == "__main__":
    if test_connection():
        print("La conexión a la base de datos fue exitosa.")

    else:
        print("No se pudo conectar a la base de datos.")


def close_connection(connection):
    if connection.is_connected():
        connection.close()
        print("🔒 Conexión cerrada correctamente")

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
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    sentiment, score = analyze_sentiment(text)
    response = f"🧠 Sentimiento: {sentiment.upper()} (puntaje: {score})"

    await update.message.reply_text(response, parse_mode="Markdown")

conn = test_connection()
if conn:
        cursor = conn.cursor()
cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user.id,))
if cursor.fetchone() is None:
            cursor.execute(
                "INSERT INTO users (user_id, username) VALUES (%s, %s)",
                (user_id, username)
            )
cursor.execute("""
            INSERT INTO messages (user_id, text, sentiment, score)
            VALUES (%s, %s, %s, %s)
        """, (user.id, text, sentiment, score))

conn.commit()
cursor.close()
conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Soy tu bot analizador de sentimientos . Mandame un mensaje ")

def main():
    TOKEN = '8308418084:AAH0FuFFB5sA0yt9g3wPX23iAIGbGF8VLIs'

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print(" Bot en marcha... Ctrl+C para detenerlo.")
    app.run_polling()



if __name__ == "__main__":
    main()