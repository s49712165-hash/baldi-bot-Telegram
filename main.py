import os
import threading
from flask import Flask
import telebot
from gigachat import GigaChat

# --- 1. ВЕБ-СЕРВЕР ДЛЯ ОБХОДА ТАЙМАУТА RENDER ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Baldi AI is active!", 200

def run_web_server():
    # Render автоматически назначает порт, Flask должен его слушать
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- 2. ВАШИ ТОКЕНЫ ---
# Телеграм токен
TG_TOKEN = "8257171581:AAG9puuLo5RvkPNKz1XW2QDDBzpri1lw0kc"
# Авторизационные данные GigaChat
GIGACHAT_CREDENTIALS = "MDE5Yjg5ZTMtZjg5Ny03ZjE4LTg2NDctODIxN2VkNWI4NTI4OjVkZjViMDlhLTExMzMtNDg2MC04MWMzLTVjNDU5MDhkNmJjOA=="

bot = telebot.TeleBot(TG_TOKEN)

# --- 3. ФУНКЦИЯ ЗАПРОСА К GIGACHAT ---
def get_ai_response(text):
    try:
        # verify_ssl_certs=False критичен для работы на некоторых серверах
        with GigaChat(credentials=GIGACHAT_CREDENTIALS, verify_ssl_certs=False) as giga:
            response = giga.chat(text)
            return response.choices[0].message.content
    except Exception as e:
        print(f"Ошибка GigaChat: {e}")
        return "Извини, я немного завис. Попробуй еще раз!"

# --- 4. ОБРАБОТКА КОМАНД И СООБЩЕНИЙ ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.reply_to(message, "Привет! Я Baldi AI. Я готов общаться через GigaChat!")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    # Показываем, что бот печатает
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Получаем ответ от нейросети
    answer = get_ai_response(message.text)
    
    # Отправляем ответ пользователю
    bot.send_message(message.chat.id, answer)
# 53 строка: Настройка твоего ID (замени на свои цифры)
ADMIN_ID = 591234567 

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    print(f"--- Сообщение от {message.from_user.id}: {message.text}")
    
    # Если это ТЫ (Админ) — бот отвечает
    if message.from_user.id == ADMIN_ID:
        bot.send_chat_action(message.chat.id, 'typing')
        ans = get_ai_answer(message.text)
        bot.send_message(message.chat.id, ans)
    # Если это КТО-ТО ДРУГОЙ — просим оплату
    else:
        bot.send_message(
            message.chat.id, 
            "❌ Доступ ограничен! Введите /premium для оплаты (100 звёзд)."
        )

# 70-я строка (примерно): Начало блока запуска
if __name__ == "__main__":

# --- 5. ЗАПУСК ВСЕЙ СИСТЕМЫ ---
if __name__ == "__main__":
    # Запускаем веб-сервер в фоновом потоке. 
    # Это "обманет" Render: он увидит открытый порт и не будет выключать бота.
    threading.Thread(target=run_web_server, daemon=True).start()
    
    print(">>> Flask запущен для проверки порта.")
    print(">>> Бот Baldi AI начинает работу...")
    # --- БЛОК ОПЛАТЫ (100 ЗВЁЗД) ---

@bot.message_handler(commands=['buy'])
def show_pay_variants(message):
    # Отправляем инвойс на 100 звёзд
    bot.send_invoice(
        message.chat.id,
        title="Доступ к Baldi AI Premium",
        description="Оплата 100 звёзд для получения полного доступа к функциям нейросети.",
        provider_token="", # Для звёзд это поле должно быть пустым
        currency="XTR",    # Код валюты для Telegram Stars
        prices=[telebot.types.LabeledPrice(label="VIP Доступ", amount=100)],
        invoice_payload="premium_access_payload"
    )

@bot.message_handler(content_types=['successful_payment'])
def success_pay(message):
    # Этот код сработает, когда пользователь успешно оплатит
    bot.send_message(message.chat.id, "🎉 Оплата прошла успешно! Теперь у вас есть полный доступ.")
    print(f"Пользователь {message.from_user.id} оплатил доступ.")

# Обязательно добавьте этот хэндлер для подтверждения готовности принять оплату
@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

    # Запуск бесконечного цикла прослушивания Телеграм
    bot.infinity_polling()
