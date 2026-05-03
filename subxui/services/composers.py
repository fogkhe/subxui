import secrets
from base64 import b64encode

import yaml
from pydantic import BaseModel

from subxui.models import (
    Clash,
    ClashProxy,
    ClashProxyGroup,
    ShareLink,
    Subscription,
    Target,
)
from subxui.settings import settings


class BaseComposer:
    def compose(self, entries: list[BaseModel]) -> Subscription:
        raise NotImplementedError


class RawComposer(BaseComposer):
    def compose(self, entries: list[ShareLink]) -> Subscription:  # type: ignore
        content = "\n".join(str(link) for link in entries)
        return Subscription(
            content=content,
            media_type="text/plain",
        )


class Base64Composer(RawComposer):
    def compose(self, entries: list[ShareLink]) -> Subscription:
        subscription = super().compose(entries)
        subscription.content = b64encode(subscription.content.encode("utf-8")).decode(
            "utf-8"
        )
        return subscription


class ClashComposer(BaseComposer):
    def compose(self, entries: list[ClashProxy]) -> Subscription:  # type: ignore
        config = Clash(
            proxies=entries,
            proxy_groups=[  # type: ignore
                ClashProxyGroup(
                    name=settings.clash_proxy_group_name,
                    type="select",
                    proxies=[proxy.name for proxy in entries],
                )
            ],
            rules=settings.clash_rules,
            authentication=[f"user:{secrets.token_urlsafe(32)}"],
            skip_auth_prefixes=[],  # type: ignore
        )

        content = yaml.safe_dump(
            data=config.model_dump(
                by_alias=True,
                exclude_none=True,
            ),
            allow_unicode=True,
        )

        return Subscription(
            content=content,
            media_type="application/yaml",
        )


class ComposerFactory:
    @staticmethod
    def get_composer(target: Target) -> BaseComposer:
        match target:
            case Target.BASE64:
                return Base64Composer()
            case Target.CLASH:
                return ClashComposer()
            case Target.RAW:
                return RawComposer()
            case _:
                raise NotImplementedError(f"Target {target} not supported")
