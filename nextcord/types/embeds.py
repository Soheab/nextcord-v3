from __future__ import annotations
from typing import Any, Optional, Union, TypeVar

from dataclasses import dataclass, field, is_dataclass


@dataclass(frozen=True)
class EmbedImage:
    url: Optional[str] = None
    proxy_url: Optional[str] = field(init=False)
    height: Optional[int] = field(init=False)
    width: Optional[int] = field(init=False)


@dataclass(frozen=True)
class EmbedProvider:
    name: Optional[str] = None
    url: Optional[str] = None


@dataclass(frozen=True)
class EmbedFooter:
    text: str
    icon_url: Optional[str] = None
    proxy_icon_url: Optional[str] = field(default=None, repr=False, init=False)

    @property
    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass(frozen=True)
class EmbedAuthor:
    name: Optional[str] = None
    url: Optional[str] = None
    icon_url: Optional[str] = None
    proxy_icon_url: Optional[str] = field(default=None, repr=False, init=False)

    @property
    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}


EMF = TypeVar("EMF", bound="EmbedField")


@dataclass
class EmbedField:
    name: str
    value: str
    inline: bool = False
    position: Optional[int] = field(default=None, repr=False, init=False)

    @property
    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}

    def edit(self: EMF, name: str = None, value: str = None, inline: bool = False) -> EMF:
        if name:
            self.name = name
        if value:
            self.value = value
        if inline:
            self.inline = inline

        return self


EM = TypeVar("EM", bound="Embed")


@dataclass
class Embed:
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    timestamp: Optional[str] = None
    colour: Optional[int] = None
    color: Optional[int] = None
    author: Optional[EmbedAuthor] = None
    footer: Optional[EmbedFooter] = None
    fields: list[EmbedField] = []

    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

    _image: Optional[EmbedImage] = field(init=False)
    _thumbnail: Optional[EmbedImage] = field(init=False)
    _video: Optional[EmbedImage] = field(default=None, repr=False, init=False)
    _provider: Optional[EmbedProvider] = field(default=None, repr=False, init=False)

    def __post_init__(self):
        if self.colour is not None:
            self.color = self.colour

        if self.image_url is not None:
            self._image = EmbedImage(url=self.image_url)
        if self.thumbnail_url:
            self._thumbnail = EmbedImage(url=self.thumbnail_url)

    @property
    def video(self) -> Optional[EmbedImage]:
        return self._video

    @property
    def provider(self) -> Optional[EmbedProvider]:
        return self._provider

    def append_field(self: EM, field: EmbedField, *, position: Optional[int] = None) -> EM:
        if position is None:
            self.fields.append(field)
        else:
            self.fields.insert(position, field)

        field.position = self.fields.index(field)
        return self

    def add_field(self: EM, name: str, value: str, inline: bool = False, *, position: int = None) -> EM:
        new_field: EmbedField = EmbedField(name=name, value=value, inline=inline)
        if position is None:
            self.fields.append(new_field)
        else:
            self.fields.insert(position, new_field)

        new_field.position = self.fields.index(new_field)
        return self

    def edit_field(
        self: EM, index: int, name: str = None, value: str = None, inline: bool = False, *, position: int = None
    ) -> EM:
        new_field: EmbedField = self.fields[index].edit(name, value, inline)
        if position is not None:
            self.fields.pop(index)
            self.fields.insert(position, new_field)

        new_field.position = self.fields.index(new_field)
        return self

    def remove_field(self, index: int) -> Optional[EmbedField]:
        try:
            return self.fields.pop(index)
        except IndexError:
            return None

    @classmethod
    def from_dict(cls, data: dict):
        embed = cls()
        for key, value in data.items():
            if key in ("title", "description", "url", "timestamp", "color"):
                setattr(embed, key, value)

            if key in ("image", "thumbnail"):
                setattr(embed, f"{key}_url", value.get("url"))
                setattr(embed, f"_{key}", EmbedImage(**value))

            if key == "fields":
                embed.fields = [EmbedField(**field) for field in data["fields"]]

            if key == "author":
                embed.author = EmbedAuthor(**data["author"])

            if key == "footer":
                embed.footer = EmbedFooter(**data["footer"])

            if key == "provider":
                embed._provider = EmbedProvider(**data["provider"])

            if key == "video":
                embed._video = EmbedImage(**data["video"])

        return embed

    def to_dict(self) -> dict:
        data: dict[str, Union[str, dict[str, str], list[Any]]] = {"type": "rich"}
        for key in self.__slots__:
            value = getattr(self, key)

            if value:
                if is_dataclass(value):
                    if key == "fields":
                        data["fields"] = [field.to_dict for field in value]
                        continue

                    value = value.to_dict

                if key == "image_url":
                    data["image"] = {"url": value}
                elif key == "thumbnail_url":
                    data["thumbnail"] = {"url": value}

                data[key] = value

        return data
