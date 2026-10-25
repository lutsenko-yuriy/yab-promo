#!/usr/bin/env python3
"""Write deck/index.html from the slide sources in deck/src/.

The deck is published as committed files, so index.html stays in the repo and needs no
build to run online or from a local clone. Edit deck/src/ and run this script; a test
fails when index.html is out of date with its sources.

deck/src/shell.html is the page; three rules make up the rest:

- `<!-- include <path> -->` alone on a line is replaced by that file (relative to
  deck/src/), each line indented to the directive's indent.
- `<!-- story <slide id> key=value ... -->` ... `<!-- /story -->` is one slide of the
  example: the block holds what the slide says, and the build puts it into the story
  skeleton with the branch diagram, step chips and switch panel from deck/src/parts/.
  `step=<step>` makes a scoping slide; `open=<unit>` a work-unit slide, with the units
  before it merged and the ones after it planned. `leaving` fades the step chips out,
  `delay=<seconds>` delays the lanes, and `last-click=<index>` makes that click merge the
  open unit, name the version and turn the switch on.
- In the parts, `{{name}}` is filled in. A placeholder alone on a line takes the line's
  indent, and its line is left out when it is empty.

Anything unknown, missing or left open stops the build with the file and line.

Usage:
    python3 tools/build_deck.py           # write deck/index.html
    python3 tools/build_deck.py --check   # exit 1 if deck/index.html is out of date
"""

import re
import sys
import textwrap
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "deck" / "src"
OUT = ROOT / "deck" / "index.html"

UNITS = ("wu-0", "wu-0c", "wu-1", "wu-2", "wu-3", "wu-4")
STEPS = ("brief", "analyze", "plan")
STORY_ARGS = ("step", "open", "leaving", "delay", "last-click")
# The parts the story block builds a slide from; nothing includes them by name.
PARTS = ("parts/story.html", "parts/track.html", "parts/branches.html",
         "parts/story-body.html", "parts/switch-panel.html")

INCLUDE = re.compile(r"^( *)<!-- include (\S+) -->[ \t]*$")
STORY = re.compile(r"^( *)<!-- story (\S+)((?: \S+)*) -->[ \t]*$")
STORY_END = re.compile(r"^ *<!-- /story -->[ \t]*$")
# Anything that looks like a directive but isn't one would otherwise pass as a comment.
DIRECTIVE_LIKE = re.compile(r"<!--\s*/?\s*(include|story)\b")
NUMBER = re.compile(r"\d+(\.\d+)?")
PLACEHOLDER = re.compile(r"\{\{([a-z0-9-]+)\}\}")

DONE = '<span class="sr-only" data-i18n="wu.done"></span>'
CURRENT = ' aria-current="step"'


class BuildError(Exception):
    """A source the build can't turn into the deck, named by file and line."""


def _indent(text: str, prefix: str) -> List[str]:
    return [prefix + line if line else "" for line in text.splitlines()]


def fill(text: str, values: Dict[str, str], where: str) -> str:
    """Fills the {{placeholders}} in text; where names the file for errors."""
    out = []
    for number, line in enumerate(text.splitlines(), 1):
        def value(name):
            if name not in values:
                raise BuildError(f"{where}:{number}: unknown placeholder {{{{{name}}}}}")
            return values[name]

        alone = PLACEHOLDER.fullmatch(line.strip())
        if alone:
            out += _indent(value(alone.group(1)), line[:len(line) - len(line.lstrip())])
        else:
            out.append(PLACEHOLDER.sub(lambda match: value(match.group(1)), line))
    return "".join(line + "\n" for line in out)


def lane_states(open_unit: str) -> Dict[str, str]:
    """Each unit's lane while open_unit is being worked on."""
    if open_unit not in UNITS:
        raise BuildError(f"unknown unit {open_unit}")
    current = UNITS.index(open_unit)
    return {unit: "is-merged" if i < current else "is-open" if i == current else "is-planned"
            for i, unit in enumerate(UNITS)}


def step_states(step: str) -> Dict[str, str]:
    """Each scoping step's chip while step is under way."""
    if step not in STEPS:
        raise BuildError(f"unknown step {step}")
    current = STEPS.index(step)
    return {name: "is-done" if i < current else "is-current" if i == current else ""
            for i, name in enumerate(STEPS)}


def _story_args(tokens: List[str], where: str) -> Dict[str, str]:
    args = {}
    for token in tokens:
        key, equals, value = token.partition("=")
        if key not in STORY_ARGS:
            raise BuildError(f"{where}: unknown story argument {key}")
        if key == "leaving" and equals:
            raise BuildError(f"{where}: leaving takes no value")
        if key != "leaving" and not value:
            raise BuildError(f"{where}: {key}= needs a value")
        args[key] = value
    if ("step" in args) == ("open" in args):
        raise BuildError(f"{where}: a story needs either step= or open=")
    if args.get("step", STEPS[0]) not in STEPS:
        raise BuildError(f"{where}: unknown step {args['step']}")
    if args.get("open", UNITS[0]) not in UNITS:
        raise BuildError(f"{where}: unknown unit {args['open']}")
    if not NUMBER.fullmatch(args.get("delay", "0")):
        raise BuildError(f"{where}: delay= takes seconds, not {args['delay']}")
    if not args.get("last-click", "0").isdigit():
        raise BuildError(f"{where}: last-click= takes a fragment index, not {args['last-click']}")
    lane_args = [key for key in ("leaving", "delay", "last-click") if key in args]
    if "step" in args and lane_args:
        raise BuildError(f"{where}: {', '.join(lane_args)} needs open=, not step=")
    return args


