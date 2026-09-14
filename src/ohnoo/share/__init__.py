"""--share: terminal-style PNG roast cards.

Renders the last roast (an ``ohnoo.engine.Diagnosis``) as a shareable,
terminal-window-styled PNG suitable for social sharing, sized for Twitter/X
link-preview cards (roughly 1200x630). No browser dependency — rendered
entirely with Pillow.
"""

from __future__ import annotations

import textwrap
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from ohnoo.engine import Diagnosis

CARD_WIDTH = 1200
CARD_HEIGHT = 630

_BG = (22, 23, 26)  # ~#16171A
_WINDOW_BG = (30, 31, 35)
_TITLEBAR_BG = (40, 41, 46)
_TEXT = (232, 230, 225)  # off-white
_MUTED = (139, 141, 148)
_GREEN = (67, 209, 122)
_PROMPT = (120, 200, 255)

_DOT_RED = (255, 95, 86)
_DOT_YELLOW = (255, 189, 46)
_DOT_GREEN = (39, 201, 63)


def _default_output_path() -> Path:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
    return Path.home() / ".cache" / "ohnoo" / "shares" / f"{ts}.png"


def _font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        # Older Pillow: load_default() has no `size` kwarg.
        return ImageFont.load_default()


def _wrap(text: str, width: int) -> list[str]:
    if not text:
        return []
    wrapped: list[str] = []
    for line in text.splitlines() or [text]:
        wrapped.extend(textwrap.wrap(line, width=width) or [""])
    return wrapped


def render_share_card(
    diagnosis: Diagnosis,
    command: str = "",
    output_path: Path | None = None,
) -> Path:
    """Render `diagnosis` as a terminal-style PNG and return the path written."""
    if output_path is None:
        output_path = _default_output_path()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), _BG)
    draw = ImageDraw.Draw(img)

    margin = 48
    window_box = (margin, margin, CARD_WIDTH - margin, CARD_HEIGHT - margin)
    radius = 16
    draw.rounded_rectangle(window_box, radius=radius, fill=_WINDOW_BG)

    titlebar_height = 44
    titlebar_box = (window_box[0], window_box[1], window_box[2], window_box[1] + titlebar_height)
    draw.rounded_rectangle(titlebar_box, radius=radius, fill=_TITLEBAR_BG)
    # Square off the bottom corners of the titlebar so it reads as one piece
    # with the window body below it.
    draw.rectangle(
        (window_box[0], window_box[1] + radius, window_box[2], titlebar_box[3]),
        fill=_TITLEBAR_BG,
    )

    dot_y = window_box[1] + titlebar_height // 2
    dot_r = 7
    dot_x = window_box[0] + 24
    for dx, color in ((0, _DOT_RED), (28, _DOT_YELLOW), (56, _DOT_GREEN)):
        cx = dot_x + dx
        draw.ellipse((cx - dot_r, dot_y - dot_r, cx + dot_r, dot_y + dot_r), fill=color)

    label_font = _font(16)
    draw.text(
        (window_box[2] - 140, dot_y - 8),
        "ohnoo",
        font=label_font,
        fill=_MUTED,
    )

    body_font = _font(24)
    fix_font = _font(22)

    text_x = window_box[0] + 40
    text_y = titlebar_box[3] + 36
    line_height = 34
    max_chars = 62

    if command:
        draw.text((text_x, text_y), "$ ", font=body_font, fill=_PROMPT)
        prompt_w = draw.textlength("$ ", font=body_font)
        for i, line in enumerate(_wrap(command, max_chars)):
            draw.text(
                (text_x + (prompt_w if i == 0 else 0), text_y + i * line_height),
                line,
                font=body_font,
                fill=_TEXT,
            )
        text_y += line_height * max(1, len(_wrap(command, max_chars))) + 18

    joke = diagnosis.joke or ""
    for line in _wrap(joke, max_chars):
        draw.text((text_x, text_y), line, font=body_font, fill=_TEXT)
        text_y += line_height

    text_y += 18
    fix_text = diagnosis.fix_command or diagnosis.fix_summary
    if fix_text:
        draw.text((text_x, text_y), "  fix: ", font=fix_font, fill=_GREEN)
        fix_prompt_w = draw.textlength("  fix: ", font=fix_font)
        for i, line in enumerate(_wrap(fix_text, max_chars - 8)):
            draw.text(
                (text_x + (fix_prompt_w if i == 0 else 0), text_y + i * line_height),
                line,
                font=fix_font,
                fill=_TEXT,
            )

    img.save(output_path, format="PNG")
    return output_path
