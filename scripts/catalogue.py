#!/usr/bin/env python3
"""Write playlists.json, the index the site (index.html) reads.

Every .m3u in playlists/ is listed with its channels, grouped by group-title,
at its raw address in this repository. playlists/catalogue.json gives each its
title, category and description; a playlist missing there is listed under its
file name, in the category Other.

An entry in catalogue.json with a "url" is a playlist hosted elsewhere: it is
fetched to list its channels and opened at that address, so it stays as its
source keeps it.

    python3 scripts/catalogue.py
"""
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = "https://raw.githubusercontent.com/c4Entertainment/m3ustreamz/main"
EXTINF = re.compile(r'#EXTINF:-?\d+((?:\s+[\w-]+="[^"]*")*)\s*,(.*)')
GROUP = re.compile(r'group-title="([^"]*)"')


def channels(text):
    groups = {}
    for line in text.splitlines():
        m = EXTINF.match(line.strip())
        if not m:
            continue
        group = GROUP.search(m.group(1))
        name = m.group(2).strip()
        groups.setdefault(group.group(1) if group and group.group(1) else "Channels", []).append(name)
    return groups


def label(url):
    """owner/repository · file for a GitHub address, otherwise host · file."""
    m = re.match(r"https://raw\.githubusercontent\.com/([^/]+/[^/]+)/[^/]+/(?:.*/)?([^/]+)$", url)
    if m:
        return f"{m.group(1)} · {m.group(2)}"
    host, _, path = url.split("://", 1)[1].partition("/")
    return f"{host} · {path.rsplit('/', 1)[-1]}"


def write():
    meta_path = ROOT / "playlists" / "catalogue.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    playlists = []
    for path in sorted((ROOT / "playlists").glob("*.m3u")):
        about = meta.get(path.name, {})
        playlists.append({
            "title": about.get("title", path.stem.replace("-", " ").capitalize()),
            "category": about.get("category", "Other"),
            "description": about.get("description", ""),
            "url": f"{RAW}/playlists/{path.name}",
            "label": f"playlists/{path.name}",
            "groups": channels(path.read_text(encoding="utf-8", errors="replace")),
        })
    local = {Path(p["label"]).name for p in playlists}
    for key, about in meta.items():
        if "url" not in about:
            if key not in local:
                print(f"playlists/catalogue.json names {key}, which is not in playlists/")
            continue
        try:
            with urllib.request.urlopen(about["url"], timeout=60) as r:
                text = r.read().decode("utf-8", errors="replace")
        except Exception as e:
            print(f"{key}: {about['url']} did not load ({e}); left out")
            continue
        playlists.append({
            "title": about.get("title", key),
            "category": about.get("category", "Other"),
            "description": about.get("description", ""),
            "url": about["url"],
            "label": label(about["url"]),
            "groups": channels(text),
        })
    out = ROOT / "playlists.json"
    out.write_text(json.dumps({"playlists": playlists}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"playlists.json: {len(playlists)} playlists")


if __name__ == "__main__":
    write()
