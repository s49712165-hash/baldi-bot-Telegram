import telebot
import requests  # Добавляем для запросов к твоему API
import time
import os
from flask import Flask
from threading import Thread

# --- НАСТРОЙКИ ---
TG_TOKEN = "8400025214:AAHAkfze6QAZjULpCY_R9av1vLAM4ec8Idk"
# Вставь сюда ключ, который тебе выдал Baldi AI
BALDI_API_KEY = "sk-baldi-ncdyzsumj4smpjfacz3bsn" 

bot = telebot.TeleBot(TG_TOKEN)
app = Flask('')

# --- HEALTH CHECK ДЛЯ RENDER ---
@app.route('/')
def home():
    return "Baldi AI Bot is Live!"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- НОВАЯ ЛОГИКА ДЛЯ ТВОЕЙ НЕЙРОСЕТИ (BALDI AI) ---
def get_ai_response(user_text):
    url = "https://api.baldi.ai/endpoint" # Адрес из твоего скриншота
    headers = {
        "Authorization": f"Bearer {BALDI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": user_text,
        "other_parameters": "значения"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Здесь нужно достать текст ответа. Обычно это data['response'] или data['choices']
            # В примере ниже просто возвращаем весь текст, если не знаем точную структуру
            return data.get("text_response", "Балди задумался...") 
        else:
            return f"❌ Ошибка API: {response.status_code}"
    except Exception as e:
        return f"❌ Ошибка подключения: {str(e)}"

# --- ОБРАБОТЧИКИ (БЕЗ КОМАНД В ЛС) ---

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Урок начинается! Я работаю на базе Baldi AI. Пиши мне прямо здесь.")

@bot.message_handler(func=lambda m: m.chat.type == 'private' and not m.text.startswith('/'))
def private_chat(message):
    bot.send_chat_action(message.chat.id, 'typing')
    answer = get_ai_response(message.text)
    bot.reply_to(message, answer)

# --- ЗАПУСК ---
if __name__ == "__main__":
    Thread(target=run_web_server).start()
    bot.remove_webhook()
    bot.delete_webhook(drop_pending_updates=True)
    time.sleep(1)
    print("Бот на базе Baldi AI запущен!")
    bot.infinity_polling(skip_pending=True)













