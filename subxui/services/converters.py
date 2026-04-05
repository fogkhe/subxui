from pydantic import BaseModel

from subxui.models import (
    ClashProxy,
    ClashRealityOpts,
    ClashVLESSProxy,
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
        if link.query.type != "tcp":
            raise NotImplementedError(f"Network {link.query.type} not supported")

        match link.scheme:
            case "vless":
                return ClashVLESSProxy(
                    name=link.fragment,
                    type=link.scheme,
                    server=link.netloc.hostname,
                    port=link.netloc.port,
                    udp=True,
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
                    network=link.query.type,
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
