import sys
import time

# Пробуем импортировать библиотеки. Если их нет, Render напишет об этом в логах.
try:
    import telebot
    from gigachat import GigaChat
except ImportError as e:
    print(f"Критическая ошибка: Не установлена библиотека! {e}")
    sys.exit(1)

# --- ТВОИ ДАННЫЕ ---
TG_TOKEN = "8400025214:AAHAkfze6QAZjULpCY_R9av1vLAM4ec8Idk"
GIGACHAT_CREDENTIALS = "MDE5YjhlMmMtNzhiOC03YThjLTk1ZTQtM2NkOTNjNThlNjkyOmJlZTdiZmUwLWMzODMtNGMxZi05N2FmLTkzZTYwOWQzMTgzMw=="

try:
    bot = telebot.TeleBot(TG_TOKEN)
except Exception as e:
    print(f"Ошибка инициализации бота: {e}")
    sys.exit(1)

# Функция для связи с GigaChat
def ask_baldi(text, is_draw=False):
    try:
        with GigaChat(credentials=GIGACHAT_CREDENTIALS, verify_ssl_certs=False) as giga:
            prompt = f"Нарисуй: {text}" if is_draw else f"Ты учитель Балди. Ответь: {text}"
            response = giga.chat(prompt)
            return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка GigaChat: {e}"

# --- КОМАНДЫ ---

@bot.message_handler(commands=['start'])
def start_msg(message):
    bot.reply_to(message, "📏 Я Балди! Команды:\n/AsktoBaldiAI [вопрос]\n/draws [описание]")

@bot.message_handler(commands=['AsktoBaldiAI'])
def handle_ask(message):
    question = message.text.replace("/AsktoBaldiAI", "").strip()
    if not question:
        bot.reply_to(message, "📏 Где вопрос?")
        return
    bot.reply_to(message, ask_baldi(question))

@bot.message_handler(commands=['draws'])
def handle_draw(message):
    desc = message.text.replace("/draws", "").strip()
    if not desc:
        bot.reply_to(message, "🎨 Что рисовать?")
        return
    
    wait = bot.reply_to(message, "Рисую...")
    try:
        res = ask_baldi(desc, is_draw=True)
        bot.send_message(message.chat.id, f"Результат:\n{res}")
        bot.delete_message(message.chat.id, wait.message_id)
    except:
        bot.edit_message_text("Ошибка рисования.", message.chat.id, wait.message_id)

# --- ЗАПУСК ---
if __name__ == "__main__":
    print("Проверка соединения...")
    try:
        # Сброс вебхука, чтобы не было ошибки 409
        bot.remove_webhook()
        time.sleep(1)
        print("Бот Балди успешно запущен и ждет сообщений!")
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"Критическая ошибка при запуске polling: {e}")
        sys.exit(1)





