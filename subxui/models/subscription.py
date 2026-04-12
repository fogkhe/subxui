from typing import Self

from pydantic import BaseModel, Field


class Subscription(BaseModel):
    content: str
    media_type: str
    user_info: SubscriptionUserInfo | None = Field(
        default=None,
    )


class SubscriptionSource(BaseModel):
    base_url: str = Field(
        alias="baseUrl",
    )
    hostname_override: str | None = Field(
        default=None,
        alias="hostnameOverride",
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
            key, value = pair.split("=", 1)
            kwargs[key.strip()] = value.strip()

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
        self.expire = min(self.expire, other.expire) if self.expire else other.expire
