# Triage

A weekly higher-or-lower game for the Super Cyber Friday (SCF) live chat, played with real CVEs from the past month. Players see two CVEs with both CVSS scores hidden and tap the one they think scores higher. Both scores are revealed, then a new pair comes up. The score gaps tighten as the streak grows. When a player misses, they paste a spoiler-free result into the chat.

Live version: https://claude.ai/artifact/5uQCPWFWQWrd8q6gsmpaHF

## How it works

- **One file.** Everything is in `index.html`, including the CVE data in a JSON block between the `<!--CVE-DATA-->` markers. No server.
- **Weekly pairs.** Everyone gets the same pairs, in the same order, each week. It rotates at **12:00 AM Pacific every Friday**, matching Lockout. Run #1 is Friday 2026-11-20 (`FIRST_WEEK`); before that the page serves practice runs. A player's first run of the week is the official one; after that they can play unlimited practice runs.
- **Difficulty.** Every 3 correct calls moves the priority up a level and narrows the score gap between the two cards in a pair:

  | Priority | Calls | Score gap |
  |---|---|---|
  | P5 | 1–3 | 3.0+ |
  | P4 | 4–6 | 2.0–2.9 |
  | P3 | 7–9 | 1.2–1.9 |
  | P2 | 10–12 | 0.6–1.1 |
  | P1 | 13–15 | 0.3–0.5 |
  | P0 | 16+ | 0.1–0.2 |

  Ties never come up, and which side holds the higher score is random.
- **Sharing.** "Copy result for chat" gives one emoji line per priority level, a rank and the link. It never names the CVEs.
- **Saved locally.** Official-run progress lives in the player's browser (`localStorage`).

## The cards

Each CVE card shows four one-sentence bullets, written from NVD's full description so nothing is ever cut off:

- **Affects:** the product, plus a component or configuration only when it matters (e.g. "only on 32-bit systems"). No version numbers.
- **Flaw:** the nature of the vulnerability
- **Access:** what an attacker needs: remote or local, logged in or not, user interaction
- **Impact:** what a successful attacker can do

Bullets never include the CVSS score or a severity word. Some NVD descriptions (Oracle's especially) quote the score, so they can't be copied in as-is.

## Refreshing the CVEs

Three steps, run from the repo root:

```bash
python3 tools/fetch_cves.py fetch --days 30
```

1. **Fetch.** This pulls the last 30 days of CVEs from the [NVD API](https://nvd.nist.gov/developers/vulnerabilities) and flags any on [CISA's KEV list](https://www.cisa.gov/known-exploited-vulnerabilities-catalog). It keeps CVEs with a CVSS v3.1 base score whose description opens with a recognizable vendor or product (the `VENDORS` list). It caps each vendor at 6 and each 1-point score band at 14, for a pool of about 110 spread across the scale. The pool, with full descriptions, goes to `data/pool.json`. It takes a couple of minutes because NVD rate-limits requests without an API key.
2. **Write the bullets** in `data/bullets.json`: `{"CVE-…": {"affects": "…", "flaw": "…", "access": "…", "impact": "…", "vendor": "optional better label"}}`. Keep each bullet to one sentence. Claude can write these from `data/pool.json` in a few minutes. Skip any CVE whose description has too little detail to say anything real; it'll be left out.
3. **Build:**

   ```bash
   python3 tools/fetch_cves.py build
   ```

   This merges the pool and bullets into `index.html`. It lists any CVE left out for missing bullets and any bullet that runs long.

**Refresh on Friday, at or just after the rotation.** The weekly queue is seeded from the week number *and* the data's fetch date. Refreshing mid-week would give later players a different queue from earlier ones, and would reset the official runs already played that week.

After refreshing, republish the artifact to the same URL. The artifact copy is `index.html` with the `<!doctype>`, `<html>`, `<head>`/`<body>` wrapper and the charset/viewport tags removed.

## Common edits

| To change | Edit in `index.html` |
|---|---|
| Difficulty curve | `LEVELS` (gap in tenths of a point) and `PER_LEVEL` |
| Rank titles | `RANKS` (minimum streak, title) |
| Rotation day, time zone, run #1 | `ROTATE_DAY`, `ROTATE_TZ`, `FIRST_WEEK` |
| Link included in the share | `BASE` |
