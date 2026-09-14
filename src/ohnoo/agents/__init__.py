"""Layer 2 — CLI agent handoff.

Detects installed agentic CLIs (claude, codex, agy) on $PATH, builds a
scoped prompt from the traceback + failing file/line, and invokes them
headlessly for --explain (read-only) or --fix (edit + confirm) mode.

Public entry points live in ohnoo.agents.handoff (explain, fix,
should_warn_this_session, cost_warning_text), ohnoo.agents.detect
(detect_available_agents, pick_agent), and ohnoo.agents.prompt_builder
(build_scoped_prompt, extract_file_line).
"""
