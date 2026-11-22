"""Safe website fetching and meaningful-content extraction."""
from __future__ import annotations

import re
import socket
from contextlib import closing
from dataclasses import dataclass, field
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from modules.errors import (
    EmptyContentError,
    JavaScriptRenderedError,
    WebsiteBlockedError,
    WebsiteFetchError,
    WebsiteSSLError,
    WebsiteTimeoutError,
    WebsiteUnavailableError,
)
from modules.security import Resolver, assert_public_url, normalize_url, sanitize_untrusted_text

USER_AGENT = "Mozilla/5.0 (compatible; WebsiteOpenerBot/1.0; educational project)"
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
MAX_REDIRECTS = 5
MIN_CONTENT_CHARS = 200
CONNECT_TIMEOUT = 5
REDIRECT_CODES = {301, 302, 303, 307, 308}

_NOISE_TAGS = ["script", "style", "noscript", "template", "svg", "iframe", "canvas", "form",
               "nav", "footer", "aside", "button", "select", "dialog"]
_NOISE_ATTR = re.compile(r"cookie|consent|gdpr|onetrust|cmp-|popup|modal|newsletter|subscribe|breadcrumb", re.I)
_BLOCK_TITLES = ("just a moment", "attention required", "access denied", "are you a human",
                 "verify you are human", "security check")
_JS_MARKERS = ('id="root"', "id='root'", 'id="__next"', 'id="app"', "__NUXT__", "ng-version",
               "enable javascript", "you need to enable javascript")


@dataclass
class WebsiteData:
    url: str
    final_url: str
    title: str = ""
    meta_description: str = ""
    headings: list[str] = field(default_factory=list)
    main_text: str = ""

    @property
    def description(self) -> str:
        if self.meta_description:
            return self.meta_description
        return (self.main_text[:300].rsplit(" ", 1)[0] + "…") if len(self.main_text) > 300 else self.main_text

    @property
    def total_chars(self) -> int:
        return len(self.meta_description) + len(self.main_text) + sum(len(h) for h in self.headings)


# --------------------------------------------------------------------------
# Fetching
# --------------------------------------------------------------------------
def _decode(body: bytes, content_type: str) -> str:
    match = re.search(r"charset=([\w-]+)", content_type or "", re.I)
    for encoding in ([match.group(1)] if match else []) + ["utf-8"]:
        try:
            return body.decode(encoding)
        except (LookupError, UnicodeDecodeError):
            continue
    return body.decode("utf-8", errors="replace")


def fetch_html(url: str, timeout: int = 10, session: requests.Session | None = None,
               resolver: Resolver = socket.getaddrinfo) -> tuple[str, str]:
    """Fetch a page safely. Returns (html, final_url). Every redirect hop is re-validated."""
    session = session or requests.Session()
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.5",
               "Accept-Language": "en-US,en;q=0.8"}
    current = url
    for _ in range(MAX_REDIRECTS + 1):
        assert_public_url(current, resolver)
        try:
            response = session.get(current, headers=headers, timeout=(CONNECT_TIMEOUT, timeout),
                                   allow_redirects=False, stream=True)
        except requests.exceptions.SSLError:
            raise WebsiteSSLError() from None
        except requests.exceptions.Timeout:
            raise WebsiteTimeoutError() from None
        except requests.exceptions.ConnectionError:
            raise WebsiteUnavailableError("The website could not be reached. Check the URL and try again.") from None
        except requests.exceptions.RequestException:
            raise WebsiteFetchError() from None

        with closing(response):
            location = response.headers.get("Location")
            if response.status_code in REDIRECT_CODES and location:
                current = normalize_url(urljoin(current, location))
                continue
            if response.status_code in (401, 403, 429):
                raise WebsiteBlockedError()
            if response.status_code in (404, 410):
                raise WebsiteUnavailableError("The page was not found (HTTP %d)." % response.status_code)
            if response.status_code >= 400:
                raise WebsiteUnavailableError(f"The website returned an error (HTTP {response.status_code}).")
            content_type = response.headers.get("Content-Type", "")
            if content_type and not re.search(r"html|xml|text/plain", content_type, re.I):
                raise WebsiteFetchError("The URL does not point to an HTML page.")
            body = bytearray()
            for chunk in response.iter_content(chunk_size=16384):
                body.extend(chunk)
                if len(body) > MAX_RESPONSE_BYTES:
                    del body[MAX_RESPONSE_BYTES:]
                    break
            return _decode(bytes(body), content_type), current
    raise WebsiteFetchError("The website redirected too many times.")


