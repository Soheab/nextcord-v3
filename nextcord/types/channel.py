from __future__ import annotations
from typing import TYPE_CHECKING, Any

from .protocols.abc import GuildChannel
from .protocols.enums import ChannelType

if TYPE_CHECKING:
    from nextcord.client.state import State


class TextChannel(GuildChannel):
    def __init__(self, state: State, guild: Any, data: dict[str, Any]):
        self._state: State = state

        self.id: int = int(data["id"])
        self._type: int = int(data["type"])

        self.__setattrs(guild, data)

    def __setattrs(self, guild: Any, data: dict[str, Any]) -> None:
        self.guild = guild
        self.name: str = data["name"]
        self.topic: str = data["topic"]

    async def edit(self, *, name: str, topic: str, reason: str = None) -> Any:
        ...

    async def _clone()