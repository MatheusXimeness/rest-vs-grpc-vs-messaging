import grpc

import ecommerce_pb2
import ecommerce_pb2_grpc
from pedidos.application.ports.outbound import IUserServicePort, UserInfo
from pedidos.domain.exceptions import UserNotFoundError
from pedidos.infrastructure.clients.grpc.errors import raise_for_rpc_error


class UserGrpcClient(IUserServicePort):
    def __init__(self, stub: ecommerce_pb2_grpc.UserServiceStub, timeout: float) -> None:
        self._stub = stub
        self._timeout = timeout

    async def get_user(self, user_id: str) -> UserInfo:
        try:
            user = await self._stub.GetUser(
                ecommerce_pb2.GetUserRequest(user_id=user_id), timeout=self._timeout
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise UserNotFoundError(f"User '{user_id}' not found") from exc
            raise_for_rpc_error(exc, "Usuario")

        return UserInfo(id=user.id, name=user.name, email=user.email)
