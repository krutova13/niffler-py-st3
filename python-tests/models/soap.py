from dataclasses import dataclass, field
from typing import Optional

from models.enums import Direction, Currency, FriendshipStatus


@dataclass
class Sort:
    property: str
    direction: Direction


@dataclass
class PageInfo:
    page: int
    size: int
    sort: list[Sort] = field(default_factory=list)


@dataclass
class SoapUser:
    id: str
    username: str
    currency: Currency
    firstname: Optional[str] = None
    surname: Optional[str] = None
    fullname: Optional[str] = None
    photo: Optional[str] = None
    photoSmall: Optional[str] = None
    friendshipStatus: Optional[FriendshipStatus] = None
