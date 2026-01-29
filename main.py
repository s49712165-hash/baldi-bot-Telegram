import telebot
import requests
import time
import os
from flask import Flask
from threading import Thread

# --- НАСТРОЙКИ ---
TG_TOKEN = "8400025214:AAHAkfze6QAZjULpCY_R9av1vLAM4ec8Idk"

# ВСТАВЬ СЮДА КЛЮЧ ИЗ ЛИЧНОГО КАБИНЕТА (который под "Hello")
BALDI_API_KEY = "ТВОЙ_КЛЮЧ_ИЗ_ЛИЧНОГО_КАБИНЕТА"
BALDI_URL = "https://api.baldicloud.ai/v1/chat"

bot = telebot.TeleBot(TG_TOKEN)
app = Flask('')

# --- КОМПОНЕНТ BALDI CLOUD ---
def ask_baldi(message_text):
    headers = {
        "Authorization": f"Bearer {BALDI_API_KEY}",
        "Content-Type": "application/json"
    }
    # Формат запроса взят прямо с твоего скриншота
    payload = {
        "message": message_text,
        "model": "baldi-3.0"  # Модель тоже со скрина
    }

    try:
        response = requests.post(BALDI_URL, json=payload, headers=headers, timeout=20)
        if response.status_code == 200:
            data = response.json()
            # Обычно нейросети возвращают ответ в поле 'response' или 'message'
            return data.get("response", data.get("message", "Балди молчит..."))
        else:
            return f"❌ Ошибка BaldiCloud: {response.status_code}\n{response.text}"
    except Exception as e:
        return f"❌ Ошибка связи: {str(e)}"

# --- ВЕБ-СЕРВЕР ---
@app.route('/')
def home():
    return "Балди на связи!"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- ОБРАБОТКА (В ЛС БЕЗ КОМАНД) ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Урок начался! Теперь я работаю на BaldiCloud. Пиши просто так!")

@bot.message_handler(func=lambda m: m.chat.type == 'private' and not m.text.startswith('/'))
def chat_in_pm(message):
    bot.send_chat_action(message.chat.id, 'typing')
    answer = ask_baldi(message.text)
    bot.reply_to(message, answer)

# --- ЗАПУСК ---
if __name__ == "__main__":
    Thread(target=run_web_server).start()
    bot.remove_webhook()
    bot.delete_webhook(drop_pending_updates=True)
    time.sleep(1)
    print("Бот успешно переключен на Baldicloud!")
    bot.infinity_polling(skip_pending=True)













