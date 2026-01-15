import telebot
from gigachat import GigaChat

# --- ТОКЕНЫ ---
TG_TOKEN = "8400025214:AAHAkfze6QAZjULpCY_R9av1vLAM4ec8Idk"
GIGACHAT_CREDENTIALS = "MDE5YjhlMmMtNzhiOC03YThjLTk1ZTQtM2NkOTNjNThlNjkyOmJlZTdiZmUwLWMzODMtNGMxZi05N2FmLTkzZTYwOWQzMTgzMw=="

bot = telebot.TeleBot(TG_TOKEN)

# --- ФУНКЦИЯ GIGACHAT ---
def ask_baldi_api(prompt, is_draw=False):
    with GigaChat(credentials=GIGACHAT_CREDENTIALS, verify_ssl_certs=False) as giga:
        if is_draw:
            text = f"Нарисуй: {prompt}"
        else:
            text = f"Ты — злой учитель Балди. Ответь ученику на это: {prompt}"
        
        res = giga.chat(text)
        return res.choices[0].message.content

# --- КОМАНДЫ ---

# Ответ в группе
@bot.message_handler(commands=['AsktoBaldiAI'])
def handle_ask(message):
    query = message.text.replace("/AsktoBaldiAI", "").strip()
    if not query:
        bot.reply_to(message, "📏 Где твой вопрос? Живее!")
        return
    answer = ask_baldi_api(query)
    bot.reply_to(message, answer)

# Рисование
@bot.message_handler(commands=['draws'])
def handle_draw(message):
    query = message.text.replace("/draws", "").strip()
    if not query:
        bot.reply_to(message, "🎨 Напиши, что нарисовать!")
        return
    
    msg = bot.reply_to(message, "Рисую... Погоди...")
    try:
        image_res = ask_baldi_api(query, is_draw=True)
        bot.send_message(message.chat.id, f"Вот твой рисунок:\n{image_res}")
    except:
        bot.send_message(message.chat.id, "❌ Не удалось нарисовать.")

# Твой блок оплаты из скриншотов
@bot.message_handler(commands=['premium'])
def send_pay(message):
    try:
        bot.send_invoice(
            message.chat.id, 
            "VIP Доступ", 
            "Покупка звезд для Балди", 
            "new_stars_test_777", 
            "", 
            "XTR", 
            [telebot.types.LabeledPrice("Цена", 1)]
        )
    except Exception as e:
        print(f"Ошибка счета: {e}")

# --- ЗАПУСК ---
if __name__ == "__main__":
    print("Балди запущен!")
    # skip_pending=True уберет ошибку 409 при перезапуске
    bot.infinity_polling(skip_pending=True)


