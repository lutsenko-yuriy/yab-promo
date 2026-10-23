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

# Slides of the example section (HAB-202), in order.
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
# The workflow steps that scope the ticket. Brief, analytics and plan carry them as a track;
# Auto-Animate keeps it in place and recolours it, and WU0 fades it out.
LEADING_STEPS = ["step-brief", "step-analyze", "step-plan"]
# The step being worked on while the ticket is scoped. Steps before the current one are
# done, those after it not yet started.
SCOPING_STEP = {
    "example-brief": "step-brief",
    "example-analyze": "step-analyze",
    "example-plan": "step-plan",
}

# Loosely trunk-based: each work unit gets its own branch and its own pull request into main.
# WU0+ was inserted after the plan, to correct WU0.
WORK_UNITS = ["wu-0", "wu-0c", "wu-1", "wu-2", "wu-3", "wu-4"]
INSERTED_UNIT = "wu-0c"
HABIT_LOOP_PULLS = "https://github.com/lutsenko-yuriy/habit-loop/pull/"
PULL_REQUESTS = {unit: f"{HABIT_LOOP_PULLS}{number}"
                 for unit, number in zip(WORK_UNITS, range(336, 342))}
# The branch open on each slide of the branch diagram; branches before it are merged, those
# after it only planned. None: the plan, where every branch is still planned. WU4 stays open
# through the review and the debrief, whose last click merges it.
OPEN_BRANCH = {
    "example-plan": None,
    "example-wu0": "wu-0",
    "example-correction": "wu-0c",
    "example-wu1": "wu-1",
    "example-wu2": "wu-2",
    "example-wu3": "wu-3",
    "example-wu4": "wu-4",
    "example-review": "wu-4",
    "example-debrief": "wu-4",
}
DIAGRAM_SLIDES = list(OPEN_BRANCH)
DEVELOPMENT_SLIDES = DIAGRAM_SLIDES[1:]
# Every part of the diagram, in markup order. Auto-Animate fades in anything unmatched, so
# each part needs a data-id to stay put from slide to slide.
DIAGRAM_IDS = ["branches", "main-line", "main-label"] + [
    f"{part}-{unit}" for unit in WORK_UNITS
    for part in ("lane", "branch", "merge", "tip", "label")
]
BRANCH_STATES = ("is-planned", "is-open", "is-merged")

# Slides that carry the switch panel (the pact chaining feature switch): from the first work
# unit through the debrief. The switch stays off until the debrief's last click turns it on.
SWITCH_SLIDES = EXAMPLE_SLIDES[EXAMPLE_SLIDES.index("example-wu0"):]
# Every part of the panel, the switch's labels included, has a data-id: Auto-Animate fades
# in anything unmatched, so a label without one would blink on every slide.
SWITCH_PANEL = ["switch-panel", "toggle", "toggle-knob", "toggle-off", "toggle-on",
                "switch-name", "switch-purpose"]
SWITCH_KEYS = {"switch.off", "switch.on", "switch.name", "switch.purpose"}
SWITCH_NAME = "pact chaining feature flag"

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
VALUES_SLIDES = ["values", "values-safe", "values-understanding", "values-human"]

PAGES_WORKFLOW = REPO / ".github" / "workflows" / "pages.yml"

# A German value may equal its English one only for these keys (proper nouns and the like).
SAME_IN_BOTH = {
    "toc.title",
    "toc.subtitle",
    "switch.name",
    "controls.lang-en",
    "controls.lang-de",
    "purpose-what.tickets",
    "flow.ticket",
    "flow.plan",
    "flow.release",
}

