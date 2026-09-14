"""Common interface for Layer 4 hosted LLM providers.

Each provider module exposes a ``diagnose(error_text, api_key)`` function
(``ollama`` takes a ``base_url`` instead of an ``api_key`` since it's local
and unauthenticated — see ``ollama.py``). ``get_provider(name)`` is the
single lookup point callers use so they never need to know the per-provider
module layout.
"""

from __future__ import annotations

from . import anthropic, groq, ollama, openai

_PROVIDERS = {
    "groq": groq,
    "anthropic": anthropic,
    "openai": openai,
    "ollama": ollama,
}


def get_provider(name: str):
    """Return the provider module for ``name`` (case-insensitive).

    Raises ``ValueError`` for an unknown provider name — this is a
    programming-contract violation (a bad config/env value), not a runtime
    condition callers are expected to catch-and-degrade for.
    """
    try:
        return _PROVIDERS[name.lower()]
    except KeyError:
        known = ", ".join(sorted(_PROVIDERS))
        raise ValueError(f"Unknown LLM provider {name!r}. Known providers: {known}") from None
