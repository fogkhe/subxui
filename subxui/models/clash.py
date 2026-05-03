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
    authentication: list[str] | None = Field(
        default=None,
    )
    skip_auth_prefixes: list[str] | None = Field(
        default=None,
        alias="skip-auth-prefixes",
    )


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
    network: str | None = Field(
        default=None,
    )  # link.query.type
    grpc_opts: ClashGRPCOpts | None = Field(
        default=None,
        alias="grpc-opts",
    )  # Only if link.query.type is "grpc"
    ws_opts: ClashWSOpts | None = Field(
        default=None,
        alias="ws-opts",
    )  # Only if link.query.type is "ws" or "httpupgrade"
    xhttp_opts: ClashXHTTPOpts | None = Field(
        default=None,
        alias="xhttp-opts",
    )  # Only if link.query.type is "xhttp"
    tfo: bool | None = Field(
        default=None,
    )  # Only if network is "tcp"
    smux: ClashSMUX | None = Field(
        default=None,
    )  # Only if network is "tcp"


class ClashGRPCOpts(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    grpc_service_name: str | None = Field(
        default=None,
        alias="grpc-service-name",
    )  # link.query.service_name


class ClashWSOpts(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    path: str | None = Field(
        default=None,
    )  # link.query.path
    headers: ClashWSHeaders | None = Field(
        default=None,
    )
    v2ray_http_upgrade: bool | None = Field(
        default=None,
        alias="v2ray-http-upgrade",
    )  # True if link.query.type is "httpupgrade"


class ClashWSHeaders(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    host: str | None = Field(
        default=None,
        alias="Host",
    )  # link.query.host


class ClashXHTTPOpts(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    path: str | None = Field(
        default=None,
    )  # link.query.path
    host: str | None = Field(
        default=None,
    )  # link.query.host
    mode: str | None = Field(
        default=None,
    )  # link.query.mode


class ClashSMUX(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    enabled: bool = Field()
    max_connections: int = Field(
        alias="max-connections",
    )
    padding: bool = Field()


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


ClashAnyProxy = ClashVLESSProxy


class ClashProxyGroup(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    name: str
    type: str
    proxies: list[str]
