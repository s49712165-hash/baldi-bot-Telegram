import os
import threading
from flask import Flask
import telebot
from gigachat import GigaChat

# --- 1. СЕРВЕР ДЛЯ RENDER ---
app = Flask(__name__)
@app.route('/')
def health_check(): return "OK", 200

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- 2. НАСТРОЙКИ ---
TG_TOKEN = "8257171581:AAG9puuLo5RvkPNKz1XW2QDDBzpri1lw0kc"
GIGA_KEY = "MDE5Yjg5ZTMtZjg5Ny03ZjE4LTg2NDctODIxN2VkNWI4NTI4OjVkZjViMDlhLTExMzMtNDg2MC04MWMzLTVjNDU5MDhkNmJjOA=="

bot = telebot.TeleBot(TG_TOKEN)

# --- 3. ЛОГИКА НЕЙРОСЕТИ ---
def get_ai_answer(text):
    try:
        # verify_ssl_certs=False нужен для работы GigaChat из-за границы
        with GigaChat(credentials=GIGA_KEY, verify_ssl_certs=False) as giga:
            response = giga.chat(text)
            return response.choices[0].message.content
    except Exception as e:
        print(f"Ошибка GigaChat: {e}")
        return "Бальди сейчас занят, попробуй написать позже!"

# --- 4. ОБРАБОТКА СООБЩЕНИЙ ---
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "Привет! Я Бальди. Спрашивай что угодно, я отвечу!")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    # Показываем, что бот "печатает"
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Получаем ответ от нейросети
    answer = get_ai_answer(message.text)
    
    # Отправляем ответ пользователю
    bot.send_message(message.chat.id, answer)

# --- 5. ЗАПУСК ---
if __name__ == "__main__":
    # Запускаем Flask в отдельном потоке
    threading.Thread(target=run_web, daemon=True).start()
    # Запускаем бота
    print("Бот запущен...")
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
