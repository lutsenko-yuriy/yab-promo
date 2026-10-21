# Architecture

## Related docs

- `docs/TECH_STACK.md` — languages, frameworks, tooling
- `docs/CODE_STYLE.md` — style rules
- `docs/CONSTRAINTS.md` — standing constraints that shape design trade-offs

## Overview

Content repo: Markdown copy plus static HTML/CSS pages, with the YAB tooling scripts in Python

## Directory structure

```
.claude/            # Slash-command stubs and onboarding gate hooks
.github/workflows/  # CI: tooling and deck tests (tests.yml), deck publishing (pages.yml)
deck/               # The YAB presentation deck, published to GitHub Pages as is
  index.html        #   All slides; visible text referenced by data-i18n keys
  css/              #   Theme (Habit Loop palette) and deck components
  js/               #   Deck start-up, controls, language switching
  i18n/             #   String tables, one per language (en.js, de.js)
  vendor/           #   Third-party files copied in unchanged (reveal.js)
docs/               # Project docs, knowledge base, workflows
scripts/            # YAB tooling (onboard, skill_router, notes, checkup) in Python
skills/             # YAB skills: configure, design, build, verify, manage
styles/             # Communication styles
tests/deck/         # Structural tests for the deck (Python standard library)
skill_router.toml   # Project config and provider mapping
```

## Layers

### Content
Promo copy and static pages. No dependency on the tooling.

The deck (`deck/`) is a reveal.js presentation with no build step. One markup file,
`deck/index.html`, holds every slide; the words live in per-language string tables
(`deck/i18n/<lang>.js`) and are swapped in place by `deck/js/i18n.js`, so switching
language keeps the current slide. Everything it loads is local, so it also runs offline
from a clone over `file://`. `tests/deck/` checks its structure (language parity, links,
local assets); it sits outside `deck/` so the published site carries no Python.

String-table keys are `<slide-id>.<part>` for text that belongs to one slide, plus four
shared groups: `meta.*` (page title), `controls.*` (language switch, full screen),
`eyebrow.<section>` (the section label repeated on every slide of a section) and
`toc.<section>` (each section's name, used on its contents card and as its opener's
title, so Auto-Animate morphs one into the other).

### Tooling
The YAB framework files copied from the template. Change them upstream in
[yuriys-agentic-boyz](https://github.com/lutsenko-yuriy/yuriys-agentic-boyz) where possible.

## Dependencies

- Tooling and tests: none beyond the Python standard library.
- Deck: [reveal.js](https://revealjs.com) 6.0.2 (MIT), vendored under
  `deck/vendor/reveal.js-6.0.2/`. No plugins, no CDN, system fonts only.
