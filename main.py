import os, threading, telebot
from flask import Flask
from gigachat import GigaChat

app = Flask(__name__)
@app.route('/')
def h(): return "OK", 200

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

# ДАННЫЕ
ADMIN_ID = 6710377474
TOKEN = "8257171581:AAG9puuLo5RvkPNKz1XW2QDDBzpri1lw0kc"
G_KEY = "MDE5Yjg5ZTMtZjg5Ny03ZjE4LTg2NDctODIxN2VkNWI4NTI4OjVkZjViMDlhLTExMzMtNDg2MC04MWMzLTVjNDU5MDhkNmJjOA=="

bot = telebot.TeleBot(TOKEN)
paid_users = []

def get_ai(text):
    try:
        with GigaChat(credentials=G_KEY, verify_ssl_certs=False) as giga:
            return giga.chat(text).choices[0].message.content
    except: return "Ошибка связи с AI."

@bot.message_handler(commands=['premium'])
def pay(m):
    try:
        bot.send_invoice(m.chat.id, "VIP", "Доступ", "invoice_final_v1", "", "XTR", [telebot.types.LabeledPrice("1 Star", 1)])
    except Exception as e: print(e)

@bot.pre_checkout_query_handler(func=lambda q: True)
def checkout(q):
    bot.answer_pre_checkout_query(q.id, ok=True) # ЭТО ПОДТВЕРЖДЕНИЕ

@bot.message_handler(content_types=['successful_payment'])
def success(m):
    paid_users.append(m.from_user.id)
    bot.send_message(m.chat.id, "✅ Доступ открыт!")

@bot.message_handler(func=lambda m: True)
def handle(m):
    if m.from_user.id == ADMIN_ID or m.from_user.id in paid_users:
        bot.send_message(m.chat.id, get_ai(m.text))
    else:
        bot.send_message(m.chat.id, "Купите доступ: /premium")

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    bot.infinity_polling()
