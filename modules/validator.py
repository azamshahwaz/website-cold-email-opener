"""Cleaning and validation of the model's three-line opener."""
from __future__ import annotations

import re

from modules.errors import InvalidOutputError

REQUIRED_LINES = 3
MIN_LINE_CHARS = 20
MAX_LINE_CHARS = 280
MAX_TOTAL_CHARS = 650

_BANNED_PHRASES = (
    "i was impressed by your company",
    "your innovative solution is amazing",
    "i came across your website",
    "i hope this email finds you well",
    "i hope this finds you well",
)
_GREETING = re.compile(r"^(?:(?:hi|hello|hey|dear|best regards|regards|sincerely|thanks)\b|subject\s*:)", re.I)
_LINE_LABEL = re.compile(r"^\s*(?:line\s*[1-3]|opener)\s*[:.\-)]\s*", re.I)
_LIST_MARKER = re.compile(r"^\s*(?:\d+\s*[.)]|[-*•>]+)\s+")


def clean_opener_text(raw: str) -> list[str]:
    """Strip markdown/numbering/labels and return the non-empty lines."""
    text = re.sub(r"```[a-zA-Z]*", "", raw or "").replace("```", "")
    lines: list[str] = []
    for line in text.splitlines():
        line = _LIST_MARKER.sub("", line)
        line = _LINE_LABEL.sub("", line)
        line = re.sub(r"^#{1,6}\s*", "", line)
        line = re.sub(r"(\*\*|__)(.+?)\1", r"\2", line)
        line = re.sub(r"(?<![\w*])[*_]([^*_\n]+)[*_](?![\w*])", r"\1", line)
        line = line.replace("`", "").strip().strip('"“”').strip()
        if line:
            lines.append(line)
    return lines


def validate_opener(raw: str) -> list[str]:
    """Return exactly three clean lines or raise InvalidOutputError."""
    lines = clean_opener_text(raw)
    if len(lines) != REQUIRED_LINES:
        raise InvalidOutputError(f"Expected exactly {REQUIRED_LINES} lines but got {len(lines)}.")
    for line in lines:
        if len(line) < MIN_LINE_CHARS:
            raise InvalidOutputError("A line was too short to be meaningful.")
        if len(line) > MAX_LINE_CHARS:
            raise InvalidOutputError("A line was too long.")
        if _GREETING.match(line):
            raise InvalidOutputError("Output contained a greeting, subject or signature.")
        if any(phrase in line.lower() for phrase in _BANNED_PHRASES):
            raise InvalidOutputError("Output contained a generic cliché.")
    if sum(len(line) for line in lines) > MAX_TOTAL_CHARS:
        raise InvalidOutputError("Output was too long.")
    return lines
