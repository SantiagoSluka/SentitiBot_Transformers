-- 1. Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS sentitito_bot;

-- 2. Usar la base de datos
USE sentitito_bot;

-- Transformamos la columna ENUM restringida a TEXTO libre
ALTER TABLE messages MODIFY COLUMN sentiment VARCHAR(50);

-- 3. Tabla de Usuarios
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    first_seen DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 4. Tabla de Mensajes
CREATE TABLE IF NOT EXISTS messages (
    message_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT,
    text TEXT,
    sentiment ENUM('positive', 'negative', 'neutral'),
    score DECIMAL(4,3),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50) DEFAULT 'telegram',
    
    -- Llave foránea para relacionar mensajes con usuarios
    FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE -- Si se borra un usuario, se borran sus mensajes
        ON UPDATE CASCADE -- Si cambia el user_id (raro), se actualiza aquí
);

-- 5. Tabla de Estadísticas (opcional para el bot, pero útil)
CREATE TABLE IF NOT EXISTS stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    total_messages INT DEFAULT 0,
    positive_count INT DEFAULT 0,
    negative_count INT DEFAULT 0,
    neutral_count INT DEFAULT 0,
    last_update DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 6. Insertar una fila inicial en la tabla de estadísticas
-- Esto es útil para que solo tengas que hacer UPDATE y no INSERT/UPDATE
INSERT INTO stats (id, total_messages, positive_count, negative_count, neutral_count)
VALUES (1, 0, 0, 0, 0)
ON DUPLICATE KEY UPDATE id=1; -- No hace nada si la fila con id=1 ya existe