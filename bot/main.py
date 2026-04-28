import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession

from app.main_menu_handlers import router as base_router
from app.auth_handlers import router as authRouter
from app.create_offer_handlers import router as createOfferRouter

async def main():
    dp = Dispatcher()
    dp.include_router(authRouter)
    dp.include_router(createOfferRouter)
    dp.include_router(base_router)

    proxy_url = os.getenv("PROXY_URL")
    session = AiohttpSession(proxy=proxy_url)

    token = os.getenv("BOT_TOKEN")
    bot = Bot(token, session=session)

    print("started bot")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())