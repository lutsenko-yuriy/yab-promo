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
- The first slide is a table of contents under the title YAB, with the full name, Yuriy's
  agentic boyz, on its own smaller line. It links to six sections:
  1. Purpose of YAB: what it is, the ticket lifecycle with its human gates, and its memory.
  2. Core values: a safe space to think, understanding before decisions, and the human stays
     in charge.
  3. An example: Habit Loop's HAB-202, from the brief, analytics and plan through six work
     units and the review to the debrief. The brief, analytics and plan carry the workflow
     steps; the plan says YAB is loosely trunk-based and why units stay small and unfinished
     parts stay behind a switch. A branch diagram stays in place at the top: a faint `main`
     behind the steps while the ticket is scoped; from WU0, once the steps have faded out,
     one branch per work unit across the width with its commits, each forking where the
     previous one merged, each label linking to its pull request. The debrief happens on
     WU4's branch. From the first work unit on, a panel beside the story shows the feature
     switch (pact chaining feature flag) and what it is for. The debrief shows what was noted,
     learned and changed in the workflow, then the numbers; its last click merges WU4 into
     main and then turns the switch on.
  4. Cases: Habit Loop (Flutter), CheckLister (React Native) and Mordovorot (Kotlin
     Multiplatform), each with screenshots, a link to its public repo, a link to the app itself where it
     is public (Mordovorot, in the browser) and, where it has them,
     numbers with the date they were counted.
  5. Plans for the future: what is not proven yet (scale, giant brownfield codebases,
     runtimes and tools, branching models other than trunk-based) and what comes in the next
     updates.
  6. Get YAB: the link to the template, three steps to start, and what YAB gives in return.
- From any slide, the viewer can open the section menu (top left) and jump to a section; the
  menu marks the section being shown.
- A talk through the whole deck takes 15 to 20 minutes, and no slide needs code to follow.
- The deck also runs offline, opened from a local clone.
