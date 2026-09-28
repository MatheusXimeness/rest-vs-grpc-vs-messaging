import asyncio

import aiohttp

from pedidos.application.ports.outbound import IUserServicePort, UserInfo
from pedidos.domain.exceptions import DependencyUnavailableError, UserNotFoundError


class UserHttpClient(IUserServicePort):
    def __init__(self, base_url: str, session: aiohttp.ClientSession) -> None:
        self._base_url = base_url.rstrip("/")
        self._session = session

    async def get_user(self, user_id: str) -> UserInfo:
        try:
            async with self._session.get(f"{self._base_url}/users/{user_id}") as response:
                if response.status == 404:
                    raise UserNotFoundError(f"User '{user_id}' not found")
                response.raise_for_status()
                data = await response.json()
        except (aiohttp.ClientConnectionError, asyncio.TimeoutError) as exc:
            raise DependencyUnavailableError(f"Usuario service unavailable: {exc!r}") from exc

        return UserInfo(id=data["id"], name=data["name"], email=data["email"])
