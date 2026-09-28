from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://estoque:estoque@localhost:5432/estoque"
    USE_IN_MEMORY_DB: bool = False
    # Sobrescreve a quantidade inicial de todos os produtos no seed. Usado nos testes
    # de carga para que o estoque não se esgote durante a execução.
    INITIAL_STOCK_QUANTITY: int | None = None

    # Estratégia de comunicação com o serviço de pedidos: rest | grpc | mensageria.
    # A API REST fica sempre ativa (health, métricas e uso manual); grpc e mensageria
    # sobem um adaptador de entrada adicional, que passa a atender o fluxo de pedido.
    COMMUNICATION_STRATEGY: Literal["rest", "grpc", "mensageria"] = "rest"
    GRPC_PORT: int = 50051
    AMQP_URL: str = "amqp://guest:guest@rabbitmq:5672/"
    # Mensagens processadas em paralelo por consumidor (não confirmadas ao mesmo tempo).
    AMQP_PREFETCH: int = 100
