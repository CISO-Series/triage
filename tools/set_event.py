#!/usr/bin/env python3
"""Set (or clear) the "next Super Cyber Friday" promo shown when a game ends.

The promo lives in index.html between <!--SCF-EVENT--> and <!--/SCF-EVENT-->. The weekly
Friday 3 PM ET task reads ClickUp's Super Cyber Friday list and runs this.

  python3 tools/set_event.py --name "Hacking Managed Services" \\
      --url https://www.crowdcast.io/c/hacking-managed-services --date 2026-11-20 --clickup 868edr1jt
  python3 tools/set_event.py --clear      # hide the promo (no upcoming event is ready)

--name is only the "Hacking ..." part of the ClickUp Episode Title (text before the colon).
Prints "changed" or "unchanged". Run from the repo root.
"""
import argparse, json, re, sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAT = re.compile(r'(<!--SCF-EVENT--><script type="application/json" id="scf-event">)(.*?)(</script><!--/SCF-EVENT-->)', re.S)

ap = argparse.ArgumentParser()
ap.add_argument("--name"); ap.add_argument("--url"); ap.add_argument("--date")
ap.add_argument("--time", default="1 PM ET"); ap.add_argument("--clickup", default="")
ap.add_argument("--clear", action="store_true")
a = ap.parse_args()

if a.clear:
    ev = {}
else:
    if not (a.name and a.url and a.date):
        sys.exit("--name, --url and --date are required (or --clear)")
    name = a.name.split(":")[0].strip()
    if not name or len(name) > 80:
        sys.exit(f"Bad name: {a.name!r}")
    if not re.match(r"^https://(www\.)?crowdcast\.io/\S+$", a.url):
        sys.exit(f"Event link must be a crowdcast.io URL: {a.url!r}")
    date.fromisoformat(a.date)  # raises on a bad date
    ev = {"name": name, "url": a.url, "date": a.date, "time": a.time, "clickup": a.clickup}

path = ROOT / "index.html"
html = path.read_text()
m = PAT.search(html)
if not m:
    sys.exit("SCF-EVENT block not found in index.html")
new = json.dumps(ev).replace("</", "<\\/")
if json.loads(m.group(2) or "{}") == ev:
    print("unchanged"); sys.exit(0)
path.write_text(html[:m.start(2)] + new + html[m.end(2):])
print("changed")
