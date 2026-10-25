# YAB Promo

Promo materials for Yuriy's agentic boyz (YAB) framework: **[lutsenko-yuriy/yuriys-agentic-boyz](https://github.com/lutsenko-yuriy/yuriys-agentic-boyz)**.

## Running it

Promo pages are static HTML/CSS: open them in a browser, no build needed to view them.

The presentation deck is live at https://lutsenko-yuriy.github.io/yab-promo/. To run it from a clone, build the page once (Python 3, nothing to install), then open `deck/index.html` straight from the file (also offline):

```bash
python3 tools/build_deck.py
```

Add `?lang=de` for German, or use the EN/DE switch.

To change the slides, edit `deck/src/` and run the build again. `deck/index.html` is generated and gitignored; the Pages workflow builds it before publishing.

## Testing

```bash
python3 -m unittest discover -s scripts/onboard/tests -t .
python3 -m unittest discover -s scripts/skill_router -t scripts
python3 -m unittest discover -s scripts/checkup/tests -t scripts
python3 -m unittest discover -s scripts/notes/tests -t .
python3 -m unittest discover -s tests -t .
```

## Architecture

Content (Markdown and static pages) sits beside the YAB tooling copied from the template. See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Working on this project with Claude Code

- Start Claude Code from the repo root: `cd yab-promo && claude`. Running `cd` inside an
  existing session isn't enough, because project settings, skills and hooks only load at launch.
- Run `/onboard` once per clone, in a session started there; a gate blocks most work until then.
- Start each session with `/summarize`.
- Issues: https://github.com/lutsenko-yuriy/yab-promo/issues
