from pydantic import BaseModel, ConfigDict, Field


class Clash(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    proxies: list[ClashAnyProxy]
    proxy_groups: list[ClashProxyGroup] = Field(
        alias="proxy-groups",
    )
    rules: list[str]


class ClashProxy(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    name: str  # link.fragment
    type: str  # link.scheme
    server: str  # link.netloc.hostname
    port: int  # link.netloc.port
    udp: bool = Field(
        default=True,
    )


class ClashTLSProxy(ClashProxy):
    tls: bool | None = Field(
        default=None,
    )  # True if link.query.security is "tls" or "reality"
    sni: str | None = Field(
        default=None,
    )  # link.query.sni if link.scheme is not "vless"
    servername: str | None = Field(
        default=None,
    )  # link.query.sni if link.scheme is "vless"
    alpn: list[str] | None = Field(
        default=None,
    )  # link.query.alpn (split by ",")
    skip_cert_verify: bool | None = Field(
        default=None,
        alias="skip-cert-verify",
    )  # link.query.allow_insecure
    client_fingerprint: str | None = Field(
        default=None,
        alias="client-fingerprint",
    )  # link.query.fp
    reality_opts: ClashRealityOpts | None = Field(
        default=None,
        alias="reality-opts",
    )  # Only if link.query.security is "reality"


class ClashRealityOpts(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    public_key: str | None = Field(
        default=None,
        alias="public-key",
    )  # link.query.pbk
    short_id: str | None = Field(
        default=None,
        alias="short-id",
    )  # link.query.sid


class ClashVLESSProxy(ClashTLSProxy):
    """Only if link.scheme is "vless"."""

    uuid: str  # link.netloc.username
    flow: str | None = Field(
        default=None,
    )  # link.query.flow
    encryption: str | None = Field(
        default=None,
    )  # link.query.encryption
    network: str | None = Field(
        default=None,
    )  # link.query.type


ClashAnyProxy = ClashVLESSProxy


class ClashProxyGroup(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    name: str
    type: str
    proxies: list[str]
