from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    databaseUrl: str = Field(
        default="postgresql://user:pass@localhost:5432/notes",
        validation_alias="DATABASE_URL"
    )
    redisUrl: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="REDIS_URL"
    )
    secretKey: str = Field(
        default="change-me",
        validation_alias="SECRET_KEY"
    )
    algorithm: str = Field(
        default="HS256",
        validation_alias="ALGORITHM"
    )
    accessTokenExpireMinutes: int = Field(
        default=30,
        validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    corsOrigins: str = Field(
        default="http://localhost:5173",
        validation_alias="CORS_ORIGINS"
    )


settings = Settings()