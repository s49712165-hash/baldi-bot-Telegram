import telebot
from gigachat import GigaChat
import time
import os
from flask import Flask
from threading import Thread

# --- НАСТРОЙКИ ---
# 1. Твой токен от BotFather
TG_TOKEN = "8400025214:AAHAkfze6QAZjULpCY_R9av1vLAM4ec8Idk"

# 2. ТВОИ АВТОРИЗАЦИОННЫЕ ДАННЫЕ (Самая длинная строка из кабинета Сбера)
GIGACHAT_CREDENTIALS "MDE5YmMyYjYtMjMwZi03OWQyLWEyYzctNWFlODQ3NmEyYzM0OjU1YWUzODQ0LWE4ZjUtNGJiZi1hNDYwLTRiYjBlYTJhNDllNQ=="

bot = telebot.TeleBot(TG_TOKEN)
app = Flask('')

# --- ЧАСТЬ ДЛЯ RENDER (Health Check) ---
@app.route('/')
def home():
    return "Бот активен!"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- ЛОГИКА GIGACHAT (С ТВОИМ SCOPE B2B) ---
def get_ai_response(text, is_draw=False):
    try:
        # Вставил scope='GIGACHAT_API_B2B' как ты и просил
        with GigaChat(credentials=GIGACHAT_CREDENTIALS, verify_ssl_certs=False, scope='GIGACHAT_API_B2B') as giga:
            if is_draw:
                prompt = f"Нарисуй: {text}"
            else:
                prompt = f"Ты учитель Балди. Пообщайся с учеником: {text}"
            
            response = giga.chat(prompt)
            return response.choices[0].message.content
    except Exception as e:
        return f"❌ ОШИБКА GIGACHAT:\n{str(e)}"

# --- ОБРАБОТЧИКИ ---

# 1. Команда рисования (работает везде)
@bot.message_handler(commands=['draws'])
def draw_command(message):
    query = message.text.replace("/draws", "").strip()
    if not query:
        bot.reply_to(message, "🎨 Напиши, что нарисовать!")
        return
    bot.reply_to(message, "🎨 Рисую... Подожди.")
    bot.send_message(message.chat.id, get_ai_response(query, is_draw=True))

# 2. Команда для ГРУПП
@bot.message_handler(commands=['AsktoBaldiAI'])
def group_command(message):
    query = message.text.replace("/AsktoBaldiAI", "").strip()
    if not query:
        bot.reply_to(message, "📏 Задай вопрос!")
        return
    bot.reply_to(message, get_ai_response(query))

# 3. ЛИЧНЫЕ СООБЩЕНИЯ (ОТВЕТ БЕЗ КОМАНД)
@bot.message_handler(func=lambda m: m.chat.type == 'private' and not m.text.startswith('/'))
def private_talk(message):
    bot.send_chat_action(message.chat.id, 'typing')
    answer = get_ai_response(message.text)
    bot.reply_to(message, answer)

# --- ЗАПУСК ---
if __name__ == "__main__":
    # Запуск сервера для Render
    Thread(target=run_web_server).start()

    # Чистка очереди (от ошибки 409)
    bot.remove_webhook()
    bot.delete_webhook(drop_pending_updates=True)
    time.sleep(1)

    print("Балди запущен с B2B scope!")
    bot.infinity_polling(skip_pending=True)













