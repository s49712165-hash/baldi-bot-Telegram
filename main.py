import telebot
from gigachat import GigaChat
import time
import os
from flask import Flask
from threading import Thread

# --- ТВОИ ТОКЕНЫ ---
TG_TOKEN = "8400025214:AAHAkfze6QAZjULpCY_R9av1vLAM4ec8Idk"
GIGACHAT_CREDENTIALS = "MDE5YjhlMmMtNzhiOC03YThjLTk1ZTQtM2NkOTNjNThlNjkyOmJlZTdiZmUwLWMzODMtNGMxZi05N2FmLTkzZTYwOWQzMTgzMw=="

bot = telebot.TeleBot(TG_TOKEN)
app = Flask('')

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER (Health Check) ---
@app.route('/')
def home():
    return "Бот работает!"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- ЛОГИКА GIGACHAT ---
def get_ai_answer(text, mode="chat"):
    try:
        with GigaChat(credentials=GIGACHAT_CREDENTIALS, verify_ssl_certs=False) as giga:
            if mode == "draw":
                prompt = f"Нарисуй: {text}"
            else:
                prompt = f"Ответь на вопрос или поддержи беседу: {text}"
            
            response = giga.chat(prompt)
            return response.choices[0].message.content
    except Exception as e:
        return "⚠️ Ошибка связи с нейросетью. Попробуй позже."

# --- ОБРАБОТКА КОМАНД ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот на базе GigaChat.\n\n"
                          "• В ЛС просто пиши мне что угодно.\n"
                          "• В группах используй /AsktoBaldiAI [вопрос].\n"
                          "• Чтобы я что-то нарисовал, пиши /draws [описание].")

# Команда рисования (везде)
@bot.message_handler(commands=['draws'])
def handle_draw(message):
    query = message.text.replace("/draws", "").strip()
    if not query:
        bot.reply_to(message, "🎨 Напиши, что именно мне нарисовать?")
        return
    
    msg = bot.reply_to(message, "🎨 Рисую, подожди немного...")
    result = get_ai_answer(query, mode="draw")
    bot.send_message(message.chat.id, result)

# Команда для групп
@bot.message_handler(commands=['AsktoBaldiAI'])
def handle_group_chat(message):
    query = message.text.replace("/AsktoBaldiAI", "").strip()
    if not query:
        bot.reply_to(message, "❓ Напиши вопрос после команды.")
        return
    bot.reply_to(message, get_ai_answer(query))

# ОБЫЧНОЕ ОБЩЕНИЕ (только для ЛС)
@bot.message_handler(func=lambda m: m.chat.type == 'private' and not m.text.startswith('/'))
def handle_private(message):
    bot.send_chat_action(message.chat.id, 'typing')
    answer = get_ai_answer(message.text)
    bot.reply_to(message, answer)

# --- ЗАПУСК ---
if __name__ == "__main__":
    # Запускаем сервер для Render в фоновом потоке
    Thread(target=run_web_server).start()

    # Исправляем ошибку 409 (Conflict)
    bot.remove_webhook()
    bot.delete_webhook(drop_pending_updates=True)
    time.sleep(1)

    print("Бот запущен!")
    bot.infinity_polling(skip_pending=True)








