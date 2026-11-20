#!/usr/bin/env python3
"""Build the link-preview score cards that social networks show for a shared Triage result.

Social sites can't receive an image from a share link, but they all show the preview image
(og:image) of a link in a post. So every possible result gets its own small page whose preview
is that result's score card:

  r/<pattern>.html  e.g. r/1011011011.html: 1 = right, 0 = wrong, question 1 first.
                    Holds the og/twitter tags and sends people on to the game.
  img/<pattern>.png 1200x630 card: score, rank, a tile per question (P5 to P0).
  img/game.png      card for the game link itself (used by index.html's og:image).

1024 patterns cover every result. The cards carry no dates or event names, so they never
need rebuilding unless the design, ranks or difficulty plan change.

Run from the repo root:  python3 tools/make_cards.py
"""
from itertools import product
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "tools" / "fonts"
SITE = "https://ciso-series.github.io/triage/"
W, H, P = 1200, 630, 64

BG, RAISE, LINE = "#0c0f14", "#1a212b", "#27303c"
TEXT, MUTED, ACCENT, GOOD, BAD = "#e3e8ef", "#8a95a5", "#7ea6ff", "#4fb886", "#e5484d"
# Must match PLAN, LEVELS and RANKS in index.html.
PLAN = ["P5", "P5", "P4", "P4", "P3", "P3", "P2", "P2", "P1", "P0"]
LEVEL_COLOR = {"P5": "#4fb886", "P4": "#4aa3df", "P3": "#dcb13f", "P2": "#ef7d3c", "P1": "#e5484d", "P0": "#a77bf3"}
RANKS = [(0, "Alert Fatigue"), (3, "Tier 1 Analyst"), (5, "Incident Handler"), (7, "Vuln Manager"),
         (8, "Threat Intel Lead"), (9, "CISO Material"), (10, "CVSS Whisperer")]


def mono(px, bold=True):
    return ImageFont.truetype(str(FONTS / ("IBMPlexMono-Bold.ttf" if bold else "IBMPlexMono-Regular.ttf")), px)


def sans(px, weight=400):
    f = ImageFont.truetype(str(FONTS / "IBMPlexSans-VF.ttf"), px)
    f.set_variation_by_axes([weight, 100])   # axes: weight, width
    return f


def spaced(d, xy, text, font, fill, gap):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + gap


def frame(d, subtitle):
    d.rectangle([0, 0, W, 8], fill=ACCENT)
    spaced(d, (P, 52), "TRIAGE", mono(44), TEXT, 9)
    d.text((W - P, 62), subtitle, font=sans(24), fill=MUTED, anchor="ra")
    d.rectangle([0, H - 76, W, H], fill=RAISE)
    d.line([0, H - 76, W, H - 76], fill=LINE, width=2)
    d.text((P, H - 38), "Play free: ciso-series.github.io/triage", font=sans(26, 600), fill=TEXT, anchor="lm")
    d.text((W - P, H - 38), "Live every Friday, 1 PM ET", font=sans(24), fill=ACCENT, anchor="rm")


def result_card(pattern):
    n = pattern.count("1")
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    frame(d, "Super Cyber Friday CVSS game")
    big = mono(170)
    d.text((P - 6, 130), str(n), font=big, fill=TEXT)
    d.text((P + d.textlength(str(n), font=big), 196), "/10", font=mono(84), fill=MUTED)
    d.text((P, 320), "more severe vulnerabilities picked", font=sans(32, 600), fill=TEXT)
    rank = [name for m, name in RANKS if n >= m][-1]
    d.text((P, 364), rank, font=sans(28, 600), fill=ACCENT)
    tw, ty = 78, 420
    gap = (W - 2 * P - 10 * tw) / 9
    for k, ch in enumerate(pattern):
        x = round(P + k * (tw + gap))
        ok = ch == "1"
        d.rounded_rectangle([x, ty, x + tw, ty + tw], radius=10, fill=GOOD if ok else BAD)
        ink, w = ("#06180f" if ok else "#ffffff"), 8
        if ok:
            d.line([(x + 20, ty + 41), (x + 34, ty + 55), (x + 58, ty + 25)], fill=ink, width=w, joint="curve")
        else:
            d.line([(x + 24, ty + 24), (x + 54, ty + 54)], fill=ink, width=w)
            d.line([(x + 54, ty + 24), (x + 24, ty + 54)], fill=ink, width=w)
        d.text((x + tw / 2, ty + tw + 22), PLAN[k], font=mono(20), fill=LEVEL_COLOR[PLAN[k]], anchor="mm")
    return img


def game_card():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    frame(d, "Super Cyber Friday CVSS game")
    d.text((P, 150), "Which CVE is more severe?", font=sans(64, 700), fill=TEXT)
    d.text((P, 240), "10 pairs of real, recent CVEs. CVSS scores hidden.", font=sans(32), fill=MUTED)
    d.text((P, 286), "Pick the more severe one. It gets harder as you go.", font=sans(32), fill=MUTED)
    tw, ty = 78, 400
    gap = (W - 2 * P - 10 * tw) / 9
    for k, lv in enumerate(PLAN):
        x = round(P + k * (tw + gap))
        d.rounded_rectangle([x, ty, x + tw, ty + tw], radius=10, outline=LEVEL_COLOR[lv], width=4)
        d.text((x + tw / 2, ty + tw / 2), "?", font=mono(36), fill=LEVEL_COLOR[lv], anchor="mm")
        d.text((x + tw / 2, ty + tw + 22), lv, font=mono(20), fill=LEVEL_COLOR[lv], anchor="mm")
    return img


def save(img, path):
    img.quantize(colors=64, method=Image.Quantize.MEDIANCUT).save(path, optimize=True)


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="CISO Series">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{alt}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{image}">
<meta http-equiv="refresh" content="0; url=../">
<link rel="canonical" href="{url}">
</head>
<body style="background:#0c0f14;color:#e3e8ef;font-family:system-ui,sans-serif;padding:24px">
<p>Opening Triage… <a href="../" style="color:#7ea6ff">Play now</a></p>
<script>location.replace("../");</script>
</body>
</html>
"""


def main():
    (ROOT / "img").mkdir(exist_ok=True)
    (ROOT / "r").mkdir(exist_ok=True)
    save(game_card(), ROOT / "img" / "game.png")
    for bits in product("10", repeat=10):
        pattern = "".join(bits)
        n = pattern.count("1")
        save(result_card(pattern), ROOT / "img" / f"{pattern}.png")
        marks = "".join("✅" if c == "1" else "❌" for c in pattern)
        (ROOT / "r" / f"{pattern}.html").write_text(PAGE.format(
            title=f"SCF Triage: {n}/10",
            desc=f"{marks} I picked the more severe vulnerability in {n} of 10 CVE pairs. Can you beat it?",
            url=f"{SITE}r/{pattern}", image=f"{SITE}img/{pattern}.png",
            alt=f"Triage score card: {n} of 10 correct"))
    total = sum(f.stat().st_size for f in (ROOT / "img").glob("*.png"))
    print(f"Wrote img/game.png, 1024 result cards in img/ and 1024 pages in r/ ({total // 1024} KB of images)")


if __name__ == "__main__":
    main()
