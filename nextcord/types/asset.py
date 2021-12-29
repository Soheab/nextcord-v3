from __future__ import annotations
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Literal

if TYPE_CHECKING:
    from nextcord.client.state import State

    StaticFormats = Literal["webp", "jpeg", "jpg", "png"]
    AllFormats = Literal["webp", "jpeg", "jpg", "png", "gif"]
    AllSizes = Literal[2, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]

BASE_CDN: str = "https://cdn.discordapp.com"


STATIC_FORMATS = {"jpeg", "jpg", "webp", "png"}
ALL_FORMATS = STATIC_FORMATS | {"gif"}
ALL_SIZES = {2, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096}


class Asset:
    def __init__(
        self,
        state: State,
        /,
        *,
        path: str,
        hash: str,
        format: str = None,  # use MISSING ?
        size: int = None,  # use MISSING ?
        animated: bool = False,
        supported_formats: set[str] = None,  # use MISSING ?
    ):
        self._state = state

        self._path: str = path
        self._hash: str = hash
        self._format: str = format or "png" if not animated else "gif"
        self._size: int = size or 1024
        self._animated: bool = animated
        self._supported_formats: set[str] = supported_formats or ALL_FORMATS

    @classmethod
    def _from_guild(
        cls,
        type: Literal["avatar", "banner", "discovery_splash", "icon", "splash"],
        state: State,
        /,
        *,
        guild_id: int,
        hash: str,
        can_be_animated: bool = False,
        supported_formats: set[str] = None,  # use MISSING ?
        **extras: dict[str, Any],
    ) -> Asset:
        animated = False if not can_be_animated else hash.startswith("a_")
        type_to_path = {
            "avatar": f"/guilds/{guild_id}/users/{extras['member_id']}/avatars/{hash}",
            "banner": f"/banners/{guild_id}/{hash}",
            "discovery_splash": f"/discovery-splashes/{guild_id}/{hash}",
            "icon": f"/icons/{guild_id}/{hash}",
            "splash": f"/splashes/{guild_id}/{hash}",
        }
        return cls(
            state,
            path=f"{BASE_CDN}{type_to_path[type]}",
            hash=hash,
            animated=animated,
            supported_formats=supported_formats,
        )

    @classmethod
    async def _from_user(
        cls,
        type: Literal["avatar", "banner", "default_avatar", "guild_banner"],
        state: State,
        /,
        *,
        user_id: int,
        hash: str,
        can_be_animated: bool = False,
        supported_formats: set[str] = None,  # use MISSING ?
        **extras: dict[str, Any],
    ) -> Asset:
        animated = False if not can_be_animated else hash.startswith("a_")
        type_to_path = {
            "avatar": f"/avatars/{user_id}/{hash}",
            "banner": f"/banners/{user_id}/{hash}",
            "default_avatar": f"/embed/avatars/{hash}.png",
            "guild_banner": f"/guilds/{extras['guild_id']}/users/{user_id}/banners/{hash}",
        }
        return cls(
            state,
            path=f"{BASE_CDN}{type_to_path[type]}",
            hash=hash,
            animated=animated,
            supported_formats=supported_formats,
        )

    @classmethod
    def _from_icon(
        cls,
        type: Literal["app", "channel", "team"],
        state: State,
        /,
        *,
        object_id: int,
        hash: str,
    ) -> Asset:
        return cls(
            state,
            path=f"{BASE_CDN}/{type}-icons/{object_id}/{hash}.png",
            hash=hash,
            format="png",
            animated=False,
            supported_formats=STATIC_FORMATS,
        )

    @classmethod
    async def _from_app_assets(
        cls,
        state: State,
        type: Literal["cover_image", "sticker_banner"],
        /,
        *,
        hash: str,
        object_id: int = None,
    ) -> Asset:
        if object_id is None and type != "sticker_banner":
            raise ValueError("object_id can only be None for sticker_banner")

        object_id = object_id or 710982414301790216  # some special id for sticker_banner?
        return cls(
            state,
            path=f"{BASE_CDN}/app-assets/{object_id}/store/{hash}",
            hash=hash,
            format="png",
            animated=False,
            supported_formats=STATIC_FORMATS,
        )

    def __str__(self) -> str:
        return f"{BASE_CDN}{self._path}.{self._format}?size={self._size}"

    def __repr__(self):
        return f"Asset(url={self._path}, format={self._format}, animated={self.is_animated})"

    def __eq__(self, other):
        return isinstance(other, Asset) and str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

    @property
    def hash(self) -> str:
        return self._hash

    @property
    def url(self) -> str:
        return str(self)

    @property
    def format(self) -> str:
        return self._format

    @property
    def size(self) -> int:
        return self._size

    @property
    def animated(self) -> bool:
        return self._animated

    @property
    def supported_formats(self) -> set[str]:
        return self._supported_formats

    def as_format(self, format: AllFormats, /) -> Asset:
        if format not in self._supported_formats:
            raise ValueError(f"{format} is not a supported format for this asset.")

        return self.replace(format=format)

    def as_size(self, size: AllSizes, /) -> Asset:
        return self.replace(size=size)

    def as_static_format(self, static_format: StaticFormats, /) -> Asset:
        if self._animated:
            return self
        return self.replace(static_format=static_format)

    # TODO: use MISSING ?
    def replace(
        self, *, format: AllFormats = None, static_format: StaticFormats = None, size: AllSizes = None
    ) -> Asset:
        MISSING = None
        format = None
        size = None

        if format is not MISSING:
            supported_formats = STATIC_FORMATS if self._animated else ALL_FORMATS
            if format not in supported_formats:
                raise ValueError(f"format must be one of {supported_formats}")

            format = format

        if static_format is not MISSING and not self._animated:
            if static_format not in STATIC_FORMATS:
                raise ValueError(f"static_format must be one of {STATIC_FORMATS}")

            format = static_format

        if size is not MISSING:
            if size not in ALL_SIZES:
                raise ValueError("size must be a power of 2 between 16 and 4096")

            size = size

        return Asset(
            self._state,
            path=self._path,
            hash=self._hash,
            format=format,
            size=size,
            animated=self._animated,
            supported_formats=self._supported_formats,
        )
