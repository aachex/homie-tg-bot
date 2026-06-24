from enum import Enum


class ChildrenEnum(str, Enum):
    """Количество детей"""
    NONE = "none"
    ONE = "one"
    TWO_PLUS = "two+"
    PLANNING = "planning"


class PetsEnum(str, Enum):
    """Тип животных"""
    NONE = "none"
    CATS = "cats"
    DOGS = "dogs"
    OTHER = "other"
    ANY = "any"


class NoiseLvlEnum(str, Enum):
    """Уровень шума"""
    QUIET = "quiet"
    NORMAL = "normal"
    LOUD = "loud"


class AlcoholEnum(str, Enum):
    """Отношение к алкоголю"""
    NEVER = "never"
    RARE = "rare"
    REGULAR = "regular"

class SexEnum(str, Enum):
    """Пол арендатора"""
    MALE = "male"
    FEMALE = "female"

class PremiumPeriod(str, Enum):
    WEEK = "week"
    MONTH = "month"
    THREE_MONTHS = "three_months"