def _story(src: Path, slide_id: str, args: Dict[str, str], content: str) -> str:
    values = {"id": slide_id, "content": content}

    leaving = "leaving" in args
    if "step" in args:
        steps = step_states(args["step"])
    else:
        steps = {name: "is-done" for name in STEPS}
    values["track-class"] = " is-leaving" if leaving else ""
    values["track-hidden"] = ' aria-hidden="true"' if leaving else ""
    for name, state in steps.items():
        values[f"state-{name}"] = f" {state}" if state else ""
        values[f"current-{name}"] = CURRENT if state == "is-current" else ""
        values[f"done-{name}"] = DONE if state == "is-done" else ""

    if "open" in args:
        for unit, state in lane_states(args["open"]).items():
            values[f"lane-{unit}"] = state
            values[f"current-{unit}"] = CURRENT if state == "is-open" else ""
            values[f"done-{unit}"] = DONE if state == "is-merged" else ""
    delay = args.get("delay")
    values["delay"] = f' data-auto-animate-delay="{delay}"' if delay else ""

    click = args.get("last-click")
    values["with-debrief"] = " with-debrief" if click else ""
    values["debrief-hidden"] = "" if click else ' aria-hidden="true"'
    values["click-class"] = " fragment custom" if click else ""
    values["click-index"] = f' data-fragment-index="{click}"' if click else ""
    if click:
        values[f"done-{args['open']}"] = (f'<span class="sr-only fragment" '
                                         f'data-fragment-index="{click}" '
                                         f'data-i18n="wu.done"></span>')

    def part(name):
        path = f"parts/{name}.html"
        return fill(_expand(src, path, [path], in_part=True), values, path)

    scoping = "step" in args
    values["scoping"] = " is-scoping" if scoping else ""
    values["track"] = part("track") if scoping or leaving else ""
    values["lanes"] = "" if scoping else part("branches")
    values["body"] = content if scoping else part("story-body")
    return part("story")


def _expand(src: Path, name: str, stack: List[str], in_part: bool = False) -> str:
    """Returns the file with its includes and story blocks built.

    stack holds the files being expanded, to catch an include cycle. Placeholders are
    only filled in the parts, so anywhere else they stop the build.
    """
    lines = (src / name).read_text(encoding="utf-8").splitlines()

    def no_placeholder(text, where):
        if not in_part and PLACEHOLDER.search(text):
            raise BuildError(f"{where}: {{{{placeholders}}}} are only filled in parts/")
    out = []
    number = 0
    while number < len(lines):
        line = lines[number]
        number += 1
        where = f"{name}:{number}"
        include = INCLUDE.match(line)
        story = STORY.match(line)
        if include:
            target = include.group(2)
            if not (src / target).is_file():
                raise BuildError(f"{where}: no such include {target}")
            if target in stack:
                raise BuildError(f"{where}: {target} ends up including itself")
            out += _indent(_expand(src, target, stack + [target], in_part), include.group(1))
        elif story:
            args = _story_args(story.group(3).split(), where)
            body = []
            while True:
                if number == len(lines):
                    raise BuildError(f"{where}: story {story.group(2)} is never closed")
                inner = lines[number]
                number += 1
                if STORY.match(inner):
                    raise BuildError(f"{name}:{number}: a story can't hold another story")
                if STORY_END.match(inner):
                    break
                if DIRECTIVE_LIKE.search(inner):
                    raise BuildError(f"{name}:{number}: not a directive: {inner.strip()}")
                no_placeholder(inner, f"{name}:{number}")
                body.append(inner)
            content = textwrap.dedent("\n".join(body)).strip("\n")
            out += _indent(_story(src, story.group(2), args, content), story.group(1))
        elif STORY_END.match(line):
            raise BuildError(f"{where}: /story without a story")
        elif DIRECTIVE_LIKE.search(line):
            raise BuildError(f"{where}: not a directive: {line.strip()}")
        else:
            no_placeholder(line, where)
            out.append(line)
    return "".join(line + "\n" for line in out)


def render(src: Path = SRC) -> str:
    """Returns the deck page built from src/shell.html."""
    if not (src / "shell.html").is_file():
        raise BuildError(f"shell.html: not found in {src}")
    return _expand(src, "shell.html", ["shell.html"])


def main(argv: List[str]) -> int:
    if argv not in ([], ["--check"]):
        print("usage: python3 tools/build_deck.py [--check]", file=sys.stderr)
        return 2
    try:
        page = render()
    except BuildError as error:
        print(f"build_deck: {error}", file=sys.stderr)
        return 1
    if "--check" in argv:
        if not OUT.is_file() or OUT.read_text(encoding="utf-8") != page:
            print("build_deck: deck/index.html is out of date; run python3 tools/build_deck.py",
                  file=sys.stderr)
            return 1
        return 0
    OUT.write_text(page, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
