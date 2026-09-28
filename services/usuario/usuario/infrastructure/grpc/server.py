"""Servidor gRPC: adaptador de entrada da estratégia gRPC (contrato em communication/grpc/proto)."""
from __future__ import annotations

import grpc

import ecommerce_pb2
import ecommerce_pb2_grpc
from usuario.application.ports.inbound import GetUserQuery
from usuario.application.use_cases.get_user import GetUserUseCase
from usuario.domain.exceptions import UserNotFoundError
from usuario.infrastructure.database.session_scope import repository_scope
from usuario.infrastructure.metrics import track


class UserServicer(ecommerce_pb2_grpc.UserServiceServicer):
    def __init__(self, state) -> None:
        self._state = state

    async def GetUser(self, request, context):
        with track("GRPC", "/ecommerce.UserService/GetUser") as obs:
            async with repository_scope(self._state) as repo:
                try:
                    user = await GetUserUseCase(repo).execute(GetUserQuery(user_id=request.user_id))
                except UserNotFoundError as exc:
                    obs.status = "404"
                    await context.abort(grpc.StatusCode.NOT_FOUND, str(exc))
            return ecommerce_pb2.User(id=user.id, name=user.name, email=user.email)


async def start_grpc_server(state, port: int) -> grpc.aio.Server:
    server = grpc.aio.server()
    ecommerce_pb2_grpc.add_UserServiceServicer_to_server(UserServicer(state), server)
    server.add_insecure_port(f"[::]:{port}")
    await server.start()
    return server
