# Product Specification

<!-- Describe what your product does from the user's perspective.
     The Product Owner agent reads this file to understand intended behaviour.
     Be specific about user-facing features, screens, and flows. -->

## Overview

YAB Promo — Promo materials for Yuriy's agentic boyz (YAB) framework (https://github.com/lutsenko-yuriy/yuriys-agentic-boyz)

## Features

### Feature 1 — YAB presentation deck (YP-2)

An animated browser presentation about YAB for developers, POs and PMs, published at
https://lutsenko-yuriy.github.io/yab-promo/ (source: `deck/`).

- The viewer can play the deck in a browser, full screen optionally (the F key or a button), and
  step through it with the arrow keys or a clicker. Slides and in-slide reveals are animated;
  with reduced motion turned on, they are not.
- The viewer can switch between English and German at any time; the current slide stays. A
  `?lang=de` link opens the deck in German.
- The first slide is a table of contents linking to five sections:
  1. Purpose of YAB: what it is, the ticket lifecycle with its human gates, and its memory.
  2. An example: Habit Loop's HAB-202, from the brief, analytics and plan through six work
     units and the review to the debrief, on a work-unit track that stays in place.
  3. Cases: Habit Loop (Flutter), CheckLister (React Native) and Mordovorot (Kotlin
     Multiplatform), each with screenshots, a link to its public repo and, where it has them,
     numbers with the date they were counted; then CheckLister on Codex.
  4. Not proven yet: scale, runtimes and tools, what comes next, and why the human staying in
     charge is a core value rather than a limit.
  5. Get YAB: the link to the template and three steps to start.
- A talk through the whole deck takes 15 to 20 minutes, and no slide needs code to follow.
- The deck also runs offline, opened from a local clone.
