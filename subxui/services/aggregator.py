import logging
import random
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
from subxui.models.subscription import SubscriptionUserInfo
from subxui.services.composers import ComposerFactory
from subxui.services.converters import ConverterFactory

logger = logging.getLogger(__name__)


class Aggregator:
    def __init__(
        self,
        sources: list[SubscriptionSource],
        limit: int | None,
    ) -> None:
        self.sources = sources
        self.limit = limit or 100

    async def aggregate(
        self,
        user_id: str,
        target: Target,
    ) -> Subscription | None:
        logger.info(
            f"Aggregating subscription for user {user_id!r} (target {target.value!r})..."
        )

        subscription_user_info = SubscriptionUserInfo(
            upload=0,
            download=0,
            total=0,
            expire=0,
        )

        links = []
        for source in self.sources:
            async with AsyncClient() as client:
                try:
                    response = await client.get(
                        f"{source.base_url}/{user_id}" if user_id else source.base_url,
                        timeout=3,
                    )
                    response.raise_for_status()
                except (HTTPStatusError, RequestError) as exc:
                    logger.error(
                        f"Could not fetch subscription from {source.base_url!r}: {exc}",
                    )
                    continue

            source_user_info = None
            if header := response.headers.get("subscription-userinfo"):
                try:
                    source_user_info = SubscriptionUserInfo.from_header(
                        header=header,
                    )
                    subscription_user_info.add(source_user_info)
                except (ValidationError, ValueError) as exc:
                    logger.error(
                        f"Could not parse 'subscription-userinfo' header {header!r} from {source.base_url!r}: {exc}",
                    )

            if len(response.text) > 10 * 1024 * 1024:
                logger.error(
                    f"Subscription too large from {source.base_url!r} ({len(response.text)} bytes), skipping",
                )
                continue

            try:
                decoded_links = b64decode(response.text).decode("utf-8")
            except (BinASCIIError, UnicodeDecodeError) as exc:
                logger.warning(
                    f"Could not Base64-decode subscription {response.text[:100]!r} from {source.base_url!r}: {exc}",
                )
                decoded_links = response.text
            for line in decoded_links.splitlines():
                try:
                    link = ShareLink.from_url(line)
                except ValidationError as exc:
                    logger.error(
                        f"Could not parse link {line!r} from {source.base_url}: {exc}",
                    )
                    continue
                if source.hostname_override is not None:
                    link.netloc.hostname = source.hostname_override
                links.append(link)

        if not links:
            logger.info(
                f"No valid links found for user {user_id!r} (target {target.value!r})"
            )
            return None

        links.sort(
            key=lambda link: link.fragment,
        )

        converter = ConverterFactory.get_converter(target)
        composer = ComposerFactory.get_composer(target)

        entries = []
        for link in links:
            try:
                entry = converter.convert(link)
            except (NotImplementedError, ValidationError) as exc:
                logger.error(
                    f"Could not convert link {link!r} for target {target.value!r}: {exc}",
                )
                continue
            entries.append(entry)

        if not entries:
            logger.info(
                f"No supported links found for user {user_id!r} (target {target.value!r})"
            )
            return None

        if len(entries) > self.limit:
            entries = random.sample(
                population=entries,
                k=self.limit,
            )

        logger.info(
            f"Aggregated {len(entries)} entries for user {user_id!r} (target {target.value!r}, user info: {subscription_user_info})",
        )

        subscription = composer.compose(entries)
        subscription.user_info = subscription_user_info

        return subscription
