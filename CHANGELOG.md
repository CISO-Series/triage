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

## 2026-11-16 (5)
- Weekly CVE refresh: the game now uses 106 CVEs published 2026-10-19 to 2026-11-16, pulled fresh from NVD. 9 are on CISA's KEV list.
- Wrote new Affects/Flaw/Access/Impact bullets for 84 CVEs and kept the existing bullets for 22 that stayed in the pool. Entries for CVEs no longer in the pool were dropped.
- Skipped 1 CVE with a description too thin to summarize: CVE-2026-76302 (Cisco software hardening release, no product or impact named). — Rich

## 2026-11-16 (6)
- Reviewed every card against NVD's CVSS vector. About a quarter didn't give a practitioner enough to reason toward the score: "not published" bullets, file bugs that read as network attacks, and missing attack difficulty, scope change, or which kind of harm.
- Rewrote all bullets so **Access** and **Impact** state, in plain words, what each CVE's CVSS vector says: how it's reached, login level, user interaction, whether it's hard to exploit, what can be read, changed or taken down (and what can't), and whether it reaches beyond the product. The score, vector and severity words are never shown.
- `fetch_cves.py fetch` now saves each CVE's vector in `data/pool.json` (for writing and checking only; it never enters the game).
- `fetch_cves.py build` now checks every card against its vector with fixed phrases and refuses to build on any mismatch. It also now checks before writing, so a failed build never touches `index.html`.
- Dropped 6 CVEs whose description contradicts NVD's scoring or is too thin: CVE-2026-113032 (Chrome address bar, described local / scored remote), CVE-2026-113061 (Chrome Remote Desktop, nothing in the description backs the full-compromise scoring), CVE-2026-123218 (IBM Aspera, described as an authorized user / scored no login), CVE-2026-125120 (Mongoose, "skews counts" / scored full compromise), CVE-2026-99030 (Linux kernel leak the description says receivers drop / scored high leak), CVE-2026-76302 (Cisco hardening note). The game now has 101 CVEs.
- Updated the weekly refresh task to write cards the same way. — Rich

## 2026-11-18
- Made the repo public and turned on GitHub Pages (`main`, root), so the game is playable at https://ciso-series.github.io/triage/ for outside testing.
- The share link now points at whichever page is being played: the GitHub Pages URL when played there, the claude.ai artifact everywhere else. — Rich

## 2026-11-18 (2)
- Game-over screen now promotes the next Super Cyber Friday: "If you enjoyed this game, you might also enjoy <event>, live on Super Cyber Friday, <date>, 1 PM ET", linked to its Crowdcast page. The event lives in the `scf-event` block in `index.html` and starts on Hacking Managed Services (2026-11-20).
- Added `tools/set_event.py` to set or clear that block (crowdcast.io links only). A scheduled task runs it every Friday at 3 PM ET from ClickUp's Super Cyber Friday list (Episode Title before the colon, plus Event Link), skipping no-show weeks.
- The promo hides itself after 3 PM ET on the event's day, so a missed update never promotes a past show. — Rich

## 2026-11-19
- Changed Triage from a streak game to a 10-question accuracy game. Every run is 10 pairs; a wrong pick shows both scores, marks the higher card and moves on with **Next question** instead of ending the run.
- Difficulty still climbs through the same gap bands: P5 for Q1–2, P4 for Q3–4, P3 for Q5–6, P2 for Q7–8, P1 for Q9, P0 for Q10 (`PLAN`). Checked over 2,000 simulated weeks: every pair lands in its band.
- New share: "🩺 SCF Triage #N · 7/10" plus one ✅/❌ per question in order, and the link. The results screen lists all 10 pairs with both scores, plus a rank out of 10.
- The top strip shows question number, correct so far, priority and a dot per question. Official progress saves per answer (`triage3:` key), so a reload resumes at the next question. — Rich

## 2026-11-20
- Weekly CVE refresh: pulled CVEs published 2026-10-21 to 2026-11-20 from NVD. The game now has 102 CVEs, 8 of them on CISA KEV, rebuilt into `index.html` and republished to the live link.
- Wrote new Affects/Flaw/Access/Impact cards for 86 CVEs from each description and CVSS vector, and kept the existing cards for 16 that stayed in the pool. Every card passed the build's vector check.
- Skipped 7 CVEs. Description too thin: CVE-2026-54859 (Preservation) and CVE-2026-62005 (Muzicon), one-line "PHP object injection" notes that don't say what the product is; CVE-2026-76300 (Cisco hardening release, no product or impact named). Description contradicts the scoring: CVE-2026-101031 (Apache Airflow example Dag, needs a user who can trigger the Dag / scored no login), CVE-2026-123218 (IBM Aspera Faspex, KEV, described as an authorized user / scored no login), CVE-2026-121906 (Adobe Connect path traversal, described as file read only / scored full compromise), CVE-2026-133193 (JetBrains Junie GitHub Action, described as code execution / scored limited impact). — Rich

## 2026-11-20 (2)
- Phone layout (screens 700px wide or less): the two cards now sit side by side so both are on screen at once, with smaller type, bullet labels above their text and "Tap to pick". The Question/Correct/Priority strip moves below the cards, the subtitle and the "Tap a card" line are hidden, and the header is one compact row. Measured across all 102 CVEs: the tallest pair ends about 565px down the page at 360–390px wide, so the cards, verdict and Next button fit a typical phone screen without scrolling.
- Layout only: this week's pairs and saved runs are unchanged. — Rich

## 2026-11-20 (3)
- Rewrote the How to Play card from review notes: it now says a higher CVSS score means a more severe vulnerability (more risk if exploited), asks players to tap the one they think is more severe, frames the final score as how many of the 10 more severe vulnerabilities they correctly picked (e.g. 7/10), and says the pairs get progressively harder, with closer scores, as the game advances.
- The results screen opens with "You picked the more severe vulnerability in N of 10 pairs." before the rank. Copy only; pairs, saved runs and the share are unchanged. — Rich

## 2026-11-20 (4)
- New "Share image" button on the results screen. It draws a 1080×1080 PNG score card in the game's style: the score out of 10, the rank, a ✓/✗ tile per question labeled P5→P0 (easier to harder), the next Super Cyber Friday (name, date, time and Crowdcast link, from the same `scf-event` block as the promo, or "Live every Friday, 1 PM ET · cisoseries.com" when none is set) and the public game link, ciso-series.github.io/triage (`PUBLIC_URL`).
- The image opens in a dialog with Share… (phones, using the system share sheet with the image plus a text version of the result, game link and event link), Copy image, and Download. Each button only shows where the browser supports it; pressing and holding the image also saves it on phones. On the claude.ai artifact, Download goes through the viewer's save prompt (the artifact now declares the `downloads` capability). — Rich

## 2026-11-20 (5)
- The share-image window now includes a caption with clickable links, since links inside an image can't be clicked: "I picked the more severe vulnerability in 7 of 10 CVE pairs on SCF Triage #N", the ✅/❌ row, "Play this week's Triage: https://ciso-series.github.io/triage/" and the next Super Cyber Friday with its Crowdcast link (or a general "every Friday at 1 PM ET" line with cisoseries.com when no event is set).
- Share… on phones sends the image and this caption together. A new Copy caption button copies it for pasting under the image on a computer. The caption is shown in the window, and the buttons stay pinned at the bottom on small screens. — Rich
