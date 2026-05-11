from dataclasses import asdict
from datetime import datetime

from .base import APIClient

from ..model.report import Report, ReportCreate


class ReportsApi(APIClient):
    """API для взаимодействия с жалобами."""

    async def get_pending(self, offset: int = 0, limit: int = 10) -> list[int]:
        reports_json = await self._request("GET", f"report/pending-reports?offset={offset}&limit={limit}")
        
        if not reports_json:
            return []
        
        return [int(rep_id) for rep_id in reports_json]
    
    async def get_by_id(self, id: int) -> Report | None:
        report_json = await self._request("GET", f"report/{id}")
        
        if not report_json:
            return None
        
        def parse_date(date_str: str | None) -> datetime:
            if not date_str:
                return datetime.now()
            if date_str.endswith('Z'):
                date_str = date_str[:-1] + '+00:00'
            return datetime.fromisoformat(date_str)
        
        return Report(
            id=int(report_json["id"]),
            offer_id=int(report_json["offer_id"]),
            reporter_id=int(report_json["reporter_id"]),
            reason=report_json.get("reason", ""),
            created_at=parse_date(report_json.get("created_at")),
        )
    
    async def count(self) -> int:
        resp = await self._request("GET", "report/count")
        return resp.get("count", 0)

    async def create_report(self, report: ReportCreate):
        """Создаёт жалобу на объявление"""
        body = asdict(report)
        await self._request("POST", "report", data=body, expected_status=201)

    async def delete_report(self, id: int):
        await self._request("DELETE", f"report/{id}")


# Глобальный экземпляр API
_reports_api = ReportsApi()

async def get_pending_reports(offset: int = 0, limit: int = 10) -> list[Report]:
    return await _reports_api.get_pending(offset, limit)

async def report_by_id(id: int) -> Report | None:
    return await _reports_api.get_by_id(id)

async def reports_count() -> int:
    return await _reports_api.count()

async def create_report(report: ReportCreate):
    """Создаёт жалобу на объявление"""
    await _reports_api.create_report(report)

async def delete_report(id: int):
    await _reports_api.delete_report(id)