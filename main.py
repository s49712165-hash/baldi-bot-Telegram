import os
import threading
from flask import Flask
import telebot
from gigachat import GigaChat

# --- 1. ВЕБ-СЕРВЕР ---
app = Flask(__name__)
@app.route('/')
def health_check():
    return "OK", 200

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- 2. НАСТРОЙКИ ---
ADMIN_ID = 6710377474 
TG_TOKEN = "8257171581:AAG9puuLo5RvkPNKz1XW2QDDBzpri1lw0kc"
GIGA_KEY = "MDE5Yjg5ZTMtZjg5Ny03ZjE4LTg2NDctODIxN2VkNWI4NTI4OjVkZjViMDlhLTExMzMtNDg2MC04MWMzLTVjNDU5MDhkNmJjOA=="

bot = telebot.TeleBot(TG_TOKEN)
total_sales = 0
paid_users = [] # Список купивших

# --- 3. ЛОГИКА GIGACHAT ---
def get_ai_answer(text):
    try:
        with GigaChat(credentials=GIGA_KEY, verify_ssl_certs=False) as giga:
            response = giga.chat(text)
            return response.choices[0].message.content
    except Exception as e:
        print(f"Ошибка GigaChat: {e}")
        return "Извини, Бальди сейчас занят."

# --- 4. ОБРАБОТКА ОПЛАТЫ ---
@bot.message_handler(commands=['premium'])
def send_pay(message):
    try:
        bot.send_invoice(
            message.chat.id, "VIP Доступ", "Доступ к Baldi AI", "payload", "", "XTR",
            [telebot.types.LabeledPrice("Купить 100 звёзд", 100)]
        )
    except Exception as e:
        print(f"Ошибка счета: {e}")

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    global total_sales
    total_sales += 1
    paid_users.append(message.from_user.id) # Добавляем в белый список
    
    bot.send_message(message.chat.id, "🎉 Оплата принята! Теперь у вас есть доступ.")
    bot.send_message(ADMIN_ID, f"💰 НОВАЯ ПРОДАЖА!\nID: `{message.from_user.id}`", parse_mode="Markdown")

# --- 5. КОМАНДЫ И ТЕКСТ ---
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "Привет! Я Baldi AI. Напиши мне что-нибудь.")

@bot.message_handler(commands=['balance'])
def check_balance(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, f"📊 Оплат: {total_sales}\n⭐ Звёзд: {total_sales * 100}")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID or user_id in paid_users:
        bot.send_chat_action(message.chat.id, 'typing')
        ans = get_ai_answer(message.text)
        bot.send_message(message.chat.id, ans)
    else:
        bot.send_message(message.chat.id, "⛔ Нет доступа. Введите /premium (100 звёзд).")

# --- 6. ЗАПУСК ---
if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    print(">>> Бот запущен!")
    bot.infinity_polling(timeout=20, long_polling_timeout=10)


