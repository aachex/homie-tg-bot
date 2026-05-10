from datetime import datetime

from .base import APIClient

class StatsApi(APIClient):
    async def create_activity(self, user_id: int, action: str, action_data: dict[str, any]):
        body = {
            "user_id": user_id,
            "action": action,
            "action_data": action_data
        }
        await self._request("POST", "stats/user-activity", data=body, expected_status=201)

_stats_api = StatsApi()

async def create_activity(user_id: int, action: str, action_data: dict[str, any]):
    await _stats_api.create_activity(user_id, action, action_data)
