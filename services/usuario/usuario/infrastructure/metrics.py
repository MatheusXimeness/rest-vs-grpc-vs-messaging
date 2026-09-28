import time
from typing import Callable

from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

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
