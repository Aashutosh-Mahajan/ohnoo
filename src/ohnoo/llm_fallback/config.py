"""Config read/write and resolution logic for Layer 4 (hosted LLM fallback).

The production config lives at ``~/.config/ohnoo/config.toml``. It NEVER
stores a raw API key — only the *name* of the environment variable the key
lives in, so an accidentally-committed dotfiles-adjacent config directory
never leaks a secret.

Tests (and any other caller that needs isolation) can override the path via
the ``OHNOO_CONFIG_PATH`` environment variable — see ``config_path()``.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - exercised only on Python <3.11
    import tomli as tomllib


def config_path() -> Path:
    """Return the path to the config file.

    Honors ``OHNOO_CONFIG_PATH`` (used by tests to avoid ever touching the
    real user home directory) before falling back to the real default of
    ``~/.config/ohnoo/config.toml``.
    """
    override = os.environ.get("OHNOO_CONFIG_PATH")
    if override:
        return Path(override)
    return Path.home() / ".config" / "ohnoo" / "config.toml"


def load_config() -> dict:
    """Read and parse the TOML config file.

    Never raises — returns ``{}`` if the file is missing, unreadable, or
    corrupt, so this layer always degrades gracefully.
    """
    path = config_path()
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError, ValueError):
        return {}


def _toml_escape(value: str) -> str:
    """Escape a string for embedding in a TOML basic string."""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def save_config(provider: str, env_var_name: str) -> None:
    """Write ``{"llm": {"provider": provider, "api_key_env_var": env_var_name}}``.

    Creates parent directories as needed. Written by hand (simple
    ``key = "value"`` lines) rather than via a TOML-writing library, since
    that's all this shape needs and keeps the dependency footprint small.
    """
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    content = (
        "[llm]\n"
        f'provider = "{_toml_escape(provider)}"\n'
        f'api_key_env_var = "{_toml_escape(env_var_name)}"\n'
    )
    path.write_text(content, encoding="utf-8")
    try:
        # Best-effort: restrict to the owner. This file names which env var
        # gets sent as an API key on ohnoo's behalf, so other local users
        # shouldn't be able to read or tamper with it. No-op-ish on Windows
        # (NTFS ACLs aren't controlled by chmod), but harmless there.
        os.chmod(path, 0o600)
    except OSError:
        pass


def clear_config() -> None:
    """Delete the config file if present. No error if already absent."""
    path = config_path()
    try:
        path.unlink()
    except FileNotFoundError:
        pass
    except OSError:
        pass


def resolve_active_config() -> dict | None:
    """Resolve the currently-active Layer 4 configuration, if any.

    Resolution order:
      1. ``OHNOO_LLM_PROVIDER`` + ``OHNOO_LLM_KEY`` env vars, if both set.
      2. The TOML config's ``provider`` + ``api_key_env_var``, looking up
         that named env var's *current* value. If the named env var isn't
         currently set in this shell session, returns ``None`` (configured,
         but not available right now) rather than raising or guessing.
      3. ``None`` if nothing is configured at all.
    """
    env_provider = os.environ.get("OHNOO_LLM_PROVIDER")
    env_key = os.environ.get("OHNOO_LLM_KEY")
    if env_provider and env_key:
        return {"provider": env_provider, "api_key": env_key, "source": "env"}

    config = load_config()
    llm = config.get("llm") if isinstance(config, dict) else None
    if not isinstance(llm, dict):
        return None

    provider = llm.get("provider")
    env_var_name = llm.get("api_key_env_var")
    if not provider or not env_var_name:
        return None

    api_key = os.environ.get(env_var_name)
    if not api_key:
        return None

    return {"provider": provider, "api_key": api_key, "source": "config"}
