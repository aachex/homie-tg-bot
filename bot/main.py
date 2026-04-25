import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart

from aiogram.client.session.aiohttp import AiohttpSession

dp = Dispatcher()

@dp.message(CommandStart())
async def start(msg: Message):
    await msg.answer("Привет!")

async def main():
    proxy_url = os.getenv("PROXY_URL")
    session = AiohttpSession(proxy=proxy_url)

    token = os.getenv("BOT_TOKEN")
    bot = Bot(token, session=session)

    await dp.start_polling(bot)

if __name__ == '__main__':
    print("START")
    asyncio.run(main())