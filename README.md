# Sentitito Bot 🤖

**Sentitito Bot** es un bot de Telegram diseñado para ser un **asistente emocional personal**, capaz de analizar **sentimientos**, **emociones faciales**, **imágenes** y **audios** enviados por el usuario.  
Forma parte del **Capstone Project** del programa **Samsung Innovation Campus (SIC)**.

---

## 🧠 ¿Qué hace?
- Recibe mensajes del usuario en Telegram
- Analiza el **tono emocional** y la **polaridad**
- Interpreta emociones en **rostros** mediante análisis de imágenes
- Analiza el contenido emocional de **imágenes generales**
- Transcribe **audios** usando SoundFile + NumPy
- Devuelve respuestas como un **asistente emocional personal**
- Registra datos en **MySQL** y en un **dataset JSON**

---

## Tecnologías utilizadas
| Tecnología | Uso |
|-----------|-----|
| **Python** | Lógica principal del bot |
| **Groq + LLaMA-3** | Análisis semántico del lenguaje |
| **Groq Vision / Audio** | Análisis facial, imágenes y transcripción |
| **SoundFile + NumPy** | Procesamiento de audio |
| **MySQL** | Almacenamiento de datos |
| **Dataset JSON** | Registro liviano para métricas |

---

## Requisitos
- Tener **Telegram** instalado en el teléfono o PC  
- Tener conexión a internet  
- Buscar el bot o acceder mediante link directo  

---

## 🚀 Cómo usarlo
1. Abrí Telegram  
2. Buscá **Sentitito Bot** o accede desde AQUi 
3. Para analizar texto: /sentimiento + lo que deseas comentar
4. Para analizar imágenes o emociones faciales: subi una foto al chat
5. 5. Para transcribir audio y analisarlo: apreta el botoncito del microfono y empeza a hablar


---

## 🎯 Objetivo del proyecto
En este proyecto buscamos:
- Explorar cómo la IA puede **acompañar emocionalmente** a los usuarios  
- Integrar **bot + IA + base de datos + dataset JSON** en un sistema funcional real  
- Procesar texto, voz e imágenes en un asistente accesible desde Telegram  

---

## 🧑‍💻 Equipo
Equipo Transformers: 
- Gael Martiniano Baroni
- Leandro Nuñez
- Santiago Ivan Sluka Antelo
- Alexis Kevin Bellido
**Capstone Project — Samsung Innovation Campus (SIC)**

---

## ▶️ Cómo ejecutarlo

### 1️⃣ Descargá e instalá los programas necesarios
Asegurate de tener instalados:

- **Python 3.10+**
- **MySQL Server + MySQL Workbench**
- **Git** (opcional pero recomendado)

#### 📥 Python  
https://www.python.org/downloads/

#### 📥 MySQL  
https://dev.mysql.com/downloads/



---

### 2️⃣ Clonar el repositorio

---

### 3️⃣ Instalar dependencias
pip install -r requirements.txt

---

###4️⃣ Configurar las claves del bot y la base de datos

Creá un archivo .env en la carpeta del proyecto:
TELEGRAM_TOKEN= 'tu_token_de_telegram'
GROQ_API_KEY= 'tu_api_key'
MYSQL_USER= 'root'
MYSQL_PASSWORD= 'tu_password'
MYSQL_HOST= 'localhost'
MYSQL_DATABASE= 'sentitito'

---

###5️⃣ Configurar la base de datos

Ingresá a MySQL Workbench y ejecutá el query de creación de tablas
(recomendamos ejecutar query por query para evitar algun error en la creacion)

---

###6️⃣ Ejecutar el bot
"python main.py"

---

7️⃣ Probar funciones

Texto: /sentimiento Hola, hoy me siento bien

Imagen: subir una foto

Emoción facial: sacate una foto de tu cara o sube una foto con un rostro y analizara

Audio: solamente debes enviar el audio

----

## Estado del proyecto
En construcción

