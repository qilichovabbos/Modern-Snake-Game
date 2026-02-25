import json
import os
from flask import Flask, request
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import CommandStart
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")  # Static site URL

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

LEADERBOARD_FILE = "leaderboard.json"

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
    user_id=str(user_id)
    if user_id not in data or score>data[user_id].get("best_score",0):
        data[user_id] = {"username":username,"best_score":score}
    save_leaderboard(data)

@dp.message(CommandStart())
async def start_handler(message: Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="🎮 Play Snake",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ]]
    )
    await message.answer("🔥 Modern Snake!\nPress the button below to play:", reply_markup=kb)

@dp.message(F.web_app_data)
async def webapp_data_handler(message: Message):
    try:
        data = json.loads(message.web_app_data.data)
        score = int(data.get("score",0))
    except:
        await message.answer("⚠️ Invalid score data.")
        return
    user = message.from_user
    update_score(user.id, user.username or user.full_name, score)
    # show top 5
    data = load_leaderboard()
    top = sorted(data.values(), key=lambda x:x["best_score"], reverse=True)[:5]
    text = "🏆 Top Players:\n"
    for i,p in enumerate(top,1):
        text += f"{i}. {p['username']} — {p['best_score']}\n"
    await message.answer(f"🎮 Game Over!\nYour Score: {score}\n\n{text}")

# ===== Flask server =====
app = Flask(__name__)

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def telegram_webhook():
    update = request.json
    await dp.process_update(update)
    return "OK"

if __name__ == "__main__":
    # Set webhook once (replace YOUR_DOMAIN with HTTPS domain)
    import asyncio
    async def set_hook():
        webhook_url = f"https://YOUR_DOMAIN/{BOT_TOKEN}"
        await bot.set_webhook(webhook_url)
    asyncio.run(set_hook())

    # Start Flask server
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
