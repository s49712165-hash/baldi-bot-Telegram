import telebot
from gigachat import GigaChat
import time
from flask import Flask
from threading import Thread
import os

# --- ТВОИ ДАННЫЕ ---
TG_TOKEN = "8400025214:AAHAkfze6QAZjULpCY_R9av1vLAM4ec8Idk"
GIGACHAT_CREDENTIALS = "MDE5YjhlMmMtNzhiOC03YThjLTk1ZTQtM2NkOTNjNThlNjkyOmJlZTdiZmUwLWMzODMtNGMxZi05N2FmLTkzZTYwOWQzMTgzMw=="

bot = telebot.TeleBot(TG_TOKEN)

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER (ЧТОБЫ НЕ БЫЛО ОШИБКИ PORT) ---
app = Flask('')

@app.route('/')
def home():
    return "Балди жив!"

def run_web_server():
    # Render дает порт в переменной окружения PORT
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- ЛОГИКА GIGACHAT ---
def ask_baldi(text, is_draw=False):
    try:
        with GigaChat(credentials=GIGACHAT_CREDENTIALS, verify_ssl_certs=False) as giga:
            prompt = f"Нарисуй: {text}" if is_draw else f"Ты учитель Балди. Ответь: {text}"
            response = giga.chat(prompt)
            return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка: {e}"

# --- КОМАНДЫ ---
@bot.message_handler(commands=['AsktoBaldiAI'])
def handle_ask(message):
    query = message.text.replace("/AsktoBaldiAI", "").strip()
    if not query:
        bot.reply_to(message, "📏 Где вопрос?")
        return
    bot.reply_to(message, ask_baldi(query))

@bot.message_handler(commands=['draws'])
def handle_draw(message):
    query = message.text.replace("/draws", "").strip()
    if not query:
        bot.reply_to(message, "🎨 Что нарисовать?")
        return
    bot.send_message(message.chat.id, ask_baldi(query, is_draw=True))

# --- ЗАПУСК ---
if __name__ == "__main__":
    # 1. Запускаем веб-сервер в фоне
    t = Thread(target=run_web_server)
    t.start()
    print("Веб-сервер запущен.")

    # 2. Сбрасываем старые соединения (лечим ошибку 409)
    print("Очистка очереди сообщений...")
    bot.remove_webhook()
    bot.delete_webhook(drop_pending_updates=True)
    time.sleep(1)

    # 3. Запускаем бота
    print("Балди готов!")
    bot.infinity_polling()






