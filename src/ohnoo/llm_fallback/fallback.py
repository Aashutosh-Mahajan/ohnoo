"""Orchestration entrypoint for Layer 4 (hosted LLM fallback).

This is the only function the rest of the codebase (cli.py, wired up
separately) needs to call. It is a pure pass-through: no configuration, no
network call, ever, unless ``resolve_active_config()`` finds an active
provider.
"""

from __future__ import annotations

from .config import resolve_active_config
from .providers import get_provider


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
