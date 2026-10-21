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
TOC_TARGETS = ["purpose", "values", "example", "cases", "limits", "get-yab"]

# Slides of the purpose section, in order. The flow and human slides share one lifecycle.
PURPOSE_SLIDES = ["purpose", "purpose-what", "purpose-flow", "purpose-human", "purpose-memory"]
LIFECYCLE_STEPS = ["idea", "ticket", "plan", "tests", "build", "review", "release", "lessons"]
HUMAN_GATES = ["ticket", "plan", "review", "release"]

# Slides of the example section (HAB-202), in order. All but the opener carry one work-unit
# track; its chips keep their data-id so Auto-Animate moves and recolours them.
EXAMPLE_SLIDES = [
    "example",
    "example-brief",
    "example-analyze",
    "example-plan",
    "example-wu0",
    "example-correction",
    "example-wu1",
    "example-wu2",
    "example-wu3",
    "example-wu4",
    "example-review",
    "example-debrief",
]
WU_TRACK = ["wu-0", "wu-0c", "wu-1", "wu-2", "wu-3", "wu-4"]
INSERTED_CHIP = "wu-0c"
# Workflow steps around the work units: brief, analytics and plan lead the track on every
# slide, the debrief joins its end on the last one.
LEADING_STEPS = ["step-brief", "step-analyze", "step-plan"]
DEBRIEF_STEP = "step-debrief"
# The step being worked on while the ticket is scoped; the work units only appear once the
# plan makes them. Steps before the current one are done, those after it not yet started.
SCOPING_STEP = {
    "example-brief": "step-brief",
    "example-analyze": "step-analyze",
    "example-plan": "step-plan",
}
# The chip being worked on per slide; chips before it are done. None: no work started
# (plan) or all done (debrief).
CURRENT_CHIP = {
    "example-plan": None,
    "example-wu0": "wu-0",
    "example-correction": "wu-0c",
    "example-wu1": "wu-1",
    "example-wu2": "wu-2",
    "example-wu3": "wu-3",
    "example-wu4": "wu-4",
    "example-review": "wu-4",
    "example-debrief": None,
}

# Slides of the cases section, in order: one per app, then the CheckLister tickets run on Codex.
CASES_SLIDES = [
    "cases",
    "cases-habit-loop",
    "cases-checklister",
    "cases-mordovorot",
    "cases-codex",
]
# The public repository each app slide links to; its screenshots live in img/cases/<app>/.
CASE_REPOS = {
    "cases-habit-loop": "https://github.com/lutsenko-yuriy/habit-loop",
    "cases-checklister": "https://github.com/lutsenko-yuriy/CheckLister",
    "cases-mordovorot": "https://github.com/lutsenko-yuriy/mordovorot",
}
# App slides with numbers; each states the date they were counted on.
CASES_WITH_STATS = ["cases-habit-loop", "cases-mordovorot"]
# CheL-36, the CheckLister feature on its slide, ran in four work units.
CHECKLISTER_TRACK = ["wu-1", "wu-2", "wu-3", "wu-4"]
# Screenshots are resized for the web before they are committed.
MAX_IMAGE_BYTES = 250 * 1024

# Slides of the limits section, in order.
LIMITS_SLIDES = ["limits", "limits-tools", "limits-next"]

# Slides of the core-values section, in order: the opener names each value, and each value
# then gets its own slide.
VALUES_SLIDES = ["values", "values-human", "values-safe", "values-understanding"]

PAGES_WORKFLOW = REPO / ".github" / "workflows" / "pages.yml"

