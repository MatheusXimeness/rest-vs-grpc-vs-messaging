from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://pedidos:pedidos@localhost:5432/pedidos"
    USUARIO_SERVICE_URL: str = "http://usuario:8001"
    ESTOQUE_SERVICE_URL: str = "http://estoque:8003"
    PAGAMENTO_SERVICE_URL: str = "http://pagamento:8002"
    USE_STUB_SERVICES: bool = True
    USE_STUB_STOCK: bool = True
    USE_IN_MEMORY_DB: bool = False
