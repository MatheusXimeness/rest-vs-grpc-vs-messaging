from decimal import Decimal
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://pagamento:pagamento@localhost:5432/pagamento"
    USE_IN_MEMORY_DB: bool = False
    MAX_PAYMENT_AMOUNT: Decimal = Decimal("10000.00")
    DECLINE_RATE: float = 0.05
    # Semente do sorteio de recusa, para reprodutibilidade dos experimentos.
    RANDOM_SEED: int | None = None

    # Estratégia de comunicação com o serviço de pedidos: rest | grpc | mensageria.
    # A API REST fica sempre ativa (health, métricas e uso manual); grpc e mensageria
    # sobem um adaptador de entrada adicional, que passa a atender o fluxo de pedido.
    COMMUNICATION_STRATEGY: Literal["rest", "grpc", "mensageria"] = "rest"
    GRPC_PORT: int = 50051
    AMQP_URL: str = "amqp://guest:guest@rabbitmq:5672/"
    # Mensagens processadas em paralelo por consumidor (não confirmadas ao mesmo tempo).
    AMQP_PREFETCH: int = 100
