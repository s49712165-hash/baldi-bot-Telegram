import telebot
from gigachat import GigaChat

# --- ТВОИ ДАННЫЕ ---
TG_TOKEN = "8400025214:AAHAkfze6QAZjULpCY_R9av1vLAM4ec8Idk"
GIGACHAT_CREDENTIALS = "MDE5YjhlMmMtNzhiOC03YThjLTk1ZTQtM2NkOTNjNThlNjkyOmJlZTdiZmUwLWMzODMtNGMxZi05N2FmLTkzZTYwOWQzMTgzMw=="

bot = telebot.TeleBot(TG_TOKEN)

# Функция для работы с GigaChat
def get_giga_answer(prompt, is_draw=False):
    with GigaChat(credentials=GIGACHAT_CREDENTIALS, verify_ssl_certs=False) as giga:
        if is_draw:
            text = f"Нарисуй: {prompt}"
        else:
            text = f"Ты — Балди из игры Baldi's Basics. Отвечай как строгий учитель математики. Твой ответ на вопрос: {prompt}"
        
        response = giga.chat(text)
        return response.choices[0].message.content

# --- КОМАНДЫ ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "📏 Привет! Я Балди. Добро пожаловать в мою школу!\n\n"
                          "Команды:\n"
                          "/AsktoBaldiAI [вопрос] — поболтать\n"
                          "/draws [описание] — нарисовать что-то")

# Общение
@bot.message_handler(commands=['AsktoBaldiAI'])
def ask_ai(message):
    query = message.text.replace("/AsktoBaldiAI", "").strip()
    if not query:
        bot.reply_to(message, "📏 Пиши вопрос, а то линейкой по рукам получишь!")
        return
    
    answer = get_giga_answer(query)
    bot.reply_to(message, answer)

# Рисование
@bot.message_handler(commands=['draws'])
def draw_ai(message):
    query = message.text.replace("/draws", "").strip()
    if not query:
        bot.reply_to(message, "🎨 Что мне нарисовать? Пустоту в твоем дневнике?")
        return
    
    msg = bot.reply_to(message, "Так-так... Сейчас нарисую... ✏️")
    try:
        result = get_giga_answer(query, is_draw=True)
        bot.send_message(message.chat.id, f"Вот твой рисунок:\n{result}")
        bot.delete_message(message.chat.id, msg.message_id)
    except:
        bot.edit_message_text("❌ Ой! Грифель сломался. Попробуй позже.", message.chat.id, msg.message_id)

# --- ЗАПУСК ---
if __name__ == "__main__":
    print("Бот запущен!")
    # skip_pending=True убирает старые сообщения и помогает избежать ошибки 409
    bot.infinity_polling(skip_pending=True)




