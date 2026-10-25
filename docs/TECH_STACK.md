# Tech Stack

## Languages

| Language | Version | Used for |
|---|---|---|
| Markdown | CommonMark / GitHub Flavored Markdown | Promo copy, docs |
| HTML | HTML5 | Static promo pages |
| CSS | CSS3 | Styling for static pages |
| Python | 3.9+ (CI matrix 3.9, 3.12 in `.github/workflows/tests.yml`) | YAB tooling under `scripts/`; the deck build (`tools/build_deck.py`) |
| Shell | Bash (`scripts/onboard/gate.sh`) | Onboarding gate hook |
| JavaScript | ES2017+, plain browser scripts, no build step | Presentation deck controls and language switching (`deck/js/`) |

## Frameworks and libraries

- [reveal.js](https://revealjs.com) 6.0.2 for the presentation deck, vendored under `deck/vendor/` (no CDN, no plugins).
- Nothing else for the promo content (plain static HTML/CSS).
- YAB tooling uses the Python standard library only.

## Platforms

- Web browsers (static pages); the deck is published on GitHub Pages by `.github/workflows/pages.yml`
- GitHub (repo and README rendering)

## Tooling

- **Build / package manager:** none to install; `python3 tools/build_deck.py` writes `deck/index.html` from `deck/src/` (gitignored; the Pages workflow builds it)
- **Test runner:** Python `unittest` for the YAB tooling and for the deck's structure and colour contrast (`tests/deck/`)
- **Linter / formatter:** none configured
- **CI:** GitHub Actions (`.github/workflows/tests.yml`)
