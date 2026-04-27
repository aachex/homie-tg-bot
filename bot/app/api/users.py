from dataclasses import dataclass, field
from typing import List, Optional

from .base import APIClient

@dataclass
class User:
    """Данные пользователя."""
    id: int = -1
    name: str = ""
    age: int = 0
    city: str = ""
    description: str = ""
    media_files: List[str] = field(default_factory=list)

@dataclass
class UserEdit:
    """Изменяемые данные пользователя."""
    name: Optional[str] = None
    age: Optional[int] = None
    city: Optional[str] = None
    description: Optional[str] = None
    media_files: Optional[List[str]] = None

class UsersApi(APIClient):
    """API для взаимодействия с пользователями."""
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Получает пользователя по ID"""
        result = await self._request("GET", f"user/{user_id}", expected_status=200)
        
        if result is None:
            return None
        
        return User(
            id=user_id,
            name=result.get("name", ""),
            age=result.get("age", 0),
            city=result.get("city", ""),
            description=result.get("description", ""),
            media_files=result.get("media_files", [])
        )
    
    async def create_user(self, user: User) -> bool:
        """Создаёт пользователя"""
        result = await self._request("POST", "user", data=user.__dict__, expected_status=201)
        return result is not None
    
    async def edit_user(self, user_id: int, user: UserEdit) -> bool:
        """Обновляет пользователя (только указанные поля)"""
        # Убираем поля со значением None
        data = {k: v for k, v in user.__dict__.items() if v is not None}
        
        if not data:
            print("No fields to update")
            return True
        
        result = await self._request("PATCH", f"user/{user_id}", data=data, expected_status=200)
        return result is not None

_client = UsersApi()

async def get_user_by_id(user_id: int) -> Optional[User]:
    return await _client.get_user_by_id(user_id)

async def create_user(u: User) -> bool:
    return await _client.create_user(u)

async def edit_user(id: int, u: UserEdit) -> bool:
    return await _client.edit_user(id, u)

async def user_exists(user_id: int) -> bool:
    user = await _client.get_user_by_id(user_id)
    return user != None