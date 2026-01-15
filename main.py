import telebot
from gigachat import GigaChat

# --- ТВОИ ТОКЕНЫ ---
TG_TOKEN = "8400025214:AAHAkfze6QAZjULpCY_R9av1vLAM4ec8Idk"
GIGACHAT_CREDENTIALS = "MDE5YjhlMmMtNzhiOC03YThjLTk1ZTQtM2NkOTNjNThlNjkyOmJlZTdiZmUwLWMzODMtNGMxZi05N2FmLTkzZTYwOWQzMTgzMw=="

bot = telebot.TeleBot(TG_TOKEN)

# Функция для запросов к GigaChat
def call_giga(prompt, mode="chat"):
    with GigaChat(credentials=GIGACHAT_CREDENTIALS, verify_ssl_certs=False) as giga:
        if mode == "draw":
            # Команда для генерации изображения
            text = f"Нарисуй: {prompt}"
        else:
            # Системная установка роли Балди
            text = f"Ты — Балди из игры Baldi's Basics. Твоя цель — отвечать как странный и строгий учитель математики. Твой ответ на: {prompt}"
        
        response = giga.chat(text)
        return response.choices[0].message.content

# --- ОБРАБОТЧИКИ КОМАНД ---

# Приветствие
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "📏 Привет! Я Балди. Добро пожаловать в мою школу!\n\n"
                          "Команды:\n"
                          "/AsktoBaldiAI [вопрос] — спросить меня о чем-то\n"
                          "/draws [описание] — заставить меня рисовать")

# Команда для групп и лички: Общение
@bot.message_handler(commands=['AsktoBaldiAI'])
def ask_handler(message):
    # Извлекаем текст после команды
    user_query = message.text.replace("/AsktoBaldiAI", "").strip()
    
    if not user_query:
        bot.reply_to(message, "📏 Ты ничего не написал! Быстро бери листок и пиши вопрос!")
        return

    try:
        answer = call_giga(user_query, mode="chat")
        bot.reply_to(message, answer)
    except Exception as e:
        bot.reply_to(message, "У меня сломалась линейка... (Ошибка API)")

# Команда для групп и лички: Рисование
@bot.message_handler(commands=['draws'])
def draw_handler(message):
    # Извлекаем промпт для рисования
    draw_query = message.text.replace("/draws", "").strip()
    
    if not draw_query:
        bot.reply_to(message, "🎨 Ты должен сказать, что рисовать! Я не гадалка!")
        return

    # Отправляем временное сообщение, чтобы пользователь видел работу
    waiting_msg = bot.reply_to(message, "Хмм... Сейчас что-нибудь изобразим... ✏️")

    try:
        image_result = call_giga(draw_query, mode="draw")
        # GigaChat возвращает ссылку или описание в тексте
        bot.send_message(message.chat.id, f"Вот, что получилось:\n{image_result}")
        bot.delete_message(message.chat.id, waiting_msg.message_id)
    except Exception as e:
        bot.edit_message_text("Ой! Краски закончились. Попробуй позже!", message.chat.id, waiting_msg.message_id)

# --- ЗАПУСК ---
if __name__ == "__main__":
    print("Бот Балди запущен и готов к урокам!")
    # skip_pending=True игнорирует сообщения, присланные пока бот был оффлайн
    bot.infinity_polling(skip_pending=True)



