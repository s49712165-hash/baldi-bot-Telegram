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
app = Flask('')

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER (РЕШАЕТ ОШИБКУ TIMEOUT/PORT) ---
@app.route('/')
def home():
    return "Бот активен!"

def run_web_server():
    # Render передает порт в переменную окружения PORT
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- ЛОГИКА НЕЙРОСЕТИ ---
def call_ai(text, is_draw=False):
    try:
        # verify_ssl_certs=False решает проблему "Ошибка связи" на серверах
        with GigaChat(credentials=GIGACHAT_CREDENTIALS, verify_ssl_certs=False) as giga:
            if is_draw:
                prompt = f"Нарисуй: {text}"
            else:
                prompt = f"Ты — умный и дружелюбный помощник. Ответь на сообщение пользователя: {text}"
            
            response = giga.chat(prompt)
            return response.choices[0].message.content
    except Exception as e:
        print(f"Ошибка GigaChat: {e}")
        return "⚠️ Извини, не смог связаться с мыслями. Попробуй еще раз чуть позже!"

# --- ОБРАБОТКА СООБЩЕНИЙ ---

# 1. Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я твой AI-помощник.\n\n"
                          "• В этом чате просто пиши мне любые вопросы.\n"
                          "• Чтобы я нарисовал что-то, пиши: /draws [описание].\n"
                          "• В группах используй: /AsktoBaldiAI [вопрос].")

# 2. Рисование (работает везде по команде /draws)
@bot.message_handler(commands=['draws'])
def draw(message):
    query = message.text.replace("/draws", "").strip()
    if not query:
        bot.reply_to(message, "🎨 Напиши, что именно мне нарисовать?")
        return
    
    msg = bot.reply_to(message, "🎨 Рисую... Это займет секунд 10-15.")
    res = call_ai(query, is_draw=True)
    bot.send_message(message.chat.id, res)

# 3. Команда для групп (в группах отвечаем ТОЛЬКО по этой команде)
@bot.message_handler(commands=['AsktoBaldiAI'])
def group_chat(message):
    query = message.text.replace("/AsktoBaldiAI", "").strip()
    if not query:
        bot.reply_to(message, "❓ Напиши свой вопрос после команды.")
        return
    bot.reply_to(message, call_ai(query))

# 4. ЛИЧНЫЕ СООБЩЕНИЯ (ОТВЕТ БЕЗ КОМАНД)
@bot.message_handler(func=lambda m: m.chat.type == 'private' and not m.text.startswith('/'))
def private_answer(message):
    bot.send_chat_action(message.chat.id, 'typing') # Показывает, что бот печатает
    answer = call_ai(message.text)
    bot.reply_to(message, answer)

# --- ЗАПУСК ---
if __name__ == "__main__":
    # Запускаем Flask в отдельном потоке (для Render Health Check)
    Thread(target=run_web_server).start()

    # Сбрасываем старые зависшие сообщения (решает ошибку 409 Conflict)
    bot.remove_webhook()
    bot.delete_webhook(drop_pending_updates=True)
    time.sleep(1)

    print("Бот запущен!")
    bot.infinity_polling(skip_pending=True)









