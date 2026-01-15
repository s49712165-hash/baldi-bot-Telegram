import telebot
from gigachat import GigaChat
import time
import os
from flask import Flask
from threading import Thread

# --- ТВОИ ДАННЫЕ ---
TG_TOKEN = "8400025214:AAHAkfze6QAZjULpCY_R9av1vLAM4ec8Idk"
# Проверь этот ключ! Возможно, он устарел.
GIGACHAT_CREDENTIALS = "MDE5YjhlMmMtNzhiOC03YThjLTk1ZTQtM2NkOTNjNThlNjkyOmJlZTdiZmUwLWMzODMtNGMxZi05N2FmLTkzZTYwOWQzMTgzMw=="

bot = telebot.TeleBot(TG_TOKEN)
app = Flask('')

# --- HEALTH CHECK ---
@app.route('/')
def home():
    return "Bot is running"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- ФУНКЦИЯ НЕЙРОСЕТИ (С ПОКАЗОМ ОШИБКИ) ---
def call_ai(text, is_draw=False):
    try:
        # verify_ssl_certs=False помогает при проблемах с защитой на сервере
        with GigaChat(credentials=GIGACHAT_CREDENTIALS, verify_ssl_certs=False) as giga:
            if is_draw:
                prompt = f"Нарисуй: {text}"
            else:
                prompt = f"Ты учитель Балди. Ответь: {text}"
            
            response = giga.chat(prompt)
            return response.choices[0].message.content
    except Exception as e:
        # ВОТ ЗДЕСЬ МЫ ТЕПЕРЬ ВИДИМ РЕАЛЬНУЮ ПРИЧИНУ
        return f"❌ ОШИБКА GIGACHAT:\n{str(e)}"

# --- ОБРАБОТЧИКИ ---

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Я работаю! Напиши мне что-нибудь.")

@bot.message_handler(commands=['draws'])
def draw(message):
    query = message.text.replace("/draws", "").strip()
    if not query:
        bot.reply_to(message, "Напиши, что рисовать!")
        return
    bot.reply_to(message, "Рисую...")
    bot.send_message(message.chat.id, call_ai(query, is_draw=True))

@bot.message_handler(commands=['AsktoBaldiAI'])
def group_ask(message):
    query = message.text.replace("/AsktoBaldiAI", "").strip()
    bot.reply_to(message, call_ai(query))

# ЛИЧКА (РАБОТАЕТ БЕЗ КОМАНД)
@bot.message_handler(func=lambda m: m.chat.type == 'private' and not m.text.startswith('/'))
def private_msg(message):
    # Отправляем ответ сразу
    answer = call_ai(message.text)
    bot.reply_to(message, answer)

# --- ЗАПУСК ---
if __name__ == "__main__":
    Thread(target=run_web_server).start()
    
    bot.remove_webhook()
    bot.delete_webhook(drop_pending_updates=True)
    time.sleep(1)
    
    bot.infinity_polling(skip_pending=True)










