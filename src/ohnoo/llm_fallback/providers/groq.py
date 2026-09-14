"""Groq provider for Layer 4 (hosted LLM fallback).

Groq exposes an OpenAI-compatible chat completions API. This is the default
recommended provider (cheapest/fastest).
"""

from __future__ import annotations

import httpx

API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.1-8b-instant"
TIMEOUT_SECONDS = 10

_PROMPT_TEMPLATE = (
    "You are a terminal error diagnosis assistant. Given the following error "
    "output, respond with a single sentence containing a diagnosis and a "
    "concrete fix suggestion. Do not add any preamble or follow-up questions.\n\n"
    "Error:\n{error_text}"
)


def diagnose(error_text: str, api_key: str | None) -> str:
    """Ask Groq for a one-sentence diagnosis + fix. Never raises."""
    if not api_key:
        return "(hosted LLM call failed: no API key configured for groq)"

    try:
        response = httpx.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL,
                "messages": [
                    {"role": "user", "content": _PROMPT_TEMPLATE.format(error_text=error_text)}
                ],
                "max_tokens": 200,
                "temperature": 0.2,
            },
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except httpx.HTTPStatusError as exc:
        return f"(hosted LLM call failed: groq returned HTTP {exc.response.status_code})"
    except httpx.HTTPError as exc:
        return f"(hosted LLM call failed: {exc.__class__.__name__})"
    except (KeyError, IndexError, TypeError, ValueError):
        return "(hosted LLM call failed: unexpected response shape from groq)"
