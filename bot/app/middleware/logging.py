from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable

from ..api.stats import create_activity

class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        action = data["handler"].callback.__name__
        action_data: dict[str, Any] = {}

        if isinstance(event, Message):
            action_data["message"] = event.text
        else:
            action_data["callback"] = event.data

        await create_activity(user_id, action, action_data)
        
        return await handler(event, data)
