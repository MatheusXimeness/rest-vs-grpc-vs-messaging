"""Cliente RPC sobre AMQP (RabbitMQ): adaptador de saída da estratégia de mensageria.

Publica a requisição na fila do serviço com reply_to apontando para uma fila de resposta
exclusiva deste processo, e aguarda a resposta com o mesmo correlation_id.
Contrato das filas: communication/messaging/rabbitmq/README.md.
"""
from __future__ import annotations

import asyncio
import json
from uuid import uuid4

import aio_pika
from aio_pika.abc import AbstractIncomingMessage, AbstractRobustConnection

from pedidos.domain.exceptions import DependencyUnavailableError


async def _connect(url: str, attempts: int = 60) -> AbstractRobustConnection:
    """Conecta ao broker, aguardando até ~60 s enquanto o RabbitMQ inicializa."""
    for attempt in range(1, attempts + 1):
        try:
            return await aio_pika.connect_robust(url)
        except (aio_pika.exceptions.AMQPConnectionError, OSError):
            if attempt == attempts:
                raise
            await asyncio.sleep(1)
    raise RuntimeError("unreachable")


class AmqpRpcClient:
    def __init__(self, timeout: float) -> None:
        self._timeout = timeout
        self._pending: dict[str, asyncio.Future] = {}

    @classmethod
    async def connect(cls, url: str, timeout: float) -> "AmqpRpcClient":
        self = cls(timeout)
        self._connection = await _connect(url)
        self._channel = await self._connection.channel()
        self._callback_queue = await self._channel.declare_queue(exclusive=True, auto_delete=True)
        await self._callback_queue.consume(self._on_response, no_ack=True)
        return self

    async def _on_response(self, message: AbstractIncomingMessage) -> None:
        future = self._pending.pop(message.correlation_id, None)
        if future is not None and not future.done():
            future.set_result(json.loads(message.body))

    async def call(self, queue: str, payload: dict) -> dict:
        """Requisição com resposta. Devolve o dict da resposta, que inclui "status"."""
        correlation_id = uuid4().hex
        future = asyncio.get_running_loop().create_future()
        self._pending[correlation_id] = future
        try:
            await self._channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(payload).encode(),
                    content_type="application/json",
                    correlation_id=correlation_id,
                    reply_to=self._callback_queue.name,
                ),
                routing_key=queue,
            )
            return await asyncio.wait_for(future, self._timeout)
        except asyncio.TimeoutError as exc:
            raise DependencyUnavailableError(f"No reply from queue '{queue}' in {self._timeout}s") from exc
        except aio_pika.exceptions.AMQPError as exc:
            raise DependencyUnavailableError(f"Broker unavailable: {exc}") from exc
        finally:
            self._pending.pop(correlation_id, None)

    async def publish(self, queue: str, payload: dict) -> None:
        """Evento sem resposta (fire-and-forget)."""
        await self._channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(payload).encode(), content_type="application/json"),
            routing_key=queue,
        )

    async def close(self) -> None:
        await self._connection.close()


def raise_for_status(reply: dict, queue: str) -> None:
    """Falha inesperada no consumidor (status 5xx), equivalente a um 500 no HTTP."""
    if reply["status"] >= 500:
        raise RuntimeError(f"Queue '{queue}' replied with status {reply['status']}")
