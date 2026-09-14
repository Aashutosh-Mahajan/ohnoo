"""Interactive setup wizard for Layer 4 (hosted LLM fallback).

``ohnoo setup-ai`` (wired up in cli.py, elsewhere) calls
``run_setup_wizard()`` and echoes its returned status string. This module
does the actual prompting via click, since click is already a core
dependency of this project.
"""

from __future__ import annotations

import os

import click

from .config import clear_config, save_config
from .fallback import try_llm_fallback
from .providers import get_provider

KNOWN_PROVIDERS = ("groq", "anthropic", "openai", "ollama")


def run_setup_wizard(disable: bool = False) -> str:
    """Run the interactive Layer 4 setup wizard, or disable it.

    If ``disable`` is True, clears any existing config and returns a
    confirmation message without prompting for anything.

    Otherwise, prompts for a provider and the NAME of an env var holding the
    API key (never the raw key itself), does a best-effort dummy test call
    if that env var is currently set, saves the config, and returns a
    user-facing status string either way.
    """
    if disable:
        clear_config()
        return "Layer 4 (hosted LLM fallback) disabled. Config removed."

    provider = click.prompt(
        "Provider",
        type=click.Choice(KNOWN_PROVIDERS, case_sensitive=False),
        default="groq",
    )
    provider = provider.lower()

    if provider == "ollama":
        env_var_name = click.prompt(
            "Env var name for the Ollama base URL (leave default if unsure)",
            default="OLLAMA_BASE_URL",
        )
    else:
        default_env_var = f"{provider.upper()}_API_KEY"
        env_var_name = click.prompt(
            f"Name of the environment variable that holds your {provider} API key "
            "(we store only this name, never the key itself)",
            default=default_env_var,
        )

    save_config(provider, env_var_name)

    current_value = os.environ.get(env_var_name)
    if not current_value:
        return (
            f"Config saved (provider={provider}, key env var={env_var_name}), but "
            f"{env_var_name} isn't currently set in this shell — set it before your "
            "next ohnoo session for Layer 4 to actually activate."
        )

    if not click.confirm("Run a dummy test call now to confirm it works?", default=True):
        return f"Config saved (provider={provider}, key env var={env_var_name}). Test call skipped."

    dummy_error = "Traceback (most recent call last): NameError: name 'ohnoo' is not defined"
    try:
        result = try_llm_fallback(dummy_error)
    except Exception as exc:  # noqa: BLE001 - providers should never raise, but be safe
        return (
            f"Config saved (provider={provider}, key env var={env_var_name}), but the "
            f"test call raised an unexpected error: {exc}"
        )

    if result is None:
        return (
            f"Config saved (provider={provider}, key env var={env_var_name}), but the "
            "test call could not run (nothing resolved as active)."
        )

    if result.startswith("(hosted LLM call failed"):
        return f"Config saved (provider={provider}, key env var={env_var_name}), but the test call failed: {result}"

    return (
        f"Config saved (provider={provider}, key env var={env_var_name}). "
        f"Test call succeeded: {result}"
    )


# Re-exported so callers that only need provider validation don't have to
# reach into ohnoo.llm_fallback.providers directly.
__all__ = ["KNOWN_PROVIDERS", "get_provider", "run_setup_wizard"]
