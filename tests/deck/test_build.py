"""Tests for tools/build_deck.py, which writes deck/index.html from deck/src/."""

import importlib.util
import re
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "deck" / "src"

_spec = importlib.util.spec_from_file_location("build_deck", ROOT / "tools" / "build_deck.py")
build_deck = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build_deck)


def _sources(files):
    """Writes {relative path: text} into a temporary source folder and returns its path."""
    folder = tempfile.TemporaryDirectory()
    root = Path(folder.name)
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(text).lstrip("\n"), encoding="utf-8")
    return folder


class EngineTest(unittest.TestCase):
    def _render(self, files):
        folder = _sources(files)
        self.addCleanup(folder.cleanup)
        return build_deck.render(Path(folder.name))

    def test_include_indents_to_the_directive_and_keeps_blank_lines_empty(self):
        out = self._render({
            "shell.html": """
                <body>
                  <!-- include part.html -->
                </body>
            """,
            "part.html": """
                <p>one</p>

                <p>two</p>
            """,
        })
        self.assertEqual(out, "<body>\n  <p>one</p>\n\n  <p>two</p>\n</body>\n")

    def test_includes_nest(self):
        out = self._render({
            "shell.html": "<!-- include a.html -->\n",
            "a.html": "<div>\n  <!-- include b.html -->\n</div>\n",
            "b.html": "<p>b</p>\n",
        })
        self.assertEqual(out, "<div>\n  <p>b</p>\n</div>\n")

    def test_other_comments_pass_through(self):
        out = self._render({"shell.html": "  <!-- The section being shown. -->\n<p></p>\n"})
        self.assertEqual(out, "  <!-- The section being shown. -->\n<p></p>\n")

    def test_missing_include_names_file_and_line(self):
        with self.assertRaisesRegex(build_deck.BuildError, r"shell\.html:2: .*nope\.html"):
            self._render({"shell.html": "<p></p>\n<!-- include nope.html -->\n"})

    def test_inline_placeholder_substitutes(self):
        self.assertEqual(build_deck.fill('<p class="a{{x}}">\n', {"x": " b"}, "t"),
                         '<p class="a b">\n')

    def test_placeholder_alone_takes_its_lines_indent(self):
        self.assertEqual(build_deck.fill("<ul>\n  {{items}}\n</ul>\n",
                                         {"items": "<li>1</li>\n\n<li>2</li>"}, "t"),
                         "<ul>\n  <li>1</li>\n\n  <li>2</li>\n</ul>\n")

    def test_empty_placeholder_alone_drops_its_line(self):
        self.assertEqual(build_deck.fill("<div>\n  {{track}}\n</div>\n", {"track": ""}, "t"),
                         "<div>\n</div>\n")

    def test_unknown_placeholder_names_file_and_line(self):
        with self.assertRaisesRegex(build_deck.BuildError, r"t:2: .*nope"):
            build_deck.fill("<p>\n{{nope}}\n", {}, "t")

    def test_unclosed_story_names_file_and_line(self):
        with self.assertRaisesRegex(build_deck.BuildError, r"shell\.html:1: .*story"):
            self._render({"shell.html": "<!-- story s open=wu-1 -->\n<h2></h2>\n"})

    def test_nested_story_is_an_error(self):
        with self.assertRaisesRegex(build_deck.BuildError, r"shell\.html:2: .*story"):
            self._render({"shell.html": "<!-- story a open=wu-1 -->\n<!-- story b open=wu-2 -->\n"
                                        "<!-- /story -->\n<!-- /story -->\n"})

    def test_unknown_story_argument_is_an_error(self):
        with self.assertRaisesRegex(build_deck.BuildError, r"shell\.html:1: .*colour"):
            self._render({"shell.html": "<!-- story s colour=red -->\n<!-- /story -->\n"})

    def test_story_needs_a_step_or_an_open_unit(self):
        with self.assertRaisesRegex(build_deck.BuildError, r"shell\.html:1: "):
            self._render({"shell.html": "<!-- story s leaving -->\n<!-- /story -->\n"})

    def test_unit_arguments_on_a_scoping_slide_are_an_error(self):
        # leaving, delay and last-click act on the lanes, which a scoping slide doesn't have.
        for arg in ("leaving", "delay=0.7", "last-click=4"):
            with self.subTest(arg=arg):
                with self.assertRaisesRegex(build_deck.BuildError, r"shell\.html:1: .*step="):
                    self._render({"shell.html": f"<!-- story s step=brief {arg} -->\n"
                                                "<!-- /story -->\n"})

    def test_bad_story_values_name_file_and_line(self):
        for args, message in (("open=", "needs a value"), ("open=wu-9", "unknown unit"),
                              ("step=review", "unknown step"), ("delay=", "needs a value"),
                              ("delay=soon", "seconds"), ("last-click=", "needs a value"),
                              ("last-click=x", "fragment index"),
                              ("last-click=\u00b2", "fragment index"),
                              ("leaving=yes", "no value"), ("delay=1 delay=2", "twice")):
            with self.subTest(args=args):
                with self.assertRaisesRegex(build_deck.BuildError,
                                            rf"shell\.html:1: .*{message}"):
                    self._render({"shell.html": f"<!-- story s {args} -->\n<!-- /story -->\n"
                                  if args.startswith(("open", "step")) else
                                  f"<!-- story s open=wu-1 {args} -->\n<!-- /story -->\n"})

    def test_trailing_whitespace_after_a_directive_is_fine(self):
        out = self._render({"shell.html": "<!-- include a.html --> \t\n", "a.html": "<p></p>\n"})
        self.assertEqual(out, "<p></p>\n")

    def test_misspelled_directive_is_an_error_not_a_comment(self):
        for line in ("<!--include a.html-->", "<!-- include  a.html -->",
                     "<!-- story s open=wu-1-->", "<!-- /story-->"):
            with self.subTest(line=line):
                with self.assertRaisesRegex(build_deck.BuildError,
                                            r"shell\.html:1: not a directive"):
                    self._render({"shell.html": line + "\n", "a.html": "<p></p>\n"})

    def test_include_cycle_is_an_error(self):
        with self.assertRaisesRegex(build_deck.BuildError, r"a\.html:1: .*a\.html"):
            self._render({"shell.html": "<!-- include a.html -->\n",
                          "a.html": "<!-- include a.html -->\n"})

    def test_missing_shell_is_an_error(self):
        with self.assertRaisesRegex(build_deck.BuildError, r"shell\.html"):
            self._render({"other.html": "<p></p>\n"})

    def test_placeholders_outside_the_parts_are_an_error(self):
        # Only the parts are filled in; {{name}} anywhere else would reach the page as is.
        for files in ({"shell.html": "<p>\n<h2>{{title}}</h2>\n"},
                      {"shell.html": "<p>\n<!-- include a.html -->\n", "a.html": "{{x}}\n"}):
            with self.subTest(files=files):
                with self.assertRaisesRegex(build_deck.BuildError, r"\.html:\d+: .*\{\{"):
                    self._render(files)


