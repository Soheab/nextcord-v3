from __future__ import annotations
from lib2to3.pgen2.token import OP
from optparse import Option
from typing import Any, TYPE_CHECKING, Optional

from .asset import AssetMixin

if TYPE_CHECKING:
    from .asset import Asset
    from nextcord.core.http import HTTPClient


class EmojiBase(AssetMixin):
    name: str
    id: Optional[int] = None
    animated: bool = False

    if TYPE_CHECKING:
        _http: Optional[HTTPClient] = None

    def __repr__(self):
        return f"<{self.__class__.__name__} animated={self.animated} name={self.name!r} id={self.id}>"

    def __str__(self) -> str:
        if not self.id:
            return self.name
        else:
            return f"<{'a' if self.animated else ''}:{self.name}:{self.id}>"

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"name": self.name}
        if self.id:
            payload["id"] = self.id
        if self.animated:
            payload["animated"] = self.animated
        return payload

    @property
    def created_at(self):
        if not self.id:
            return None

        return ...  # time from snowflake smh

    @property
    def url(self):
        raise NotImplementedError


class Emoji(EmojiBase):
    def __init__(self, http: HTTPClient, /, data: dict[str, Any]) -> None:
        self._http: HTTPClient = http

        self.id: int = int(data["id"])
        self.name: str = data["name"]
        # self.creator: User = User(..., data=data["user"])

        #           Optional[list[Role]] = [Role(..., data=role) for role in data.get("roles", [])]
        self.roles: Optional[list[str]] = data.get("roles", [])
        self.requires_colons: bool = data.get("require_colons", False)
        self.is_managed: bool = data.get("managed", False)
        self.is_animated: bool = data.get("animated", False)
        self.is_available: bool = data.get("available", False)

    @property
    def url(self) -> Optional[Asset]:
        ...


class PartialEmoji(EmojiBase):
    def __init__(self, *, name: str, animated: bool = False, id: Optional[int] = None) -> None:
        self.name: str = name
        self.id: Optional[int] = int(id) if id else None
        self.animated: bool = animated
        self.is_unicode: bool = id is not None
        self.is_custom_emoji = self.is_unicode

    @classmethod
    def from_str(cls, input: str) -> PartialEmoji:
        ...

    @property
    def url(self) -> Optional[Asset]:
        ...
