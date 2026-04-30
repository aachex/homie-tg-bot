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
    district: str = ""
    price: int = 0
    type: str = ""
    media_files: list[str] = field(default_factory=list)

@dataclass
class HouseOfferCreate:
    """Данные, необходимые для создания объявления."""
    owner_id: int = 0
    title: str = ""
    description: str = ""
    city: str = ""
    district: str = ""
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
        offer_json = await self._request("GET", f"offer/{offer_id}")
        offer = HouseOffer(
            id=offer_id,
            owner_id=int(offer_json["owner_id"]),
            is_active=offer_json["is_active"],
            title=offer_json["title"],
            description=offer_json["description"],
            city=offer_json["city"],
            district=offer_json["district"],
            price=int(offer_json["price"]),
            type=offer_json["type"],
            media_files=offer_json["media_files"],
        )
        return offer

    async def get_user_offers(self, user_id: int) -> list[HouseOfferPreview]:
        offers_json = await self._request("GET", f"user/{user_id}/offers")
        offers = list(offers_json)
        result = [
            HouseOfferPreview(
                id=int(offer["id"]),
                is_active=bool(offer["is_active"]),
                title=offer["title"]
            )
            for offer in offers
        ]
        return result
    
    async def create_offer(self, offer: HouseOfferCreate):
        await self._request("POST", f"offer", data=offer.__dict__, expected_status=201)
    
_offers_api = HouseOffersApi()

async def get_offer_by_id(offer_id: int) -> HouseOffer:
    return await _offers_api.get_by_id(offer_id)

async def get_user_offers(user_id: int) -> list[HouseOfferPreview]:
    return await _offers_api.get_user_offers(user_id)

async def create_offer(offer: HouseOfferCreate):
    r = await _offers_api.create_offer(offer)
    print(r)
