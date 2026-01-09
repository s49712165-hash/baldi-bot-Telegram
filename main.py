import os
import threading
from flask import Flask
import telebot
from gigachat import GigaChat

# --- 1. ВЕБ-СЕРВЕР ДЛЯ RENDER ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "OK", 200

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- 2. НАСТРОЙКИ (ТВОЙ ID И ТОКЕНЫ) ---
ADMIN_ID = 6710377474  # Твой ID вставлен!

TG_TOKEN = "8257171581:AAG9puuLo5RvkPNKz1XW2QDDBzpri1lw0kc"
GIGA_KEY = "MDE5Yjg5ZTMtZjg5Ny03ZjE4LTg2NDctODIxN2VkNWI4NTI4OjVkZjViMDlhLTExMzMtNDg2MC04MWMzLTVjNDU5MDhkNmJjOA=="

bot = telebot.TeleBot(TG_TOKEN)
total_sales = 0
paid_users = []  # <--- ДОБАВЬ ЭТУ СТРОКУ

# --- 3. ЛОГИКА GIGACHAT ---
def get_ai_answer(text):
    try:
        with GigaChat(credentials=GIGA_KEY, verify_ssl_certs=False) as giga:
            response = giga.chat(text)
            return response.choices[0].message.content

