#!/usr/bin/env python3
"""Refresh Triage's CVE pool. Two steps, run from the repo root:

  1. python3 tools/fetch_cves.py fetch [--days 30]
       Pulls recent CVEs from NVD (and CISA's KEV list), picks a balanced pool of about 110,
       and writes data/pool.json with each CVE's full NVD description.

  2. Write data/bullets.json: for every CVE in the pool, three short plain-English bullets
       {"CVE-…": {"affects": "...", "flaw": "...", "access": "...", "impact": "...", "vendor": "(optional label)"}}
     These are written by a person (or Claude) from the full description, so nothing on a
     card is ever truncated. "affects" names the product (and a component or configuration only
     when it matters), with no version numbers. "access" is what an attacker needs (remote or
     local, logged in or not, user interaction). Keep each bullet to one sentence, and never include the
     CVSS score or a severity word (some NVD descriptions quote them). "vendor" overrides the
     card's label when the auto-detected one is off (e.g. "Pillow" instead of "Python").

  3. python3 tools/fetch_cves.py build
       Merges pool + bullets into the CVE-DATA block in index.html. CVEs without bullets
       are left out (and listed), so a half-written bullets file never ships cut-off text.

Source: NVD CVE API 2.0 (public, no key; requests are spaced for its rate limit).
"""
import argparse, json, random, re, sys, time, urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

NVD = "https://services.nvd.nist.gov/rest/json/cves/2.0"
KEV = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
ROOT = Path(__file__).resolve().parent.parent
INDEX, POOL, BULLETS = ROOT / "index.html", ROOT / "data" / "pool.json", ROOT / "data" / "bullets.json"
UA = {"User-Agent": "triage-game-cve-fetch"}

# Vendors/products people will recognize. Matched only at the start of a description.
VENDORS = [
    "Microsoft", "Windows", "Exchange", "SharePoint", "Azure", "Apple", "macOS", "iOS", "Google", "Chrome",
    "Android", "Cisco", "Fortinet", "FortiOS", "FortiGate", "Palo Alto Networks", "PAN-OS", "Ivanti", "VMware",
    "Citrix", "NetScaler", "Juniper", "F5", "BIG-IP", "SonicWall", "Check Point", "Zyxel", "TP-Link", "D-Link",
    "Netgear", "ASUS", "Synology", "QNAP", "Oracle", "SAP", "Adobe", "Atlassian", "Confluence", "Jira",
    "GitLab", "GitHub", "Jenkins", "Apache", "Tomcat", "Kafka", "Struts", "nginx", "OpenSSL", "OpenSSH",
    "Linux kernel", "Mozilla", "Firefox", "Thunderbird", "WordPress", "Drupal", "Joomla", "IBM", "HPE",
    "Dell", "Lenovo", "Intel", "AMD", "NVIDIA", "Qualcomm", "Samsung", "Siemens", "Schneider Electric",
    "Rockwell", "Veeam", "SolarWinds", "Zoom", "Slack", "Salesforce", "ServiceNow", "Splunk", "Elastic",
    "Kubernetes", "Docker", "Redis", "PostgreSQL", "MySQL", "MongoDB", "Grafana", "Moodle", "Roundcube",
    "Zimbra", "Progress", "MOVEit", "WS_FTP", "Kemp", "Sophos", "Trend Micro", "ESET", "Bitdefender",
    "CrowdStrike", "SentinelOne", "Okta", "Cloudflare", "AWS", "Amazon", "Node.js", "PHP", "Python",
    "Go ", "Rust", "curl", "libxml2", "Ghostscript", "ImageMagick", "FFmpeg", "Vim", "Git ", "Erlang",
    "Langflow", "Ollama", "ComfyUI", "n8n", "Next.js", "React", "Django", "Spring", "WatchGuard", "Ubiquiti",
    "MikroTik", "Hikvision", "Dahua", "Commvault", "Veritas", "CyberArk", "BeyondTrust", "SysAid",
    "ManageEngine", "Zoho", "Craft CMS", "Magento", "Adobe Commerce", "Microsoft Edge", "Office", "Outlook",
]
CANON = {"Windows": "Microsoft", "Exchange": "Microsoft", "SharePoint": "Microsoft", "Azure": "Microsoft",
         "Office": "Microsoft", "Outlook": "Microsoft", "Microsoft Edge": "Microsoft", "macOS": "Apple",
         "iOS": "Apple", "Chrome": "Google", "Android": "Google", "FortiOS": "Fortinet", "FortiGate": "Fortinet",
         "PAN-OS": "Palo Alto Networks", "NetScaler": "Citrix", "BIG-IP": "F5", "Confluence": "Atlassian",
         "Jira": "Atlassian", "Tomcat": "Apache", "Kafka": "Apache", "Struts": "Apache", "Firefox": "Mozilla",
         "Thunderbird": "Mozilla", "MOVEit": "Progress", "WS_FTP": "Progress", "Magento": "Adobe",
         "Adobe Commerce": "Adobe", "ManageEngine": "Zoho", "Go ": "Go", "Git ": "Git"}
GENERIC = {"PHP", "Python", "Go", "Rust", "Node.js", "Git", "React", "Erlang"}
PER_VENDOR = 6       # variety: no vendor floods the pool
PER_BUCKET = 14      # per 1.0-wide score band, so "higher" isn't always the safe call
WP_PLUGIN = re.compile(r"plugin for WordPress", re.I)


def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                return json.load(r)
        except Exception:  # NVD rate-limits with 403/503; back off and retry
            if i == tries - 1:
                raise
            time.sleep(10 * (i + 1))


