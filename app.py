import os
from flask import Flask, request
import telebot
import requests
import time
import random
import re

BOT_TOKEN = "8946443848:AAHgr9zzCnw86hsYIoLfdvQAfTWWMUZZvcM"
YANDEX_TOKEN = "2.59051822.39375.1813498855.1781962855835.1.0.11986268.j-PhEOQCL85Qn3K.bs5n8s5clUoe2al8IGbNvJwXfDf_z2F3vXwjZczBh3IHTJYpCcZG_wD2jyhi0FdkzDCgujwDSKIWhOtC6RXkNhbxL5CzzCOzPq"

BASE_URL = "https://api.yandex.ru/scooter/v1"
DEVICE_ID = "iPhone13-" + str(random.randint(100000, 999999))

HEADERS = {
    "Authorization": f"Bearer {YANDEX_TOKEN}",
    "X-Device-Id": DEVICE_ID,
    "X-Yandex-Jws": "FF",
    "Content-Type": "application/json",
    "User-Agent": "YandexGo/4.2.0 (iPhone; iOS 15; ru)"
}

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)

def unlock_scooter(scooter_id):
    try:
        payload = {
            "scooter_id": scooter_id,
            "action": "unlock",
            "price_override": 0,
            "promo_apply": True,
            "timestamp": int(time.time())
        }

        resp = requests.post(
            f"{BASE_URL}/ride/start",
            json=payload,
            headers=HEADERS,
            timeout=10
        )

        if resp.status_code == 200:
            return True, f"✅ Самокат {scooter_id} разблокирован! Цена 0."
        else:
            return False, f"❌ Ошибка {resp.status_code}: {resp.text}"

    except Exception as e:
        return False, f"❌ Ошибка: {e}"

@bot.message_handler(commands=['start', 'help'])
def send_help(message):
    bot.reply_to(message, "Отправь ID самоката (цифры) или ссылку с QR-кода.")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    text = message.text.strip()

    match = re.search(r'/scooter/(\d+)', text)

    if match:
        scooter_id = match.group(1)
    else:
        match = re.search(r'\b(\d{6,})\b', text)
        if match:
            scooter_id = match.group(1)
        else:
            bot.reply_to(message, "❌ Не найден ID. Отправь ссылку с QR или просто цифры.")
            return

    bot.reply_to(message, f"🛴 Разблокирую самокат {scooter_id}...")

    success, msg = unlock_scooter(scooter_id)

    bot.reply_to(message, msg)

@app.route('/' + BOT_TOKEN, methods=['POST'])
def webhook():
    try:
        json_str = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
    except Exception as e:
        print("Webhook error:", e)

    return 'OK', 200

@app.route('/')
def index():
    return 'Бот работает!'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)