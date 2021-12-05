"""
The MIT License (MIT)
Copyright (c) 2021-present vcokltfre & tag-epic
Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from aiohttp.client_reqrep import ClientResponse
from . import __version__
from .protocols import http
from .exceptions import DiscordException

from typing import Any, Literal, Optional
from asyncio import Future, Lock, get_event_loop
from aiohttp import ClientSession
from collections import defaultdict
from logging import getLogger
from time import time

logger = getLogger("nextcord.http")


class Route(http.Route):
    def __init__(
        self,
        method: Literal[
            "GET",
            "HEAD",
            "POST",
            "PUT",
            "DELETE",
            "CONNECT",
            "OPTIONS",
            "TRACE",
            "PATCH",
        ],
        path: str,
        **parameters: Any,
    ):
        self.method = method
        self.path = path.format(**parameters)

        self.guild_id: Optional[int] = parameters.get("guild_id")
        self.channel_id: Optional[int] = parameters.get("channel_id")
        self.webhook_id: Optional[int] = parameters.get("webhook_id")
        self.webhook_token: Optional[str] = parameters.get("webhook_token")

    @property
    def bucket(self) -> str:
        return "{}/{};{}/{}".format(
            self.guild_id, self.channel_id, self.webhook_id, self.webhook_token
        )


class Bucket(http.Bucket):
    def __init__(self, route: Route):
        self._remaining: Optional[int] = None
        self.limit: Optional[int] = None
        self.reset_at: Optional[float] = None
        self._route: Route = route
        self._pending: list[Future] = []
        self._reserved: int = 0
        self._loop = get_event_loop()
        self._pending_reset: bool = False  # Prevents duplicate reset tasks

    @property
    def remaining(self) -> Optional[int]:
        return self._remaining

    @remaining.setter
    def remaining(self, new_value: int):
        self._remaining = new_value
        if new_value == 0 and not self._pending_reset:
            self._pending_reset = True
            sleep_time = self.reset_at - time()
            print(sleep_time)
            self._loop.call_later(sleep_time, self._reset)

    def _reset(self):
        print("Reset called")
        self.remaining = self.limit

        for future in self._pending:
            if self.remaining is not None and self.remaining <= 0:
                break
            future.set_result(None)
            self._pending.remove(future)
        self._pending_reset = False

    @property
    def _calculated_remaining(self) -> int:
        if self.remaining is None:
            return 1
        return self.remaining - self._reserved

    async def __aenter__(self) -> "Bucket":
        if self.remaining is None:
            self._reserved += 1
            return self  # We have no ratelimiting info, let's just try
        if self._calculated_remaining <= 0:
            # Ratelimit pending, let's wait
            future = Future()
            self._pending.append(future)
            logger.debug(
                f"Waiting for {str(self)} to clear up. {len(self._pending)} pending"
            )
            await future
        self._reserved += 1
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self._reserved -= 1
        if self.remaining is not None:
            self.remaining -= 1


class HTTPClient(http.HTTPClient):
    def __init__(self, token: Optional[str] = None):
        self.version = 9
        self.api_base = "https://discord.com/api/v{}".format(self.version)

        self._global_lock = Bucket(Route("POST", "/global"))
        self._webhook_global_lock = Bucket(Route("POST", "/global/webhook"))
        self._session = ClientSession()
        self._buckets: dict[str, Bucket] = {}
        self._http_errors = defaultdict((lambda: DiscordException), {})

        self._headers = {
            "User-Agent": "DiscordBot (https://github.com/nextcord/nextcord, {})".format(
                __version__
            )
        }
        if token:
            self._headers["Authorization"] = "Bot " + token

    async def request(
        self,
        route: Route,
        *,
        use_webhook_global=False,
        headers: dict[str, Any] = None,
        **kwargs,
    ) -> ClientResponse:
        global_lock = (
            self._webhook_global_lock if use_webhook_global else self._global_lock
        )

        if headers is None:
            headers = {}
        headers |= self._headers

        for _ in range(5):
            async with global_lock:
                bucket_str = route.bucket
                bucket = self._buckets.get(bucket_str)

                if bucket is None:
                    self._buckets[bucket_str] = Bucket(route)
                    bucket = self._buckets[bucket_str]  # TODO: Possibly shorten this?

                async with bucket:
                    r = await self._session.request(
                        route.method,
                        self.api_base + route.path,
                        headers=headers,
                        **kwargs,
                    )
                logger.debug(f"{route.method} {route.path}")

                try:
                    bucket.reset_at = float(r.headers["X-RateLimit-Reset"])
                    bucket.limit = int(r.headers["X-RateLimit-Limit"])
                    bucket.remaining = int(r.headers["X-RateLimit-Remaining"])
                except KeyError:
                    # Ratelimiting info is not sent on some routes and on error
                    pass

                if (status := r.status) >= 300:
                    if status == 429:
                        logger.debug("Ratelimit exceeded")
                        continue
                    raise self._http_errors[status](await r.text())

                return r

        raise DiscordException(
            "Ratelimiting failed 5 times. This should only happen if you are running multiple bots with the same IP."
        )
