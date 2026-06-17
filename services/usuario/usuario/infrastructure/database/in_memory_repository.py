from usuario.application.ports.outbound import IUserRepository
from usuario.domain.user import User

_SEED: list[User] = [
    User(id="user-1", name="Alice Silva", email="alice@example.com"),
    User(id="user-2", name="Bob Souza", email="bob@example.com"),
    User(id="user-3", name="Carol Lima", email="carol@example.com"),
]


class InMemoryUserRepository(IUserRepository):
    def __init__(self) -> None:
        self._store: dict[str, User] = {u.id: u for u in _SEED}

    async def save(self, user: User) -> None:
        self._store[user.id] = user

    async def find_by_id(self, user_id: str) -> User | None:
        return self._store.get(user_id)

    async def find_all(self) -> list[User]:
        return list(self._store.values())