class CommandLineTest(unittest.TestCase):
    def test_options_are_refused(self):
        # --check compared against a committed page; the page isn't committed any more.
        for argv in (["--chek"], ["--check"]):
            with self.subTest(argv=argv):
                self.assertEqual(build_deck.main(argv), 2)


class RulesTest(unittest.TestCase):
    def test_units_before_the_open_one_are_merged_and_after_it_planned(self):
        self.assertEqual(build_deck.lane_states("wu-2"), {
            "wu-0": "is-merged", "wu-0c": "is-merged", "wu-1": "is-merged",
            "wu-2": "is-open", "wu-3": "is-planned", "wu-4": "is-planned",
        })

    def test_steps_before_the_current_one_are_done(self):
        self.assertEqual(build_deck.step_states("analyze"),
                         {"brief": "is-done", "analyze": "is-current", "plan": ""})

    def test_unknown_unit_is_an_error(self):
        with self.assertRaises(build_deck.BuildError):
            build_deck.lane_states("wu-9")


class PublishingTest(unittest.TestCase):
    """deck/index.html is built, not committed (the Pages workflow builds it)."""

    def test_index_is_ignored_and_not_committed(self):
        def git(*args):
            return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)

        self.assertEqual(git("check-ignore", "-q", "deck/index.html").returncode, 0,
                         "deck/index.html is not in .gitignore")
        self.assertEqual(git("ls-files", "deck/index.html").stdout, "",
                         "deck/index.html is still committed")


class DeckSourcesTest(unittest.TestCase):
    def test_page_says_it_is_generated(self):
        head = build_deck.render(SRC).splitlines()[1]
        self.assertIn("Generated by tools/build_deck.py", head)

    def test_no_source_is_longer_than_150_lines(self):
        for path in sorted(SRC.rglob("*.html")):
            with self.subTest(path=path.relative_to(SRC)):
                self.assertLessEqual(len(path.read_text(encoding="utf-8").splitlines()), 150)

    def test_the_diagram_and_switch_panel_are_written_once(self):
        example = (SRC / "03-example.html").read_text(encoding="utf-8")
        for copy in ("branch-art", 'class="lane', "switch-panel", "wu-track"):
            with self.subTest(copy=copy):
                self.assertNotIn(copy, example)

    def test_every_source_is_used(self):
        used = set()
        pending = ["shell.html", *build_deck.PARTS]
        while pending:
            name = pending.pop()
            used.add(name)
            text = (SRC / name).read_text(encoding="utf-8")
            pending += [n for n in re.findall(r"<!-- include (\S+) -->", text) if n not in used]
        every = {p.relative_to(SRC).as_posix() for p in SRC.rglob("*.html")}
        self.assertEqual(sorted(every - used), [])


if __name__ == "__main__":
    unittest.main()
