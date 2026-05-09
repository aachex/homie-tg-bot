import json

from dataclasses import asdict

from .base import APIClient
from ..model.house_offer import *
from ..model.ruleset import Ruleset


class HouseOffersApi(APIClient):
    async def get_by_id(self, offer_id: int) -> HouseOffer | None:
        return await self.__get_offer(f"offer/{offer_id}")
    
    async def get_rand(self, exclude_user_id: int, city: str, ruleset: Ruleset) -> HouseOffer | None:
        if ruleset is None:
            ruleset = Ruleset(smoking=True, children=True, pets=True)
        
        url = f"offer/rand?userId={exclude_user_id}&city={city}&smoking={ruleset.smoking}&children={ruleset.children}&pets={ruleset.pets}"
        return await self.__get_offer(url)
    
    async def __get_offer(self, url: str) -> HouseOffer | None:
        offer_json = await self._request("GET", url)
        if offer_json is None:
            return None
        
        offer = HouseOffer(
            id=int(offer_json.get("id", 0)),
            owner_id=int(offer_json.get("owner_id", 0)),
            is_active=bool(offer_json.get("is_active", False)),
            title=offer_json.get("title", ""),
            description=offer_json.get("description", ""),
            city=offer_json.get("city", ""),
            district=offer_json.get("district", ""),
            price=int(offer_json.get("price", 0)),
            media_files=list(offer_json.get("media_files", [])),
            ruleset=Ruleset(
                smoking=bool(offer_json["ruleset"]["smoking"]),
                children=bool(offer_json["ruleset"]["children"]),
                pets=bool(offer_json["ruleset"]["pets"])
            )
        )
        return offer

    async def get_user_offers(self, user_id: int) -> list[HouseOfferPreview]:
        offers_json = await self._request("GET", f"user/{user_id}/offers")
        offers = list(offers_json)
        result = [
            HouseOfferPreview(
                id=int(offer["id"]),
                is_active=bool(offer["is_active"]),
                title=offer["title"],
                likes_count=int(offer["likes_count"])
            )
            for offer in offers
        ]
        return result
    
    async def create_offer(self, offer: HouseOfferCreate):
        await self._request("POST", f"offer", data=asdict(offer), expected_status=201)

    async def set_active_offer(self, offer_id: int, active: bool):
        await self._request("PATCH", f"offer/{offer_id}?active={active}")

    async def delete_offer(self, offer_id: int):
        await self._request("DELETE", f"offer/{offer_id}")
    
    async def get_likes(self, offer_id: int) -> list[HouseOfferLike]:
        likes_json = await self._request("GET", f"offer/{offer_id}/likes")
        likes = [
            HouseOfferLike(
                id=int(like.get("id", 0)),
                user_id=int(like.get("user_id", 0)),
                offer_id=int(like.get("offer_id", 0)),
            )
            for like in likes_json
        ]
        return likes
    
    async def add_like(self, offer_id: int, user_id: int):
        await self._request("POST", f"offer/{offer_id}/like?userId={user_id}", expected_status=201)

    async def delete_like(self, offer_id: int, user_id: int):
        await self._request("DELETE", f"offer/{offer_id}/like?userId={user_id}")

_offers_api = HouseOffersApi()

async def get_offer_by_id(offer_id: int) -> HouseOffer | None:
    return await _offers_api.get_by_id(offer_id)

async def get_rand_offer(exclude_user_id: int, city: str, ruleset: Ruleset | None) -> HouseOffer | None:
    return await _offers_api.get_rand(exclude_user_id, city, ruleset)

async def get_user_offers(user_id: int) -> list[HouseOfferPreview]:
    return await _offers_api.get_user_offers(user_id)

async def create_offer(offer: HouseOfferCreate):
    await _offers_api.create_offer(offer)

async def set_active_offer(offer_id: int, active: bool):
    await _offers_api.set_active_offer(offer_id, active)

async def delete_offer(offer_id: int):
    await _offers_api.delete_offer(offer_id)

async def get_offer_likes(offer_id: int) -> list[HouseOfferLike]:
    return await _offers_api.get_likes(offer_id)

async def add_like_to_offer(offer_id: int, user_id: int):
    await _offers_api.add_like(offer_id, user_id)

async def delete_like(offer_id: int, user_id: int):
    await _offers_api.delete_like(offer_id, user_id)
