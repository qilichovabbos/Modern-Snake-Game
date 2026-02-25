import asyncio
import json
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import CommandStart
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")  # URL hosting snake.html

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

async def main():
    await dp.start_polling(bot)

if __name__=="__main__":
    asyncio.run(main())