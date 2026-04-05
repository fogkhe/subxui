from pydantic import BaseModel, Field


class Subscription(BaseModel):
    content: str
    media_type: str


class SubscriptionSource(BaseModel):
    base_url: str = Field(
        alias="baseUrl",
    )
    hostname_override: str | None = Field(
        default=None,
        alias="hostnameOverride",
    )
