"""Tests for Layer 4 provider modules. Mocks httpx.post so no real network
calls are ever made."""

from unittest.mock import MagicMock, patch

import httpx

from ohnoo.llm_fallback.providers import anthropic, get_provider, groq, ollama, openai


def _mock_response(json_body, status_code=200):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_body
    if status_code >= 400:
        request = httpx.Request("POST", "https://example.invalid")
        resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error", request=request, response=httpx.Response(status_code, request=request)
        )
    else:
        resp.raise_for_status.return_value = None
    return resp


def test_get_provider_returns_expected_modules():
    assert get_provider("groq") is groq
    assert get_provider("GROQ") is groq
    assert get_provider("anthropic") is anthropic
    assert get_provider("openai") is openai
    assert get_provider("ollama") is ollama


def test_get_provider_unknown_raises_value_error():
    try:
        get_provider("not-a-real-provider")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "not-a-real-provider" in str(exc)


def test_groq_diagnose_success():
    body = {"choices": [{"message": {"content": "It's a missing module; pip install it."}}]}
    with patch("httpx.post", return_value=_mock_response(body)):
        result = groq.diagnose("ModuleNotFoundError: no module named foo", api_key="key")
    assert result == "It's a missing module; pip install it."


def test_groq_diagnose_no_api_key_fails_gracefully():
    result = groq.diagnose("some error", api_key=None)
    assert result.startswith("(hosted LLM call failed")


def test_groq_diagnose_network_error_fails_gracefully():
    with patch("httpx.post", side_effect=httpx.ConnectTimeout("timed out")):
        result = groq.diagnose("some error", api_key="key")
    assert result.startswith("(hosted LLM call failed")


def test_groq_diagnose_http_error_status_fails_gracefully():
    with patch("httpx.post", return_value=_mock_response({}, status_code=500)):
        result = groq.diagnose("some error", api_key="key")
    assert result.startswith("(hosted LLM call failed")


def test_openai_diagnose_success():
    body = {"choices": [{"message": {"content": "Port already in use; kill the process."}}]}
    with patch("httpx.post", return_value=_mock_response(body)):
        result = openai.diagnose("EADDRINUSE", api_key="key")
    assert result == "Port already in use; kill the process."


def test_openai_diagnose_bad_shape_fails_gracefully():
    with patch("httpx.post", return_value=_mock_response({"unexpected": "shape"})):
        result = openai.diagnose("some error", api_key="key")
    assert result.startswith("(hosted LLM call failed")


def test_anthropic_diagnose_success():
    body = {"content": [{"text": "Not a git repo; run git init."}]}
    with patch("httpx.post", return_value=_mock_response(body)):
        result = anthropic.diagnose("fatal: not a git repository", api_key="key")
    assert result == "Not a git repo; run git init."


def test_anthropic_diagnose_no_api_key_fails_gracefully():
    result = anthropic.diagnose("some error", api_key=None)
    assert result.startswith("(hosted LLM call failed")


def test_ollama_diagnose_success():
    body = {"response": "Undefined name; import it first."}
    with patch("httpx.post", return_value=_mock_response(body)):
        result = ollama.diagnose("NameError: name 'x' is not defined")
    assert result == "Undefined name; import it first."


def test_ollama_diagnose_network_error_fails_gracefully():
    with patch("httpx.post", side_effect=httpx.ConnectError("connection refused")):
        result = ollama.diagnose("some error")
    assert result.startswith("(hosted LLM call failed")
