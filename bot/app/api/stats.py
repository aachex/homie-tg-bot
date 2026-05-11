from datetime import datetime, timezone

from .base import APIClient
from ..model.stats import DailyStat

class StatsApi(APIClient):
    async def get_dau(self, from_date: datetime, to_date: datetime) -> list[DailyStat] | None:
        body = {
            "from": from_date.astimezone(timezone.utc).isoformat(),
            "to": to_date.astimezone(timezone.utc).isoformat()
        }
        daily_dau = await self._request("POST", "stats/dau", data=body)
        if daily_dau is None:
            return None
        
        dau_list = list(daily_dau)
        return [DailyStat(dau=int(s["dau"]), date=s["date"]) for s in dau_list]

    async def create_activity(self, user_id: int, action: str, action_data: dict[str, any]):
        body = {
            "user_id": user_id,
            "action": action,
            "action_data": action_data
        }
        await self._request("POST", "stats/user-activity", data=body, expected_status=201)

_stats_api = StatsApi()

async def get_dau(from_date: datetime, to_date: datetime) -> list[DailyStat] | None:
    return await _stats_api.get_dau(from_date, to_date)

async def create_activity(user_id: int, action: str, action_data: dict[str, any]):
    await _stats_api.create_activity(user_id, action, action_data)
