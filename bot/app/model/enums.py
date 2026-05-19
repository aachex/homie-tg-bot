from enum import Enum


class ChildrenEnum(str, Enum):
    """Количество детей"""
    ZERO = "zero"
    ONE = "one"
    TWO_PLUS = "two+"
    PLANNING = "planning"


class PetsEnum(str, Enum):
    """Тип животных"""
    NONE = "none"
    CATS = "cats"
    DOGS = "dogs"
    OTHER = "other"


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