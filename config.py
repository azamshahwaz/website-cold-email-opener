"""Application configuration loaded from environment variables (or Streamlit secrets)."""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "gemini-3.1-flash-lite"


def _read_secret(name: str) -> str:
    """Environment variable first, then Streamlit secrets (Community Cloud)."""
    value = os.getenv(name, "").strip()
    if value:
        return value
    try:
        import streamlit as st

        return str(st.secrets.get(name, "")).strip()
    except Exception:  # no secrets file / not running in Streamlit
        return ""


def _read_number(name: str, default: float, cast=int):
    try:
        return cast(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class Settings:
    api_key: str
    model: str
    max_content_chars: int
    request_timeout: int
    cache_ttl_seconds: int
    max_retries: int
    price_input_per_1m: float
    price_output_per_1m: float

    @property
    def has_api_key(self) -> bool:
        return bool(self.api_key) and self.api_key != "your_api_key_here"


def load_settings() -> Settings:
    return Settings(
        api_key=_read_secret("GEMINI_API_KEY"),
        model=_read_secret("GEMINI_MODEL") or DEFAULT_MODEL,
        max_content_chars=_read_number("MAX_CONTENT_CHARS", 6000),
        request_timeout=_read_number("REQUEST_TIMEOUT_SECONDS", 10),
        cache_ttl_seconds=_read_number("CACHE_TTL_SECONDS", 3600),
        max_retries=_read_number("MAX_RETRIES", 2),
        price_input_per_1m=_read_number("PRICE_INPUT_PER_1M_USD", 0.25, float),
        price_output_per_1m=_read_number("PRICE_OUTPUT_PER_1M_USD", 1.50, float),
    )
