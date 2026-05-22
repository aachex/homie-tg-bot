from dataclasses import dataclass, field
from .enums import *

@dataclass
class OwnerPreferences:
    """Флаги арендатора"""
    smoking: bool | None = None
    children: ChildrenEnum | None = None
    pets: PetsEnum | None = None
    occupants_count: int | None = None
    noise_lvl: NoiseLvlEnum | None = None
    works_from_home: bool | None = None
    alcohol: AlcoholEnum | None = None
    age_min: int | None = None
    age_max: int | None = None
    sex: SexEnum | None = None


@dataclass
class HouseOffer:
    """Данные объявления о сдаче/продаже жилья."""
    id: int = 0
    owner_id: int = 0
    is_active: bool = False
    title: str = ""
    description: str = ""
    city: str = ""
    district: str = ""
    price: int = 0
    media_files: list[str] = field(default_factory=list)
    flag_processing: bool = False
    preferences: OwnerPreferences = field(default_factory=OwnerPreferences)


@dataclass
class HouseOfferCreate:
    """Данные, необходимые для создания объявления."""
    owner_id: int = 0
    title: str = ""
    description: str = ""
    city: str = ""
    district: str = ""
    price: int = 0
    media_files: list[str] = field(default_factory=list)
    tenant_description: str = ""


@dataclass
class HouseOfferPreview:
    """Поверхностные данные, которые видит владелец своих объявлений."""
    id: int = 0
    is_active: bool = False
    title: str = ""
    likes_count: int = 0


@dataclass
class HouseOfferLike:
    id: int = 0
    offer_id: int = 0
    user_id: int = 0


@dataclass
class RelevantOffer:
    relevance_sum: int = 0
    relevance_percent: int = 0
    offer: HouseOffer = field(default_factory=HouseOffer)
