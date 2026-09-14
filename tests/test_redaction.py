"""Tests for Layer 4's secret redaction, applied before crash text is ever
sent to a hosted LLM provider. Stderr scrollback can legitimately contain
credentials (a printed token, a signed URL, an echoed env var); Layer 4 is
opt-in but not a license to exfiltrate whatever happens to be on screen.
"""

from unittest.mock import MagicMock, patch

from ohnoo.llm_fallback.fallback import redact_secrets, try_llm_fallback


def test_redacts_github_token():
    text = "remote: Invalid username or token. Token: ghp_1234567890abcdef1234567890abcdef1234"
    assert "ghp_1234567890abcdef1234567890abcdef1234" not in redact_secrets(text)
    assert "[REDACTED_GITHUB_TOKEN]" in redact_secrets(text)


def test_redacts_aws_access_key():
    text = "botocore.exceptions.ClientError: AKIAIOSFODNN7EXAMPLE is not authorized"
    redacted = redact_secrets(text)
    assert "AKIAIOSFODNN7EXAMPLE" not in redacted
    assert "[REDACTED_AWS_ACCESS_KEY]" in redacted


def test_redacts_stripe_live_key():
    text = "StripeError: sk_live_51H8xyzabcdefghijklmnop invalid"
    redacted = redact_secrets(text)
    assert "sk_live_51H8xyzabcdefghijklmnop" not in redacted


def test_redacts_bearer_header():
    text = "curl failed: Authorization: Bearer abc123.def456-ghi789 rejected"
    redacted = redact_secrets(text)
    assert "abc123.def456-ghi789" not in redacted
    assert "Bearer [REDACTED]" in redacted


def test_redacts_private_key_block():
    text = (
        "loading key...\n"
        "-----BEGIN RSA PRIVATE KEY-----\n"
        "MIIEpAIBAAKCAQEA1234567890abcdef\n"
        "-----END RSA PRIVATE KEY-----\n"
        "done"
    )
    redacted = redact_secrets(text)
    assert "MIIEpAIBAAKCAQEA1234567890abcdef" not in redacted
    assert "[REDACTED_PRIVATE_KEY]" in redacted


def test_redacts_generic_key_value_secret():
    text = "config error: DATABASE_PASSWORD=hunter2superSecret123 refused connection"
    redacted = redact_secrets(text)
    assert "hunter2superSecret123" not in redacted
    # The key name stays -- it's useful diagnostic context, unlike the value.
    assert "PASSWORD" in redacted


def test_leaves_ordinary_traceback_text_unchanged():
    text = "ModuleNotFoundError: No module named 'requests'"
    assert redact_secrets(text) == text


def test_try_llm_fallback_sends_redacted_text_to_the_provider(monkeypatch, tmp_path):
    monkeypatch.setenv("OHNOO_CONFIG_PATH", str(tmp_path / "config.toml"))
    monkeypatch.setenv("OHNOO_LLM_PROVIDER", "groq")
    monkeypatch.setenv("OHNOO_LLM_KEY", "test-groq-key")

    resp = MagicMock()
    resp.status_code = 200
    resp.raise_for_status.return_value = None
    resp.json.return_value = {"choices": [{"message": {"content": "diagnosis"}}]}

    captured = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["body"] = json
        return resp

    with patch("httpx.post", side_effect=fake_post):
        result = try_llm_fallback(
            "leaked token ghp_1234567890abcdef1234567890abcdef1234 in traceback"
        )

    assert result == "diagnosis"
    sent_content = captured["body"]["messages"][0]["content"]
    assert "ghp_1234567890abcdef1234567890abcdef1234" not in sent_content
    assert "[REDACTED_GITHUB_TOKEN]" in sent_content
