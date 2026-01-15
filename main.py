import telebot
from gigachat import GigaChat

# --- ТВОИ ДАННЫЕ ---
TG_TOKEN = "8400025214:AAHAkfze6QAZjULpCY_R9av1vLAM4ec8Idk"
GIGACHAT_CREDENTIALS = "MDE5YjhlMmMtNzhiOC03YThjLTk1ZTQtM2NkOTNjNThlNjkyOmJlZTdiZmUwLWMzODMtNGMxZi05N2FmLTkzZTYwOWQzMTgzMw=="

bot = telebot.TeleBot(TG_TOKEN)

# Функция для связи с GigaChat
def giga_request(prompt, is_draw=False):
    with GigaChat(credentials=GIGACHAT_CREDENTIALS, verify_ssl_certs=False) as giga:
        content = f"Нарисуй: {prompt}" if is_draw else f"Ты Балди из игры. Ответь ученику: {prompt}"
        response = giga.chat(content)
        return response.choices[0].message.content

# --- КОМАНДЫ ---

# Команда для группы
@bot.message_handler(commands=['AsktoBaldiAI'])
def ask_baldi(message):
    text = message.text.replace("/AsktoBaldiAI", "").strip()
    if not text:
        bot.reply_to(message, "📏 Пиши вопрос, лентяй!")
        return
    bot.reply_to(message, giga_request(text))

# Команда рисования
@bot.message_handler(commands=['draws'])
def draw_baldi(message):
    text = message.text.replace("/draws", "").strip()
    if not text:
        bot.reply_to(message, "🎨 Что рисовать?")
        return
    msg = bot.reply_to(message, "Рисую...")
    try:
        res = giga_request(text, is_draw=True)
        bot.send_message(message.chat.id, f"Результат:\n{res}")
    except:
        bot.edit_message_text("Ошибка!", message.chat.id, msg.message_id)

# Исправленный блок оплаты (твои звезды)
@bot.message_handler(commands=['premium'])
def send_pay(message):
    try:
        bot.send_invoice(
            message.chat.id, 
            "VIP Доступ", 
            "Покупка звезд", 
            "stars_pay_777", 
            "", 
            "XTR", 
            [telebot.types.LabeledPrice("Цена", 1)]
        )
    except Exception as e:
        print(f"Ошибка счета: {e}")

# Обязательные обработчики для оплаты
@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    bot.send_message(message.chat.id, "✅ Оплата прошла! Ты теперь VIP!")

# --- ЗАПУСК ---
if __name__ == "__main__":
    print("Бот Балди запущен!")
    # skip_pending=True решает проблему Error 409
    bot.infinity_polling(skip_pending=True)


