import logging
from pathlib import Path

import yaml
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from subxui.models import SubscriptionProfile


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    clash_proxy_group_name: str = Field(
        default="PROXY",
        validation_alias=AliasChoices(
            "clash_proxy_group_name",
            "clash-proxy-group-name",
        ),
    )
    clash_rules: list[str] = Field(
        default_factory=lambda: ["MATCH,PROXY"],
        validation_alias=AliasChoices(
            "clash_rules",
            "clash-rules",
        ),
    )
    log_level: str = Field(
        default="INFO",
        validation_alias=AliasChoices(
            "log_level",
            "log-level",
        ),
    )
    profiles: list[SubscriptionProfile] = Field(
        default_factory=list,
    )


def load_config() -> Settings:
    # config.yaml is higher priority than environment variables.

    config_path = Path(__file__).resolve().parent.parent / "config.yaml"

    try:
        with config_path.open(mode="r", encoding="utf-8") as file:
            data = yaml.safe_load(file) or {}

    except FileNotFoundError:
        logging.warning(
            "Could not find config.yaml. "
            "Using environment variables and default settings only.",
        )
        data = {}

    except OSError as exc:
        logging.error(
            f"Could not read config.yaml: {exc}",
        )
        data = {}

    except yaml.YAMLError as exc:
        logging.error(
            f"Could not parse config.yaml: {exc}",
        )
        data = {}

    if not isinstance(data, dict):
        logging.error(
            "Could not load config.yaml: expected a mapping at the root level.",
        )
        data = {}

    return Settings(**data)


settings = load_config()


logging.basicConfig(
    level=settings.log_level,
)
