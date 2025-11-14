# Importa el conector oficial de Python para bases de datos MySQL.
import mysql.connector
# Importa específicamente la clase 'Error' del conector para poder capturar errores de la base de datos.
from mysql.connector import Error
# Importa la librería 'os' para interactuar con el sistema operativo, principalmente para leer variables de entorno.
import os
# Importa la librería estándar de logging para registrar eventos y errores.
import logging
# Importa la función 'load_dotenv' de la librería python-dotenv para cargar variables desde un archivo .env.
from dotenv import load_dotenv

# Ejecuta la función para cargar las variables definidas en el archivo .env en el entorno del script.
load_dotenv()
# Obtiene una instancia del logger para este módulo, permitiendo registrar mensajes específicos de esta parte del código.
logger = logging.getLogger(__name__)

# Define una clase llamada 'DatabaseManager' para encapsular toda la lógica de la base de datos.
class DatabaseManager:
    
    # El método constructor de la clase, que se ejecuta automáticamente al crear un objeto de tipo DatabaseManager.
    def __init__(self):
        # Lee el valor de la variable de entorno 'DB_HOST' y lo asigna al atributo 'db_host' de la instancia.
        self.db_host = os.getenv('DB_HOST')
        # Lee el valor de la variable de entorno 'DB_USER' y lo asigna al atributo 'db_user'.
        self.db_user = os.getenv('DB_USER')
        # Lee el valor de la variable de entorno 'DB_PASSWORD' y lo asigna al atributo 'db_password'.
        self.db_password = os.getenv('DB_PASSWORD')
        # Lee el valor de la variable de entorno 'DB_NAME' y lo asigna al atributo 'db_name'.
        self.db_name = os.getenv('DB_NAME')
        
    # Define un método para crear y devolver una conexión a la base de datos.
    def create_connection(self):
        # Inicia un bloque 'try' para manejar posibles errores de conexión.
        try:
            # Intenta establecer una conexión con la base de datos usando las credenciales almacenadas en los atributos de la clase.
            connection = mysql.connector.connect(
                host=self.db_host,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name
            )
            # Si la conexión es exitosa, devuelve el objeto de conexión.
            return connection
        # Si ocurre un error de tipo 'Error' (de mysql.connector) durante la conexión.
        except Error as e:
            # Registra un mensaje de error detallado en el log.
            logger.error(f"Error al conectar a MySQL: {e}")
            # Devuelve 'None' para indicar que la conexión falló.
            return None

    # Define un método para verificar si la conexión a la base de datos se puede establecer correctamente.
    def test_connection(self):
        # Llama a su propio método 'create_connection' para intentar conectarse.
        conn = self.create_connection()
        # Si el objeto de conexión 'conn' no es 'None' (es decir, la conexión fue exitosa).
        if conn:
            # Cierra la conexión para liberar los recursos.
            conn.close()
            # Devuelve 'True' para indicar que la prueba fue exitosa.
            return True
        # Si 'conn' es 'None', devuelve 'False'.
        return False

    # Define un método para guardar el mensaje de un usuario y, si es necesario, crear el registro del usuario.
    def save_message_and_user(self, user_id, username, text, sentiment, score, source='telegram'):
        # Inicializa las variables de conexión y cursor a 'None' para que existan fuera del bloque 'try'.
        conn = None
        cursor = None
        # Inicia un bloque 'try' para manejar cualquier error durante las operaciones SQL.
        try:
            # Obtiene un objeto de conexión.
            conn = self.create_connection()
            # Si la conexión falló, termina la ejecución del método.
            if not conn: return

            # Crea un objeto cursor a partir de la conexión, que permite ejecutar comandos SQL.
            cursor = conn.cursor()
            
            # 1. Ejecuta una consulta para verificar si ya existe un usuario con el 'user_id' proporcionado.
            cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
            # Intenta obtener un resultado de la consulta. Si no hay filas, devuelve 'None'.
            if cursor.fetchone() is None:
                # Si el usuario no existe, ejecuta un comando 'INSERT' para crearlo en la tabla 'users'.
                cursor.execute(
                    "INSERT INTO users (user_id, username) VALUES (%s, %s)",
                    (user_id, username)
                )
            
            # 2. Ejecuta un comando 'INSERT' para guardar el nuevo mensaje en la tabla 'messages'.
            cursor.execute(
                """
                INSERT INTO messages (user_id, text, sentiment, score, source)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (user_id, text, sentiment, score, source)
            )
            
            # Confirma y guarda permanentemente todas las operaciones SQL realizadas desde el último commit.
            conn.commit()
            # Registra un mensaje informativo de que el mensaje se guardó con éxito.
            logger.info(f"✅ Mensaje guardado: {sentiment}")

        # Si ocurre un error SQL durante las operaciones en el bloque 'try'.
        except Error as e:
            # Registra el error SQL específico.
            logger.error(f"❌ Error SQL al guardar: {e}")
            # Si la conexión existe, revierte cualquier cambio hecho en la transacción actual para mantener la integridad de los datos.
            if conn: conn.rollback()
        # El bloque 'finally' se ejecuta siempre, haya ocurrido un error o no.
        finally:
            # Si el cursor fue creado, lo cierra para liberar recursos.
            if cursor: cursor.close()
            # Si la conexión fue creada y sigue abierta, la cierra.
            if conn and conn.is_connected(): conn.close()

    # Define un método para obtener los últimos mensajes de un usuario específico.
    def obtener_historial_reciente(self, user_id, limite=5):
        # Inicializa las variables de conexión, cursor y resultados.
        conn = None
        cursor = None
        resultados = []
        # Inicia un bloque 'try' para manejar errores de lectura de la base de datos.
        try:
            # Obtiene una conexión a la base de datos.
            conn = self.create_connection()
            # Si la conexión falla, devuelve una lista vacía.
            if not conn: return []

            # Crea un objeto cursor para ejecutar la consulta.
            cursor = conn.cursor()
            
            # Define la consulta SQL para seleccionar el texto y el sentimiento de los mensajes de un usuario.
            # Los ordena por 'message_id' en orden descendente (los más nuevos primero) y limita el número de resultados.
            query = """
                SELECT text, sentiment, source
                FROM messages 
                WHERE user_id = %s 
                ORDER BY message_id DESC 
                LIMIT %s
            """
            # Ejecuta la consulta, pasando los parámetros de forma segura para evitar inyección SQL.
            cursor.execute(query, (user_id, limite))
            # Recupera todas las filas del resultado de la consulta y las guarda en la variable 'resultados'.
            resultados = cursor.fetchall() 
            
        # Si ocurre un error SQL.
        except Error as e:
            # Registra el error.
            logger.error(f"Error al leer historial: {e}")
        # El bloque 'finally' se asegura de que la conexión y el cursor se cierren.
        finally:
            # Cierra el cursor si existe.
            if cursor: cursor.close()
            # Cierra la conexión si existe y está abierta.
            if conn and conn.is_connected(): conn.close()
            
        # Devuelve la lista de resultados (puede estar vacía si no se encontraron mensajes o si hubo un error).
        return resultados