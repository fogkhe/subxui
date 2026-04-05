import logging
from base64 import b64decode
from binascii import Error as BinASCIIError

from httpx import AsyncClient, HTTPStatusError, RequestError
from pydantic import ValidationError

from subxui.models import (
    ShareLink,
    Subscription,
    SubscriptionSource,
    Target,
)
from subxui.services.composers import ComposerFactory
from subxui.services.converters import ConverterFactory


logger = logging.getLogger(__name__)


class Aggregator:
    def __init__(self, sources: list[SubscriptionSource]) -> None:
        self.sources = sources

    async def aggregate(
        self,
        user_id: str,
        target: Target,
    ) -> Subscription | None:
        logger.info(
            f"Aggregating subscription for user {user_id!r} (target {target!r})..."
        )

        links = []
        for source in self.sources:
            async with AsyncClient(base_url=source.base_url) as client:
                try:
                    response = await client.get(f"/{user_id}")
                    response.raise_for_status()
                except (HTTPStatusError, RequestError):
                    logger.error(
                        f"Could not fetch subscription from {source.base_url!r}",
                        exc_info=True,
                    )
                    continue
            try:
                decoded_links = b64decode(response.text).decode("utf-8")
            except (BinASCIIError, UnicodeDecodeError):
                logger.error(
                    f"Could not Base64-decode subscription {response.text!r} from {source.base_url!r}",
                    exc_info=True,
                )
                continue
            for line in decoded_links.splitlines():
                try:
                    link = ShareLink.from_url(line)
                except ValidationError:
                    logger.error(
                        f"Could not parse link {line!r} from {source.base_url}",
                        exc_info=True,
                    )
                    continue
                if source.hostname_override is not None:
                    link.netloc.hostname = source.hostname_override
                links.append(link)

        converter = ConverterFactory.get_converter(target)
        composer = ComposerFactory.get_composer(target)

        entries = []
        for link in links:
            try:
                entry = converter.convert(link)
            except (NotImplementedError, ValidationError):
                logger.error(
                    f"Could not convert link {link!r} for target {target!r}",
                    exc_info=True,
                )
                continue
            entries.append(entry)

        logger.info(
            f"Aggregated {len(entries)} entries for user {user_id!r} (target {target!r})"
        )

        return composer.compose(entries)
