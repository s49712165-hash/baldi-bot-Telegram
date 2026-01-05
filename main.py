import asyncio
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
import edge_tts
import speech_recognition as sr
from pydub import AudioSegment

# === КОНФИГУРАЦИЯ ===
# Твой актуальный токен
TOKEN = "8257171581:AAG9puuLo5RvkPNKz1XW2QDDBzpri1lw0kc"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Функция для превращения текста в голос (как у Салюта)
async def text_to_voice(text):
    output_file = "answer.mp3"
    # Голос 'ru-RU-SvetlanaNeural' очень похож на человеческий
    communicate = edge_tts.Communicate(text, "ru-RU-SvetlanaNeural")
    await communicate.save(output_file)
    return output_file

# Функция для распознавания того, что ты сказал в ГС
def voice_to_text(file_path):
    r = sr.Recognizer()
    # Конвертируем .ogg (из телеги) в .wav (для распознавания)
    audio = AudioSegment.from_file(file_path)
    audio.export("temp.wav", format="wav")
    
    with sr.AudioFile("temp.wav") as source:
        audio_data = r.record(source)
        try:
            return r.recognize_google(audio_data, language="ru-RU")
        except:
            return "Не удалось распознать речь"

# Обработка команды /start
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Я Балди. Я теперь слышу твои ГС и отвечаю голосом!")

# ОБРАБОТКА ГОЛОСОВЫХ СООБЩЕНИЙ (Голос на Голос)
@dp.message(F.voice)
async def handle_voice(message: types.Message):
    # 1. Скачиваем ГС
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = "user_voice.ogg"
    await bot.download_file(file.file_path, file_path)

    # 2. Переводим голос в текст
    user_text = voice_to_text(file_path)
    
    # 3. Формируем ответ (здесь можно подключить твою нейросеть)
    ai_response = f"Ты сказал: '{user_text}'. Я тебя услышал!" 

    # 4. Превращаем ответ в голос
    voice_file = await text_to_voice(ai_response)

    # 5. Отправляем голосовой ответ
    await message.answer_voice(types.FSInputFile(voice_file))
    
    # Чистим временные файлы
    if os.path.exists(file_path): os.remove(file_path)
    if os.path.exists(voice_file): os.remove(voice_file)

# Обработка обычного текста (тоже отвечает голосом)
@dp.message(F.text)
async def handle_text(message: types.Message):
    ai_response = f"Балди говорит: {message.text}" # Тут твоя логика нейронки
    voice_file = await text_to_voice(ai_response)
    await message.answer_voice(types.FSInputFile(voice_file))
    if os.path.exists(voice_file): os.remove(voice_file)

async def main():
    print(">>> БОТ BALDI AI ЗАПУЩЕН!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


