CREATE DATABASE IF NOT EXISTS sentitito_bot;
USE sentitito_bot;
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    first_seen DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS messages (
    message_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT,
    text TEXT,
    sentiment ENUM('positive', 'negative', 'neutral'),
    score DECIMAL(4,3),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50) DEFAULT 'telegram',
    FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
CREATE TABLE IF NOT EXISTS stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    total_messages INT DEFAULT 0,
    positive_count INT DEFAULT 0,
    negative_count INT DEFAULT 0,
    neutral_count INT DEFAULT 0,
    last_update DATETIME DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO stats (total_messages, positive_count, negative_count, neutral_count)
VALUES (0, 0, 0, 0);messagesmessagesstats
