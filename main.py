import telebot
from gigachat import GigaChat
import time
import os
from flask import Flask
from threading import Thread

# --- НАСТРОЙКИ ---
TG_TOKEN = "8400025214:AAHAkfze6QAZjULpCY_R9av1vLAM4ec8Idk"
GIGACHAT_CREDENTIALS = "MDE5YjhlMmMtNzhiOC03YThjLTk1ZTQtM2NkOTNjNThlNjkyOmJlZTdiZmUwLWMzODMtNGMxZi05N2FmLTkzZTYwOWQzMTgzMw=="

bot = telebot.TeleBot(TG_TOKEN)

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER (ЧТОБЫ НЕ БЫЛО ОШИБКИ PORT) ---
app = Flask('')

@app.route('/')
def home():
    return "Балди на связи!"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- ЛОГИКА GIGACHAT ---
def ask_baldi(text, is_draw=False):
    try:
        with GigaChat(credentials=GIGACHAT_CREDENTIALS, verify_ssl_certs=False) as giga:
            if is_draw:
                prompt = f"Нарисуй: {text}"
            else:
                prompt = f"Ты — строгий учитель Балди из игры Baldi's Basics. Отвечай коротко и в характере. Текст: {text}"
            
            response = giga.chat(prompt)
            return response.choices[0].message.content
    except Exception as e:
        return "📐 Ошибка в тетрадке! (Проблема с API)"

# --- ОБРАБОТЧИКИ ---

# Команда для рисования (работает везде)
@bot.message_handler(commands=['draws'])
def handle_draw(message):
    query = message.text.replace("/draws", "").strip()
    if not query:
        bot.reply_to(message, "🎨 Напиши, что нарисовать!")
        return
    
    bot.reply_to(message, "Рисую...")
    res = ask_baldi(query, is_draw=True)
    bot.send_message(message.chat.id, res)

# Команда только для ГРУПП
@bot.message_handler(commands=['AsktoBaldiAI'])
def handle_group_ask(message):
    if message.chat.type in ['group', 'supergroup']:
        query = message.text.replace("/AsktoBaldiAI", "").strip()
        if not query:
            bot.reply_to(message, "📏 Где твой вопрос?")
            return
        bot.reply_to(message, ask_baldi(query))

# Обработка ЛЮБЫХ сообщений в ЛС (без команд)
@bot.message_handler(func=lambda message: message.chat.type == 'private', content_types=['text'])
def handle_private_chat(message):
    # Если это не команда (не начинается с /)
    if not message.text.startswith('/'):
        bot.send_chat_action(message.chat.id, 'typing')
        answer = ask_baldi(message.text)
        bot.reply_to(message, answer)

# --- ЗАПУСК ---
if __name__ == "__main__":
    # 1. Запуск веб-сервера для Render
    Thread(target=run_web_server).start()

    # 2. Очистка от конфликтов 409
    print("Сброс сессии...")
    bot.remove_webhook()
    bot.delete_webhook(drop_pending_updates=True)
    time.sleep(1)

    print("Балди запущен!")
    bot.infinity_polling(skip_pending=True)







