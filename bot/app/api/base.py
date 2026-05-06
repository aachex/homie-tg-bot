import aiohttp
import os

from typing import Optional

API_HOST = os.getenv("API_HOST")
API_PORT = os.getenv("API_PORT")
API_KEY = os.getenv("API_KEY")

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
    
    



