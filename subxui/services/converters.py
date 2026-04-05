from pydantic import BaseModel

from subxui.models import (
    ClashGRPCOpts,
    ClashProxy,
    ClashRealityOpts,
    ClashVLESSProxy,
    ClashWSHeaders,
    ClashWSOpts,
    ShareLink,
    Target,
)


class BaseConverter:
    def convert(self, link: ShareLink) -> BaseModel:
        raise NotImplementedError


class ShareLinkConverter(BaseConverter):
    def convert(self, link: ShareLink) -> ShareLink:
        return link


class ClashConverter(BaseConverter):
    def convert(self, link: ShareLink) -> ClashProxy:
        if link.query.type not in ("tcp", "grpc", "ws", "httpupgrade"):
            raise NotImplementedError(f"Network {link.query.type} not supported")

        match link.scheme:
            case "vless":
                return ClashVLESSProxy(
                    name=link.fragment,
                    type=link.scheme,
                    server=link.netloc.hostname,
                    port=link.netloc.port,
                    udp=True,
                    network=link.query.type,
                    grpc_opts=ClashGRPCOpts(  # type: ignore
                        grpc_service_name=link.query.service_name,  # type: ignore
                    )
                    if link.query.type == "grpc"
                    else None,
                    ws_opts=ClashWSOpts(  # type: ignore
                        path=link.query.path,
                        headers=ClashWSHeaders(
                            host=link.query.host,  # type: ignore
                        )
                        if link.query.host
                        else None,
                        v2ray_http_upgrade=(link.query.type == "httpupgrade"),  # type: ignore
                    )
                    if link.query.type in ("ws", "httpupgrade")
                    else None,
                    tls=link.query.security in ("tls", "reality"),
                    sni=link.query.sni if link.scheme != "vless" else None,
                    servername=link.query.sni if link.scheme == "vless" else None,
                    alpn=link.query.alpn.split(",") if link.query.alpn else None,
                    skip_cert_verify=link.query.allow_insecure,  # type: ignore
                    client_fingerprint=link.query.fp,  # type: ignore
                    reality_opts=(  # type: ignore
                        ClashRealityOpts(
                            public_key=link.query.pbk,  # type: ignore
                            short_id=link.query.sid,  # type: ignore
                        )
                        if link.query.security == "reality"
                        else None
                    ),
                    uuid=link.netloc.username,
                    flow=link.query.flow,
                    encryption=link.query.encryption,
                )

            case _:
                raise NotImplementedError(f"Protocol {link.scheme} not supported")


class ConverterFactory:
    @staticmethod
    def get_converter(target: Target) -> BaseConverter:
        match target:
            case Target.BASE64:
                return ShareLinkConverter()
            case Target.CLASH:
                return ClashConverter()
            case Target.RAW:
                return ShareLinkConverter()
            case _:
                raise NotImplementedError(f"Target {target} not supported")
