from dataclasses import dataclass

import grpc

import ecommerce_pb2_grpc


@dataclass
class GrpcStubs:
    """Um canal HTTP/2 por serviço, aberto no startup e reutilizado por todas as chamadas."""

    user: ecommerce_pb2_grpc.UserServiceStub
    stock: ecommerce_pb2_grpc.StockServiceStub
    payment: ecommerce_pb2_grpc.PaymentServiceStub
    channels: list[grpc.aio.Channel]

    @classmethod
    def open(cls, user_target: str, stock_target: str, payment_target: str) -> "GrpcStubs":
        user_ch = grpc.aio.insecure_channel(user_target)
        stock_ch = grpc.aio.insecure_channel(stock_target)
        payment_ch = grpc.aio.insecure_channel(payment_target)
        return cls(
            user=ecommerce_pb2_grpc.UserServiceStub(user_ch),
            stock=ecommerce_pb2_grpc.StockServiceStub(stock_ch),
            payment=ecommerce_pb2_grpc.PaymentServiceStub(payment_ch),
            channels=[user_ch, stock_ch, payment_ch],
        )

    async def close(self) -> None:
        for channel in self.channels:
            await channel.close()
