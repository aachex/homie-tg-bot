from dataclasses import dataclass, field

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