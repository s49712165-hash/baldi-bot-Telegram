import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from gigachat import GigaChat

# --- ДАННЫЕ АВТОРИЗАЦИИ ---
TG_TOKEN = "8400025214:AAHAkfze6QAZjULpCY_R9av1vLAM4ec8Idk"
GIGACHAT_CREDENTIALS = "MDE5YjhlMmMtNzhiOC03YThjLTk1ZTQtM2NkOTNjNThlNjkyOmJlZTdiZmUwLWMzODMtNGMxZi05N2FmLTkzZTYwOWQzMTgzMw=="

# Инициализация ботов
bot = Bot(token=TG_TOKEN)
dp = Dispatcher()

# --- ФУНКЦИИ GIGACHAT ---

def get_baldi_response(text, is_image=False):
    # verify_ssl_certs=False нужен, если не установлены сертификаты Минцифры
    with GigaChat(credentials=GIGACHAT_CREDENTIALS, verify_ssl_certs=False) as giga:
        if is_image:
            # Для генерации фото просим GigaChat нарисовать
            prompt = f"Нарисуй: {text}"
            res = giga.chat(prompt)
            # Гигачат возвращает тег <img src='...'> в тексте
            return res.choices[0].message.content
        else:
            # Для общения задаем роль Балди
            payload = {
                "messages": [
                    {"role": "system", "content": "Ты — Балди из Baldi's Basics. Ты учитель математики, который злится, когда ошибаются, и обожаешь шлепать линейкой по руке. Твоя речь строгая, странная и учительская."},
                    {"role": "user", "content": text}
                ]
            }
            res = giga.chat(payload)
            return res.choices[0].message.content

# --- ОБРАБОТЧИКИ ---

# Команда для общения в группе
@dp.message(Command("AsktoBaldiAI"))
async def ask_handler(message: types.Message):
    # Получаем текст после команды
    user_text = message.text.replace("/AsktoBaldiAI", "").strip()
    
    if not user_text:
        await message.reply("Ты что-то промямлил? Пиши четче, или получишь линейкой! 📏")
        return

    response = get_baldi_response(user_text)
    await message.reply(response)

# Команда для рисования
@dp.message(Command("draws"))
async def draw_handler(message: types.Message):
    prompt = message.text.replace("/draws", "").strip()
    
    if not prompt:
        await message.reply("Что мне нарисовать? У тебя пустая голова, как этот лист! 🎨")
        return

    status_msg = await message.answer("Так-так... Рисую... ✏️")
    
    try:
        result = get_baldi_response(prompt, is_image=True)
        # Если GigaChat вернул ссылку или описание картинки
        await message.answer(f"Вот твой результат для '{prompt}':\n\n{result}")
        await status_msg.delete()
    except Exception as e:
        logging.error(e)
        await status_msg.edit_text("Ошибка в школьном журнале! (Не удалось создать фото)")

# Запуск
async def main():
    logging.basicConfig(level=logging.INFO)
    print("Балди запущен и готов учить!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

