# Glossary

Canonical domain terms for this project. Skills and documentation use these names consistently.
When a new term is introduced during a `brief` session, add it here before creating the ticket.

<!-- Format: one table per domain area. Example:

## Core concepts

| Term | Definition | Code symbol |
|---|---|---|
| Pact | A user's commitment to show up for a habit N times | `Pact` |
| Showup | A single instance of fulfilling a pact | `Showup` |

## Known aliases to avoid

| Avoid | Use instead |
|---|---|
| session | showup |
| commitment | pact |

-->

## Presentation deck

| Term | Definition | Code symbol |
|---|---|---|
| Deck | The animated YAB presentation published on GitHub Pages | `deck/` |
| Contents slide | The first slide: a card per section, linking to its opener | `#toc`, `toc.*` keys |
| Section | One of the deck's six parts, listed on the contents slide and in the section menu | `toc.<section>` |
| Section opener | The first slide of a section; its title morphs from the section's contents card | `id="<section>"` |
| Section menu | The menu at the top left that jumps to any section and marks the one being shown | `.yab-menu` |
| Section label | The fixed text beside the section menu naming the section being shown | `.yab-section`, `eyebrow.<section>` keys |
| Plans for the future | Section 5: what YAB has not proven yet and what comes next | `limits` |
| Case | A real project built with YAB, shown with screenshots and a link to its repo | `cases-<app>` |
| Work-unit track | The row of chips showing workflow steps (brief, analytics and plan slides of the example) or work units (`cases-checklister`) | `.wu-track`, `.wu-chip` |
| Branch diagram | The top of the example's slides from the brief to the debrief: a `main` line, faint while the ticket is scoped; from WU0, once the scoping steps have gone, one branch per work unit across the full width (planned, then open while worked on, then merged back), its commits as dots, each label linking to that unit's pull request; WU4's reads "+ debrief" on the debrief | `.branches`, `.lane`, `.branch-art`, `.story-head` |
| Loosely trunk-based | YAB's way of branching: one branch and pull request per work unit, each merged straight into `main` | — |
| Night mode | The deck's dark theme, after Habit Loop's: follows the system setting until the viewer picks one with the button beside full screen, then remembers that choice in the browser | `.yab-theme`, `data-theme` |
| Pact chaining | The whole HAB-202 feature in the example: restarting a finished pact as a new, linked one, plus the links between them; behind the flag `pact_chaining_enabled`, shown on the slides as "pact chaining feature flag" | `pact_chaining_enabled` |
| Switch panel | The left part of each example slide from WU0 to the debrief: the feature switch, its name and purpose, set off by a thin divider | `.switch-panel`, `switch.*` keys |
| String table | The per-language file holding every visible deck string by key | `deck/i18n/<lang>.js` |

## Known aliases to avoid

| Avoid | Use instead |
|---|---|
| Eyebrow (outside the `eyebrow.*` keys) | Section label |
| Limits, Not proven yet | Plans for the future |
| TOC (in copy) | Contents slide |
| Dark mode, dark theme (in copy) | Night mode |
