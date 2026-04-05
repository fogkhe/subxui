from typing import Self
from urllib.parse import (
    SplitResult,
    parse_qs,
    quote,
    unquote,
    urlencode,
    urlsplit,
    urlunsplit,
)

from pydantic import BaseModel, ConfigDict, Field


class ShareLink(BaseModel):
    scheme: str  # Protocol
    netloc: ShareLinkNetloc
    query: ShareLinkQuery
    fragment: str  # Remark

    @classmethod
    def from_url(cls, url: str) -> Self:
        split_result = urlsplit(url)
        return cls(
            scheme=split_result.scheme,
            netloc=ShareLinkNetloc(
                username=split_result.username,  # type: ignore
                hostname=split_result.hostname,  # type: ignore
                port=split_result.port,  # type: ignore
            ),
            query=ShareLinkQuery.model_validate(
                {key: values[0] for key, values in parse_qs(split_result.query).items()}
            ),
            fragment=unquote(split_result.fragment),
        )

    def __str__(self) -> str:
        return urlunsplit(
            SplitResult(
                scheme=self.scheme,
                netloc=f"{self.netloc.username}@{self.netloc.hostname}:{self.netloc.port}",
                path="/",
                query=urlencode(
                    self.query.model_dump(
                        by_alias=True,
                        exclude_none=True,
                    )
                ),
                fragment=quote(self.fragment),
            )
        )


class ShareLinkNetloc(BaseModel):
    username: str  # User ID
    hostname: str
    port: int


class ShareLinkQuery(BaseModel):
    model_config = ConfigDict(
        extra="allow",
    )

    type: str  # Network
    security: str
    encryption: str | None = Field(
        default=None,
    )  # Only if protocol is "vless"
    host: str | None = Field(
        default=None,
    )  # Only if network is "httpupgrade", "tcp" (http header), "ws", or "xhttp"
    path: str | None = Field(
        default=None,
    )  # Only if network is "httpupgrade", "tcp" (http header), "ws", or "xhttp"
    header_type: str | None = Field(
        default=None,
        alias="headerType",
    )  # Only if network is "kcp" or "tcp" (http header)
    mode: str | None = Field(
        default=None,
    )  # Only if network is "grpc" or "xhttp"
    authority: str | None = Field(
        default=None,
    )  # Only if network is "grpc"
    service_name: str | None = Field(
        default=None,
        alias="serviceName",
    )  # Only if network is "grpc"
    seed: str | None = Field(
        default=None,
    )  # Only if network is "kcp"
    sni: str | None = Field(
        default=None,
    )  # Only if security is "tls" or "reality"
    fp: str | None = Field(
        default=None,
    )  # Only if security is "tls" or "reality"
    allow_insecure: str | None = Field(
        default=None,
        alias="allowInsecure",
    )  # Only if security is "tls"
    alpn: str | None = Field(
        default=None,
    )  # Only if security is "tls"
    pbk: str | None = Field(
        default=None,
    )  # Only if security is "reality"
    pqv: str | None = Field(
        default=None,
    )  # Only if security is "reality"
    sid: str | None = Field(
        default=None,
    )  # Only if security is "reality"
    spx: str | None = Field(
        default=None,
    )  # Only if security is "reality"
    flow: str | None = Field(
        default=None,
    )  # Only if protocol is "vless" or "trojan" and network is "tcp" and security is "tls" or "reality"
