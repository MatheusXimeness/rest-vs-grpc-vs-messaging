from pedidos.application.ports.outbound import IUserServicePort, UserInfo
from pedidos.domain.exceptions import UserNotFoundError
from pedidos.infrastructure.clients.amqp.rpc_client import AmqpRpcClient, raise_for_status

QUEUE = "usuario.get_user"


class UserAmqpClient(IUserServicePort):
    def __init__(self, rpc: AmqpRpcClient) -> None:
        self._rpc = rpc

    async def get_user(self, user_id: str) -> UserInfo:
        reply = await self._rpc.call(QUEUE, {"user_id": user_id})
        if reply["status"] == 404:
            raise UserNotFoundError(f"User '{user_id}' not found")
        raise_for_status(reply, QUEUE)
        return UserInfo(id=reply["id"], name=reply["name"], email=reply["email"])
