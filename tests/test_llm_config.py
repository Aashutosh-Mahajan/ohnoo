"""Tests for Layer 4 config read/write/resolve logic.

CRITICAL: every test here sets OHNOO_CONFIG_PATH to a tmp_path location via
monkeypatch.setenv BEFORE calling any config function, so the real path
(~/.config/ohnoo/config.toml) is never touched.
"""

from pathlib import Path

from ohnoo.llm_fallback.config import (
    clear_config,
    config_path,
    load_config,
    resolve_active_config,
    save_config,
)
from ohnoo.llm_fallback.fallback import try_llm_fallback


def _isolate(monkeypatch, tmp_path: Path) -> Path:
    """Point config at a throwaway path and strip relevant env vars."""
    cfg = tmp_path / "config.toml"
    monkeypatch.setenv("OHNOO_CONFIG_PATH", str(cfg))
    monkeypatch.delenv("OHNOO_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("OHNOO_LLM_KEY", raising=False)
    return cfg


def test_config_path_honors_override(monkeypatch, tmp_path):
    cfg = _isolate(monkeypatch, tmp_path)
    assert config_path() == cfg


def test_load_config_missing_file_returns_empty_dict(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    assert load_config() == {}


def test_load_config_corrupt_file_returns_empty_dict(monkeypatch, tmp_path):
    cfg = _isolate(monkeypatch, tmp_path)
    cfg.parent.mkdir(parents=True, exist_ok=True)
    cfg.write_text("this is not [ valid toml {{{", encoding="utf-8")
    assert load_config() == {}


def test_save_config_creates_parent_dirs_and_writes_shape(monkeypatch, tmp_path):
    cfg = tmp_path / "nested" / "config.toml"
    monkeypatch.setenv("OHNOO_CONFIG_PATH", str(cfg))
    monkeypatch.delenv("OHNOO_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("OHNOO_LLM_KEY", raising=False)
    assert not cfg.parent.exists()

    save_config("groq", "GROQ_API_KEY")

    assert cfg.exists()
    data = load_config()
    assert data == {"llm": {"provider": "groq", "api_key_env_var": "GROQ_API_KEY"}}


def test_save_config_never_writes_raw_key(monkeypatch, tmp_path):
    cfg = _isolate(monkeypatch, tmp_path)
    monkeypatch.setenv("MY_SECRET_KEY", "sk-super-secret-value-12345")

    save_config("groq", "MY_SECRET_KEY")

    raw = cfg.read_text(encoding="utf-8")
    assert "sk-super-secret-value-12345" not in raw
    assert "MY_SECRET_KEY" in raw


def test_clear_config_removes_file(monkeypatch, tmp_path):
    cfg = _isolate(monkeypatch, tmp_path)
    save_config("groq", "GROQ_API_KEY")
    assert cfg.exists()

    clear_config()

    assert not cfg.exists()


def test_clear_config_no_error_if_absent(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    clear_config()  # should not raise


def test_resolve_active_config_prefers_env_vars(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    save_config("anthropic", "ANTHROPIC_API_KEY")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "config-key-value")

    monkeypatch.setenv("OHNOO_LLM_PROVIDER", "openai")
    monkeypatch.setenv("OHNOO_LLM_KEY", "env-key-value")

    result = resolve_active_config()

    assert result == {"provider": "openai", "api_key": "env-key-value", "source": "env"}


def test_resolve_active_config_from_saved_config(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    save_config("groq", "GROQ_API_KEY")
    monkeypatch.setenv("GROQ_API_KEY", "abc123")

    result = resolve_active_config()

    assert result == {"provider": "groq", "api_key": "abc123", "source": "config"}


def test_resolve_active_config_none_when_named_env_var_unset(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    save_config("groq", "GROQ_API_KEY")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    assert resolve_active_config() is None


def test_resolve_active_config_none_when_nothing_configured(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    assert resolve_active_config() is None


def test_resolve_active_config_none_with_partial_env_vars(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    monkeypatch.setenv("OHNOO_LLM_PROVIDER", "groq")
    # OHNOO_LLM_KEY intentionally left unset.

    assert resolve_active_config() is None


def test_try_llm_fallback_returns_none_with_no_config_at_all(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    assert try_llm_fallback("Traceback (most recent call last): boom") is None
