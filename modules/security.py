"""URL validation, SSRF protection and handling of untrusted website text."""
from __future__ import annotations

import ipaddress
import re
import socket
from typing import Callable
from urllib.parse import urlsplit, urlunsplit

from modules.errors import InvalidURLError, UnsafeURLError

ALLOWED_SCHEMES = {"http", "https"}
ALLOWED_PORTS = {None, 80, 443}
MAX_URL_LENGTH = 2048
BLOCKED_HOSTNAMES = {"localhost", "localhost.localdomain", "metadata.google.internal"}
BLOCKED_SUFFIXES = (".localhost", ".local", ".internal", ".lan", ".home", ".corp")

Resolver = Callable[..., list]


def normalize_url(raw_url: str) -> str:
    """Trim, add https:// when missing and return a canonical URL (no fragment)."""
    url = (raw_url or "").strip()
    if not url:
        raise InvalidURLError("Please enter a website URL.")
    if len(url) > MAX_URL_LENGTH or re.search(r"[\s\x00-\x1f]", url):
        raise InvalidURLError()
    if "://" not in url:
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", url) and not re.match(r"^[^/]*:\d+(/|$)", url):
            raise InvalidURLError("Only http:// and https:// URLs are supported.")
        url = "https://" + url.lstrip("/")
    parts = urlsplit(url)
    if parts.scheme.lower() not in ALLOWED_SCHEMES:
        raise InvalidURLError("Only http:// and https:// URLs are supported.")
    try:
        hostname, port = parts.hostname, parts.port
    except ValueError:
        raise InvalidURLError() from None
    if not hostname or "@" in parts.netloc:
        raise InvalidURLError("URLs with embedded credentials or without a host are not allowed.")
    if port not in ALLOWED_PORTS:
        raise UnsafeURLError("Only the standard web ports (80 and 443) are allowed.")
    if not _looks_like_host(hostname):
        raise InvalidURLError()
    host_part = f"[{hostname}]" if ":" in hostname else hostname  # IPv6 literals need brackets
    netloc = host_part if port is None else f"{host_part}:{port}"
    return urlunsplit((parts.scheme.lower(), netloc, parts.path or "/", parts.query, ""))


def _looks_like_host(hostname: str) -> bool:
    try:
        ipaddress.ip_address(hostname)
        return True
    except ValueError:
        pass
    if "." not in hostname or len(hostname) > 253:
        return hostname.lower() in BLOCKED_HOSTNAMES  # let the SSRF check reject it by name
    labels = hostname.rstrip(".").split(".")
    return all(re.fullmatch(r"[a-zA-Z0-9_]([a-zA-Z0-9_-]{0,61}[a-zA-Z0-9_])?", label) for label in labels)


def _is_public_ip(ip: ipaddress._BaseAddress) -> bool:
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
        ip = ip.ipv4_mapped
    return ip.is_global and not ip.is_multicast


def assert_public_url(url: str, resolver: Resolver = socket.getaddrinfo) -> str:
    """Raise UnsafeURLError unless every address the host resolves to is public."""
    hostname = (urlsplit(url).hostname or "").lower().rstrip(".")
    if not hostname:
        raise InvalidURLError()
    if hostname in BLOCKED_HOSTNAMES or hostname.endswith(BLOCKED_SUFFIXES):
        raise UnsafeURLError()
    try:
        addresses = [ipaddress.ip_address(hostname)]
    except ValueError:
        try:
            infos = resolver(hostname, None, proto=socket.IPPROTO_TCP)
        except socket.gaierror:
            raise InvalidURLError("This domain could not be resolved. Check the spelling of the URL.") from None
        addresses = []
        for info in infos:
            try:
                addresses.append(ipaddress.ip_address(info[4][0].split("%")[0]))
            except ValueError:
                continue
    if not addresses:
        raise InvalidURLError("This domain could not be resolved. Check the spelling of the URL.")
    if not all(_is_public_ip(addr) for addr in addresses):
        raise UnsafeURLError()
    return url


def validate_url(raw_url: str, resolver: Resolver = socket.getaddrinfo) -> str:
    """Normalize and verify a user-supplied URL. Returns the safe, normalized URL."""
    return assert_public_url(normalize_url(raw_url), resolver)


# --- Untrusted text handling ---------------------------------------------
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b-\x1f\x7f\u200b-\u200f\u202a-\u202e\u2060\ufeff]")
_DELIMITER_TAGS = re.compile(r"</?\s*(website_data|system|assistant|user|instructions?)\b[^>]*>", re.I)


def sanitize_untrusted_text(text: str) -> str:
    """Strip control/invisible characters and neutralize prompt-delimiter tags."""
    text = _CONTROL_CHARS.sub("", text or "")
    text = _DELIMITER_TAGS.sub("", text)
    return re.sub(r"[ \t]{2,}", " ", text).strip()


def redact_secrets(text: str, secrets: list[str]) -> str:
    """Replace any secret values in text (used before logging)."""
    for secret in secrets:
        if secret and len(secret) >= 6:
            text = text.replace(secret, "[REDACTED]")
    return text
