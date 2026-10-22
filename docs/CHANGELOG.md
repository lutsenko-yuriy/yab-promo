# Changelog

A record of all versioned releases. For planned work and known issues, see @docs/BACKLOG.md.

---

## [0.3.1] — 2026-10-23 (PR #17 merged)

### Changed
- [user] YP-16: the core values now read as a chain — a safe space to think, understanding before decisions, and the human stays in charge (PR #17)
- [meta] YP-16: trivial changes start with the ticket and a branch from the latest `origin/main`, before any file is touched (PR #17)

## [0.3.0] — 2026-10-22 (PR #15 merged)

### Changed
- [user] YP-14: the presentation's example now shows its feature switch from the first work unit on, beside the story, with what it is for; it stays off until the retrospective has been shown, then turns on. The title slide shows YAB on its own with the full name below it, and the analytics slide asks its question right under the title (PR #15)
- [non-user] YP-14: switch panel with stable Auto-Animate ids (the switch labels included, so they no longer fade in on every slide), shared `.subtitle` style, shorter German analytics copy so the slide keeps the shared story height, deck tests for all of it

## [0.2.1] — 2026-10-22 (PR #13 merged)

### Added
- [test] YP-12: deck test for the theme's colour contrast — 4.5:1 for text, 3:1 for arrows, list markers and progress bar exempt as decoration (PR #13)

## [0.2.0] — 2026-10-22 (PR #10 merged)

### Added
- [user] YP-2: animated YAB presentation deck in EN and DE, published on GitHub Pages at https://lutsenko-yuriy.github.io/yab-promo/ — six sections (purpose, core values, the HAB-202 example, cases for Habit Loop, CheckLister and Mordovorot, plans for the future, get YAB), a section menu with the current section beside it, full screen, offline use from a clone, and a hint to turn phones sideways (PR #10)
- YP-2 WU1: presentation deck foundation — contents slide, five section openers, EN/DE switch that keeps the current slide, full-screen button, Habit Loop theme, vendored reveal.js 6.0.2, deck structure tests in CI (PR #6) [wip]
- YP-2 WU2: Purpose section — what YAB is, the ticket lifecycle with its skills, human approval gates, and how lessons feed back into the workflow, in EN and DE (PR #7) [wip]
- YP-2 WU3: HAB-202 example story — the plan, each work unit on one animated track between the brief/analyze/plan and debrief steps, the inserted correction, the audit catch, the kill switch, live review and the retrospective, in EN and DE (PR #8) [wip]
- YP-2 WU4: HAB-202 brief and analytics slides before the plan, the track growing from the workflow steps to the work units (revealed on one click) with dividers between its phases, in EN and DE (PR #9) [wip]

## [0.1.0] — 2026-10-21 (PR #4 merged)

### Added
- [meta] Claude Code onboarding guide for new teammates (ONBOARDING.md)
- [meta] Debrief: clearer launch instructions in README; feature branches no longer track main

<!-- This file is maintained by the Product Owner agent.
     New sections are prepended after each merged PR in the format:

## [X.Y.Z] — YYYY-MM-DD (PR #N merged)

### Added / Changed / Fixed
- ...
-->
