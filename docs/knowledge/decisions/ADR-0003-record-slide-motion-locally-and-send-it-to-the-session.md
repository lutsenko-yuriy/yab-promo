# ADR-0003 — check slide motion in the smoke test with an Auto-Animate probe and frame strips, and send an MP4 of the touched slides to the session

## Status
`accepted`

## Context
Screenshots of end states can't show motion bugs. On YP-32 they looked right, yet text faded in on every slide change (Auto-Animate fading in an element without a `data-id`), and the human found it by clicking through.

The agent can read images and text but can't watch a video. The repo is public. The deck tooling installs nothing. Recordings must not pile up on disk or in the repo. Full findings: `docs/knowledge/notes/YP-35.md`.

## Decision
- **When:** every PR that touches `deck/src/` or `deck/css/` gets a recording in its smoke test, of only the slides it touches. Each is entered from its previous slide and stepped through each click, in English.
- **How:** headless system Chrome over CDP, using Node's built-in WebSocket and [`Page.startScreencast`](https://github.com/ChromeDevTools/devtools-protocol/blob/master/json/browser_protocol.json) (experimental in the protocol). ffmpeg turns the frames into the MP4 and the strips. No new installs.
- **The agent's check:**
  - After each step, list the elements reveal.js marked `data-auto-animate-target="unmatched"` on the current slide. That marker is reveal.js 6.0.2's own label for elements Auto-Animate fades in.
  - Read a 10 fps frame strip of each step.
  - Both caught a removed `data-id` in the YP-35 prototype.
- **For the human:** the MP4 (about 80–90 KB for a few seconds) is sent to the session, which reaches the phone, as on YP-14.
- **Storage:**
  - Output goes in `$CLAUDE_JOB_DIR/tmp` when that's set, otherwise in a gitignored `.recordings/`.
  - Frames and the Chrome profile (about 21 MB per run) are deleted as soon as the MP4 is encoded.
  - `/ship` empties `.recordings/`.

## Alternatives considered
| Option | Why not chosen |
|---|---|
| [Playwright `recordVideo`](https://playwright.dev/docs/videos) | It needs npm and its own browser download, and the video is only saved when the context closes. |
| [Puppeteer `page.screencast`](https://pptr.dev/api/puppeteer.page.screencast) | It's an npm install, and the API is marked obsolete. |
| Attach to the PR ([gh 2.99+ `--attach`](https://github.blog/changelog/2026-09-01-github-cli-media-in-issues-pull-requests-and-comments)) | Uploads are public and permanent for this public repo, and the local gh is older. Sending to the session reaches the phone with nothing left behind. |
| Video only on request (the YP-14 debrief rule) | YP-32 shows the human then finds the bug first. The probe and strips cost seconds. |
| Screenshots of end states | They miss motion bugs (YP-32). |
| A `/checkup` sweep of old recordings | Not needed when intermediates go right away and `/ship` empties the folder. |

## Related ticket
YP-35 (research); implementation: YP-45

## Date
2026-10-26
