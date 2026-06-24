import asyncio
import os
import aiohttp
from typing import Optional
from urllib.parse import quote_plus

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


async def check_proxy(session: aiohttp.ClientSession, proxy: str, timeout: int = 5) -> Optional[str]:
    """
    Проверяет один прокси на работоспособность через Telegram API
    """
    # Добавляем схему если нужно
    if not proxy.startswith(('socks5://', 'http://', 'https://')):
        proxy = f"socks5://{proxy}"
    
    try:
        async with session.get(
            "https://api.telegram.org",
            proxy=proxy,
            timeout=aiohttp.ClientTimeout(total=timeout)
        ) as response:
            if response.status == 200:
                return proxy
    except Exception as e:
        # Прокси не работает
        pass
    return None


async def find_working_proxy_parallel(proxy_string: str, max_concurrent: int = 20) -> Optional[str]:
    """
    Находит рабочий прокси из строки с прокси через запятую.
    Проверка происходит параллельно для скорости.
    """
    if not proxy_string:
        print("⚠️ PROXY_URL не задан")
        return None
    
    # Парсим строку с прокси
    proxy_list = [p.strip() for p in proxy_string.split(',') if p.strip()]
    
    if not proxy_list:
        print("⚠️ Список прокси пуст")
        return None
    
    print(f"🔍 Начинаем проверку {len(proxy_list)} прокси...")
    
    # Добавляем схему для всех прокси
    proxy_list = [
        f"socks5://{p}" if not p.startswith(('socks5://', 'http://', 'https://')) else p
        for p in proxy_list
    ]
    
    working_proxy = None
    
    async with aiohttp.ClientSession() as session:
        # Проверяем порциями для контроля нагрузки
        for i in range(0, len(proxy_list), max_concurrent):
            chunk = proxy_list[i:i + max_concurrent]
            
            # Создаем задачи для параллельной проверки
            tasks = [
                check_proxy(session, proxy) 
                for proxy in chunk
            ]
            
            # Ждем завершения всех проверок в чанке
            results = await asyncio.gather(*tasks)
            
            # Ищем первый рабочий
            for result in results:
                if result:
                    working_proxy = result
                    print(f"✅ Найден рабочий прокси: {working_proxy}")
                    return working_proxy
            
            print(f"   Проверено {min(i + max_concurrent, len(proxy_list))} из {len(proxy_list)}...")
    
    print("❌ Ни один прокси не работает!")
    return None


async def get_working_proxy_with_retry(proxy_string: str, max_retries: int = 3) -> Optional[str]:
    """
    Пытается найти рабочий прокси с повторными попытками
    """
    for attempt in range(max_retries):
        print(f"🔄 Попытка {attempt + 1} из {max_retries}")
        proxy = await find_working_proxy_parallel(proxy_string)
        if proxy:
            return proxy
        # Небольшая задержка перед повторной попыткой
        await asyncio.sleep(0.5)
    
    return None


async def main():
    # Инициализация Redis
    redis_password = os.getenv("REDIS_PASSWORD")
    redis_host = os.getenv("REDIS_HOST")
    redis_port = os.getenv("REDIS_PORT")

    redis_url = f"redis://{redis_host}:{redis_port}/0"
    if redis_password:
        redis_password = quote_plus(redis_password)
        redis_url = f"redis://:{redis_password}@{redis_host}:{redis_port}/0"

    redis_client = Redis.from_url(redis_url)
    fsm_storage = RedisStorage(redis=redis_client)

    # Настройка диспетчера
    dp = Dispatcher(storage=fsm_storage)
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())

    # Подключение роутеров
    dp.include_router(base_router)
    dp.include_router(premium_router)
    dp.include_router(auth_router)
    dp.include_router(manage_offers_router)
    dp.include_router(search_offers_router)
    dp.include_router(admin_router)

    # --- РАБОТА С ПРОКСИ ---
    proxy_url = os.getenv("PROXY_URL")
    
    working_proxy = None
    
    if proxy_url:
        # Пытаемся найти рабочий прокси
        working_proxy = await get_working_proxy_with_retry(proxy_url, max_retries=2)
        
        if working_proxy:
            print(f"✅ Бот будет использовать прокси: {working_proxy}")
        else:
            print("⚠️ Не удалось найти рабочий прокси. Бот запустится без прокси.")
            working_proxy = None
    else:
        print("ℹ️ PROXY_URL не задан, бот запускается без прокси")

    # Создаем сессию с рабочим прокси (или без него)
    if working_proxy:
        session = AiohttpSession(proxy=working_proxy)
    else:
        session = AiohttpSession()  # Без прокси

    # Инициализация бота
    token = os.getenv("BOT_TOKEN")
    bot = Bot(token, session=session)

    print("🚀 Бот запущен и готов к работе!")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
