from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class ClashSettings(BaseModel):
    proxy_group_name: str = Field(
        default="PROXY",
        validation_alias=AliasChoices(
            "proxy_group_name",
            "proxy-group-name",
        ),
    )
    rules: list[str] = Field(
        default_factory=lambda: ["MATCH,PROXY"],
    )
    dns: ClashDNS | None = Field(
        default=None,
    )


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
    dns: ClashDNS | None = Field(
        default=None,
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


class ClashDNS(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    enable: bool = Field(
        default=True,
    )
    cache_algorithm: str | None = Field(
        default=None,
        alias="cache-algorithm",
    )
    prefer_h3: bool | None = Field(
        default=None,
        alias="prefer-h3",
    )
    listen: str | None = Field(
        default=None,
    )
    ipv6: bool | None = Field(
        default=None,
    )
    enhanced_mode: str | None = Field(
        default=None,
        alias="enhanced-mode",
    )
    fake_ip_range: str | None = Field(
        default=None,
        alias="fake-ip-range",
    )
    fake_ip_range6: str | None = Field(
        default=None,
        alias="fake-ip-range6",
    )
    fake_ip_filter: list[str] | None = Field(
        default=None,
        alias="fake-ip-filter",
    )
    fake_ip_filter_mode: str | None = Field(
        default=None,
        alias="fake-ip-filter-mode",
    )
    fake_ip_ttl: int | None = Field(
        default=None,
        alias="fake-ip-ttl",
    )
    use_hosts: bool | None = Field(
        default=None,
        alias="use-hosts",
    )
    use_system_hosts: bool | None = Field(
        default=None,
        alias="use-system-hosts",
    )
    respect_rules: bool | None = Field(
        default=None,
        alias="respect-rules",
    )
    default_nameserver: list[str] | None = Field(
        default=None,
        alias="default-nameserver",
    )
    nameserver_policy: dict[str, str | list[str]] | None = Field(
        default=None,
        alias="nameserver-policy",
    )
    proxy_server_nameserver: list[str] | None = Field(
        default=None,
        alias="proxy-server-nameserver",
    )
    proxy_server_nameserver_policy: dict[str, str | list[str]] | None = Field(
        default=None,
        alias="proxy-server-nameserver-policy",
    )
    direct_nameserver: list[str] | None = Field(
        default=None,
        alias="direct-nameserver",
    )
    direct_nameserver_follow_policy: bool | None = Field(
        default=None,
        alias="direct-nameserver-follow-policy",
    )
    nameserver: list[str] | None = Field(
        default=None,
    )
    fallback: list[str] | None = Field(
        default=None,
    )
    fallback_filter: ClashDNSFallbackFilter | None = Field(
        default=None,
        alias="fallback-filter",
    )


class ClashDNSFallbackFilter(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    geoip: bool | None = Field(
        default=None,
    )
    geoip_code: str | None = Field(
        default=None,
        alias="geoip-code",
    )
    geosite: list[str] | None = Field(
        default=None,
    )
    ipcidr: list[str] | None = Field(
        default=None,
    )
    domain: list[str] | None = Field(
        default=None,
    )
