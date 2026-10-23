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
tests/deck/         # Structural and contrast tests for the deck (Python standard library)
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
local assets) and the theme's colour contrast (`test_contrast.py`: 4.5:1 for text, 3:1 for
arrows, with list markers and the progress bar exempt as decoration); it sits outside
`deck/` so the published site carries no Python.

String-table keys are `<slide-id>.<part>` for text that belongs to one slide, plus seven
shared groups: `meta.*` (page title), `controls.*` (language switch, full screen),
`eyebrow.<section>` (the section label fixed beside the menu, naming the section being shown),
`toc.<section>` (each section's name, used on its contents card and as its opener's
title, so Auto-Animate morphs one into the other), `flow.<step>` (the lifecycle
steps, shown on both `purpose-flow` and `purpose-human`), `wu.<unit>` (the work-unit
labels, on the example's branch diagram and on CheL-36's track on `cases-checklister`) and
`switch.*` (the feature switch shown in the example section, its name and its purpose).
Elements name their key in `data-i18n` (inner HTML),
`data-i18n-aria` (`aria-label` and tooltip) or `data-i18n-alt` (an image's `alt`).

The example section's slides (`class="story"`) share one height so what runs across them
stays in place while Auto-Animate recolours it. From the brief to the debrief a fixed band
at the top (`.story-head`) holds the branch diagram (`.branches`). On the brief, analytics
and plan slides the workflow steps (`data-id="step-<skill>"`) sit on a faint `main`
(`.branches.is-scoping`); the plan adds one lane per work unit (`data-id="lane-<unit>"`), and
WU0 keeps a hidden copy of the steps (`.wu-track.is-leaving`) so they fade out instead of
vanishing. Each lane holds a small inline SVG (`art-<unit>`): the branch leaving main at an
angle, the merge leg climbing back, the unit's commits (its pull request's real count,
capped at three) and the fork and merge commits on main (`branch-`, `merge-`,
`commit-<unit>-<n>`, `fork-`, `mnode-<unit>`), then the label (`label-<unit>`). Each branch
forks where the one before it merged, so the two share one commit. Lanes are `is-planned`,
`is-open` or `is-merged`; every part keeps the same box on every slide and only fades or
recolours, because Auto-Animate morphs neither shapes nor sizes. Every element inside the
diagram and the switch panel has a `data-id`, links' inner text aside: Auto-Animate fades in
anything unmatched, so a part without one would blink on every slide.
From WU0 to the debrief, everything below the band sits in `.story-body`: a switch panel
(`.switch-panel`, with stable `data-id`s for the switch, its name and its purpose, so it
stays put too) beside the slide's own content (`.story-main`). The switch is off on every
one of those slides. On the debrief, WU4's merge leg, its merge commit on main and the switch
are `fragment custom` sharing the highest `data-fragment-index`, so its last click merges
WU4 and, 0.7s later, turns the switch on. After a slide auto-animates, reveal.js pins its
matched elements' colours, opacity, outline and transition with `!important` until the slide
is left; only CSS transitions outrank that, so the last click uses transitions to
`!important` end states, and the WU4 regression flash animates `stroke` and `fill`, which
reveal.js leaves alone.

`.github/workflows/pages.yml` publishes `deck/` alone to GitHub Pages on every push to `main`
that changes it, so the site carries neither the docs nor the tooling.

### Tooling
The YAB framework files copied from the template. Change them upstream in
[yuriys-agentic-boyz](https://github.com/lutsenko-yuriy/yuriys-agentic-boyz) where possible.

## Dependencies

- Tooling and tests: none beyond the Python standard library.
- Deck: [reveal.js](https://revealjs.com) 6.0.2 (MIT), vendored under
  `deck/vendor/reveal.js-6.0.2/`. No plugins, no CDN, system fonts only.
