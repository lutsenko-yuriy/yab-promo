"""Structural checks for the presentation deck in deck/.

The deck has no JavaScript test setup, so these tests read the files as text: the
markup in deck/index.html and the string tables in deck/i18n/<lang>.js.
"""

import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DECK = REPO / "deck"
LANGS = ("en", "de")

# Sections the table-of-contents slide links to, in order.
TOC_TARGETS = ["purpose", "example", "cases", "limits", "get-yab"]

# A German value may equal its English one only for these keys (proper nouns and the like).
SAME_IN_BOTH = {
    "toc.title",
    "controls.lang-en",
    "controls.lang-de",
}

ALLOWED_INLINE_TAGS = {"strong", "em", "br", "span"}

TABLE_RE = re.compile(
    r"\Awindow\.YAB_I18N = window\.YAB_I18N \|\| \{\};\n"
    r"window\.YAB_I18N\.(?P<lang>[a-z]{2}) = (?P<body>\{.*\});\n\Z",
    re.DOTALL,
)


class _DeckParser(HTMLParser):
    """Collects what the tests need from deck/index.html in one pass."""

    def __init__(self):
        super().__init__()
        self.slides = []  # [{"id": str, "attrs": dict, "data_ids": [str], "links": [str]}]
        self.nested_sections = 0
        self.i18n_keys = []
        self.code_tags = 0
        self.asset_refs = []  # (tag, url)
        self._section_depth = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "section":
            self._section_depth += 1
            if self._section_depth > 1:
                self.nested_sections += 1
            self.slides.append(
                {"id": attrs.get("id"), "attrs": attrs, "data_ids": [], "links": []}
            )
        slide = self.slides[-1] if self._section_depth else None
        for name in ("data-i18n", "data-i18n-aria"):
            if name in attrs:
                self.i18n_keys.append(attrs[name])
        if slide is not None and "data-id" in attrs:
            slide["data_ids"].append(attrs["data-id"])
        if slide is not None and tag == "a" and "href" in attrs:
            slide["links"].append(attrs["href"])
        if tag in ("code", "pre"):
            self.code_tags += 1
        if tag in ("script", "img") and "src" in attrs:
            self.asset_refs.append((tag, attrs["src"]))
        if tag == "link" and "href" in attrs:
            self.asset_refs.append((tag, attrs["href"]))

    def handle_endtag(self, tag):
        if tag == "section":
            self._section_depth -= 1


def _parse_deck():
    parser = _DeckParser()
    parser.feed((DECK / "index.html").read_text(encoding="utf-8"))
    return parser


def _load_table(lang):
    text = (DECK / "i18n" / f"{lang}.js").read_text(encoding="utf-8")
    match = TABLE_RE.match(text)
    if match is None or match.group("lang") != lang:
        raise AssertionError(f"deck/i18n/{lang}.js does not have the expected wrapper")
    return json.loads(match.group("body"))


class StringTableTest(unittest.TestCase):
    def test_string_tables_parse(self):
        for lang in LANGS:
            with self.subTest(lang=lang):
                self.assertIsInstance(_load_table(lang), dict)

    def test_languages_have_identical_keys(self):
        en, de = _load_table("en"), _load_table("de")
        self.assertEqual(sorted(set(en) - set(de)), [], "missing in de")
        self.assertEqual(sorted(set(de) - set(en)), [], "missing in en")

    def test_no_empty_or_untranslated_strings(self):
        en, de = _load_table("en"), _load_table("de")
        for lang, table in (("en", en), ("de", de)):
            empty = [key for key, value in table.items() if not str(value).strip()]
            self.assertEqual(empty, [], f"empty values in {lang}")
        untranslated = [
            key for key in en if key not in SAME_IN_BOTH and de.get(key) == en[key]
        ]
        self.assertEqual(untranslated, [], "de values copied from en")

    def test_inline_html_only(self):
        for lang in LANGS:
            for key, value in _load_table(lang).items():
                tags = {tag.lower() for tag in re.findall(r"</?([a-zA-Z0-9]+)", value)}
                with self.subTest(lang=lang, key=key):
                    self.assertLessEqual(tags, ALLOWED_INLINE_TAGS)


class MarkupTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.deck = _parse_deck()

    def test_markup_keys_match_tables(self):
        markup = set(self.deck.i18n_keys)
        table = set(_load_table("en"))
        self.assertEqual(sorted(markup - table), [], "keys used in markup but not in tables")
        self.assertEqual(sorted(table - markup), [], "keys in tables but unused in markup")

    def test_slides_are_flat(self):
        self.assertEqual(self.deck.nested_sections, 0, "vertical stacks are not used")

    def test_slide_ids_unique(self):
        ids = [slide["id"] for slide in self.deck.slides]
        self.assertNotIn(None, ids, "every slide needs an id")
        self.assertEqual(len(ids), len(set(ids)))

    def test_auto_animate_data_ids_unique_per_slide(self):
        for slide in self.deck.slides:
            with self.subTest(slide=slide["id"]):
                data_ids = slide["data_ids"]
                self.assertEqual(len(data_ids), len(set(data_ids)))

    def test_toc_links_resolve(self):
        toc = self.deck.slides[0]
        self.assertEqual(toc["id"], "toc")
        self.assertEqual(toc["links"], [f"#/{target}" for target in TOC_TARGETS])
        ids = {slide["id"] for slide in self.deck.slides}
        for target in TOC_TARGETS:
            self.assertIn(target, ids)

    def test_no_code_on_slides(self):
        self.assertEqual(self.deck.code_tags, 0)

    def test_local_assets_exist_and_no_external_requests(self):
        self.assertTrue(self.deck.asset_refs, "the deck loads no assets")
        for tag, url in self.deck.asset_refs:
            with self.subTest(tag=tag, url=url):
                self.assertNotRegex(url, r"^(?:[a-z][a-z0-9+.-]*:|//|/)", "must be relative")
                self.assertTrue((DECK / url).is_file(), "file missing under deck/")

    def test_vendored_reveal_has_licence(self):
        licences = list((DECK / "vendor").glob("reveal.js-*/LICENSE"))
        self.assertEqual(len(licences), 1)


if __name__ == "__main__":
    unittest.main()
