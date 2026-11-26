from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    databaseUrl: str = "postgresql://user:pass@localhost:5432/notes"
    redisUrl: str = "redis://localhost:6379/0"
    secretKey: str = "change-me"
    algorithm: str = "HS256"
    accessTokenExpireMinutes: int = 30
    corsOrigins: str = "http://localhost:3000"


settings = Settings()