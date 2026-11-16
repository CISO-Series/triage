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

Each CVE card shows four one-sentence bullets, so nothing is ever cut off:

- **Affects:** the product, plus a component or configuration only when it matters (e.g. "only on 32-bit systems"). No version numbers.
- **Flaw:** the nature of the vulnerability, from NVD's description.
- **Access:** what an attacker needs, written from the CVE's CVSS vector.
- **Impact:** what a successful attacker can do, also written from the vector.

The goal is that a reasonably informed security practitioner can reason toward the score from the card. So Access and Impact always state, in plain words, the facts the CVSS score is built from. Players never see the score, the vector or a severity word. `fetch_cves.py build` enforces this with fixed phrases and refuses to build any card that disagrees with its vector:

| Vector | Card must say |
|---|---|
| Attack vector N / A / L / P | Access starts "Remote" / "Adjacent network" / "Local" / "Physical access" |
| Privileges N / L / H | "no login" / "low-privilege" / "high-privilege" |
| User interaction R / N | "a user must …" / "no user action" |
| Attack complexity H | "hard to exploit" (and only then) |
| Scope changed | Impact says it reaches "beyond" the product (and only then) |
| C / I / A scored H or L | Impact describes the read / change / outage. "run code" or "take over" covers any that are H |
| C / I / A scored N | Impact rules it out: "No data is read" / "Nothing is changed" / "No outage" |
| Any L | Impact uses a limiting word: some, limited, partial |

CVEs are left out when the description is too thin to name the product or flaw, or when it contradicts the scoring (e.g. described as a local attack but scored as remote), since no honest card could match the score.

## Refreshing the CVEs

Three steps, run from the repo root:

```bash
python3 tools/fetch_cves.py fetch --days 30
```

1. **Fetch.** This pulls the last 30 days of CVEs from the [NVD API](https://nvd.nist.gov/developers/vulnerabilities) and flags any on [CISA's KEV list](https://www.cisa.gov/known-exploited-vulnerabilities-catalog). It keeps CVEs with a CVSS v3.1 base score whose description opens with a recognizable vendor or product (the `VENDORS` list). It caps each vendor at 6 and each 1-point score band at 14, for a pool of about 110 spread across the scale. The pool, with full descriptions and each CVE's CVSS vector, goes to `data/pool.json`. The vector is only used to write and check the bullets; it never goes into the game. It takes a couple of minutes because NVD rate-limits requests without an API key.
2. **Write the bullets** in `data/bullets.json`: `{"CVE-…": {"affects": "…", "flaw": "…", "access": "…", "impact": "…", "vendor": "optional better label"}}`, following the card rules above. Keep each bullet to one sentence. Claude can write these from `data/pool.json` in a few minutes. Skip any CVE whose description has too little detail to say anything real; it'll be left out.
3. **Build:**

   ```bash
   python3 tools/fetch_cves.py build
   ```

   This merges the pool and bullets into `index.html`. It lists any CVE left out for missing bullets and any bullet that runs long. It checks every card first and refuses to build, leaving `index.html` untouched, if any Affects bullet has a version number, any bullet hints at the score, or any Access or Impact bullet disagrees with the vector.
4. **Publish:** `python3 tools/make_artifact.py` writes the publishable copy to `.artifact/index.html` (git-ignored), which is then republished to the live link.

### Automatic weekly refresh

A Claude Code scheduled task, **Triage weekly CVE refresh**, runs these steps on Rich's Mac every **Friday at 3:10 AM Eastern** (12:10 AM Pacific, just after the weekly rotation). It fetches, writes the bullets from each description and vector, builds, republishes the live link, logs the change here and pushes to GitHub. It runs while the Claude desktop app is open; if the app is closed at that time, it runs the next time the app opens. If the NVD fetch fails, it keeps last week's CVEs and changes nothing.

**Refresh on Friday, at or just after the rotation.** The weekly queue is seeded from the week number *and* the data's fetch date. Refreshing mid-week would give later players a different queue from earlier ones, and would reset the official runs already played that week.

After refreshing, republish the artifact to the same URL. The artifact copy is `index.html` with the `<!doctype>`, `<html>`, `<head>`/`<body>` wrapper and the charset/viewport tags removed.

## Common edits

| To change | Edit in `index.html` |
|---|---|
| Difficulty curve | `LEVELS` (gap in tenths of a point) and `PER_LEVEL` |
| Rank titles | `RANKS` (minimum streak, title) |
| Rotation day, time zone, run #1 | `ROTATE_DAY`, `ROTATE_TZ`, `FIRST_WEEK` |
| Link included in the share | `BASE` |
