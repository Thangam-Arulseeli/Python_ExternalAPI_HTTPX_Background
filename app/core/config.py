#### app/core/config.py

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "External API Training Application"

    external_api_base_url: str = (
        "https://jsonplaceholder.typicode.com"
    )

    external_api_key: str | None = None

    external_api_timeout: float = 5.0
    external_api_max_retries: int = 2

    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


'''
Explanation
===================

BaseSettings    --> Reads configuration from environment variables and the configured .env file.

SettingsConfigDict  --> Defines how configuration is loaded.

@lru_cache  --> Caches the settings object so repeated calls to get_settings() return the same instance.

external_api_key    --> Stores the API key if the external service requires one.


NOTE: 
Never commit a real .env file containing credentials to source control.

Also note that environment variables are configuration, not a complete secrets-management solution. Production deployments may use a dedicated secrets manager.

'''


