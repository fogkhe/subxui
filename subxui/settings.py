import logging

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from subxui.models import SubscriptionProfile


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    clash_proxy_group_name: str = "PROXY"
    clash_rules: list[str] = Field(
        default_factory=lambda: ["MATCH,PROXY"],
    )
    log_level: str = Field(
        default="INFO",
    )
    profiles: list[SubscriptionProfile] = Field(
        default_factory=list,
    )


settings = Settings()


logging.basicConfig(
    level=settings.log_level,
)
