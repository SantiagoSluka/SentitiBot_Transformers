# Sentitito Bot 🤖

**Sentitito Bot** es un bot de Telegram diseñado para ser un **asistente emocional personal**, capaz de analizar **sentimientos**, **emociones faciales**, **imágenes** y **audios** enviados por el usuario.  
Forma parte del **Capstone Project** del programa **Samsung Innovation Campus (SIC)**.

---

## 🧠 ¿Qué hace?
- Recibe mensajes del usuario mediante Telegram.
- Analiza el **tono emocional** y la **polaridad** de los mensajes.
- Interpreta emociones en **rostros** mediante análisis de imágenes.
- Analiza el contenido emocional de **imágenes generales**.
- Transcribe **audios** usando SoundFile + NumPy.
- Devuelve respuestas como un **asistente emocional personal**.
- Mantiene un registro de tus emociones a lo largo del tiempo.
- Registra los  datos de cada usuario mediante **MySQL**.
- Utiliza frases mediante un **dataset JSON**.

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
- (En caso de ser Desarrollador, PC para ejecutar el servidor)

---

## 🚀 Cómo usarlo
1. Abrí Telegram  
2. Buscá **@SENTITIBOT_BOT** o accede desde AQUi https://t.me/SENTITIBOT_BOT
3. Para analizar texto: /sentimiento + lo que deseas comentar
4. Para analizar imágenes o emociones faciales: subi una foto al chat
5. Para transcribir audio y analisarlo: apreta el botoncito del microfono y empeza a grabar
6. Para poder mantener un registro de tus emociones utiliza: /diario



---


## 🎯 Objetivo del proyecto
En este proyecto buscamos:
- Explorar cómo la IA puede **Acompañar Emocionalmente** a los usuarios  
- Integrar **Bot + IA + Base de Datos + Dataset JSON** en un sistema funcional real  
- Procesar texto, voz e imágenes en un asistente accesible desde Telegram  

---

## 🧑‍💻 Equipo del Capstone Project — Samsung Innovation Campus (SIC):
Somos el Equipo **Transformers** compuesto por: 
- Gael Martiniano Baroni
- Leandro Nuñez
- Santiago Ivan Sluka Antelo
- Alexis Kevin Bellido
Nosotros Realizamos este proyecto como parte del curso intensivo de Samsung con Mirgor 

---

## ▶️ Cómo ejecutarlo

### 1️⃣ Descargá e instalá los programas necesarios
Asegurate de tener instalados:

- **Python 3.10+**
- **MySQL Server + MySQL Workbench**
- **Git** Nesecario para descargar los archivos

#### 📥 Python  
https://www.python.org/downloads/

#### 📥 MySQL  
https://dev.mysql.com/downloads/

- dejamos un tutorial de como instalar MySQL:
https://youtu.be/_K2nOYwOq1E?si=dhSo9GQiyaLSjcgQ


---

## 2️⃣ Clonar el repositorio
Ejecuta en git: git init
Ejecuta en git: git clone https://github.com/SantiagoSluka/SentitiBot_Transformers.git
ejecuta en git: git pull

---

## 3️⃣ Instalar dependencias utilizando
pip install -r requirements.txt

---

##4️⃣ Configurar las claves del bot y la base de datos

Creá un archivo .env en la carpeta del proyecto:
- TELEGRAM_TOKEN= 'tu_token_de_telegram'
- GROQ_API_KEY= 'tu_api_key'
- MYSQL_USER= 'root'
- MYSQL_PASSWORD= 'tu_password'
- MYSQL_HOST= 'localhost'
- MYSQL_DATABASE= 'sentitito'

---

##5️⃣ Configurar la base de datos

Ingresá a MySQL Workbench y ejecutá el query de creación de tablas
(recomendamos ejecutar query por query para evitar algun error en la creacion)

- Mini tutorial para hacer el archivo connect.py a la base de datos con Python:
https://youtu.be/mHtALpiRpRI?si=EFmFJcqcfgL_Nats

---

##6️⃣ Ejecutar el bot
"python main.py"

---

##7️⃣ Probar funciones
Para pobrar las funciones podes:
**Chat con IA**: Manda un mensaje cualquiera 
**Analizador de Sentimiento**: /sentimiento Estoy triste
**Diario Personal**: /diario
**Analizador de Imagenes**: Sube una imagen y deja que la magia suceda
**Analizador Facial**: Sube una foto de tu cara y ve que emocion desprendes
**Transcriptor de Audio**: Graba un Audio y conversa mas fluidamente con Sentitito

----

## Estado del proyecto Actual
V1.0 


