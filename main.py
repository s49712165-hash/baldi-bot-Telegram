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
ADMIN_ID = 6710377475 
TG_TOKEN = "8257171581:AAG9puuLo5RvkPNKz1XW2QDDBzpri1lw0kc"
GIGA_KEY = "MDE5Yjg5ZTMtZjg5Ny03ZjE4LTg2NDctODIxN2VkNWI4NTI4OjVkZjViMDlhLTExMzMtNDg2MC04MWMzLTVjNDU5MDhkNmJjOA=="

bot = telebot.TeleBot(TG_TOKEN)
paid_users = [] # Список купивших

# --- 3. НЕЙРОСЕТЬ ---
def get_ai_answer(text):
    try:
        with GigaChat(credentials=GIGA_KEY, verify_ssl_certs=False) as giga:
            return giga.chat(text).choices[0].message.content
    except: return "Бальди занят, попробуй позже."

# --- 4. ОПЛАТА ---
@bot.message_handler(commands=['premium'])
def send_pay(message):
    try:
        bot.send_invoice(
            message.chat.id, 
            "VIP Доступ", 
            "Доступ к Бальди", 
            "new_stars_test_777", # Твой новый payload
            "", 
            "XTR", 
            [telebot.types.LabeledPrice("VIP за 1 звезду", 1)]
        )
    except Exception as e:
        print(f"Ошибка счета: {e}")

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    paid_users.append(message.from_user.id)
    bot.send_message(message.chat.id, "🎉 Оплата принята! Теперь я тебе отвечаю.")
    bot.send_message(ADMIN_ID, f"💰 Продажа: {message.from_user.id}")

# --- 5. ОБРАБОТКА ТЕКСТА ---
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "Я Бальди! Напиши мне или купи /premium.")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    u_id = message.from_user.id
    if u_id == ADMIN_ID or u_id in paid_users:
        bot.send_chat_action(message.chat.id, 'typing')
        bot.send_message(message.chat.id, get_ai_answer(message.text))
    else:
        bot.send_message(message.chat.id, "⛔ Нет доступа. Купите /premium (1 звезда).")

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    bot.infinity_polling(timeout=20, long_polling_timeout=10)


