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
.github/workflows/  # CI for the YAB tooling tests
docs/               # Project docs, knowledge base, workflows
scripts/            # YAB tooling (onboard, skill_router, notes, checkup) in Python
skills/             # YAB skills: configure, design, build, verify, manage
styles/             # Communication styles
skill_router.toml   # Project config and provider mapping
```

Promo content does not exist yet; add its directories here as they are created.

## Layers

### Content
Promo copy and static pages. No dependency on the tooling.

### Tooling
The YAB framework files copied from the template. Change them upstream in
[yuriys-agentic-boyz](https://github.com/lutsenko-yuriy/yuriys-agentic-boyz) where possible.

## Dependencies

- None beyond the Python standard library.
