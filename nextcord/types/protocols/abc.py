from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional

from .enums import ChannelType

if TYPE_CHECKING:
    from nextcord.client.state import State

class GuildChannel:
    _state: State

    id: int
    type: ChannelType
    name: str

    guild: Any
    position: int
    overwrites: Any

    if TYPE_CHECKING:

        def __init__(self, state: State, guild: Any, data: dict[str, Any]):
            ...

    def __str__(self) -> str:
        return self.name

    def __int__(self) -> int:
        return self.id

    def _setattrs_from_data(self, guild: Any, data: dict[str, Any]) -> None:
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

    async def edit(self, *, name: str, reason: str = None) -> Any:
        ...

    async def delete(self, *, reason: str = None) -> Any:
        ...

    async def fetch_message(self, message_id: int, /) -> Any:
        ...

    # TODO: obj = Member or Role
    async def permissions_for(self, obj: Any) -> Any:
        ...

    # TODO: obj = Member or Role
    async def overwrite_for(self, obj: Any) -> Any:
        ...

    async def create_invite(self, *, reason: str = None) -> Any:
        ...

    async def clone(self, *, reason: str = None) -> Any:
        ...
