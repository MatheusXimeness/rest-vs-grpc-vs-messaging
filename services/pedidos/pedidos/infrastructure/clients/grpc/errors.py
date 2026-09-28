import grpc

from pedidos.domain.exceptions import DependencyUnavailableError

_UNAVAILABLE = {grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.DEADLINE_EXCEEDED}


def raise_for_rpc_error(exc: grpc.aio.AioRpcError, service: str) -> None:
    """Traduz falhas de transporte para DependencyUnavailableError, como no cliente HTTP."""
    if exc.code() in _UNAVAILABLE:
        raise DependencyUnavailableError(f"{service} service unavailable: {exc.details()}") from exc
    raise exc
