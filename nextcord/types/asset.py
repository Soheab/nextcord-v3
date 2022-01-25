from __future__ import annotations
from typing import TYPE_CHECKING, ClassVar, Literal, Union
from io import BufferedIOBase


__all__: tuple[str, ...] = ("Asset",)

if TYPE_CHECKING:
    from nextcord.core.http import HTTPClient

    from os import PathLike

    ValidStaticFormats = Literal["webp", "jpeg", "jpg", "png"]
    ValidFormats = Literal["webp", "jpeg", "jpg", "png", "gif"]
    ValidSizes = Literal[2, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]


VALID_STATIC_FORMATS: set[str] = {"jpeg", "jpg", "webp", "png"}
VALID_FORMATS: set[str] = VALID_STATIC_FORMATS | {"gif"}
VALID_SIZES: set[int] = {2, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096}


class AssetMixin:
    _http: HTTPClient
    url: str

    async def read(self, url: str = None) -> bytes:
        return await self._http.get_cdn(url)  # type: ignore

    async def save(self, fp: Union[str, bytes, PathLike, BufferedIOBase]) -> int:
        data: bytes = await self.read()
        if isinstance(fp, BufferedIOBase):
            written = fp.write(data)
            fp.seek(0)
            return written

        with open(fp, "wb") as f:
            return f.write(data)


