from typing import Optional
from dataclasses import asdict

from .base import APIClient

from ..model.user import *

class UsersApi(APIClient):
    """API для взаимодействия с пользователями."""
    async def get_user_by_id(self, user_id: int) -> User | None:
        """Получает пользователя по ID"""
        result = await self._request("GET", f"user/{user_id}", expected_status=200)
        if result is None:
            return None
        
        # Извлекаем ruleset из ответа, если есть
        ruleset_data = result.get("details", {})
        ruleset = Ruleset(
            smoking=ruleset_data.get("smoking", False),
            children=ruleset_data.get("children", False),
            pets=ruleset_data.get("pets", False)
        )
        
        return User(
            id=user_id,
            name=result.get("name", ""),
            age=result.get("age", 0),
            city=result.get("city", ""),
            description=result.get("description", ""),
            media_files=result.get("media_files", []),
            details=ruleset
        )
    
    async def create_user(self, user: User) -> bool:
        """Создаёт пользователя"""
        body = asdict(user)
        await self._request("POST", "user", data=body, expected_status=201)
    
    async def edit_user(self, user_id: int, user: UserVisibleData):
        """Обновляет пользователя (только указанные поля)"""
        # Убираем поля со значением None
        data = {k: v for k, v in asdict(user).items() if v is not None}
        
        if not data:
            print("No fields to update")
        
        await self._request("PATCH", f"user/{user_id}", data=data, expected_status=200)

_users_api = UsersApi()

async def get_user_by_id(user_id: int) -> Optional[User]:
    return await _users_api.get_user_by_id(user_id)

async def create_user(u: User):
    await _users_api.create_user(u)

async def edit_user(id: int, u: UserVisibleData):
    await _users_api.edit_user(id, u)

async def user_exists(user_id: int) -> bool:
    user = await _users_api.get_user_by_id(user_id)
    return user != None