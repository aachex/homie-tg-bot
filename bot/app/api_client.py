import aiohttp
import os
from dataclasses import dataclass, field
from typing import List, Optional, Any
from functools import wraps

API_HOST = os.getenv("API_HOST")
API_PORT = os.getenv("API_PORT")
API_KEY = os.getenv("API_KEY")

# ========== Классы ==========
@dataclass
class UserEdit:
    name: Optional[str] = None
    age: Optional[int] = None
    city: Optional[str] = None
    description: Optional[str] = None
    media_files: Optional[List[str]] = None

@dataclass
class User(UserEdit):
    id: int = -1
    name: str = ""
    age: int = 0
    city: str = ""
    description: str = ""
    media_files: List[str] = field(default_factory=list)

class APIClient:
    """Базовый API клиент с общими методами"""
    
    def __init__(self):
        self.base_url = f"http://{API_HOST}:{API_PORT}/api/v1"
        self.headers = {
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        }
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
        expected_status: int = 200
    ) -> Optional[dict]:
        """Универсальный метод для всех HTTP запросов"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data
                ) as resp:
                    if resp.status == 404:
                        return None
                    
                    if resp.status != expected_status:
                        print(f"Unexpected status {resp.status}: {await resp.text()}")
                        return None
                    
                    if resp.status == 204:  # No content
                        return {}
                    
                    return await resp.json()
                    
        except aiohttp.ClientError as e:
            print(f"HTTP error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    
    # ========== User методы ==========
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


_client = APIClient()

async def get_user_by_id(user_id: int) -> Optional[User]:
    return await _client.get_user_by_id(user_id)

async def create_user(u: User) -> bool:
    return await _client.create_user(u)

async def edit_user(id: int, u: UserEdit) -> bool:
    return await _client.edit_user(id, u)

async def user_exists(user_id: int) -> bool:
    user = await _client.get_user_by_id(user_id)
    return user != None
