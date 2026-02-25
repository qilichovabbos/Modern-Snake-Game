import os
from flask import Flask, request
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ===== Environment variables =====
BOT_TOKEN = os.getenv("BOT_TOKEN")       # Telegram token
WEBAPP_URL = os.getenv("WEBAPP_URL")     # Static site URL (HTML fayling URL)
DOMAIN = os.getenv("DOMAIN")             # Render / Railway domain, HTTPS bilan

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ===== Leaderboard =====
LEADERBOARD_FILE = "leaderboard.json"

import json

def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE,"r",encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_leaderboard(data):
    with open(LEADERBOARD_FILE,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2,ensure_ascii=False)

def update_score(user_id, username, score):
    data = load_leaderboard()
    user_id = str(user_id)
    if user_id not in data or score > data[user_id].get("best_score",0):
        data[user_id] = {"username": username, "best_score": score}
    save_leaderboard(data)

# ===== /start handler =====
@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(
        text="🎮 Play Snake",
        url=WEBAPP_URL
    ))
    bot.send_message(
        message.chat.id,
        "🔥 Modern Snake!\nPress the button below to play:",
        reply_markup=markup
    )

# ===== Webhook endpoint =====
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = request.json
    bot.process_new_updates([telebot.types.Update.de_json(update)])
    return "OK"

# ===== Set webhook va Flask server =====
if __name__ == "__main__":
    # Telegram webhook sozlash
    bot.remove_webhook()
    bot.set_webhook(f"{DOMAIN}/{BOT_TOKEN}")

    # Flask server ishga tushirish
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
