from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://estoque:estoque@localhost:5432/estoque"
    USE_IN_MEMORY_DB: bool = False
    # Sobrescreve a quantidade inicial de todos os produtos no seed. Usado nos testes
    # de carga para que o estoque não se esgote durante a execução.
    INITIAL_STOCK_QUANTITY: int | None = None
