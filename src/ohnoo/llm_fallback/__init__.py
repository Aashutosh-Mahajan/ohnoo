"""Layer 4 — hosted LLM fallback.

Off by default. Supports Groq, Anthropic, OpenAI, or local Ollama for a
single-sentence diagnosis + fix on errors nothing else recognizes.

Public entrypoints:
    - ``ohnoo.llm_fallback.fallback.try_llm_fallback(error_text)`` — the
      orchestration entrypoint the rest of the CLI calls.
    - ``ohnoo.llm_fallback.wizard.run_setup_wizard(disable=False)`` — the
      interactive wizard behind ``ohnoo setup-ai``.
"""