# --------------------------------------------------------------------------
# Extraction
# --------------------------------------------------------------------------
def _clean_line(text: str) -> str:
    return re.sub(r"\s+", " ", sanitize_untrusted_text(text)).strip()


def _meta(soup: BeautifulSoup, *names: str) -> str:
    for name in names:
        tag = soup.find("meta", attrs={"name": name}) or soup.find("meta", attrs={"property": name})
        if tag and tag.get("content"):
            return _clean_line(tag["content"])
    return ""


def _strip_noise(soup: BeautifulSoup) -> None:
    for tag in soup.find_all(_NOISE_TAGS):
        tag.decompose()
    for header in soup.find_all("header"):
        if not header.find("h1"):
            header.decompose()
    candidates = [t for t in soup.find_all(True) if not t.decomposed]
    for tag in candidates:
        if tag.decomposed or tag.attrs is None:
            continue
        marker = " ".join([tag.get("id") or "", " ".join(tag.get("class") or [])])
        if _NOISE_ATTR.search(marker) or tag.get("role") in {"navigation", "dialog", "alertdialog"} \
                or tag.get("aria-modal") == "true":
            tag.decompose()


def _dedupe(lines: list[str]) -> list[str]:
    seen, result = set(), []
    for line in lines:
        key = re.sub(r"\W+", " ", line.lower()).strip()
        if key and key not in seen:
            seen.add(key)
            result.append(line)
    return result


def truncate_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    cut = text[:max_chars]
    return (cut.rsplit("\n", 1)[0] if "\n" in cut[max_chars // 2:] else cut.rsplit(" ", 1)[0]).strip()


def _trafilatura_text(html: str, url: str) -> str:
    try:
        import trafilatura

        return trafilatura.extract(html, url=url, include_comments=False, include_tables=False,
                                   favor_recall=True) or ""
    except Exception:  # extraction is best-effort; BeautifulSoup fallback follows
        return ""


def _looks_js_rendered(html: str) -> bool:
    lowered = html.lower()
    return any(marker.lower() in lowered for marker in _JS_MARKERS) or lowered.count("<script") >= 3


def extract_content(html: str, url: str, final_url: str | None = None, max_chars: int = 6000) -> WebsiteData:
    """Turn raw HTML into compact, de-duplicated website data."""
    soup = BeautifulSoup(html or "", "html.parser")
    title = _clean_line(soup.title.get_text()) if soup.title else ""
    title = title or _meta(soup, "og:title")
    if any(block in title.lower() for block in _BLOCK_TITLES):
        raise WebsiteBlockedError()
    meta_description = _meta(soup, "description", "og:description", "twitter:description")

    _strip_noise(soup)
    headings = _dedupe([h for h in (_clean_line(t.get_text()) for t in soup.find_all(["h1", "h2", "h3"]))
                        if 3 <= len(h) <= 160])[:15]

    text = _clean_line_block(_trafilatura_text(html, final_url or url))
    if len(text) < 200:  # trafilatura found little; fall back to paragraph/list text
        parts = [_clean_line(t.get_text(" ")) for t in soup.find_all(["p", "li", "blockquote", "h4"])]
        text = "\n".join(_dedupe([p for p in parts if len(p) >= 25]))
    text = truncate_text(text, max_chars)

    data = WebsiteData(url=url, final_url=final_url or url, title=title, meta_description=meta_description,
                       headings=headings, main_text=text)
    if data.total_chars < MIN_CONTENT_CHARS:
        raise (JavaScriptRenderedError() if _looks_js_rendered(html) else EmptyContentError())
    return data


def _clean_line_block(text: str) -> str:
    return "\n".join(_dedupe([line for line in (_clean_line(l) for l in text.splitlines()) if line]))


def extract_website(url: str, max_chars: int = 6000, timeout: int = 10,
                    session: requests.Session | None = None, resolver: Resolver = socket.getaddrinfo) -> WebsiteData:
    """Fetch and extract a (already validated) URL."""
    html, final_url = fetch_html(url, timeout=timeout, session=session, resolver=resolver)
    return extract_content(html, url, final_url=final_url, max_chars=max_chars)
