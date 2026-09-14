"""Ollama provider for Layer 4 (hosted LLM fallback).

Ollama runs locally and needs no API key, so this module's ``diagnose``
intentionally has a different signature from the other providers: a
``base_url`` instead of an ``api_key``. Callers that dispatch generically by
provider name should special-case ollama's call, or pass ``base_url`` as a
keyword when calling through ``get_provider("ollama").diagnose``.
"""

from __future__ import annotations

import httpx

DEFAULT_BASE_URL = "http://localhost:11434"
MODEL = "llama3.1"
TIMEOUT_SECONDS = 10

_PROMPT_TEMPLATE = (
    "You are a terminal error diagnosis assistant. Given the following error "
    "output, respond with a single sentence containing a diagnosis and a "
    "concrete fix suggestion. Do not add any preamble or follow-up questions.\n\n"
    "Error:\n{error_text}"
)


def diagnose(error_text: str, base_url: str = DEFAULT_BASE_URL) -> str:
    """Ask a local Ollama server for a one-sentence diagnosis + fix. Never raises."""
    try:
        response = httpx.post(
            f"{base_url.rstrip('/')}/api/generate",
            json={
                "model": MODEL,
                "prompt": _PROMPT_TEMPLATE.format(error_text=error_text),
                "stream": False,
            },
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
        return data["response"].strip()
    except httpx.HTTPStatusError as exc:
        return f"(hosted LLM call failed: ollama returned HTTP {exc.response.status_code})"
    except httpx.HTTPError as exc:
        return f"(hosted LLM call failed: {exc.__class__.__name__})"
    except (KeyError, IndexError, TypeError, ValueError):
        return "(hosted LLM call failed: unexpected response shape from ollama)"