class Asset(AssetMixin):
    DISCORD_CDN: ClassVar[str] = "https://cdn.discordapp.com"

    __slots__: tuple[str, ...] = ("_path", "_hash", "_format", "_size", "_animated")

    def __init__(
        self,
        http: HTTPClient,
        /,
        *,
        path: str,
        hash: str,
        format: str = None,  # use MISSING ?
        size: int = None,  # use MISSING ?
        animated: bool = False,
    ) -> None:
        self._http: HTTPClient = http

        self._path: str = path
        self._hash: str = hash
        self._format: str = format or "png" if not animated else "gif"
        self._size: int = size or 1024
        self._animated: bool = animated

        self.url = f"{self.DISCORD_CDN}{self._path}.{self._format}{'?size={self._size}' if self._size else ''}"

    @classmethod
    def _from_guild(
        cls,
        type: Literal["avatar", "banner", "channel_banner", "discovery_splash", "icon", "splash"],
        http: HTTPClient,
        /,
        *,
        hash: str,
        animated: bool = False,
        guild_id: int = None,  # use MISSING ?
        member_id: int = None,  # use MISSING ?
        channel_id: int = None,  # use MISSING ?
    ) -> Asset:
        """:class:`Asset` for a guild asset.

        Parameters
        ----------
        type: str
            Type of guild asset. This must be one of ``avatar``, ``banner``, ``channel_banner``, ``discovery_splash``, ``icon``, or ``splash``.

        Returns
        -------
        :class:`Asset`
            Asset for the guild.
        """
        animated = False if not animated else hash.startswith("a_")
        type_to_path = {
            "avatar": f"/guilds/{guild_id}/users/{member_id}/avatars/{hash}",
            "banner": f"/banners/{guild_id}/{hash}",
            "channel_banner": f"/channels/{channel_id}/banners/{hash}",
            "discovery_splash": f"/discovery-splashes/{guild_id}/{hash}",
            "icon": f"/icons/{guild_id}/{hash}",
            "splash": f"/splashes/{guild_id}/{hash}",
        }
        return cls(
            http,
            path=type_to_path[type],
            hash=hash,
            animated=animated,
        )

    @classmethod
    def _from_user(
        cls,
        type: Literal["avatar", "banner", "default_avatar", "guild_banner"],
        http: HTTPClient,
        /,
        *,
        hash: str,
        animated: bool = False,
        user_id: int = None,  # use MISSING ?
        guild_id: int = None,  # use MISSING ?
    ) -> Asset:
        """:class:`Asset`

        Parameters
        ----------
        type: str
            Type of user asset. This must be one of ``avatar``, ``banner``, ``default_avatar``, or ``guild_banner``.

        Returns
        -------
        :class:`Asset`
            Asset for the user.
        """
        animated = False if not animated else hash.startswith("a_")
        type_to_path = {
            "avatar": f"/avatars/{user_id}/{hash}",
            "banner": f"/banners/{user_id}/{hash}",
            "default_avatar": f"/embed/avatars/{hash}",
            "guild_banner": f"/guilds/{guild_id}/users/{user_id}/banners/{hash}",
        }
        return cls(
            http,
            path=type_to_path[type],
            hash=hash,
            animated=animated,
        )

    @classmethod
    def _from_icon(
        cls,
        type: Literal["app", "channel", "team"],
        http: HTTPClient,
        /,
        *,
        object_id: int,
        hash: str,
    ) -> Asset:
        """:class:`Asset`

        Parameters
        ----------
        type: str
            Type of the icon. This must be one of ``app``, ``channel``, or ``team``.

        Returns
        -------
        :class:`Asset`
            Asset for the icon.
        """
        return cls(
            http,
            path=f"/{type}-icons/{object_id}/{hash}",
            hash=hash,
            format="png",
            animated=False,
        )

    @classmethod
    def _from_app_assets(
        cls,
        type: Literal["cover_image", "sticker_banner"],
        http: HTTPClient,
        /,
        *,
        hash: str,
        object_id: int = None,
    ) -> Asset:
        """:class:`Asset` Returns an asset for an app's cover image or sticker banner.

        Parameters
        ----------
        type: :class:`str`
            Type of the asset. This must be either ``cover_image`` or ``sticker_banner``.

        Raises
        ------
        ValueError
            If object_id is not provided and type is not ``sticker_banner``.

        Returns
        -------
        :class:`Asset`
            Asset for the app.
        """
        if object_id is None and type != "sticker_banner":
            raise ValueError("object_id can only be None for sticker_banner")

        object_id = object_id or 710982414301790216  # some special id for sticker_banner?
        return cls(
            http,
            path=f"/app-assets/{object_id}/store/{hash}",
            hash=hash,
            format="png",
            animated=False,
        )

    def __str__(self) -> str:
        return self.url

    def __repr__(self) -> str:
        return f"Asset(url={self._path}, format={self._format}, animated={self._animated})"

    def __eq__(self, other) -> bool:
        return isinstance(other, Asset) and str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

    @property
    def hash(self) -> str:
        """:class:`str`: The hash of the asset."""
        return self._hash

    @property
    def format(self) -> str:
        """:class:`str`: The format of the asset."""
        return self._format

    @property
    def size(self) -> int:
        """:class:`int`: The size of the asset."""
        return self._size

    @property
    def animated(self) -> bool:
        """:class:`bool`: Whether the asset is animated or not."""
        return self._animated

    def format_to(self, format: ValidFormats, /) -> Asset:
        """Returns a new asset with the format set to the given format.


        Parameters
        ----------
        format: str
            The format to set the asset to.

        Returns
        -------
        :class:`Asset`
            A new asset with the given format.

        Raises
        ------
        ValueError
            The format is not supported on this asset.
        """

        return self.replace(format=format)

    def size_to(self, size: ValidSizes, /) -> Asset:
        """:class:`Asset` Returns a new asset with the size set to the given size."""

        return self.replace(size=size)

    def static_format_to(self, static_format: ValidStaticFormats, /) -> Asset:
        """:class:`Asset` Returns a new asset with the static format set to the given format."""
        if self._animated:
            return self

        return self.replace(static_format=static_format)

    # TODO: use MISSING ?
    def replace(
        self, *, format: ValidFormats = None, static_format: ValidStaticFormats = None, size: ValidSizes = None
    ) -> Asset:
        """Returns a new asset with the given parameters replaced.

        Parameters
        ----------
        format: str
            The format to set the asset to.
        static_format: str
            The static format to set the asset to.
        size: int
            The size to set the asset to.

        Returns
        -------
        :class:`Asset`
            A new asset with the given parameters replaced.
        """
        MISSING = None

        if format is not MISSING:
            supported_formats = VALID_STATIC_FORMATS if self._animated else VALID_FORMATS
            if format not in supported_formats:
                raise ValueError(f"format must be one of {supported_formats}")

            format = format

        if static_format is not MISSING and not self._animated:
            if static_format not in VALID_STATIC_FORMATS:
                raise ValueError(f"static_format must be one of {VALID_STATIC_FORMATS}")

            format = static_format

        if size is not MISSING:
            if size not in VALID_SIZES:
                raise ValueError(f"size must be one of {VALID_SIZES}")

            size = size

        return Asset(
            self._http,
            path=self._path,
            hash=self._hash,
            format=format,
            size=size,
            animated=self._animated,
        )
