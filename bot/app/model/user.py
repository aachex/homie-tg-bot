from dataclasses import dataclass, field
from datetime import datetime
from .enums import *


@dataclass
class UserFlags:
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
class User:
    """Данные пользователя."""
    id: int = 0
    name: str = ""
    city: str = ""
    description: str = ""
    media_files: list[str] = field(default_factory=list)
    flag_processing: bool = False
    flags: UserFlags = field(default_factory=UserFlags)


@dataclass
class UserCreate:
    """Данные для создания пользователя"""
    id: int
    name: str
    city: str
    description: str
    media_files: list[str] = field(default_factory=list)


@dataclass
class UserEdit:
    """Изменяемые данные пользователя"""
    name: str | None = None
    city: str | None = None
    description: str | None = None
    media_files: list[str] = field(default_factory=list)


@dataclass
class PremiumData:
    is_premium: bool
    until: datetime


@dataclass
class UserLimits:
    """Лимиты пользователя (обычный или премиум)"""
    premium: PremiumData
    max_offers: int
    max_likes_per_day: int


@dataclass
class TodayLikes:
    user_id: int
    likes_count: int
    max_likes: int
