from dataclasses import dataclass, field

from .base import APIClient

@dataclass
class HouseOffer:
    """Данные объявления о сдаче/продаже жилья."""
    id: int = -1
    owner_id: int = -1
    is_active: bool = False
    title: str = ""
    description: str = ""
    city: str = ""
    price: int = 0
    type: str = ""
    media_files: list[str] = field(default_factory=list)

@dataclass
class HouseOfferCreate:
    """Данные, которые нужно ввести для создания объявления."""
    title: str = ""
    description: str = ""
    city: str = ""
    price: int = 0
    type: str = ""
    media_files: list[str] = field(default_factory=list)

@dataclass
class HouseOfferPreview:
    """Поверхностные данные, которые видит владелец своих объявлений."""
    id: int
    is_active: bool
    title: str


class HouseOffersApi(APIClient):
    async def get_by_id(self, offer_id: int) -> HouseOffer:
        offer = await self._request("GET", f"offer/{offer_id}")

    async def get_user_offers(self, user_id: int) -> list[HouseOfferPreview]:
        offersJson = await self._request("GET", f"user/{user_id}/offers")
        offers = list(offersJson)
        result = [
            HouseOfferPreview(
                id=int(offer["id"]),
                is_active=bool(offer["is_active"]),
                title=offer["title"]
            )
            for offer in offers
        ]
        return result
    
_offers_api = HouseOffersApi()

async def get_user_offers(user_id: int) -> list[HouseOfferPreview]:
    return await _offers_api.get_user_offers(user_id)
