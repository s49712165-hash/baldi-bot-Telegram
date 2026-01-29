import telebot
import requests
import time
import os
from flask import Flask
from threading import Thread

# --- НАСТРОЙКИ ---
TG_TOKEN = "8400025214:AAHAkfze6QAZjULpCY_R9av1vLAM4ec8Idk"

# ВСТАВЬ СЮДА СВОЙ API КЛЮЧ (длинная строка из кабинета)
BALDI_API_KEY = "sk-baldi-ncdyzsumj4smpjfacz3bsn"

# ВАЖНО: Проверь адрес. На скринах был api.baldicloud.ai или api.baldi.ai
# Давай попробуем этот, он самый свежий на скринах:
BALDI_URL = "https://api.baldicloud.ai/v1/chat"

bot = telebot.TeleBot(TG_TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Бот онлайн"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- УЛУЧШЕННЫЙ КОМПОНЕНТ BALDI AI ---
def ask_baldi(message_text):
    headers = {
        "Authorization": f"Bearer {BALDI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Мы пробуем формат 'message', так как на скрине 4799 был он
    payload = {
        "message": message_text,
        "model": "baldi-3.0"
    }

    try:
        print(f"Отправка запроса к {BALDI_URL}...")
        # Ставим таймаут 10 секунд, чтобы бот не зависал вечно
        response = requests.post(BALDI_URL, json=payload, headers=headers, timeout=10)
        
        print(f"Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            # Пытаемся достать ответ из разных полей на всякий случай
            answer = data.get("response") or data.get("message") or data.get("text")
            return answer if answer else "Нейросеть прислала пустой ответ."
        else:
            return f"❌ Ошибка сервера Baldi: {response.status_code}\nТекст: {response.text[:100]}"
            
    except requests.exceptions.Timeout:
        return "❌ Нейросеть слишком долго думала (тайм-аут)."
    except Exception as e:
        return f"❌ Ошибка связи: {str(e)}"

# --- ОБРАБОТКА ---

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Балди на связи! Я готов к уроку. Пиши мне сообщения.")

@bot.message_handler(func=lambda m: m.chat.type == 'private' and not m.text.startswith('/'))
def chat(message):
    bot.send_chat_action(message.chat.id, 'typing')
    reply = ask_baldi(message.text)
    bot.reply_to(message, reply)

# --- ЗАПУСК ---
if __name__ == "__main__":
    Thread(target=run_web_server).start()
    bot.remove_webhook()
    bot.delete_webhook(drop_pending_updates=True)
    time.sleep(1)
    print("Бот запущен!")
    bot.infinity_polling(skip_pending=True)














