import socket

import pytest

PUBLIC_IP = "93.184.216.34"


def make_resolver(mapping: dict[str, str] | None = None, default: str = PUBLIC_IP):
    """Fake DNS resolver: no real network lookups happen in the test-suite."""
    mapping = mapping or {}

    def resolver(host, *args, **kwargs):
        ip = mapping.get(host, default)
        family = socket.AF_INET6 if ":" in ip else socket.AF_INET
        return [(family, socket.SOCK_STREAM, 6, "", (ip, 0))]

    return resolver


@pytest.fixture
def public_resolver():
    return make_resolver()


class FakeResponse:
    def __init__(self, body: str | bytes = "", status: int = 200, headers: dict | None = None, chunk: int = 16384):
        self.content = body.encode("utf-8") if isinstance(body, str) else body
        self.status_code = status
        self.headers = {"Content-Type": "text/html; charset=utf-8", **(headers or {})}
        self._chunk = chunk
        self.closed = False
        self.bytes_served = 0

    def iter_content(self, chunk_size=16384):
        for i in range(0, len(self.content), self._chunk):
            piece = self.content[i:i + self._chunk]
            self.bytes_served += len(piece)
            yield piece

    def close(self):
        self.closed = True


class FakeSession:
    """Returns queued responses (or raises queued exceptions) and records requested URLs."""

    def __init__(self, *responses):
        self.queue = list(responses)
        self.requested: list[str] = []

    def get(self, url, **kwargs):
        self.requested.append(url)
        item = self.queue.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


SAMPLE_HTML = """
<html><head>
<title>Acme Routes — Delivery routing for local bakeries</title>
<meta name="description" content="Acme Routes plans daily delivery routes for independent bakeries and cafes.">
<style>.x{color:red}</style><script>var tracking = "SECRET_JS_CONTENT";</script>
</head><body>
<nav><a href="/pricing">Pricing</a> <a href="/login">Login Portal</a></nav>
<div id="cookie-banner">We use cookies. Accept all cookies to continue browsing.</div>
<header><h1>Plan every bakery delivery in minutes</h1></header>
<main>
<p>Acme Routes builds daily delivery routes for independent bakeries and cafes that deliver fresh bread to local restaurants.</p>
<p>Drivers receive the optimised stop order on their phones, and kitchens see accurate arrival windows for each customer.</p>
<h2>Built for small bakeries</h2>
<p>Most of our customers run between two and ten delivery vans and do not have a dedicated logistics team.</p>
<p>Most of our customers run between two and ten delivery vans and do not have a dedicated logistics team.</p>
<h2>Why routing matters</h2>
<p>Fresh bread has a short shelf life, so a late delivery costs real money in returned product.</p>
</main>
<footer>Copyright 2020 Acme Routes. All rights reserved. Terms Privacy FOOTER_CLUTTER</footer>
</body></html>
"""
