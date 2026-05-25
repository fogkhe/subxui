from typing import Self

from pydantic import AliasChoices, BaseModel, Field


class Subscription(BaseModel):
    content: str
    media_type: str
    user_info: SubscriptionUserInfo | None = Field(
        default=None,
    )


class SubscriptionSource(BaseModel):
    base_url: str = Field(
        validation_alias=AliasChoices(
            "base_url",
            "base-url",
            "baseUrl",  # Deprecated.
        ),
    )
    hostname_override: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "hostname_override",
            "hostname-override",
            "hostnameOverride",  # Deprecated.
        ),
    )


class SubscriptionProfile(BaseModel):
    path: str
    sources: list[SubscriptionSource] = Field(
        default_factory=list,
    )
    per_user: bool = Field(
        default=True,
        validation_alias=AliasChoices(
            "per_user",
            "per-user",
            "perUser",  # Deprecated.
        ),
    )
    limit: int | None = Field(
        default=None,
    )


class SubscriptionUserInfo(BaseModel):
    upload: int = Field()
    download: int = Field()
    total: int = Field()
    expire: int = Field()

    @classmethod
    def from_header(cls, header: str) -> Self:
        kwargs = {}

        pairs = header.split(";")
        for pair in pairs:
            pair = pair.strip()
            if not pair or "=" not in pair:
                continue
            key, value = pair.split("=", 1)
            kwargs[key.strip()] = int(value.strip())

        return cls(**kwargs)

    def __str__(self) -> str:
        return "; ".join(
            f"{key}={value}"
            for key, value in self.model_dump(
                by_alias=True,
                exclude_none=True,
            ).items()
        )

    def add(self, other: Self) -> None:
        self.upload += other.upload
        self.download += other.download
        self.total += other.total
        self.expire = (
            min(self.expire, other.expire) if self.expire > 0 else other.expire
        )
