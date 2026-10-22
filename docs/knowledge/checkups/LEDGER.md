# Checkup ledger

Tracks due status and open findings for the two-tier periodic code-quality checkup defined in [ADR-0001](../decisions/ADR-0001-two-tier-periodic-code-quality-checkup.md). `scripts/checkup/due.py` reads the **Cadence & due status** table below to report which tier(s) are due; the `/checkup` skill updates this file after each run.

## Cadence & due status

Each tier is tracked as "not yet done this period" — a period label, not an exact-day match — so it stays flagged as overdue until actually run (see ADR-0001). `Period covered` is the period label (`YYYY-MM` for light, `YYYY-Qn` for heavy) of the most recently completed run.

| Tier | Cadence | Last run | Period covered | Next due |
|---|---|---|---|---|
| Light | 1st of every calendar month | 2026-10-22 | 2026-10 | 2026-11-01 |
| Heavy | 14th of Jan/Apr/Jul/Oct | 2026-10-22 | 2026-Q4 | 2027-01-14 |

## Open findings

Findings needing human decision or larger effort, each carrying an explicit deadline — no individual PM ticket is filed (per ADR-0001). Classified using [Fowler's Technical Debt Quadrant](https://martinfowler.com/bliki/TechnicalDebtQuadrant.html) before being written up.

| ID | Opened | Tier | Dimension | Debt quadrant | Summary | Deadline | Write-up |
|---|---|---|---|---|---|---|---|
| CHK-2026-10-22-light-1 | 2026-10-22 | light | Scenario quality | prudent-inadvertent | `onboard` reads origin with `git remote get-url`, so host `insteadOf` rewrites break `test_url_sets_origin` in cloud containers (upstream) | 2026-12-01 | [CHK-2026-10-22-light](CHK-2026-10-22-light.md) |
| CHK-2026-10-22-light-2 | 2026-10-22 | light | Doc-reality drift | prudent-inadvertent | No skill adds new tickets to BACKLOG.md, so it drifts from GitHub Issues (upstream) | 2026-12-01 | [CHK-2026-10-22-light](CHK-2026-10-22-light.md) |
## Resolved findings

Archive of findings once fixed or otherwise closed out.

| ID | Opened | Resolved | Tier | Dimension | Summary | Write-up |
|---|---|---|---|---|---|---|
| CHK-2026-10-22-heavy-1 | 2026-10-22 | 2026-10-22 | heavy | Accessibility | Light-green deck arrows at 1.93:1; arrows now use `#558b2f` (3.78:1) | [CHK-2026-10-22-heavy](CHK-2026-10-22-heavy.md) |
