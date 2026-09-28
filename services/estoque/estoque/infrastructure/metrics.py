import time
from contextlib import contextmanager
from typing import Callable, Iterator

from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# As métricas mantêm o prefixo "http_" por compatibilidade com o coletor, mas também
# registram chamadas gRPC e AMQP (label method = "GRPC" ou "AMQP"). Nessas, o label
# http_status recebe o código HTTP equivalente (200, 404, 422, 500), para que a taxa
# de erro seja calculada da mesma forma nas três estratégias.
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "http_status"],
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    # Buckets mais finos entre 1 ms e 100 ms, onde fica a latência típica do fluxo,
    # para reduzir o erro da estimativa de p95 por interpolação.
    buckets=[0.001, 0.0025, 0.005, 0.0075, 0.01, 0.0125, 0.015, 0.02, 0.025, 0.035, 0.05,
             0.075, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

_EXCLUDED_PATHS = {"/metrics", "/health"}


def _endpoint_label(request: Request) -> str:
    # Usa o template da rota (/users/{user_id}) em vez do path literal (/users/1),
    # para que cada ID não vire uma série distinta nas métricas.
    route = request.scope.get("route")
    return getattr(route, "path", None) or "<nao_mapeado>"


class Observation:
    """Status da chamada em andamento; o adaptador altera quando a resposta não é 200."""

    def __init__(self) -> None:
        self.status = "200"


@contextmanager
def track(method: str, endpoint: str) -> Iterator[Observation]:
    """Mede uma chamada recebida por gRPC ou mensageria, como o middleware faz com o HTTP."""
    obs = Observation()
    start = time.perf_counter()
    try:
        yield obs
    except BaseException:
        if obs.status.startswith("2"):
            obs.status = "500"
        raise
    finally:
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(time.perf_counter() - start)
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, http_status=obs.status).inc()


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in _EXCLUDED_PATHS:
            return await call_next(request)

        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start

        endpoint = _endpoint_label(request)
        REQUEST_DURATION.labels(
            method=request.method,
            endpoint=endpoint,
        ).observe(duration)
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=endpoint,
            http_status=str(response.status_code),
        ).inc()

        return response
