import aiohttp
import os
import json
from dataclasses import dataclass, field
from typing import List

API_HOST = os.getenv("API_HOST")
API_PORT = os.getenv("API_PORT")
API_KEY = os.getenv("API_KEY")

@dataclass
class UserEdit:
    name: str | None = None
    age: int | None = None
    city: str | None = None
    description: str | None = None
    media_files: List[str] | None = None

@dataclass
class User(UserEdit):
    id: int = -1
    name: str = ""
    age: int = 0
    city: str = ""
    description: str = ""
    media_files: List[str] = field(default_factory=list)

async def get_user_by_id(user_id: int) -> User:
    """Асинхронно получает пользователя по ID из API"""
    url = f"http://{API_HOST}:{API_PORT}/api/v1/user/{user_id}"
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, headers=headers) as resp:
                if resp.status == 404:
                    return User(id=-1)  # Пользователь не найден
                
                resp.raise_for_status()
                data = await resp.json()  # await для JSON
                
                return User(
                    id=user_id,
                    name=data.get("name", ""),
                    age=data.get("age", 0),
                    city=data.get("city", ""),
                    description=data.get("description"),
                    media_files=data.get("media_files", [])
                )
                
    except aiohttp.ClientError as e:
        print(f"HTTP error while fetching user {user_id}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
    
async def create_user(u: User):
    url = f"http://{API_HOST}:{API_PORT}/api/v1/user"
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, headers=headers, json=u.__dict__) as resp:
                resp.raise_for_status()
    except aiohttp.ClientError as e:
        print(f"HTTP error while creating user: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

async def edit_user(id: int, u: UserEdit):
    url = f"http://{API_HOST}:{API_PORT}/api/v1/user/{id}"
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.patch(url=url, headers=headers, json=u.__dict__) as resp:
                resp.raise_for_status()
                
                
    except aiohttp.ClientError as e:
        print(f"HTTP error while creating user: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None