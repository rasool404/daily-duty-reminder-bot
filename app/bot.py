import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from app.config import settings

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.answer("Salom! I'm the navbatchilik bot.")


@dp.message(F.text == "/ping")
async def cmd_ping(message: Message):
    await message.answer("pong")


async def run_bot():
    """Start polling Telegram for updates."""
    print("Starting Telegram bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run_bot())
