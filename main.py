import os
import threading
from flask import Flask
import telebot
from gigachat import GigaChat

# --- 1. НАСТРОЙКА ВЕБ-СЕРВЕРА (Для Render) ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is running!", 200

def run_web_server():
    # Render выдает порт автоматически
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- 2. НАСТРОЙКА API КЛЮЧЕЙ ---
# Рекомендуется добавить их в Environment Variables на Render
TG_TOKEN = "ВАШ_ТЕЛЕГРАМ_ТОКЕН"
GIGACHAT_CREDENTIALS = "ВАШ_GIGACHAT_AUTH_ДАННЫЕ"

bot = telebot.TeleBot(TG_TOKEN)

# --- 3. ЛОГИКА GIGACHAT ---
def get_giga_response(user_text):
    try:
        # Авторизация и запрос к GigaChat
        with GigaChat(credentials=GIGACHAT_CREDENTIALS, verify_ssl_certs=False) as giga:
            response = giga.chat(user_text)
            return response.choices[0].message.content
    except Exception as e:
        print(f"Ошибка GigaChat: {e}")
        return "Извини, произошла ошибка при запросе к нейросети."

# --- 4. ОБРАБОТЧИКИ ТЕЛЕГРАМ ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я Baldi AI. Напиши мне что угодно, и я отвечу с помощью GigaChat.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Отправляем статус "печатает", пока ждем нейросеть
    bot.send_chat_action(message.chat.id, 'typing')
    
    answer = get_giga_response(message.text)
    bot.reply_to(message, answer)

# --- 5. ЗАПУСК ВСЕЙ СИСТЕМЫ ---
if __name__ == "__main__":
    # Запускаем Flask в отдельном потоке
    print("Запуск веб-сервера для Health Check...")
    threading.Thread(target=run_web_server, daemon=True).start()
    
    # Запускаем бота
    print("Бот запущен и ожидает сообщений...")
    # infinity_polling предотвращает вылет бота при сетевых ошибках
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
