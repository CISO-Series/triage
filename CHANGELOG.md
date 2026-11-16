# Changelog

All notable changes to the CISO Series Triage repo are logged here.

## 2026-11-16
- Created Triage, a weekly CVSS higher-or-lower game for the Super Cyber Friday chat, as a single `index.html`.
- Uses 233 real CVEs published 2026-10-17 to 2026-11-16, pulled from NVD with CVSS v3.1 base scores. They're balanced across the score range, and the 9 on CISA's KEV list get a 🔥 badge.
- Difficulty ramps from P5 (gap 3.0+) to P0 (gap 0.1–0.2), one level per 3 correct calls.
- Everyone gets the same queue each week. It rotates Friday 12:00 AM Pacific, and run #1 is 2026-11-20. Unlimited practice runs after the official one.
- Spoiler-free "Copy result for chat" share: one emoji line per priority level, plus a rank (Alert Fatigue up to CVSS Whisperer).
- Added `tools/fetch_cves.py` to refresh the CVE pool from NVD and CISA KEV, plus this README and changelog. — Rich
