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
  index.html        #   All slides; visible text and alt text referenced by i18n keys
  css/              #   Theme (Habit Loop palette) and deck components
  js/               #   Deck start-up, section menu and controls, language switching
  i18n/             #   String tables, one per language (en.js, de.js)
  img/cases/<app>/  #   App screenshots for the cases section, resized for the web
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

String-table keys are `<slide-id>.<part>` for text that belongs to one slide, plus six
shared groups: `meta.*` (page title), `controls.*` (language switch, full screen),
`eyebrow.<section>` (the section label repeated on every slide of a section),
`toc.<section>` (each section's name, used on its contents card and as its opener's
title, so Auto-Animate morphs one into the other), `flow.<step>` (the lifecycle
steps, shown on both `purpose-flow` and `purpose-human`) and `wu.<unit>` (the labels on
the work-unit tracks: the one that runs through the example section, and CheL-36's on
`cases-checklister`). Elements name their key in `data-i18n` (inner HTML),
`data-i18n-aria` (`aria-label` and tooltip) or `data-i18n-alt` (an image's `alt`).

The example section's slides (`class="story"`) share one height so the work-unit track
stays in place while Auto-Animate recolours its chips from slide to slide: the work units
(`data-id="wu-<n>"`) between the workflow steps around them (`data-id="step-<skill>"`:
brief, analyze and plan before, debrief after). The
brief and analytics slides show only those steps; the work units appear once the plan makes them.

`.github/workflows/pages.yml` publishes `deck/` alone to GitHub Pages on every push to `main`
that changes it, so the site carries neither the docs nor the tooling.

### Tooling
The YAB framework files copied from the template. Change them upstream in
[yuriys-agentic-boyz](https://github.com/lutsenko-yuriy/yuriys-agentic-boyz) where possible.

## Dependencies

- Tooling and tests: none beyond the Python standard library.
- Deck: [reveal.js](https://revealjs.com) 6.0.2 (MIT), vendored under
  `deck/vendor/reveal.js-6.0.2/`. No plugins, no CDN, system fonts only.