ALLOWED_INLINE_TAGS = {"strong", "em", "br", "span"}
VOID_TAGS = {"br", "img", "input", "link", "meta", "hr", "source", "wbr"}

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
        #   "id_attrs": {data_id: dict}, "links": [str], "i18n": [str], "images": [dict],
        #   "i18n_attrs": {key: dict}, "fragments": [dict]}]
        self.slides = []
        self.nested_sections = 0
        self.i18n_keys = []
        self.code_tags = 0
        self.asset_refs = []  # (tag, url)
        self.anchors = []  # attrs of every <a href>
        self._section_depth = 0
        self._open = []  # (tag, attrs) of the elements open inside the current slide

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
                    "i18n_attrs": {},
                    "fragments": [],
                    "tags": {},
                    "fragment_of": {},
                    "unnamed_in_diagram": [],
                }
            )
            self._open = []
        slide = self.slides[-1] if self._section_depth else None
        if slide is not None and tag != "section":
            self._track(slide, tag, attrs)
        for name in ("data-i18n", "data-i18n-aria", "data-i18n-alt"):
            if name in attrs:
                self.i18n_keys.append(attrs[name])
                if slide is not None:
                    slide["i18n"].append(attrs[name])
                    slide["i18n_attrs"][attrs[name]] = attrs
        if slide is not None and "fragment" in (attrs.get("class") or "").split():
            slide["fragments"].append(attrs)
        if slide is not None and "data-id" in attrs:
            slide["tags"][attrs["data-id"]] = tag
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

    def _track(self, slide, tag, attrs):
        """Records what an element sits inside: the nearest fragment and the diagram."""
        ancestors = self._open + [(tag, attrs)]
        fragment = next((a for _, a in reversed(ancestors)
                         if "fragment" in (a.get("class") or "").split()), None)
        if fragment is not None and "data-i18n" in attrs:
            slide["fragment_of"][attrs["data-i18n"]] = fragment.get("data-fragment-index")
        in_diagram = any("branches" in (a.get("class") or "").split() for _, a in self._open)
        in_link = any(t == "a" for t, _ in self._open)
        if in_diagram and not in_link and "data-id" not in attrs:
            slide["unnamed_in_diagram"].append((tag, attrs.get("class")))
        if tag not in VOID_TAGS:
            self._open.append((tag, attrs))

    def handle_endtag(self, tag):
        if tag == "section":
            self._section_depth -= 1
        elif self._open and self._open[-1][0] == tag:
            self._open.pop()


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

    def test_step_chips_lead_the_scoping_slides(self):
        for slide_id, current in SCOPING_STEP.items():
            slide = self._slide(slide_id)
            steps = [i for i in slide["data_ids"] if i.startswith("step-")]
            done = LEADING_STEPS[:LEADING_STEPS.index(current)]
            with self.subTest(slide=slide_id):
                self.assertIn("data-auto-animate", slide["attrs"])
                self.assertIn("story", slide["attrs"].get("class", "").split())
                self.assertEqual(steps, LEADING_STEPS)
                self.assertEqual([i for i in slide["data_ids"] if i.startswith("wu-")], [])
                self.assertNotIn("is-leaving", slide["classes"]["track"])
                for step in steps:
                    classes = slide["classes"][step]
                    self.assertIn("is-step", classes)
                    self.assertEqual("is-current" in classes, step == current)
                    aria = slide["id_attrs"][step].get("aria-current")
                    self.assertEqual(aria, "step" if step == current else None)
                    self.assertEqual("is-done" in classes, step in done)

    def test_step_chips_fade_out_on_wu0(self):
        wu0 = self._slide("example-wu0")
        self.assertLessEqual({"wu-track", "is-leaving"}, wu0["classes"]["track"])
        self.assertEqual(wu0["id_attrs"]["track"].get("aria-hidden"), "true")
        self.assertEqual([i for i in wu0["data_ids"] if i.startswith("step-")], LEADING_STEPS)
        for slide_id in DEVELOPMENT_SLIDES[1:]:
            slide = self._slide(slide_id)
            with self.subTest(slide=slide_id):
                self.assertNotIn("track", slide["data_ids"])
                self.assertEqual([i for i in slide["data_ids"] if i.startswith("step-")], [])

    def test_branch_diagram_persists_from_plan_to_debrief(self):
        plan = self._slide("example-plan")
        for slide in self.deck.slides:
            parts = [i for i in slide["data_ids"] if i in DIAGRAM_IDS]
            with self.subTest(slide=slide["id"]):
                if slide["id"] not in DIAGRAM_SLIDES:
                    self.assertEqual(parts, [])
                    continue
                self.assertIn("data-auto-animate", slide["attrs"])
                self.assertIn("story", slide["attrs"].get("class", "").split())
                self.assertEqual(parts, DIAGRAM_IDS)
                self.assertEqual({i: slide["tags"][i] for i in parts},
                                 {i: plan["tags"][i] for i in parts},
                                 "Auto-Animate only matches elements with the same tag")
                for unit in WORK_UNITS:
                    self.assertIn("lane", slide["classes"][f"lane-{unit}"])
                    self.assertEqual(slide["tags"][f"label-{unit}"], "a")
                    self.assertEqual("is-inserted" in slide["classes"][f"lane-{unit}"],
                                     unit == INSERTED_UNIT)

    def test_every_diagram_part_has_a_data_id(self):
        for slide_id in DIAGRAM_SLIDES:
            with self.subTest(slide=slide_id):
                self.assertEqual(self._slide(slide_id)["unnamed_in_diagram"], [])

    def test_branch_states(self):
        for slide_id, current in OPEN_BRANCH.items():
            slide = self._slide(slide_id)
            merged = WORK_UNITS[:WORK_UNITS.index(current)] if current else []
            for unit in WORK_UNITS:
                expected = ("is-open" if unit == current
                            else "is-merged" if unit in merged else "is-planned")
                states = slide["classes"][f"lane-{unit}"] & set(BRANCH_STATES)
                with self.subTest(slide=slide_id, unit=unit):
                    self.assertEqual(states, {expected})
                    aria = slide["id_attrs"][f"label-{unit}"].get("aria-current")
                    self.assertEqual(aria, "step" if unit == current else None)

    def test_branch_labels_link_their_pull_requests(self):
        plan = self._slide("example-plan")
        for unit in WORK_UNITS:
            with self.subTest(slide="example-plan", unit=unit):
                self.assertNotIn("href", plan["id_attrs"][f"label-{unit}"],
                                 "no pull request exists yet when the plan is made")
        for slide_id in DEVELOPMENT_SLIDES:
            for unit in WORK_UNITS:
                label = self._slide(slide_id)["id_attrs"][f"label-{unit}"]
                with self.subTest(slide=slide_id, unit=unit):
                    self.assertEqual(label.get("href"), PULL_REQUESTS[unit])
                    self.assertEqual(label.get("target"), "_blank")
                    self.assertIn("noopener", (label.get("rel") or "").split())

    def test_plan_states_the_branching_rule(self):
        plan = self._slide("example-plan")
        self.assertNotIn("fragment", self._key_classes(plan, "example-plan.lead"))
        principles = ["example-plan.small", "example-plan.switch"]
        for key in principles:
            with self.subTest(key=key):
                self.assertIn("fragment", self._key_classes(plan, key))
        keys = plan["i18n"]
        self.assertEqual(keys[keys.index("example-plan.lead") + 1:][:2], principles,
                         "one click per principle, after the lead")
        en = _load_table("en")
        self.assertEqual(en["example-plan.lead"],
                         "Loosely trunk-based: one branch per unit, each merged into main "
                         "through its own pull request.")
        self.assertEqual(en["example-plan.small"],
                         "Each unit is small enough to review in one sitting.")
        self.assertEqual(en["example-plan.switch"],
                         "Unfinished parts stay behind a switch until the last unit ships.")

    def test_debrief_reveals_three_columns_then_numbers(self):
        debrief = self._slide("example-debrief")
        order = {"example-debrief.noted": "0", "example-debrief.learned": "1",
                 "example-debrief.changed": "2", "example-debrief.units": "3"}
        for key, index in order.items():
            with self.subTest(key=key):
                self.assertEqual(debrief["fragment_of"].get(key), index)
        for column in ("noted", "learned", "changed"):
            items = [k for k in debrief["i18n"] if k.startswith(f"example-debrief.{column}-")]
            with self.subTest(column=column):
                self.assertEqual(len(items), 2)
                for item in items:
                    self.assertEqual(debrief["fragment_of"].get(item), order[
                        f"example-debrief.{column}"], "an item shows with its column")

    def test_limits_tools_names_branching(self):
        slide = self._slide("limits-tools")
        keys = slide["i18n"]
        self.assertEqual(keys[keys.index("limits-tools.pm") + 1], "limits-tools.branching")
        self.assertIn("fragment", self._key_classes(slide, "limits-tools.branching"))
        en = _load_table("en")["limits-tools.branching"]
        self.assertIn("<strong>Branching</strong>", en)
        self.assertIn("trunk-based", en)
        self.assertIn("<strong>Branching</strong>", _load_table("de")["limits-tools.branching"])

    def _key_classes(self, slide, key):
        return set((slide["i18n_attrs"][key].get("class") or "").split())

    def test_contents_title_puts_the_name_on_its_own_line(self):
        toc = self._slide("toc")
        keys = toc["i18n"]
        self.assertEqual(keys[keys.index("toc.title") + 1], "toc.subtitle")
        self.assertIn("subtitle", self._key_classes(toc, "toc.subtitle"))
        for lang in LANGS:
            with self.subTest(lang=lang):
                self.assertEqual(_load_table(lang)["toc.title"], "YAB")
                self.assertEqual(_load_table(lang)["toc.subtitle"], "Yuriy's agentic boyz")

    def test_analyze_question_shows_under_the_title(self):
        analyze = self._slide("example-analyze")
        keys = analyze["i18n"]
        self.assertEqual(keys[keys.index("example-analyze.title") + 1],
                         "example-analyze.question")
        question = self._key_classes(analyze, "example-analyze.question")
        self.assertIn("subtitle", question)
        self.assertNotIn("fragment", question)
        for card in ("button", "links", "changes"):
            with self.subTest(card=card):
                self.assertIn("fragment",
                              self._key_classes(analyze, f"example-analyze.{card}"))
        for lang in LANGS:
            with self.subTest(lang=lang):
                self.assertNotIn(":", _load_table(lang)["example-analyze.question"])

    def test_switch_panel_from_wu0_to_debrief(self):
        for slide in self.deck.slides:
            with self.subTest(slide=slide["id"]):
                panel = [data_id for data_id in slide["data_ids"] if data_id in SWITCH_PANEL]
                if slide["id"] not in SWITCH_SLIDES:
                    self.assertEqual(panel, [])
                    self.assertFalse(SWITCH_KEYS & set(slide["i18n"]))
                    continue
                self.assertEqual(panel, SWITCH_PANEL)
                self.assertGreater(slide["data_ids"].index("switch-panel"),
                                   slide["data_ids"].index("label-wu-4"),
                                   "the panel sits below the branch diagram")
                self.assertLessEqual(SWITCH_KEYS, set(slide["i18n"]))

    def test_switch_is_off_until_the_debrief_has_shown(self):
        last_click = ["merge-wu-4", "toggle"]
        for slide_id in SWITCH_SLIDES[:-1]:
            for data_id in last_click:
                with self.subTest(slide=slide_id, part=data_id):
                    classes = self._slide(slide_id)["classes"][data_id]
                    self.assertNotIn("fragment", classes)
                    self.assertNotIn("is-on", classes)
        debrief = self._slide("example-debrief")
        for data_id in last_click:
            with self.subTest(part=data_id):
                self.assertLessEqual({"fragment", "custom"}, debrief["classes"][data_id])
        indexes = [int(fragment["data-fragment-index"]) for fragment in debrief["fragments"]
                   if "data-fragment-index" in fragment]
        self.assertEqual(len(indexes), len(debrief["fragments"]),
                         "every fragment on the debrief needs an index")
        last = max(indexes)
        on_last = sorted(fragment.get("data-id") for fragment in debrief["fragments"]
                         if int(fragment["data-fragment-index"]) == last)
        self.assertEqual(on_last, sorted(last_click),
                         "the last click merges WU4, then turns the switch on")

    def test_switch_is_named_as_a_feature_flag(self):
        for lang in LANGS:
            with self.subTest(lang=lang):
                self.assertEqual(_load_table(lang)["switch.name"], SWITCH_NAME)

    def test_wu4_ships_the_whole_feature(self):
        self.assertEqual(_load_table("en")["example-wu4.title"], "The pact chaining ships")

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
        # The contents slide first, then every section.
        self.assertEqual(
            re.findall(r'href="([^"]+)"', menu), ["#/toc"] + [f"#/{t}" for t in TOC_TARGETS]
        )
        self.assertEqual(
            re.findall(r'data-i18n="((?:toc|controls)\.[^"]+)"', menu),
            ["controls.contents"] + [f"toc.{t}" for t in TOC_TARGETS],
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
