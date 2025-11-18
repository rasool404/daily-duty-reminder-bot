import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message

from app.config import settings
from app.database import SessionLocal
from app import crud

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    # Create DB session
    db = SessionLocal()
    try:
        user = crud.upsert_user_from_telegram(db, message.from_user)
        db.commit()
    except Exception as e:
        db.rollback()
        print("Error in /start handler:", e)
        await message.answer("Something went wrong while registering you. Try again later.")
        return
    finally:
        db.close()

    await message.answer(
        f"Salom, {message.from_user.full_name}!\n"
        "I'll remind you about your \"navbatchilik\" when you are on duty. ✅"
    )


@dp.message(F.text == "/ping")
async def cmd_ping(message: Message):
    await message.answer("pong")


async def run_bot():
    """Start polling Telegram for updates."""
    print("Starting Telegram bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run_bot())
