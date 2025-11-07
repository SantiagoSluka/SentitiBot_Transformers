import mysql.connector
from mysql.connector import Error
import os
import logging
from dotenv import load_dotenv


load_dotenv()
logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Maneja toda la conexión y escritura en la BD siguiendo POO.
    """
    
    def __init__(self):
        """Lee las variables de la BD al crear el objeto."""
        self.db_host = os.getenv('DB_HOST')
        self.db_user = os.getenv('DB_USER')
        self.db_password = os.getenv('DB_PASSWORD')
        self.db_name = os.getenv('DB_NAME')
        
        # Comprobar que todas las variables existan
        if not all([self.db_host, self.db_user, self.db_password, self.db_name]):
            logger.error("Error CRÍTICO: Faltan variables de entorno de la base de datos.")
            # raise es mejor que return, detiene la ejecución si falta algo vital
            raise ValueError("Faltan variables de entorno de la BD (DB_HOST, DB_USER, etc.)")

    def create_connection(self):
        """Crea y devuelve una nueva conexión a la BD."""
        try:
            connection = mysql.connector.connect(
                host=self.db_host,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name
            )
            if connection.is_connected():
                return connection
        except Error as e:
            logger.error(f"Error al crear conexión a MySQL: {e}")
            return None

    def test_connection(self):
        """Prueba la conexión y la cierra."""
        conn = self.create_connection()
        if conn:
            conn.close()
            logger.info("✅ Conexión de prueba a la base de datos exitosa.")
            return True
        return False

    def save_message_and_user(self, user_id, username, text, sentiment, score):
        """
        Guarda el usuario (si es nuevo) y el mensaje en la BD.
        Este método contiene toda la lógica de guardado.
        """
        conn = None
        cursor = None
        try:
            conn = self.create_connection()
            if not conn:
                logger.error("No se pudo crear conexión para guardar mensaje.")
                return

            cursor = conn.cursor()
            
            # Revisar y crear usuario si no existe
            cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
            if cursor.fetchone() is None:
                # Si no existe, lo creamos.
                cursor.execute(
                    "INSERT INTO users (user_id, username) VALUES (%s, %s)",
                    (user_id, username)
                )
            
            # Insertar el mensaje
            cursor.execute(
                """
                INSERT INTO messages (user_id, text, sentiment, score)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, text, sentiment, score)
            )
            
            conn.commit() # Confirmamos los cambios
            logger.info(f"Mensaje de {user_id} guardado en la BD.")

        except Error as e:
            logger.error(f"Error de BD al guardar mensaje: {e}")
            if conn:
                conn.rollback() # Revertir cambios si algo salió mal
        finally:
            # Siempre cerrar la conexión y el cursor
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()