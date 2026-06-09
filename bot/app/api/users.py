import datetime
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
        
        sex = None
        if flags_data.get("sex"):
            sex = SexEnum(flags_data["sex"])
        
        flags = UserFlags(
            smoking=flags_data.get("smoking"),
            children=children,
            pets=pets,
            occupants_count=flags_data.get("occupants_count"),
            noise_lvl=noise_lvl,
            works_from_home=flags_data.get("works_from_home"),
            alcohol=alcohol,
            sex=sex,
            age_min=flags_data.get("age_min"),
            age_max=flags_data.get("age_max"),
        )
        
        return User(
            id=user_id,
            name=result.get("name", ""),
            city=result.get("city", ""),
            description=result.get("description", ""),
            media_files=result.get("media_files", []),
            flag_processing=result.get("flag_processing", False),
            flags=flags,
        )
    
    async def create_user(self, user: UserCreate) -> bool:
        """Создаёт пользователя"""
        body = asdict(user)
        await self._request("POST", "user", data=body, expected_status=201)
    
    async def edit_user(self, user_id: int, user: UserEdit):
        """Обновляет пользователя (только указанные поля)"""
        # Убираем поля со значением None
        data = asdict(user)
        await self._request("PUT", f"user/{user_id}", data=data, expected_status=200)

    async def get_premium_data(self, user_id: int) -> PremiumData | None:
        result = await self._request("GET", f"user/{user_id}/premium", expected_status=200)
        if result is None:
            return None
        
        return PremiumData(
            is_premium=result.get("is_premium", False),
            until=datetime.fromisoformat(result.get("premium_until", datetime.now()))
        )

    async def get_limits(self, user_id: int) -> UserLimits | None:
        """Получает лимиты пользователя"""
        result = await self._request("GET", f"user/{user_id}/limits", expected_status=200)
        if result is None:
            return None
        
        premium_data = result.get("premium_data")
        
        return UserLimits(
            premium=PremiumData(
                is_premium=premium_data.get("is_premium"),
                until=datetime.fromisoformat(premium_data.get("premium_until", datetime.now()))
            ),
            max_offers=result.get("max_offers_count"),
            max_likes_per_day=result.get("max_likes_per_day")
        )
    
    async def renew_premium(self, user_id: int, days: int) -> datetime | None:
        data = {
            "user_id": user_id,
            "days": days,
        }
        resp_json = await self._request("POST", "user/renew-premium", data=data)
        if resp_json is None:
            return None
        
        return datetime.fromisoformat(resp_json["premium_until"])

_users_api = UsersApi()

async def get_user_by_id(user_id: int) -> Optional[User]:
    return await _users_api.get_user_by_id(user_id)

async def create_user(u: UserCreate):
    await _users_api.create_user(u)

async def edit_user(id: int, u: UserEdit):
    await _users_api.edit_user(id, u)

async def get_user_limits(id: int) -> UserLimits:
    return await _users_api.get_limits(id)

async def get_premium_data(user_id: int) -> PremiumData | None:
    return await _users_api.get_premium_data(user_id)

async def renew_premium(user_id: int, days: int) -> datetime | None:
    return await _users_api.renew_premium(user_id, days)
