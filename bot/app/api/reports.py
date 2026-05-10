from dataclasses import asdict
from datetime import datetime

from .base import APIClient

from ..model.report import Report, ReportCreate


class ReportsApi(APIClient):
    """API для взаимодействия с жалобами."""
    
    async def create_report(self, report: ReportCreate):
        """Создаёт жалобу на объявление"""
        body = asdict(report)
        await self._request("POST", "report", data=body, expected_status=201)


# Глобальный экземпляр API
_reports_api = ReportsApi()


async def create_report(report: ReportCreate):
    """Создаёт жалобу на объявление"""
    await _reports_api.create_report(report)