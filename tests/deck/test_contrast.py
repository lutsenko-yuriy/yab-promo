"""Colour contrast of the deck theme in deck/css/theme.css.

Each rule that sets a colour is checked against the background it sits on: its own
background if it sets one, otherwise the page background. A rule without its own
background may sit on a white card instead; the theme's foregrounds are all darker than
the page, so the page is the harder case.
"""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
THEME = REPO / "deck" / "css" / "theme.css"

TEXT_MINIMUM = 4.5  # WCAG 1.4.3, normal text
GRAPHIC_MINIMUM = 3.0  # WCAG 1.4.11, graphics needed to follow the slide

PAGE_BACKGROUND = "yab-background"

# Arrows show the order of steps and the branch diagram's lines and commits show each work
# unit's branch, so they are graphics; everything else that sets a colour is text.
GRAPHIC_SELECTOR = re.compile(
    r"arrow|main-line|branch-line|merge-line|commit|main-node|::after|::before"
)

# Kept light green on purpose (checkup heavy-1, PR #11): list markers and the progress
# bar only decorate, the slide reads the same without them.
DECORATIVE_SELECTORS = {
    ".reveal .points li::marker",
    ".reveal .progress",
}

_COMMENT = re.compile(r"/\*.*?\*/", re.S)
_RULE = re.compile(r"([^{}]+)\{([^{}]*)\}")
_TOKEN = re.compile(r"--([\w-]+):\s*(#[0-9a-fA-F]{6})\s*;")
_COLOR = re.compile(r"(?:^|;)\s*color:\s*([^;]+)")
_BACKGROUND = re.compile(r"(?:^|;)\s*background(?:-color)?:\s*([^;]+)")
_VAR = re.compile(r"var\(--([\w-]+)\)")
_HEX = re.compile(r"#[0-9a-fA-F]{6}")


def _luminance(hex_colour):
    channels = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(first, second):
    lighter, darker = sorted((_luminance(first), _luminance(second)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def _resolve(value, tokens):
    """The hex colour a declaration value names, or None (transparent, inherit, …)."""
    var = _VAR.fullmatch(value.strip())
    if var:
        return tokens.get(var.group(1))
    hex_colour = _HEX.fullmatch(value.strip())
    return hex_colour.group(0) if hex_colour else None


def coloured_rules(css):
    """(selector, foreground, background) for every rule that sets a colour."""
    css = _COMMENT.sub("", css)
    tokens = dict(_TOKEN.findall(css))
    rules = []
    for selector, body in _RULE.findall(css):
        colour = _COLOR.search(body)
        if not colour:
            continue
        foreground = _resolve(colour.group(1), tokens)
        if foreground is None:
            continue
        background = _BACKGROUND.search(body)
        background = _resolve(background.group(1), tokens) if background else None
        rules.append((" ".join(selector.split()), foreground,
                      background or tokens[PAGE_BACKGROUND]))
    return rules


class ContrastTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = coloured_rules(THEME.read_text(encoding="utf-8"))

    def test_finds_the_coloured_rules(self):
        selectors = [selector for selector, _, _ in self.rules]
        self.assertIn(".reveal h1, .reveal h2", selectors)
        self.assertIn(".reveal .chain-arrow", selectors)
        self.assertTrue([s for s in selectors if "branch-line" in s], "no branch line colour")
        self.assertLessEqual(DECORATIVE_SELECTORS, set(selectors), "stale exception")

    def test_text_and_graphics_stand_out_from_their_background(self):
        too_faint = []
        for selector, foreground, background in self.rules:
            if selector in DECORATIVE_SELECTORS:
                continue
            graphic = GRAPHIC_SELECTOR.search(selector)
            minimum = GRAPHIC_MINIMUM if graphic else TEXT_MINIMUM
            ratio = contrast(foreground, background)
            if ratio < minimum:
                too_faint.append(f"{selector}: {foreground} on {background} is "
                                 f"{ratio:.2f}:1, needs {minimum}:1")
        self.assertEqual(too_faint, [])

    def test_contrast_formula(self):
        self.assertAlmostEqual(contrast("#000000", "#ffffff"), 21.0)
        self.assertAlmostEqual(contrast("#777777", "#777777"), 1.0)


if __name__ == "__main__":
    unittest.main()
