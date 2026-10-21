# Tech Stack

## Languages

| Language | Version | Used for |
|---|---|---|
| Markdown | CommonMark / GitHub Flavored Markdown | Promo copy, docs |
| HTML | HTML5 | Static promo pages and the reveal.js deck |
| CSS | CSS3 | Styling for static pages |
| Python | 3.9+ (CI matrix 3.9, 3.12 in `.github/workflows/tests.yml`) | YAB tooling under `scripts/` |
| Shell | Bash (`scripts/onboard/gate.sh`) | Onboarding gate hook |

## Frameworks and libraries

- [reveal.js](https://revealjs.com) for the animated presentation (full-screen playback, Auto-Animate, fragments). Vendored in `deck/vendor/reveal.js-5.1.0/` (keeps its MIT licence file), so the deck works offline; no build step.
- Other promo content is plain static HTML/CSS.
- YAB tooling uses the Python standard library only.

## Platforms

- Web browsers (static pages, hostable on GitHub Pages)
- GitHub (repo and README rendering)

## Tooling

- **Build / package manager:** none (static files)
- **Test runner:** Python `unittest` for the YAB tooling
- **Linter / formatter:** none configured
- **CI:** GitHub Actions (`.github/workflows/tests.yml`)
