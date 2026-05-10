from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class Report:
    """Модель жалобы на объявление"""
    id: int
    offer_id: int
    reporter_id: int
    reason: str
    status: str
    created_at: datetime
    admin_comment: str | None = None


@dataclass
class ReportCreate:
    """Данные для создания жалобы"""
    offer_id: int
    reporter_id: int
    reason: str
