# Changelog

All notable changes to the CISO Series Triage repo are logged here.

## 2026-11-16
- Created Triage, a weekly CVSS higher-or-lower game for the Super Cyber Friday chat, as a single `index.html`.
- Uses 233 real CVEs published 2026-10-17 to 2026-11-16, pulled from NVD with CVSS v3.1 base scores. They're balanced across the score range, and the 9 on CISA's KEV list get a 🔥 badge.
- Difficulty ramps from P5 (gap 3.0+) to P0 (gap 0.1–0.2), one level per 3 correct calls.
- Everyone gets the same queue each week. It rotates Friday 12:00 AM Pacific, and run #1 is 2026-11-20. Unlimited practice runs after the official one.
- Spoiler-free "Copy result for chat" share: one emoji line per priority level, plus a rank (Alert Fatigue up to CVSS Whisperer).
- Added `tools/fetch_cves.py` to refresh the CVE pool from NVD and CISA KEV, plus this README and changelog. — Rich

## 2026-11-16 (2)
- Replaced the truncated NVD description on each card with three complete bullets: **Affects**, **Flaw** and **Impact**. Nothing on a card is cut off anymore; all 110 cards were checked at phone width.
- Bullets are written per CVE in `data/bullets.json` from NVD's full description. They never include the score or a severity word. Cards now also name the actual product (e.g. Pillow, Wagtail, Apache Kafka) instead of the language or a parent vendor.
- Trimmed the pool to 110 CVEs (6 per vendor, 14 per score band) so each gets a careful summary. Dropped 2 CVEs whose NVD entries had no usable detail.
- `fetch_cves.py` is now three steps: `fetch` writes `data/pool.json` with full descriptions, bullets go in `data/bullets.json`, and `build` merges them into `index.html`. — Rich

## 2026-11-16 (3)
- New mechanic: each round shows two CVEs with **both scores hidden**, and the player taps the one they think scores higher. Both scores are revealed, then a fresh pair comes up. This replaces higher-or-lower against a shown score, which made it unclear which CVE you were judging.
- Layout: the two cards are the answer buttons, side by side with a VS marker (stacked on phones). The separate Higher/Lower buttons are gone, so the cards take about 93% of the game width. The picked card is marked ✓ or ✗ after the reveal, and CVE IDs link to NVD once scored.
- Bullets rewritten for all 110 CVEs. **Affects** now names only the product (plus a component or configuration when it matters, never version numbers). A new **Access** bullet says what an attacker needs, and **Flaw** and **Impact** are fuller sentences. `fetch_cves.py build` now requires all four.
- Difficulty is tighter: every pair is chosen fresh for its level, so P0 pairs land at 0.1–0.2 consistently. Saved progress uses a new key, so test runs under the old mechanic don't carry over. — Rich

## 2026-11-16 (4)
- Set up the weekly CVE refresh as a Claude Code scheduled task: Fridays at 3:10 AM Eastern (12:10 AM Pacific, right after the rotation). It fetches from NVD, writes the bullets, builds, republishes the live game, logs here and pushes.
- `fetch_cves.py build` now refuses to build if an Affects bullet contains a version number or any bullet hints at the score (critical, severity, CVSS, etc.).
- Added `tools/make_artifact.py`, which writes the publishable copy to `.artifact/index.html` (git-ignored). — Rich
