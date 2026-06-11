import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.redis import RedisStorage

from redis.asyncio import Redis

from app.middleware.logging import LoggingMiddleware

from app.handlers.main_menu import router as base_router
from app.handlers.auth import router as auth_router
from app.handlers.offer import router as manage_offers_router
from app.handlers.search_offers import router as search_offers_router
from app.handlers.admin import router as admin_router
from app.handlers.premium import router as premium_router

async def main():
    redis_password = os.getenv("REDIS_PASSWORD")
    redis_host = os.getenv("REDIS_HOST")
    redis_port = os.getenv("REDIS_PORT")
    redis_url = f"redis://:{redis_password}@{redis_host}:{redis_port}/0"

    redis_client = Redis.from_url(redis_url)

    fsm_storage = RedisStorage(redis=redis_client)

    dp = Dispatcher(storage=fsm_storage)
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())

    dp.include_router(base_router)
    dp.include_router(premium_router)
    dp.include_router(auth_router)
    dp.include_router(manage_offers_router)
    dp.include_router(search_offers_router)
    dp.include_router(admin_router)

    proxy_url = os.getenv("PROXY_URL")
    session = AiohttpSession(proxy=proxy_url)

    token = os.getenv("BOT_TOKEN")
    bot = Bot(token, session=session)

    print("started bot")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
