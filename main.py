import telebot
import requests
import time
import os
from flask import Flask
from threading import Thread

# --- НАСТРОЙКИ ---
TG_TOKEN = "8400025214:AAHAkfze6QAZjULpCY_R9av1vLAM4ec8Idk"
# Твой новый ключ уже здесь:
BALDI_API_KEY = "sk-baldi-ncdyzsumj4smpjfacz3bsn"

# Основной адрес (даже если там опечатка, бот будет пробовать достучаться)
BALDI_URL = "https://api.baldicloud.ai/v1/chat"

bot = telebot.TeleBot(TG_TOKEN)
app = Flask('')

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER ---
@app.route('/')
def home():
    return "Балди AI бот запущен и готов к урокам!"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- КОМПОНЕНТ BALDI CLOUD ---
def ask_baldi(message_text):
    headers = {
        "Authorization": f"Bearer {BALDI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "message": message_text,
        "model": "baldi-3.0"
    }

    try:
        # Пытаемся отправить запрос
        response = requests.post(BALDI_URL, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # Пробуем достать ответ из разных полей (зависит от настроек API)
            answer = data.get("response") or data.get("message") or data.get("answer")
            return answer if answer else "Балди прислал пустой ответ, проверь настройки модели."
        elif response.status_code == 401:
            return "❌ Ошибка: Неверный API ключ. Проверь его в коде!"
        else:
            return f"❌ Ошибка сервера Baldi: {response.status_code}. Возможно, на сайте опечатка."
            
    except requests.exceptions.ConnectionError:
        return "❌ Ошибка связи: Адрес api.baldicloud.ai не найден. Похоже, в названии сайта действительно опечатка или он временно не работает."
    except Exception as e:
        return f"❌ Непредвиденная ошибка: {str(e)}"

# --- ОБРАБОТЧИКИ СООБЩЕНИЙ ---

@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = (
        "🎓 **Привет! Я твой учитель Балди.**\n\n"
        "Теперь я работаю на собственной нейросети BaldiCloud!\n"
        "Пиши мне прямо сюда, и я отвечу."
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

# Логика для ЛС (Личные сообщения)
@bot.message_handler(func=lambda m: m.chat.type == 'private' and not m.text.startswith('/'))
def chat_logic(message):
    bot.send_chat_action(message.chat.id, 'typing')
    answer = ask_baldi(message.text)
    bot.reply_to(message, answer)

# --- ЗАПУСК ---
if __name__ == "__main__":
    # Запускаем Flask в отдельном потоке
    Thread(target=run_web_server).start()

    # Очищаем старые сообщения,














