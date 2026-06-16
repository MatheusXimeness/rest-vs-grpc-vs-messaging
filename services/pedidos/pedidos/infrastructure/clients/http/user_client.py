import httpx

from pedidos.application.ports.outbound import IUserServicePort, UserInfo
from pedidos.domain.exceptions import UserNotFoundError


class UserHttpClient(IUserServicePort):
    def __init__(self, base_url: str, client: httpx.AsyncClient) -> None:
        self._base_url = base_url.rstrip("/")
        self._client = client

    async def get_user(self, user_id: str) -> UserInfo:
        try:
            response = await self._client.get(f"{self._base_url}/users/{user_id}")
        except httpx.RequestError as exc:
            raise UserNotFoundError(f"Usuario service unavailable: {exc}") from exc

        if response.status_code == 404:
            raise UserNotFoundError(f"User '{user_id}' not found")

        response.raise_for_status()
        data = response.json()
        return UserInfo(id=data["id"], name=data["name"], email=data["email"])
