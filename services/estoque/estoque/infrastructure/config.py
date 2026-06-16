from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://estoque:estoque@localhost:5432/estoque"
    USE_IN_MEMORY_DB: bool = False
