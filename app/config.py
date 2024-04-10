from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    api_key: SecretStr
    database_hostname: str
    database_port: str = "5432"
    database_name: str
    database_username: str
    database_password: SecretStr
    secret_key: SecretStr
    algorithm: str
    access_token_expire_minutes: int


settings = Settings()  # type: ignore
