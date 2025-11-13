import mysql.connector
from mysql.connector import Error
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class DatabaseManager:
    
    def __init__(self):
        self.db_host = os.getenv('DB_HOST')
        self.db_user = os.getenv('DB_USER')
        self.db_password = os.getenv('DB_PASSWORD')
        self.db_name = os.getenv('DB_NAME')
        
    def create_connection(self):
        try:
            connection = mysql.connector.connect(
                host=self.db_host,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name
            )
            return connection
        except Error as e:
            logger.error(f"Error al conectar a MySQL: {e}")
            return None

    def test_connection(self):
        conn = self.create_connection()
        if conn:
            conn.close()
            return True
        return False

    def save_message_and_user(self, user_id, username, text, sentiment, score):
        conn = None
        cursor = None
        try:
            conn = self.create_connection()
            if not conn: return

            cursor = conn.cursor()
            
            # 1. Revisar/Crear Usuario (user_id es BIGINT)
            cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
            if cursor.fetchone() is None:
                cursor.execute(
                    "INSERT INTO users (user_id, username) VALUES (%s, %s)",
                    (user_id, username)
                )
            
            # 2. Insertar mensaje (Guardamos el sentimiento tal cual viene: 'alegria', 'tristeza')
            cursor.execute(
                """
                INSERT INTO messages (user_id, text, sentiment, score, source)
                VALUES (%s, %s, %s, %s, 'telegram')
                """,
                (user_id, text, sentiment, score)
            )
            
            conn.commit()
            logger.info(f"✅ Mensaje guardado: {sentiment}")

        except Error as e:
            logger.error(f"❌ Error SQL al guardar: {e}")
            if conn: conn.rollback()
        finally:
            if cursor: cursor.close()
            if conn and conn.is_connected(): conn.close()

    def obtener_historial_reciente(self, user_id, limite=5):
        conn = None
        cursor = None
        resultados = []
        try:
            conn = self.create_connection()
            if not conn: return []

            cursor = conn.cursor()
            
            # Ordenamos por message_id que es tu Primary Key
            query = """
                SELECT text, sentiment 
                FROM messages 
                WHERE user_id = %s 
                ORDER BY message_id DESC 
                LIMIT %s
            """
            cursor.execute(query, (user_id, limite))
            resultados = cursor.fetchall() 
            
        except Error as e:
            logger.error(f"Error al leer historial: {e}")
        finally:
            if cursor: cursor.close()
            if conn and conn.is_connected(): conn.close()
            
        return resultados