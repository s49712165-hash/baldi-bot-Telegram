import asyncio
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
import edge_tts
import speech_recognition as sr
from pydub import AudioSegment
from gigachat import GigaChat

# === КОНФИГУРАЦИЯ ===
# Твой токен бота
TOKEN = "8257171581:AAG9puuLo5RvkPNKz1XW2QDDBzpri1lw0kc"
# Твой ключ GigaChat (уже вставлен!)
GIGACHAT_API_KEY = "MDE5Yjg5ZTMtZjg5Ny03ZjE4LTg2NDctODIxN2VkNWI4NTI4OjVkZjViMDlhLTExMzMtNDg2MC04MWMzLTVjNDU5MDhkNmJjOA=="

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Инициализация GigaChat (отключаем проверку сертификатов для работы на Render)
giga = GigaChat(credentials=GIGACHAT_API_KEY, verify_ssl_certs=False)

# Функция для превращения текста в голос (Светлана)
async def text_to_voice(text):
    output_file = "answer.mp3"
    communicate = edge_tts.Communicate(text, "ru-RU-SvetlanaNeural")
    await communicate.save(output_file)
    return output_file

# Функция для распознавания твоего ГС в текст
def voice_to_text(file_path):
    r = sr.Recognizer()
    try:
        audio = AudioSegment.from_file(file_path)
        audio.export("temp.wav", format="wav")
        with sr.AudioFile("temp.wav") as source:
            audio_data = r.record(source)
            return r.recognize_google(audio_data, language="ru-RU")
    except Exception:
        return None

# Запрос к нейросети GigaChat
async def get_ai_response(text):
    try:
        # Промпт: задаем характер Балди
        response = giga.chat(f"Ты — Балди из игры Baldi's Basics. Ты строгий учитель, любишь математику и иногда пугаешь учеников. Отвечай коротко. Фраза ученика: {text}")
        return response.choices[0].message.content
    except Exception as e:
        print(f"Ошибка GigaChat: {e}")
        return "У меня линейка сломалась, не могу ответить!"

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Я Балди! Я подключен к GigaChat. Присылай текст или ГС, и я отвечу тебе своим голосом!")

# Обработка голосовых сообщений
@dp.message(F.voice)
async def handle_voice(message: types.Message):
    file = await bot.get_file(message.voice.file_id)
    file_path = "user_voice.ogg"
    await bot.download_file(file.file_path, file_path)

    user_text = voice_to_text(file_path)
    
    if user_text:
        ai_response = await get_ai_response(user_text)
        voice_file = await text_to_voice(ai_response)
        await message.answer_voice(types.FSInputFile(voice_file))
        if os.path.exists(voice_file): os.remove(voice_file)
    else:
        await message.answer("Я не разобрал твоё бубнение! Говори четче!")
    
    for f in [file_path, "temp.wav"]:
        if os.path.exists(f): os.remove(f)

# Обработка текстовых сообщений
@dp.message(F.text)
async def handle_text(message: types.Message):
    ai_response = await get_ai_response(message.text)
    voice_file = await text_to_voice(ai_response)
    await message.answer_voice(types.FSInputFile(voice_file))
    if os.path.exists(voice_file): os.remove(voice_file)

async def main():
    print(">>> БОТ BALDI (GIGACHAT) ЗАПУЩЕН!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