def fetch_nvd(days):
    end = datetime.now(timezone.utc).replace(microsecond=0)
    start = end - timedelta(days=days)
    fmt = lambda d: d.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    out, idx = [], 0
    while True:
        d = get(f"{NVD}?pubStartDate={fmt(start)}&pubEndDate={fmt(end)}&resultsPerPage=2000&startIndex={idx}")
        out += d["vulnerabilities"]
        idx += d["resultsPerPage"]
        print(f"  NVD: {idx}/{d['totalResults']}", file=sys.stderr)
        if idx >= d["totalResults"] or not d["resultsPerPage"]:
            return out
        time.sleep(7)


def pick_vendor(desc):
    # Only the opening of a description names the affected product; later mentions are often
    # dependencies or examples ("...via curl") that would mislabel the card.
    head = desc[:70]
    hits = [(m.start(), v) for v in VENDORS
            for m in [re.search(r"(?<![\w-])" + re.escape(v.strip()) + r"(?![\w-])", head)] if m]
    if not hits:
        return None
    # Language names often describe the bug class ("PHP Object Injection in <product>").
    specific = [h for h in hits if h[1].strip() not in GENERIC]
    v = min(specific or hits)[1]
    return CANON.get(v, v).strip()


def cmd_fetch(a):
    kev = set()
    try:
        kev = {v["cveID"] for v in get(KEV)["vulnerabilities"]}
    except Exception as e:
        print(f"  KEV fetch failed ({e}); continuing without it", file=sys.stderr)

    cands = []
    for item in fetch_nvd(a.days):
        c = item["cve"]
        if c.get("vulnStatus") == "Rejected":
            continue
        m = c.get("metrics", {}).get("cvssMetricV31") or []
        if not m:
            continue
        m = next((x for x in m if x.get("type") == "Primary"), m[0])
        desc = re.sub(r"\s+", " ", next((d["value"] for d in c.get("descriptions", []) if d["lang"] == "en"), "")).strip()
        if not desc or "DISPUTED" in desc or WP_PLUGIN.search(desc):
            continue
        vendor = pick_vendor(desc)
        if not vendor:
            continue
        cwe = next((d["value"] for w in c.get("weaknesses", []) for d in w.get("description", [])
                    if d["value"].startswith("CWE-")), "")
        cands.append({"id": c["id"], "score": m["cvssData"]["baseScore"], "sev": m["cvssData"]["baseSeverity"],
                      "vendor": vendor, "cwe": cwe, "pub": c["published"][:10], "kev": c["id"] in kev,
                      "description": desc})

    rng = random.Random(a.seed)
    rng.shuffle(cands)
    cands.sort(key=lambda x: not x["kev"])          # exploited-in-the-wild first
    per_vendor, per_bucket, seen, pool = {}, {}, set(), []
    for x in cands:
        b = min(int(x["score"]), 9)
        key = x["description"][:60]
        if per_vendor.get(x["vendor"], 0) >= PER_VENDOR or per_bucket.get(b, 0) >= PER_BUCKET or key in seen:
            continue
        per_vendor[x["vendor"]] = per_vendor.get(x["vendor"], 0) + 1
        per_bucket[b] = per_bucket.get(b, 0) + 1
        seen.add(key)
        pool.append(x)
    pool.sort(key=lambda x: x["id"])
    POOL.parent.mkdir(exist_ok=True)
    POOL.write_text(json.dumps({"fetched": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "days": a.days,
                                "cves": pool}, indent=1, ensure_ascii=False))
    print(f"Wrote {len(pool)} CVEs ({sum(x['kev'] for x in pool)} KEV, {len(per_vendor)} vendors) to {POOL.relative_to(ROOT)}. "
          f"Score bands: " + " ".join(f"{b}:{per_bucket.get(b,0)}" for b in range(10)))
    print(f"Next: write {BULLETS.relative_to(ROOT)}, then run `build`.")


def cmd_build(a):
    pool = json.loads(POOL.read_text())
    bullets = json.loads(BULLETS.read_text()) if BULLETS.exists() else {}
    keep, missing, long = [], [], []
    for x in pool["cves"]:
        b = bullets.get(x["id"])
        if not b or not all(b.get(k) for k in ("affects", "flaw", "access", "impact")):
            missing.append(x["id"]); continue
        long += [f"{x['id']} {k}: {len(b[k])} chars" for k in ("affects", "flaw", "access", "impact") if len(b[k]) > 140]
        keep.append({k: x[k] for k in ("id", "score", "sev", "vendor", "cwe", "pub", "kev")} |
                    {"vendor": b.get("vendor") or x["vendor"],   # optional override for a better label
                     "affects": b["affects"], "flaw": b["flaw"], "access": b["access"], "impact": b["impact"]})
    data = {"fetched": pool["fetched"], "days": pool["days"], "cves": keep}
    block = "<!--CVE-DATA-->\n<script type=\"application/json\" id=\"cve-data\">" + \
            json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + \
            "</script>\n<!--/CVE-DATA-->"
    html, n = re.subn(r"<!--CVE-DATA-->.*?<!--/CVE-DATA-->", lambda _: block, INDEX.read_text(), flags=re.S)
    if n != 1:
        sys.exit("Couldn't find the CVE-DATA markers in index.html.")
    INDEX.write_text(html)
    print(f"Built {len(keep)} CVEs into index.html.")
    if missing:
        print(f"Left out {len(missing)} without bullets: {', '.join(missing)}")
    if long:
        print("Bullets over 140 chars (they'll wrap to more lines):\n  " + "\n  ".join(long))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch"); f.add_argument("--days", type=int, default=30); f.add_argument("--seed", type=int)
    sub.add_parser("build")
    a = ap.parse_args()
    {"fetch": cmd_fetch, "build": cmd_build}[a.cmd](a)


if __name__ == "__main__":
    main()
