# Code Style

## Base standard

Markdown: [Google Markdown style guide](https://google.github.io/styleguide/docguide/style.html)
HTML: [Google HTML/CSS Style Guide](https://google.github.io/styleguide/htmlcssguide.html)
CSS: [Google HTML/CSS Style Guide](https://google.github.io/styleguide/htmlcssguide.html)
Python: [PEP 8](https://peps.python.org/pep-0008/)
Shell: [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html)
JavaScript: [Google JavaScript Style Guide](https://google.github.io/styleguide/jsguide.html)

## Formatting

No formatter configured; CI enforces nothing beyond the tooling and deck tests. Keep Markdown lines unwrapped (one paragraph per line) and indent HTML/CSS/JavaScript with 2 spaces. Deck JavaScript is plain browser scripts: no modules, no bundler.

## Linting

No linter configured.

## Naming and structure

Kebab-case file names for content and pages (e.g. `landing-page.html`). Python tests live in `tests/` next to the module they cover, named `test_<module>.py`.

## Comments

Explain why, not what, in one concise line. No comments in promo copy.

## Deck copy

- No code on slides: the audience includes POs and PMs. `tests/deck/` rejects `<code>` and `<pre>`.
- One idea per slide, at most about 25 visible words.
- All visible text goes through the string tables in `deck/i18n/`; German is translated, not copied from English. The one exception is names: the chip names on the work-unit tracks and the branch diagram (`Brief`, `Plan`, `WU1`, …) name skills and work units, and the diagram's `main` names a branch, so they stay in the markup, the same in both languages.
