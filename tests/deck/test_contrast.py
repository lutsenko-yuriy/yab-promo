"""Colour contrast of the deck theme in deck/css/theme.css, light and night mode.

Each rule that sets a colour is checked against the background it sits on: its own
background if it sets one, otherwise both the page background and the card surface, since
it may sit on either. Night mode redefines the colour tokens; every rule is checked with
each theme's tokens.
"""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
THEME = REPO / "deck" / "css" / "theme.css"

TEXT_MINIMUM = 4.5  # WCAG 1.4.3, normal text
GRAPHIC_MINIMUM = 3.0  # WCAG 1.4.11, graphics needed to follow the slide

PAGE_BACKGROUND = "yab-background"
CARD_SURFACE = "yab-surface"

# The token blocks: light on :root, night mode under two selectors with the same values,
# one for the button's choice and one for the system setting.
LIGHT = ":root"
DARK_CHOSEN = ':root[data-theme="dark"]'
DARK_SYSTEM = ':root:not([data-theme="light"])'

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
_TOKEN = re.compile(r"--([\w-]+):\s*([^;]+);")
_COLOR = re.compile(r"(?:^|;)\s*color:\s*([^;]+)")
_BACKGROUND = re.compile(r"(?:^|;)\s*background(?:-color)?:\s*([^;]+)")
_VAR = re.compile(r"var\(--([\w-]+)\)")
_HEX = re.compile(r"#[0-9a-fA-F]{6}")
_RAW_COLOUR = re.compile(r"#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(")


def _luminance(hex_colour):
    channels = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(first, second):
    lighter, darker = sorted((_luminance(first), _luminance(second)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def _rules(css):
    """(selector, body) for every rule, comments removed and whitespace collapsed."""
    return [(" ".join(selector.split()), body)
            for selector, body in _RULE.findall(_COMMENT.sub("", css))]


def tokens(css, selector):
    """The custom properties a token block sets, by name; {} if there is no such block."""
    found = {}
    for rule_selector, body in _rules(css):
        if rule_selector == selector:
            found.update((name, value.strip()) for name, value in _TOKEN.findall(body))
    return found


def colour_tokens(block):
    """The tokens in a block whose value carries a colour."""
    return {name for name, value in block.items() if _RAW_COLOUR.search(value)}


def _resolve(value, tokens):
    """The hex colour a declaration value names, or None (transparent, inherit, …)."""
    var = _VAR.fullmatch(value.strip())
    if var:
        value = tokens.get(var.group(1), "")
    hex_colour = _HEX.fullmatch(value.strip())
    return hex_colour.group(0) if hex_colour else None


def coloured_rules(css, theme_tokens):
    """(selector, foreground, backgrounds) for every rule that sets a colour."""
    rules = []
    for selector, body in _rules(css):
        colour = _COLOR.search(body)
        if not colour:
            continue
        foreground = _resolve(colour.group(1), theme_tokens)
        if foreground is None:
            continue
        background = _BACKGROUND.search(body)
        background = _resolve(background.group(1), theme_tokens) if background else None
        backgrounds = ([background] if background else
                       [theme_tokens[PAGE_BACKGROUND], theme_tokens[CARD_SURFACE]])
        rules.append((selector, foreground, backgrounds))
    return rules


class ContrastTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = THEME.read_text(encoding="utf-8")
        cls.light = tokens(cls.css, LIGHT)
        cls.dark = tokens(cls.css, DARK_CHOSEN)
        cls.themes = {"light": cls.light, "night": {**cls.light, **cls.dark}}

    def test_finds_the_coloured_rules(self):
        selectors = [selector for selector, _, _ in coloured_rules(self.css, self.light)]
        self.assertIn(".reveal h1, .reveal h2", selectors)
        self.assertIn(".reveal .chain-arrow", selectors)
        self.assertTrue([s for s in selectors if "branch-line" in s], "no branch line colour")
        self.assertLessEqual(DECORATIVE_SELECTORS, set(selectors), "stale exception")

    def test_text_and_graphics_stand_out_from_their_background(self):
        for theme, theme_tokens in self.themes.items():
            too_faint = []
            for selector, foreground, backgrounds in coloured_rules(self.css, theme_tokens):
                if selector in DECORATIVE_SELECTORS:
                    continue
                graphic = GRAPHIC_SELECTOR.search(selector)
                minimum = GRAPHIC_MINIMUM if graphic else TEXT_MINIMUM
                for background in backgrounds:
                    ratio = contrast(foreground, background)
                    if ratio < minimum:
                        too_faint.append(f"{selector}: {foreground} on {background} is "
                                         f"{ratio:.2f}:1, needs {minimum}:1")
            with self.subTest(theme=theme):
                self.assertEqual(too_faint, [])

    def test_night_mode_redefines_every_colour_token(self):
        self.assertEqual(colour_tokens(self.light) - set(self.dark), set())

    def test_night_mode_is_the_same_by_button_and_by_system_setting(self):
        self.assertTrue(self.dark, "no night mode tokens")
        self.assertEqual(tokens(self.css, DARK_SYSTEM), self.dark)

    def test_colours_are_only_set_in_token_blocks(self):
        # Night mode swaps the token values, so a colour written straight into a rule
        # would stay the same in both themes.
        raw = [selector for selector, body in _rules(self.css)
               if ":root" not in selector and _RAW_COLOUR.search(body)]
        self.assertEqual(raw, [])

    def test_contrast_formula(self):
        self.assertAlmostEqual(contrast("#000000", "#ffffff"), 21.0)
        self.assertAlmostEqual(contrast("#777777", "#777777"), 1.0)


if __name__ == "__main__":
    unittest.main()
