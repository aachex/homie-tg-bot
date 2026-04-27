from dataclasses import dataclass, field
from typing import List, Optional

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
    media_files: List[str] = field(default_factory=list)

@dataclass
class HouseOfferCreate:
    """Данные, которые нужно ввести для создания объявления."""
    title: str = ""
    description: str = ""
    city: str = ""
    price: int = 0
    type: str = ""
    media_files: List[str] = field(default_factory=list)

class HouseOffersApi(APIClient):
    ...
