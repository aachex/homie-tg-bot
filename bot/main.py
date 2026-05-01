import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession

from app.handlers.main_menu import router as base_router
from app.handlers.auth import router as authRouter
from app.handlers.offer import router as manageOffersRouter
from app.handlers.search_offers import router as searchOffersRouter

async def main():
    dp = Dispatcher()
    dp.include_router(base_router)
    dp.include_router(authRouter)
    dp.include_router(manageOffersRouter)
    dp.include_router(searchOffersRouter)

    proxy_url = os.getenv("PROXY_URL")
    session = AiohttpSession(proxy=proxy_url)

    token = os.getenv("BOT_TOKEN")
    bot = Bot(token, session=session)

    print("started bot")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
