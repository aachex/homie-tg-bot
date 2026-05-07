from dataclasses import dataclass, field

@dataclass
class User:
    """Данные пользователя."""
    id: int = 0
    name: str = ""
    age: int = 0
    city: str = ""
    description: str = ""
    media_files: list[str] = field(default_factory=list)

@dataclass
class UserVisibleData:
    """Видимые данные пользователя."""
    name: str | None = None
    age: int | None = None
    city: str | None = None
    description: str | None = None
    media_files: list[str] | None = None