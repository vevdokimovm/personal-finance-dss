"""A11Y P1.1 — contrast guard (both themes).

Parses the design tokens for each theme from the single stylesheet, composites
the translucent surface tokens over the opaque backgrounds, and asserts that
every text-bearing token clears WCAG 2.1 AA (4.5:1 for normal text) against the
worst-case (lowest-contrast) effective background it can sit on, in BOTH the
default dark theme (:root) and the light theme ([data-theme="light"], which
inherits unset tokens from :root).

This is a regression lock for both themes: dropping any guarded token below AA
fails CI. Screen-reader and live visual checks (NVDA/VoiceOver) remain manual.
"""

import re
from pathlib import Path

import pytest

CSS_PATH = Path(__file__).resolve().parents[1] / "frontend" / "static" / "css" / "styles.css"
AA_NORMAL = 4.5

TEXT_TOKENS = ["--c-text", "--c-text2", "--c-text3", "--c-accent"]
SURFACE_TOKENS = ["--c-bg", "--c-bg2", "--c-surface", "--c-surface-up"]
THEMES = ["dark", "light"]
RGB = tuple[int, int, int]


def _block(css: str, pattern: str) -> str:
    match = re.search(pattern, css, re.DOTALL)
    assert match, f"block not found: {pattern!r}"
    return match.group(1)


def _parse(block: str) -> dict[str, str]:
    return {name: value.strip() for name, value in re.findall(r"(--c-[\w-]+)\s*:\s*([^;]+);", block)}


def _themes(css: str) -> dict[str, dict[str, str]]:
    root = _parse(_block(css, r":root\s*\{(.*?)\}"))
    light = _parse(_block(css, r'\[data-theme="light"\]\s*\{(.*?)\}'))
    return {"dark": root, "light": {**root, **light}}


def _to_rgb(value: str) -> RGB:
    value = value.split("/*", 1)[0].strip()
    hex_match = re.fullmatch(r"#([0-9a-fA-F]{6})", value)
    if hex_match:
        h = hex_match.group(1)
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    rgba_match = re.fullmatch(r"rgba?\(([^)]+)\)", value)
    if rgba_match:
        parts = [p.strip() for p in rgba_match.group(1).split(",")]
        return int(parts[0]), int(parts[1]), int(parts[2])
    raise ValueError(f"unsupported color value: {value!r}")


def _alpha(value: str) -> float:
    rgba_match = re.fullmatch(r"rgba\(([^)]+)\)", value.split("/*", 1)[0].strip())
    if not rgba_match:
        return 1.0
    parts = [p.strip() for p in rgba_match.group(1).split(",")]
    return float(parts[3]) if len(parts) == 4 else 1.0


def _composite(fg: RGB, alpha: float, bg: RGB) -> RGB:
    return tuple(round(alpha * f + (1 - alpha) * b) for f, b in zip(fg, bg))


def _channel(c: int) -> float:
    s = c / 255
    return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4


def _luminance(rgb: RGB) -> float:
    r, g, b = rgb
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def _contrast(fg: RGB, bg: RGB) -> float:
    a, b = _luminance(fg), _luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def _backgrounds(tok: dict[str, str]) -> list[RGB]:
    bg = _to_rgb(tok["--c-bg"])
    bg2 = _to_rgb(tok["--c-bg2"])
    surface = _composite(_to_rgb(tok["--c-surface"]), _alpha(tok["--c-surface"]), bg)
    surface_up = _composite(_to_rgb(tok["--c-surface-up"]), _alpha(tok["--c-surface-up"]), surface)
    return [bg, bg2, surface, surface_up]


@pytest.fixture(scope="module")
def themes() -> dict[str, dict[str, str]]:
    return _themes(CSS_PATH.read_text(encoding="utf-8"))


@pytest.mark.parametrize("theme", THEMES)
@pytest.mark.parametrize("token", TEXT_TOKENS)
def test_text_token_meets_aa(themes: dict[str, dict[str, str]], theme: str, token: str) -> None:
    tok = themes[theme]
    fg = _to_rgb(tok[token])
    backgrounds = _backgrounds(tok)
    worst = min(_contrast(fg, bg) for bg in backgrounds)
    assert worst >= AA_NORMAL, f"[{theme}] {token} worst contrast {worst:.2f} < AA {AA_NORMAL}"
