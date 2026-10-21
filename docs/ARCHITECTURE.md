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
deck/               # reveal.js presentation: en/, de/, shared assets/, vendored reveal.js
.github/workflows/  # CI for the YAB tooling tests
docs/               # Project docs, knowledge base, workflows
scripts/            # YAB tooling (onboard, skill_router, notes, checkup) in Python
skills/             # YAB skills: configure, design, build, verify, manage
styles/             # Communication styles
skill_router.toml   # Project config and provider mapping
```

Add new promo content directories here as they are created.

## Layers

### Content
Promo copy and static pages. No dependency on the tooling. The deck has one HTML file per
language (`deck/en/`, `deck/de/`) with identical slide structure; keep them in sync.

### Tooling
The YAB framework files copied from the template. Change them upstream in
[yuriys-agentic-boyz](https://github.com/lutsenko-yuriy/yuriys-agentic-boyz) where possible.

## Dependencies

- [reveal.js](https://revealjs.com) for the presentation deck.
- The YAB tooling needs nothing beyond the Python standard library.
