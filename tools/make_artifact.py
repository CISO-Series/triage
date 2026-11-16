#!/usr/bin/env python3
"""Write the publishable artifact copy of index.html to .artifact/index.html (git-ignored).

The artifact host adds its own <!doctype>, <html>, <head>/<body> and charset/viewport tags,
so those are stripped. Publish the result to https://claude.ai/artifact/5uQCPWFWQWrd8q6gsmpaHF.
Run from the repo root:  python3 tools/make_artifact.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STRIP = ['<!doctype html>\n<html lang="en">\n<head>\n', '<meta charset="utf-8">\n',
         '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n',
         '</head>\n<body>\n', '</body>\n</html>\n']

html = (ROOT / "index.html").read_text()
for s in STRIP:
    if s not in html:
        sys.exit(f"Expected wrapper text not found in index.html: {s!r}")
    html = html.replace(s, "")
out = ROOT / ".artifact" / "index.html"
out.parent.mkdir(exist_ok=True)
out.write_text(html)
print(f"Wrote {out.relative_to(ROOT)} ({len(html)//1024} KB)")
