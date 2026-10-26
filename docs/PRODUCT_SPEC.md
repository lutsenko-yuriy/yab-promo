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
- The deck follows the device's light or dark setting. A night mode button beside full screen
  switches it on the current slide; the choice is remembered in that browser and wins over the
  device setting from then on. Night mode uses Habit Loop's dark colours; the app screenshots get
  a thin frame.
- A share button at the right end of the top-right controls offers two links, both keeping the
  language and the section toggles: this slide, or the deck from the start. Where the browser
  has a system share sheet, the link goes to it; elsewhere it is copied and "Link copied"
  shows. If neither works (e.g. the clipboard is refused), the link is shown, selected, to copy
  by hand.
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
     switch (pact chaining feature flag) and what it is for, in three bullets: it ships hidden,
     turns on after release, and turns off without a release. The debrief shows what was noted,
     learned and changed in the workflow, then the numbers; its last click merges WU4 into
     main, puts "from 0.53.0" in place of "after release", and then turns the switch on.
  4. Cases: Habit Loop (Flutter), Mordovorot (Kotlin Multiplatform) and CheckLister
     (React Native), each with screenshots, a link to its public repo, a link to the app itself
     where it is public (Mordovorot, in the browser) and, where it has them,
     numbers with the date they were counted.
  5. Plans for the future: what is not proven yet (scale, giant brownfield codebases,
     runtimes and tools, branching models other than trunk-based) and what comes in the next
     updates.
  6. Get YAB: the link to the template, three steps to start, and what YAB gives in return.
- From any slide, the viewer can open the section menu (top left) and jump to a section; the
  menu marks the section being shown.
- Each section in the menu has a switch, all on by default. Clicking through (keys, clicker,
  swipe, the arrows) skips the slides of a switched-off section, forward and back; the
  contents slide stays unchanged, and opening an off section from it or from the menu still
  shows it, with clicking forward continuing to the next section that is on. The choices are
  carried in the link (`?skip=cases+limits`, next to `?lang=`), updated in place, so a
  tailored talk can be shared or bookmarked. The slide number and progress bar still count
  the whole deck. On phones held upright reveal.js scrolls through every slide, so nothing
  is skipped there.
- A talk through the whole deck takes 15 to 20 minutes, and no slide needs code to follow.
- The deck also runs offline from a local clone, after one command builds the page
  (`python3 tools/build_deck.py`, needs Python 3).
