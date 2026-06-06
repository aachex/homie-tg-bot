import json

from dataclasses import asdict

from .base import APIClient
from ..model.house_offer import *
from ..model.user import UserFlags


class HouseOffersApi(APIClient):
    async def get_by_id(self, offer_id: int) -> HouseOffer | None:
        return await self.__get_offer(f"offer/{offer_id}")
    
    async def get_rand(self, exclude_user_id: int, city: str, user_flags: UserFlags | None) -> RelevantOffer | None:
        data = {
            "user_id": exclude_user_id,
            "min_rel": 70,
            "city": city,
            "user_flags": asdict(user_flags) if user_flags else None,
        }
        
        resp_json = await self._request("POST", "offer/relevant", data=data, expected_status=200)
        if resp_json is None:
            return None

        offer_json = resp_json.get("offer", {})

        flags_json = offer_json.get("flags", {})
        flags = OfferFlags(
            district=flags_json.get("district"),
            rooms_count=flags_json.get("rooms_count"),
            price=offer_json.get("price"),

            smoking=flags_json.get("smoking"),
            children=ChildrenEnum(flags_json["children"]) if flags_json.get("children") else None,
            pets=PetsEnum(flags_json["pets"]) if flags_json.get("pets") else None,
            occupants_count=flags_json.get("occupants_count"),
            noise_lvl=NoiseLvlEnum(flags_json["noise_lvl"]) if flags_json.get("noise_lvl") else None,
            works_from_home=flags_json.get("works_from_home"),
            alcohol=AlcoholEnum(flags_json["alcohol"]) if flags_json.get("alcohol") else None,
            age_min=flags_json.get("age_min"),
            age_max=flags_json.get("age_max"),
            sex=flags_json.get("sex")
        )

        offer = RelevantOffer(
            relevance_sum=resp_json.get("relevance_sum", 0),
            relevance_percent=resp_json.get("relevance_percent", 0),
            offer=HouseOffer(
                id=int(offer_json.get("id", 0)),
                owner_id=int(offer_json.get("owner_id", 0)),
                is_active=bool(offer_json.get("is_active", False)),
                description=offer_json.get("description", ""),
                city=offer_json.get("city", ""),
                media_files=list(offer_json.get("media_files", [])),
                flag_processing=offer_json.get("flag_processing", False),
                flags=flags,
            )
        )

        return offer
    
    async def __get_offer(self, url: str) -> HouseOffer | None:
        offer_json = await self._request("GET", url)
        if offer_json is None:
            return None
        
        flags_json = offer_json.get("flags", {})
        
        flags = OfferFlags(
            district=flags_json.get("district"),
            rooms_count=flags_json.get("rooms_count"),
            price=offer_json.get("price"),

            smoking=flags_json.get("smoking"),
            children=ChildrenEnum(flags_json["children"]) if flags_json.get("children") else None,
            pets=PetsEnum(flags_json["pets"]) if flags_json.get("pets") else None,
            occupants_count=flags_json.get("occupants_count"),
            noise_lvl=NoiseLvlEnum(flags_json["noise_lvl"]) if flags_json.get("noise_lvl") else None,
            works_from_home=flags_json.get("works_from_home"),
            alcohol=AlcoholEnum(flags_json["alcohol"]) if flags_json.get("alcohol") else None,
            age_min=flags_json.get("age_min"),
            age_max=flags_json.get("age_max"),
            sex=flags_json.get("sex")
        )
        
        return HouseOffer(
            id=int(offer_json.get("id", 0)),
            owner_id=int(offer_json.get("owner_id", 0)),
            is_active=bool(offer_json.get("is_active", False)),
            description=offer_json.get("description", ""),
            city=offer_json.get("city", ""),
            
            media_files=list(offer_json.get("media_files", [])),
            flag_processing=offer_json.get("flag_processing", False),
            flags=flags,
        )

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
                relevance=int(like.get("relevance", 0))
            )
            for like in likes_json
        ]
        return likes
    
    async def add_like(self, like: AddLikeRequest):
        data = asdict(like)
        await self._request("POST", f"offer/{like.offer_id}/like", data=data, expected_status=201)

    async def delete_like(self, offer_id: int, user_id: int):
        await self._request("DELETE", f"offer/{offer_id}/like?userId={user_id}")

_offers_api = HouseOffersApi()

async def get_offer_by_id(offer_id: int) -> HouseOffer | None:
    return await _offers_api.get_by_id(offer_id)

async def get_rand_offer(exclude_user_id: int, city: str, user: UserFlags | None) -> RelevantOffer | None:
    return await _offers_api.get_rand(exclude_user_id, city, user)

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

async def add_like_to_offer(like: AddLikeRequest):
    await _offers_api.add_like(like)

async def delete_like(offer_id: int, user_id: int):
    await _offers_api.delete_like(offer_id, user_id)
