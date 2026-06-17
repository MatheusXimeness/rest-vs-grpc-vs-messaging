from decimal import Decimal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://pagamento:pagamento@localhost:5432/pagamento"
    USE_IN_MEMORY_DB: bool = False
    MAX_PAYMENT_AMOUNT: Decimal = Decimal("10000.00")
    DECLINE_RATE: float = 0.05
