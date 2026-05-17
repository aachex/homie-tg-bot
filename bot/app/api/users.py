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
        
        # Извлекаем флаги из ответа
        flags_data = result.get("flags", {})
        
        # Парсим enum-поля
        children = None
        if flags_data.get("children"):
            children = ChildrenEnum(flags_data["children"])
        
        pets = None
        if flags_data.get("pets"):
            pets = PetsEnum(flags_data["pets"])
        
        noise_lvl = None
        if flags_data.get("noise_lvl"):
            noise_lvl = NoiseLvlEnum(flags_data["noise_lvl"])
        
        alcohol = None
        if flags_data.get("alcohol"):
            alcohol = AlcoholEnum(flags_data["alcohol"])
        
        flags = UserFlags(
            smoking=flags_data.get("smoking"),
            children=children,
            pets=pets,
            occupants_count=flags_data.get("occupants_count"),
            noise_lvl=noise_lvl,
            works_from_home=flags_data.get("works_from_home"),
            alcohol=alcohol,
            age_min=flags_data.get("age_min"),
            age_max=flags_data.get("age_max"),
        )
        
        return User(
            id=user_id,
            name=result.get("name", ""),
            city=result.get("city", ""),
            media_files=result.get("media_files", []),
            flags=flags,
        )
    
    async def create_user(self, user: UserCreate) -> bool:
        """Создаёт пользователя"""
        body = asdict(user)
        await self._request("POST", "user", data=body, expected_status=201)
    
    async def edit_user(self, user_id: int, user: UserEdit):
        """Обновляет пользователя (только указанные поля)"""
        # Убираем поля со значением None
        data = {k: v for k, v in asdict(user).items() if v is not None}
        
        if not data:
            print("No fields to update")
        
        await self._request("PATCH", f"user/{user_id}", data=data, expected_status=200)

_users_api = UsersApi()

async def get_user_by_id(user_id: int) -> Optional[User]:
    return await _users_api.get_user_by_id(user_id)

async def create_user(u: UserCreate):
    await _users_api.create_user(u)

async def edit_user(id: int, u: UserEdit):
    await _users_api.edit_user(id, u)

async def user_exists(user_id: int) -> bool:
    user = await _users_api.get_user_by_id(user_id)
    return user != None