import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession

from app.create_user import router as createUserRouter

from dotenv import load_dotenv

async def main():
    load_dotenv("../config/dev/bot.env")

    dp = Dispatcher()
    dp.include_router(createUserRouter)

    proxy_url = os.getenv("PROXY_URL")
    session = AiohttpSession(proxy=proxy_url)

    token = os.getenv("BOT_TOKEN")
    bot = Bot(token, session=session)

    await dp.start_polling(bot)

if __name__ == '__main__':
    print("START")
    asyncio.run(main())