"""Anthropic provider for Layer 4 (hosted LLM fallback).

Uses the Messages API at api.anthropic.com.
"""

from __future__ import annotations

import httpx

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-3-5-haiku-20241022"
ANTHROPIC_VERSION = "2023-06-01"
TIMEOUT_SECONDS = 10

_PROMPT_TEMPLATE = (
    "You are a terminal error diagnosis assistant. Given the following error "
    "output, respond with a single sentence containing a diagnosis and a "
    "concrete fix suggestion. Do not add any preamble or follow-up questions.\n\n"
    "Error:\n{error_text}"
)


def diagnose(error_text: str, api_key: str | None) -> str:
    """Ask Anthropic for a one-sentence diagnosis + fix. Never raises."""
    if not api_key:
        return "(hosted LLM call failed: no API key configured for anthropic)"

    try:
        response = httpx.post(
            API_URL,
            headers={
                "x-api-key": api_key,
                "anthropic-version": ANTHROPIC_VERSION,
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL,
                "max_tokens": 200,
                "messages": [
                    {"role": "user", "content": _PROMPT_TEMPLATE.format(error_text=error_text)}
                ],
            },
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
        return data["content"][0]["text"].strip()
    except httpx.HTTPStatusError as exc:
        return f"(hosted LLM call failed: anthropic returned HTTP {exc.response.status_code})"
    except httpx.HTTPError as exc:
        return f"(hosted LLM call failed: {exc.__class__.__name__})"
    except (KeyError, IndexError, TypeError, ValueError):
        return "(hosted LLM call failed: unexpected response shape from anthropic)"
