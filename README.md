# Triage

A weekly higher-or-lower game for the Super Cyber Friday (SCF) live chat, played with real CVEs from the past month. Players see one CVE with its CVSS score and call whether the next one scores higher or lower. The score gaps tighten as the streak grows. When a player misses, they paste a spoiler-free result into the chat.

Live version: https://claude.ai/artifact/5uQCPWFWQWrd8q6gsmpaHF

## How it works

- **One file.** Everything is in `index.html`, including the CVE data in a JSON block between the `<!--CVE-DATA-->` markers. No server.
- **Weekly queue.** Everyone gets the same sequence of CVEs each week. It rotates at **12:00 AM Pacific every Friday**, matching Lockout. Run #1 is Friday 2026-11-20 (`FIRST_WEEK`); before that the page serves practice runs. A player's first run of the week is the official one; after that they can play unlimited practice runs.
- **Difficulty.** Every 3 correct calls moves the priority up a level and narrows the score gap between the two cards:

  | Priority | Calls | Score gap |
  |---|---|---|
  | P5 | 1–3 | 3.0+ |
  | P4 | 4–6 | 2.0–2.9 |
  | P3 | 7–9 | 1.2–1.9 |
  | P2 | 10–12 | 0.6–1.1 |
  | P1 | 13–15 | 0.3–0.5 |
  | P0 | 16+ | 0.1–0.2 |

  Ties never come up, and each pair is about a 50/50 split between higher and lower.
- **Sharing.** "Copy result for chat" gives one emoji line per priority level, a rank and the link. It never names the CVEs.
- **Saved locally.** Official-run progress lives in the player's browser (`localStorage`).

## Refreshing the CVEs

```bash
python3 tools/fetch_cves.py --days 30
```

This pulls the last 30 days of CVEs from the [NVD API](https://nvd.nist.gov/developers/vulnerabilities) and flags any on [CISA's KEV list](https://www.cisa.gov/known-exploited-vulnerabilities-catalog). It keeps CVEs with a CVSS v3.1 base score whose description opens with a recognizable vendor or product (the `VENDORS` list). It then caps each vendor at 10 and each 1-point score band at 32, so the pool spreads across the scale. The result is written into `index.html`. A full pull takes a couple of minutes because NVD rate-limits requests without an API key.

**Refresh on Friday, at or just after the rotation.** The weekly queue is seeded from the week number *and* the data's fetch date. Refreshing mid-week would give later players a different queue from earlier ones, and would reset the official runs already played that week.

After refreshing, republish the artifact to the same URL. The artifact copy is `index.html` with the `<!doctype>`, `<html>`, `<head>`/`<body>` wrapper and the charset/viewport tags removed.

## Common edits

| To change | Edit in `index.html` |
|---|---|
| Difficulty curve | `LEVELS` (gap in tenths of a point) and `PER_LEVEL` |
| Rank titles | `RANKS` (minimum streak, title) |
| Rotation day, time zone, run #1 | `ROTATE_DAY`, `ROTATE_TZ`, `FIRST_WEEK` |
| Link included in the share | `BASE` |
