from __future__ import annotations
from optparse import Option
from typing import Any, TYPE_CHECKING, Optional, Literal

from enum import IntEnum

from .asset import Asset

if TYPE_CHECKING:
    from nextcord.core.http import HTTPClient


# no idea how this works, goodluck!
# class ApplicationFlags:
# 1 << 12	GATEWAY_PRESENCE
# 1 << 13	GATEWAY_PRESENCE_LIMITED
# 1 << 14	GATEWAY_GUILD_MEMBERS
# 1 << 15	GATEWAY_GUILD_MEMBERS_LIMITED
# 1 << 16	VERIFICATION_PENDING_GUILD_LIMIT
# 1 << 17	EMBEDDED
# 1 << 18	GATEWAY_MESSAGE_CONTENT
# 1 << 19	GATEWAY_MESSAGE_CONTENT_LIMITED


class ApplicationTeamMemberState(IntEnum):
    invited = 1
    accepted = 2


class ApplicationTeamMember:
    __slots__: tuple[str, ...] = (
        "team",
        "team_id",
        "permissions",
        "id",
        "discriminator",
        "name",
        "_http",
        "_user",
    )

    def __init__(self, http: HTTPClient, /, team: ApplicationTeam, data: dict[str, Any]) -> None:
        self._http: HTTPClient = http

        self.team: ApplicationTeam = team
        self.team_id: int = int(data["team_id"])
        # self.membership_state: ApplicationTeamMemberState = ???
        self.permissions: list[str] = data["permissions"]

        self._user: dict[Literal["avatar", "discriminator", "id", "username"], str] = data["user"]
        self.id: int = int(self._user["id"])
        self.discriminator: str = self._user["discriminator"]
        self.name: str = self._user["username"]

    def __str__(self) -> str:
        return f"{self.name}#{self.discriminator}"

    @property
    def avatar(self) -> Optional[Asset]:
        avatar_hash: Optional[str] = self._user["avatar"]
        if not avatar_hash:
            return None

        return Asset._from_user("avatar", self._http, user_id=int(self._user["id"]), hash=avatar_hash)


class ApplicationTeam:
    __slots__: tuple[str, ...] = ("id", "name", "owner_id", "members", "_http", "_icon")

    def __init__(self, http: HTTPClient, /, data: dict[str, Any]) -> None:
        self._http: HTTPClient = http
        self._icon: Optional[str] = data["icon"]

        self.id: int = int(data["id"])
        self.name: str = data["name"]
        self.owner_id: int = int(data["owner_user_id"])
        self.members: list[ApplicationTeamMember] = [
            ApplicationTeamMember(self._http, team=self, data=member) for member in data["members"]
        ]

    @property
    def icon(self) -> Optional[Asset]:
        if not self._icon:
            return None

        return Asset._from_icon("team", self._http, object_id=self.id, hash=self._icon)


class Application:
    __slots__: tuple[str, ...] = (
        "id",
        "name",
        "description",
        "rpc_origins",
        "bot_public",
        "bot_require_code_grant",
        "summary",
        "team",
        "verify_key",
        "guild_id",
        "primary_sku_id",
        "slug",
        "terms_of_service_url",
        "privacy_policy_url",
        "_http",
        "_icon",
        "_cover_image",
    )

    def __init__(self, http: HTTPClient, /, data: dict[str, Any]) -> None:
        self._http: HTTPClient = http

        # always present
        self._icon: Optional[str] = data["icon"]

        self.bot_public: bool = data["bot_public"]
        self.bot_require_code_grant: bool = data["bot_require_code_grant"]
        self.description: str = data["description"]
        self.id: int = int(data["id"])
        self.name: str = data["name"]

        self.summary: str = data["summary"]  # for games?
        self.team: ApplicationTeam = ApplicationTeam(self._http, data["team"])

        self.verify_key: str = data["verify_key"]

        # optional
        self._cover_image: Optional[str] = data.get("cover_image")

        self.rpc_origins: Optional[list[str]] = data.get("rpc_origins")
        self.terms_of_service_url: Optional[str] = data.get("terms_of_service_url")
        self.privacy_policy_url: Optional[str] = data.get("privacy_policy_url")

        # self.owner: Optional[dict[str, Any]] = data.get("owner")  # user object

        self.guild_id: Optional[int] = data.get("guild_id")
        # self.guild: Guild = get from cache from id?
        self.primary_sku_id: Optional[str] = data.get("primary_sku_id")
        self.slug: Optional[str] = data.get("slug")
        # self.flags: Optional[ApplicationFlags] = ApplicationFlags(data.get("flags")) ? idk

    @property
    def icon(self) -> Optional[Asset]:
        if not self._icon:
            return None

        return Asset._from_icon("app", self._http, object_id=self.id, hash=self._icon)

    @property
    def cover_image(self) -> Optional[Asset]:
        if not self._cover_image:
            return None

        return Asset._from_app_assets("cover_image", self._http, hash=self._cover_image)
