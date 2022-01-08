from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional

from .enums import ChannelType

if TYPE_CHECKING:
    from nextcord.client.state import State


class GuildChannel:
    _state: State

    id: int
    name: str
    type: ChannelType

    guild: Any
    position: int
    category_id: Optional[int]
    _overwrites: list[Any]

    if TYPE_CHECKING:

        def __init__(self, state: State, guild: Any, data: dict[str, Any]):
            ...

    def __str__(self) -> str:
        return self.name

    def __int__(self) -> int:
        return self.id

    def __setattrs(self, guild: Any, data: dict[str, Any]) -> None:
        raise NotImplementedError

    @property
    def category(self) -> Any:
        ...

    @property
    def created_at(self):
        ...

    @property
    def mention(self):
        return f"<#{self.id}>"

    @property
    def overwrites(self) -> Any:
        ...

    async def _edit(self, *, name: str, reason: str = None) -> Any:
        ...

    async def delete(self, *, reason: str = None) -> Any:
        ...

    # TODO: obj = Member or Role
    async def permissions_for(self, obj: Any) -> Any:
        ...

    async def set_permissions(self) -> Any:
        ...

    # TODO: obj = Member or Role
    async def overwrites_for(self, obj: Any) -> Any:
        ...

    async def create_invite(self, *, reason: str = None) -> Any:
        ...

    async def invites(self) -> Any:
        ...

    async def _clone(self) -> Any:
        ...

    async def clone(self, *, reason: str = None) -> Any:
        raise NotImplementedError

    async def _move(self) -> Any:
        ...

    async def move(self, *, position: int, reason: str = None) -> Any:
        ...
