"""Orchestration entrypoint for Layer 4 (hosted LLM fallback).

This is the only function the rest of the codebase (cli.py, wired up
separately) needs to call. It is a pure pass-through: no configuration, no
network call, ever, unless ``resolve_active_config()`` finds an active
provider.
"""

from __future__ import annotations

import re

from .config import resolve_active_config
from .providers import get_provider

# Best-effort redaction of common credential shapes before crash text ever
# leaves the machine via Layer 4. Not exhaustive -- Layer 4 is opt-in and
# explicitly configured, not a guarantee no secret can ever leak -- but it
# closes off the highest-confidence, most common patterns that legitimately
# show up in stderr scrollback (a printed token, a signed URL, a stray
# `echo $SECRET`).
_REDACTION_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}"), "[REDACTED_GITHUB_TOKEN]"),
    (re.compile(r"glpat-[A-Za-z0-9\-_]{20,}"), "[REDACTED_GITLAB_TOKEN]"),
    (re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"), "[REDACTED_SLACK_TOKEN]"),
    (re.compile(r"sk_live_[A-Za-z0-9]{16,}"), "[REDACTED_STRIPE_KEY]"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "[REDACTED_AWS_ACCESS_KEY]"),
    (re.compile(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"), "[REDACTED_JWT]"),
    (
        re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.DOTALL),
        "[REDACTED_PRIVATE_KEY]",
    ),
    (re.compile(r"(?i)\bBearer\s+[A-Za-z0-9\-_.~+/]+=*"), "Bearer [REDACTED]"),
    (
        re.compile(
            r"(?i)(api[_-]?key|access[_-]?key|secret[_-]?key|secret|token|password|passwd|pwd)"
            r"(\s*[:=]\s*)['\"]?([A-Za-z0-9\-_./+]{6,})['\"]?"
        ),
        r"\1\2[REDACTED]",
    ),
]


def redact_secrets(text: str) -> str:
    """Apply every pattern in _REDACTION_PATTERNS in sequence."""
    for pattern, replacement in _REDACTION_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def try_llm_fallback(error_text: str) -> str | None:
    """Run the Layer 4 hosted LLM fallback for ``error_text``, if configured.

    Returns ``None`` immediately (zero network calls) if Layer 4 isn't
    configured at all. Otherwise dispatches to the configured provider and
    returns its diagnosis string — providers already format their own
    failure messages as strings, so this never raises.
    """
    active = resolve_active_config()
    if active is None:
        return None

    error_text = redact_secrets(error_text)

    provider_name = active["provider"]
    api_key = active["api_key"]

    try:
        provider = get_provider(provider_name)
    except ValueError as exc:
        return f"(hosted LLM call failed: {exc})"

    if provider_name.lower() == "ollama":
        # Ollama is local/unauthenticated; the "api_key" slot (if any) is
        # ignored rather than treated as a base_url, to avoid silently
        # sending an unrelated secret somewhere as a URL.
        return provider.diagnose(error_text)

    return provider.diagnose(error_text, api_key)
