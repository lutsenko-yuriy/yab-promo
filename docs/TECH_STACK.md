# Tech Stack

## Languages

| Language | Version | Used for |
|---|---|---|
| Markdown | CommonMark / GitHub Flavored Markdown | Promo copy, docs |
| HTML | HTML5 | Static promo pages |
| CSS | CSS3 | Styling for static pages |
| Python | 3.9+ (CI matrix 3.9, 3.12 in `.github/workflows/tests.yml`) | YAB tooling under `scripts/` |
| Shell | Bash (`scripts/onboard/gate.sh`) | Onboarding gate hook |

## Frameworks and libraries

- None for the promo content (plain static HTML/CSS). A presentation on a separate stack is planned and will be briefed after onboarding.
- YAB tooling uses the Python standard library only.

## Platforms

- Web browsers (static pages, hostable on GitHub Pages)
- GitHub (repo and README rendering)

## Tooling

- **Build / package manager:** none (static files)
- **Test runner:** Python `unittest` for the YAB tooling
- **Linter / formatter:** none configured
- **CI:** GitHub Actions (`.github/workflows/tests.yml`)
