"""Servidor RPC sobre AMQP (RabbitMQ): adaptador de entrada da estratégia de mensageria.

Cada fila tem um handler que recebe o payload JSON e devolve um dict com "status"
(código HTTP equivalente) e os campos da resposta. Se a mensagem tem reply_to, a
resposta é publicada lá com o mesmo correlation_id; sem reply_to, é um evento sem
resposta. Contrato das filas: communication/messaging/rabbitmq/README.md.

Este arquivo é idêntico em todos os serviços que consomem filas.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Awaitable, Callable

import aio_pika
from aio_pika.abc import AbstractChannel, AbstractIncomingMessage, AbstractRobustConnection

from ..metrics import track

logger = logging.getLogger(__name__)

Handler = Callable[[dict], Awaitable[dict]]


async def connect(url: str, attempts: int = 60) -> AbstractRobustConnection:
    """Conecta ao broker, aguardando até ~60 s enquanto o RabbitMQ inicializa."""
    for attempt in range(1, attempts + 1):
        try:
            return await aio_pika.connect_robust(url)
        except (aio_pika.exceptions.AMQPConnectionError, OSError):
            if attempt == attempts:
                raise
            await asyncio.sleep(1)
    raise RuntimeError("unreachable")


async def start_rpc_server(
    url: str, handlers: dict[str, Handler], prefetch: int
) -> AbstractRobustConnection:
    connection = await connect(url)
    channel = await connection.channel()
    # Limita quantas mensagens não confirmadas o consumidor processa ao mesmo tempo.
    await channel.set_qos(prefetch_count=prefetch)
    for queue_name, handler in handlers.items():
        queue = await channel.declare_queue(queue_name, durable=False)
        await queue.consume(_consumer(channel, queue_name, handler))
    return connection


def _consumer(channel: AbstractChannel, queue_name: str, handler: Handler):
    async def on_message(message: AbstractIncomingMessage) -> None:
        # process() confirma (ack) a mensagem ao final do bloco.
        async with message.process():
            with track("AMQP", queue_name) as obs:
                try:
                    reply = await handler(json.loads(message.body))
                except Exception:
                    logger.exception("Falha ao processar mensagem da fila %s", queue_name)
                    reply = {"status": 500}
                obs.status = str(reply["status"])

            if message.reply_to:
                await channel.default_exchange.publish(
                    aio_pika.Message(
                        body=json.dumps(reply).encode(),
                        content_type="application/json",
                        correlation_id=message.correlation_id,
                    ),
                    routing_key=message.reply_to,
                )

    return on_message
