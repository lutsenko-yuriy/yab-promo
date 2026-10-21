# YAB Promo

Promo materials for Yuriy's agentic boyz (YAB) framework: **[lutsenko-yuriy/yuriys-agentic-boyz](https://github.com/lutsenko-yuriy/yuriys-agentic-boyz)**.

## Running it

Promo pages are static HTML/CSS: open them in a browser. No build step.

## Testing

```bash
python3 -m unittest discover -s scripts/onboard/tests -t .
python3 -m unittest discover -s scripts/skill_router/tests -t scripts
```

## Architecture

Content (Markdown and static pages) sits beside the YAB tooling copied from the template. See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Working on this project with Claude Code

- Launch Claude Code from the repo root.
- Run `/onboard` once per clone; a gate blocks most work until then.
- Start each session with `/summarize`.
- Issues: https://github.com/lutsenko-yuriy/yab-promo/issues