# A German value may equal its English one only for these keys (proper nouns and the like).
SAME_IN_BOTH = {
    "toc.title",
    "controls.lang-en",
    "controls.lang-de",
    "purpose-what.tickets",
    "flow.ticket",
    "flow.plan",
    "flow.release",
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
        # [{"id": str, "attrs": dict, "data_ids": [str], "classes": {data_id: set},
        #   "id_attrs": {data_id: dict}, "links": [str], "i18n": [str], "images": [dict]}]
        self.slides = []
        self.nested_sections = 0
        self.i18n_keys = []
        self.code_tags = 0
        self.asset_refs = []  # (tag, url)
        self.anchors = []  # attrs of every <a href>
        self._section_depth = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "section":
            self._section_depth += 1
            if self._section_depth > 1:
                self.nested_sections += 1
            self.slides.append(
                {
                    "id": attrs.get("id"),
                    "attrs": attrs,
                    "data_ids": [],
                    "classes": {},
                    "id_attrs": {},
                    "links": [],
                    "i18n": [],
                    "images": [],
                }
            )
        slide = self.slides[-1] if self._section_depth else None
        for name in ("data-i18n", "data-i18n-aria", "data-i18n-alt"):
            if name in attrs:
                self.i18n_keys.append(attrs[name])
                if slide is not None:
                    slide["i18n"].append(attrs[name])
        if slide is not None and "data-id" in attrs:
            slide["data_ids"].append(attrs["data-id"])
            slide["classes"][attrs["data-id"]] = set((attrs.get("class") or "").split())
            slide["id_attrs"][attrs["data-id"]] = attrs
        if tag == "a" and "href" in attrs:
            self.anchors.append(attrs)
            if slide is not None:
                slide["links"].append(attrs["href"])
        if slide is not None and tag == "img":
            slide["images"].append(attrs)
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

    def _slide(self, slide_id):
        return next(slide for slide in self.deck.slides if slide["id"] == slide_id)

    def test_purpose_section_order(self):
        ids = [slide["id"] for slide in self.deck.slides]
        start = ids.index("purpose")
        self.assertEqual(ids[start:start + len(PURPOSE_SLIDES)], PURPOSE_SLIDES)
        self.assertEqual(ids[start + len(PURPOSE_SLIDES)], "values")

    def test_example_section_order(self):
        ids = [slide["id"] for slide in self.deck.slides]
        start = ids.index("example")
        self.assertEqual(ids[start:start + len(EXAMPLE_SLIDES)], EXAMPLE_SLIDES)
        self.assertEqual(ids[start + len(EXAMPLE_SLIDES)], "cases")

    def test_cases_section_order(self):
        ids = [slide["id"] for slide in self.deck.slides]
        start = ids.index("cases")
        self.assertEqual(ids[start:start + len(CASES_SLIDES)], CASES_SLIDES)
        self.assertEqual(ids[start + len(CASES_SLIDES)], "limits")

    def test_limits_section_order(self):
        ids = [slide["id"] for slide in self.deck.slides]
        start = ids.index("limits")
        self.assertEqual(ids[start:start + len(LIMITS_SLIDES)], LIMITS_SLIDES)
        self.assertEqual(ids[start + len(LIMITS_SLIDES)], "get-yab")
        self.assertEqual(ids[-1], "get-yab")

    def test_values_section_order(self):
        ids = [slide["id"] for slide in self.deck.slides]
        start = ids.index("values")
        self.assertEqual(ids[start:start + len(VALUES_SLIDES)], VALUES_SLIDES)
        self.assertEqual(ids[start + len(VALUES_SLIDES)], "example")

    def test_values_opener_names_each_value(self):
        opener = self._slide("values")
        for slide_id in VALUES_SLIDES[1:]:
            with self.subTest(value=slide_id):
                self.assertIn(f"#/{slide_id}", opener["links"])
                self.assertIn(f"{slide_id}.title", opener["i18n"])
                self.assertIn(f"{slide_id}.title", self._slide(slide_id)["i18n"])

    def test_deck_ends_on_what_yab_gives_not_thanks(self):
        self.assertFalse([k for k in self._slide("get-yab")["i18n"] if k.endswith(".thanks")])

    def test_case_slides_link_their_repo(self):
        for slide_id, repo in CASE_REPOS.items():
            with self.subTest(slide=slide_id):
                self.assertIn(repo, self._slide(slide_id)["links"])

    def test_case_slides_show_their_screenshots(self):
        for slide_id in CASE_REPOS:
            app = slide_id.removeprefix("cases-")
            images = self._slide(slide_id)["images"]
            with self.subTest(slide=slide_id):
                self.assertTrue(images, "no screenshots")
            for image in images:
                with self.subTest(slide=slide_id, src=image.get("src")):
                    self.assertTrue(image.get("src", "").startswith(f"img/cases/{app}/"))
                    self.assertIn("data-i18n-alt", image, "alt text comes from the tables")

    def test_screenshots_are_web_sized(self):
        images = sorted((DECK / "img").rglob("*.*"))
        self.assertTrue(images, "no images under deck/img")
        for path in images:
            with self.subTest(image=str(path.relative_to(DECK))):
                self.assertLessEqual(path.stat().st_size, MAX_IMAGE_BYTES)

    def test_case_stats_state_when_they_were_counted(self):
        for slide_id in CASES_WITH_STATS:
            with self.subTest(slide=slide_id):
                self.assertIn(f"{slide_id}.as-of", self._slide(slide_id)["i18n"])

    def test_checklister_shows_its_work_units(self):
        slide = self._slide("cases-checklister")
        chips = [i for i in slide["data_ids"] if i.startswith("wu-")]
        self.assertEqual(chips, CHECKLISTER_TRACK)

    def test_external_links_open_in_a_new_tab(self):
        external = [a for a in self.deck.anchors if a["href"].startswith("http")]
        self.assertTrue(external)
        for anchor in external:
            with self.subTest(href=anchor["href"]):
                self.assertEqual(anchor.get("target"), "_blank")
                self.assertIn("noopener", (anchor.get("rel") or "").split())

    def test_work_unit_track_persists_across_example(self):
        for slide_id in CURRENT_CHIP:
            slide = self._slide(slide_id)
            with self.subTest(slide=slide_id):
                self.assertIn("data-auto-animate", slide["attrs"])
                chips = [i for i in slide["data_ids"] if i.startswith("wu-")]
                inserted = EXAMPLE_SLIDES.index(slide_id) >= EXAMPLE_SLIDES.index(
                    "example-correction"
                )
                expected = [c for c in WU_TRACK if inserted or c != INSERTED_CHIP]
                self.assertEqual(chips, expected)
                for chip in chips:
                    self.assertIn("wu-chip", slide["classes"][chip])
                if INSERTED_CHIP in chips:
                    self.assertIn("is-inserted", slide["classes"][INSERTED_CHIP])

    def test_work_unit_chip_states(self):
        for slide_id, current in CURRENT_CHIP.items():
            slide = self._slide(slide_id)
            chips = [i for i in slide["data_ids"] if i.startswith("wu-")]
            if current is not None:
                done = chips[:chips.index(current)]
            elif slide_id == "example-debrief":
                done = chips
            else:
                done = []
            for chip in chips:
                classes = slide["classes"][chip]
                with self.subTest(slide=slide_id, chip=chip):
                    self.assertEqual("is-current" in classes, chip == current)
                    aria = slide["id_attrs"][chip].get("aria-current")
                    self.assertEqual(aria, "step" if chip == current else None)
                    self.assertEqual("is-done" in classes, chip in done)

    def test_scoping_slides_show_only_the_steps(self):
        for slide_id in SCOPING_STEP.keys() - CURRENT_CHIP.keys():
            slide = self._slide(slide_id)
            with self.subTest(slide=slide_id):
                self.assertIn("data-auto-animate", slide["attrs"])
                self.assertIn("story", slide["attrs"].get("class", "").split())
                self.assertEqual([i for i in slide["data_ids"] if i.startswith("wu-")], [])
                self.assertNotIn(DEBRIEF_STEP, slide["data_ids"])

    def test_leading_steps_precede_work_units(self):
        for slide_id in EXAMPLE_SLIDES[1:]:
            slide = self._slide(slide_id)
            steps = [i for i in slide["data_ids"] if i in LEADING_STEPS]
            current = SCOPING_STEP.get(slide_id)
            done = LEADING_STEPS[:LEADING_STEPS.index(current)] if current else LEADING_STEPS
            with self.subTest(slide=slide_id):
                self.assertEqual(steps, LEADING_STEPS)
                if WU_TRACK[0] in slide["data_ids"]:
                    self.assertLess(slide["data_ids"].index(LEADING_STEPS[-1]),
                                    slide["data_ids"].index(WU_TRACK[0]))
                for step in steps:
                    classes = slide["classes"][step]
                    self.assertIn("is-step", classes)
                    self.assertEqual("is-current" in classes, step == current)
                    aria = slide["id_attrs"][step].get("aria-current")
                    self.assertEqual(aria, "step" if step == current else None)
                    self.assertEqual("is-done" in classes, step in done)

    def test_plan_reveals_work_units_with_one_click(self):
        plan = self._slide("example-plan")
        indexes = set()
        for chip in WU_TRACK:
            if chip == INSERTED_CHIP:
                continue
            with self.subTest(chip=chip):
                self.assertIn("fragment", plan["classes"][chip])
                indexes.add(plan["id_attrs"][chip].get("data-fragment-index"))
        self.assertEqual(len(indexes), 1)
        self.assertIsNotNone(indexes.pop())

    def test_debrief_step_follows_work_units_on_last_slide(self):
        for slide_id in EXAMPLE_SLIDES[1:]:
            slide = self._slide(slide_id)
            with self.subTest(slide=slide_id):
                if slide_id != "example-debrief":
                    self.assertNotIn(DEBRIEF_STEP, slide["data_ids"])
                    continue
                self.assertEqual(slide["data_ids"].index(DEBRIEF_STEP),
                                 slide["data_ids"].index(WU_TRACK[-1]) + 1)
                self.assertLessEqual({"wu-chip", "is-step", "is-current"},
                                     slide["classes"][DEBRIEF_STEP])
                self.assertEqual(slide["id_attrs"][DEBRIEF_STEP].get("aria-current"), "step")

    def test_kill_switch_turns_on_in_last_work_unit(self):
        off, on = self._slide("example-wu3"), self._slide("example-wu4")
        self.assertIn("toggle", off["classes"]["toggle"])
        self.assertNotIn("is-on", off["classes"]["toggle"])
        self.assertIn("is-on", on["classes"]["toggle"])

    def test_lifecycle_flow_auto_animates_into_human_gates(self):
        steps = [f"flow-{step}" for step in LIFECYCLE_STEPS]
        gates = [f"human-{gate}" for gate in HUMAN_GATES]
        flow, human = self._slide("purpose-flow"), self._slide("purpose-human")
        for slide in (flow, human):
            self.assertIn("data-auto-animate", slide["attrs"])
        self.assertEqual([i for i in flow["data_ids"] if i.startswith("flow-")], steps)
        self.assertEqual([i for i in human["data_ids"] if i.startswith("flow-")], steps)
        self.assertEqual([i for i in flow["data_ids"] if i.startswith("human-")], [])
        self.assertEqual([i for i in human["data_ids"] if i.startswith("human-")], gates)

    def test_section_menu_links_every_section(self):
        html = (DECK / "index.html").read_text(encoding="utf-8")
        menu = re.search(r'<nav class="yab-menu".*?</nav>', html, re.DOTALL)
        self.assertIsNotNone(menu, "no section menu")
        menu = menu.group(0)
        self.assertEqual(re.findall(r'href="([^"]+)"', menu), [f"#/{t}" for t in TOC_TARGETS])
        self.assertEqual(
            re.findall(r'data-i18n="(toc\.[^"]+)"', menu), [f"toc.{t}" for t in TOC_TARGETS]
        )
        toggle = re.search(r'<button[^>]*class="yab-menu-toggle"[^>]*>', menu).group(0)
        self.assertIn('aria-expanded="false"', toggle)
        list_id = re.search(r'aria-controls="([^"]+)"', toggle).group(1)
        self.assertRegex(menu, rf'id="{list_id}"[^>]*hidden')

    def test_section_label_sits_beside_the_menu(self):
        html = (DECK / "index.html").read_text(encoding="utf-8")
        label = re.search(r'<p class="yab-section".*?</p>', html, re.DOTALL)
        self.assertIsNotNone(label, "no fixed section label")
        self.assertEqual(
            re.findall(r'data-section="([^"]+)" data-i18n="eyebrow\.\1"', label.group(0)),
            TOC_TARGETS,
        )
        for slide in self.deck.slides:
            with self.subTest(slide=slide["id"]):
                eyebrows = [k for k in slide["i18n"] if k.startswith("eyebrow.")]
                self.assertEqual(eyebrows, [], "the section label is no longer on the slides")

    def test_phones_held_upright_are_asked_to_turn(self):
        html = (DECK / "index.html").read_text(encoding="utf-8")
        hint = re.search(r'<div class="yab-rotate".*?</div>', html, re.DOTALL)
        self.assertIsNotNone(hint, "no rotate hint")
        self.assertIn('data-i18n="controls.rotate"', hint.group(0))
        self.assertRegex(hint.group(0), r'<button[^>]*data-i18n="controls\.rotate-dismiss"')
        css = (DECK / "css" / "theme.css").read_text(encoding="utf-8")
        self.assertRegex(css, r"@media \(orientation: portrait\) and \(max-width: \d+px\)")

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


class PagesWorkflowTest(unittest.TestCase):
    """The deck, and only the deck, is published to GitHub Pages from main."""

    @classmethod
    def setUpClass(cls):
        cls.text = PAGES_WORKFLOW.read_text(encoding="utf-8")

    def test_runs_on_deck_changes_to_main(self):
        self.assertRegex(self.text, r"branches:\s*\[\s*main\s*\]")
        self.assertIn('"deck/**"', self.text)
        self.assertIn("workflow_dispatch", self.text)

    def test_publishes_only_the_deck_folder(self):
        self.assertIn("actions/upload-pages-artifact@v3", self.text)
        self.assertRegex(self.text, r"\n\s+path: deck\n")
        self.assertIn("actions/deploy-pages@v4", self.text)

    def test_has_pages_permissions(self):
        self.assertIn("pages: write", self.text)
        self.assertIn("id-token: write", self.text)


if __name__ == "__main__":
    unittest.main()
