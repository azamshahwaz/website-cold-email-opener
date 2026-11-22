"""Orchestrates validate -> fetch -> extract -> generate -> validate, with caching."""
from __future__ import annotations

import socket
from dataclasses import dataclass
from typing import Callable

import requests

from config import Settings
from modules.ai_generator import GenerationResult, OpenerGenerator
from modules.errors import MissingAPIKeyError
from modules.security import Resolver, validate_url
from modules.utils import TTLCache, content_hash
from modules.website_extractor import WebsiteData, extract_website

StepCallback = Callable[[str], None]


@dataclass
class PipelineResult:
    website: WebsiteData
    opener: GenerationResult
    website_from_cache: bool = False
    opener_from_cache: bool = False


class OpenerPipeline:
    def __init__(self, settings: Settings, generator: OpenerGenerator | None = None,
                 session: requests.Session | None = None, resolver: Resolver = socket.getaddrinfo):
        self.settings = settings
        self._generator = generator
        self._session, self._resolver = session, resolver
        self._website_cache = TTLCache(settings.cache_ttl_seconds)
        self._opener_cache = TTLCache(settings.cache_ttl_seconds)

    def _get_generator(self) -> OpenerGenerator:
        if self._generator is None:
            if not self.settings.has_api_key:
                raise MissingAPIKeyError()
            self._generator = OpenerGenerator(self.settings.api_key, self.settings.model,
                                              max_retries=self.settings.max_retries)
        return self._generator

    def run(self, raw_url: str, on_step: StepCallback | None = None, force_regenerate: bool = False) -> PipelineResult:
        step = on_step or (lambda _msg: None)

        generator = self._get_generator()  # fail fast on a missing key, before any DNS/network work
        step("Validating URL")
        url = validate_url(raw_url, self._resolver)

        website = self._website_cache.get(url)
        website_from_cache = website is not None
        if website is None:
            step("Fetching website")
            website = extract_website(url, max_chars=self.settings.max_content_chars,
                                      timeout=self.settings.request_timeout, session=self._session,
                                      resolver=self._resolver)
            step("Extracting content")
            self._website_cache.set(url, website)

        key = content_hash(url, website.title, website.main_text, generator.model)
        if not force_regenerate:
            cached = self._opener_cache.get(key)
            if cached is not None:
                return PipelineResult(website, cached, website_from_cache, opener_from_cache=True)

        step("Generating opener with Gemini")
        opener = generator.generate(website)
        step("Validating output")
        self._opener_cache.set(key, opener)
        return PipelineResult(website, opener, website_from_cache, opener_from_cache=False)
