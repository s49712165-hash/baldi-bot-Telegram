import os
import threading
from flask import Flask
import telebot
from gigachat import GigaChat

# --- 1. ВЕБ-СЕРВЕР ДЛЯ RENDER ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "OK", 200

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- 2. НАСТРОЙКИ (ТВОЙ ID И ТОКЕНЫ) ---
ADMIN_ID = 6710377475  # Твой ID вставлен!

TG_TOKEN = "8257171581:AAG9puuLo5RvkPNKz1XW2QDDBzpri1lw0kc"
GIGA_KEY = "MDE5Yjg5ZTMtZjg5Ny03ZjE4LTg2NDctODIxN2VkNWI4NTI4OjVkZjViMDlhLTExMzMtNDg2MC04MWMzLTVjNDU5MDhkNmJjOA=="

bot = telebot.TeleBot(TG_TOKEN)

# --- 3. ЛОГИКА GIGACHAT ---
def get_ai_answer(text):
    try:
        with GigaChat(credentials=GIGA_KEY, verify_ssl_certs=False) as giga:
            response = giga.chat(text)
            return response.choices[0].message.content
    except Exception as e:
        print(f"Ошибка GigaChat: {e}")
        return "Извини, Бальди сейчас занят (ошибка нейросети)."

# --- 4. ОБРАБОТЧИКИ ОПЛАТЫ ---
@bot.message_handler(commands=['premium'])
def send_pay(message):
    try:
        bot.send_invoice(
            message.chat.id, 
            "VIP Доступ к Baldi AI", 
            "Доступ к общению с нейросетью без ограничений.", 
            "baldi_payload", 
            "", 
            "XTR", 
            [telebot.types.LabeledPrice("Купить 100 звёзд", 100)]
        )
    except Exception as e:
        print(f"Ошибка создания счета: {e}")

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    bot.send_message(message.chat.id, "🎉 Оплата прошла успешно! Теперь у вас есть доступ (напишите боту снова).")

# --- 5. ГЛАВНЫЙ ОБРАБОТЧИК СООБЩЕНИЙ ---
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "Привет! Я Baldi AI. Напиши мне что-нибудь!")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    print(f"Сообщение от {message.from_user.id}: {message.text}")
    
    # ПРОВЕРКА: Если пишет АДМИН
    if message.from_user.id == ADMIN_ID:
        bot.send_chat_action(message.chat.id, 'typing')
        ans = get_ai_answer(message.text)
        bot.send_message(message.chat.id, ans)
    
    # ПРОВЕРКА: Если пишет КТО-ТО ДРУГОЙ
    else:
        bot.send_message(
            message.chat.id, 
            "⛔ Ошибка доступа! Чтобы общаться с Baldi AI, нужно купить Premium.\n\n"
            "Стоимость: 100 звёзд ⭐\n"
            "Команда для оплаты: /premium"
        )

# --- 6. ЗАПУСК ВСЕЙ СИСТЕМЫ ---
if __name__ == "__main__":
    # Запуск Flask в отдельном потоке
    threading.Thread(target=run_web, daemon=True).start()
    
    print(">>> Бальди выходит на охоту (бот запущен)...")
    try:
        bot.infinity_polling(timeout=20, long_polling_timeout=10)
    except Exception as e:
        print(f"Критическая ошибка: {e}")

