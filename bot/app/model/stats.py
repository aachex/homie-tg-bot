from datetime import datetime
from dataclasses import dataclass

@dataclass
class UserActivity:
    id: int = 0
    user_id: int = 0
    action: str = ""
    time: datetime = datetime.now()

@dataclass
class DailyStat:
    dau: int = 0
    date: datetime = datetime.now()