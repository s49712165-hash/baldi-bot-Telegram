import asyncio, urllib.parse, requests, uuid
from aiogram import Bot, Dispatcher, types

# === ТВОИ ДАННЫЕ ===
TG_TOKEN = "8257171581:AAG9puuLo5RvkPNKz1XW2QDDBzpri1lw0kc"

# Твой авторизационный код GigaChat
GIGA_AUTH_CODE = "MDE5Yjg5ZTMtZjg5Ny03ZjE4LTg2NDctODIxN2VkNWI4NTI4OjI4OGYzOTNlLWEzMDctNDZlNC1iNTgyLWRlODg2ZjYxNWRmZQ=="

bot, dp = Bot(token=TG_TOKEN), Dispatcher()

# Функция получения токена (ключа) от Сбера
def get_giga_token(auth_code):
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),
        'Authorization': f'Basic {auth_code}'
    }
    payload = {'scope': 'GIGACHAT_API_PERS'}
    # Игнорируем проверку SSL для работы на Android
    response = requests.post(url, headers=headers, data=payload, verify=False)
    return response.json().get('access_token')

@dp.message()
async def handle_message(m: types.Message):
    if not m.text: return
    
    # Команда рисования картинок
    if m.text.startswith("/рисуй"):
        prompt = m.text[7:].strip()
        if not prompt:
            await m.answer("Напиши, что нарисовать, например: /рисуй кота")
            return
        await m.answer_photo(f"https://pollinations.ai/p/{urllib.parse.quote(prompt)}?width=1024&height=1024&model=flux")
        return

    # Общение с GigaChat
    try:
        await bot.send_chat_action(m.chat.id, "typing")
        
        # Получаем временный доступ
        token = get_giga_token(GIGA_AUTH_CODE)
        
        if not token:
            await m.answer("❌ Ошибка авторизации. Проверь ключ Сбера!")
            return

        # Отправляем запрос нейросети
        url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        data = {
            "model": "GigaChat",
            "messages": [{"role": "user", "content": m.text}],
            "temperature": 0.7
        }
        
        res = requests.post(url, headers=headers, json=data, verify=False)
        answer = res.json()['choices'][0]['message']['content']
        await m.answer(answer)
            
    except Exception as e:
        await m.answer(f"🤖 У меня возникла заминка. Попробуй еще раз!\nОшибка: {e}")

async def main():
    # Отключаем лишние предупреждения в консоли
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    print(">>> БОТ BALDI AI УСПЕШНО ЗАПУЩЕН!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

