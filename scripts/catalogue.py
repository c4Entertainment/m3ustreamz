#!/usr/bin/env python3
"""Write playlists.json, the index the site (index.html) reads.

Every .m3u in playlists/ is listed with its channels, grouped by group-title.
Its title, category and description come from playlists/catalogue.json; a
playlist missing there is listed under its file name, in the category Other.

    python3 scripts/catalogue.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXTINF = re.compile(r'#EXTINF:-?\d+((?:\s+[\w-]+="[^"]*")*)\s*,(.*)')
GROUP = re.compile(r'group-title="([^"]*)"')


def channels(path):
    groups = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = EXTINF.match(line.strip())
        if not m:
            continue
        group = GROUP.search(m.group(1))
        name = m.group(2).strip()
        groups.setdefault(group.group(1) if group and group.group(1) else "Channels", []).append(name)
    return groups


def write():
    meta_path = ROOT / "playlists" / "catalogue.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    playlists = []
    for path in sorted((ROOT / "playlists").glob("*.m3u")):
        about = meta.get(path.name, {})
        playlists.append({
            "file": f"playlists/{path.name}",
            "title": about.get("title", path.stem.replace("-", " ").capitalize()),
            "category": about.get("category", "Other"),
            "description": about.get("description", ""),
            "groups": channels(path),
        })
    for name in sorted(set(meta) - {p["file"].split("/", 1)[1] for p in playlists}):
        print(f"playlists/catalogue.json names {name}, which is not in playlists/")
    out = ROOT / "playlists.json"
    out.write_text(json.dumps({"playlists": playlists}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"playlists.json: {len(playlists)} playlists")


if __name__ == "__main__":
    write()
