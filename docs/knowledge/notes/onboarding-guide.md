---
bookmarks: [upstream-candidate]
---

# Onboarding guide (PR #4): Claude Code onboarding guide for new teammates

## Notes

## Debrief summary

### 2026-10-21

**What went well**
- The guide came together quickly from a concrete draft, and the user came away feeling onboarded.

**What was hard or surprising**
- Claude Code was launched from the parent folder, so the repo's CLAUDE.md, skills and onboarding gate didn't load at launch. The advice to "launch Claude Code from inside `yab-promo/`" was read as "`cd` into it," and the `cd` failed.
- `git checkout -b <branch> origin/main` set `origin/main` as the new branch's upstream, so a bare `git push` would have targeted `main`.

**What to change**
- README now gives the exact launch command (`cd yab-promo && claude`) and says a `cd` inside a running session isn't enough.
- FEATURE.md step 1.5 now uses `--no-track` when branching from `origin/main`. Upstream the same fix to yuriys-agentic-boyz.
