#!/usr/bin/env python3
"""Build the curated playlists in playlists/ from the iptv-org API.

Each playlist names the iptv-org channels it takes. For every feed of those
channels it keeps one stream: the first that answers with an HLS playlist,
otherwise the first listed (it may be geo-blocked here and play elsewhere).
Streams iptv-org labels Geo-blocked are tried last.

    python3 scripts/build.py            # rebuild every playlist
    python3 scripts/build.py --no-probe # trust the listed order, skip probing
"""
import concurrent.futures
import json
import sys
import urllib.request
from pathlib import Path

API = "https://iptv-org.github.io/api"
ROOT = Path(__file__).resolve().parent.parent

PLAYLISTS = {
    "trace-afrobeat.m3u": [
        ("Trace", lambda c: c["name"].startswith("Trace ")),
        ("Afrobeat", lambda c: c["id"] == "AfrobeatTVEntertainment.uk"),
    ],
}


def fetch(name):
    with urllib.request.urlopen(f"{API}/{name}.json", timeout=60) as r:
        return json.load(r)


def plays(url):
    try:
        with urllib.request.urlopen(url, timeout=12) as r:
            return b"#EXTM3U" in r.read(4096)
    except Exception:
        return False


def main():
    probe = "--no-probe" not in sys.argv
    channels = fetch("channels")
    streams = fetch("streams")
    feeds = {(f["channel"], f["id"]): f for f in fetch("feeds")}
    logos = {}
    for logo in fetch("logos"):
        logos.setdefault((logo["channel"], logo.get("feed")), logo["url"])

    for filename, groups in PLAYLISTS.items():
        picked = []
        for group, match in groups:
            for c in sorted(channels, key=lambda c: c["name"]):
                if c.get("closed") or not match(c):
                    continue
                by_feed = {}
                for s in streams:
                    if s["channel"] == c["id"]:
                        by_feed.setdefault(s["feed"], []).append(s)
                for feed, candidates in by_feed.items():
                    picked.append((group, c, feed, candidates))

        if probe:
            urls = {s["url"] for *_, cands in picked for s in cands}
            with concurrent.futures.ThreadPoolExecutor(16) as ex:
                live = dict(zip(urls, ex.map(plays, urls)))
        else:
            live = {}

        lines = ["#EXTM3U"]
        for group, c, feed, candidates in picked:
            candidates.sort(key=lambda s: "Geo-blocked" in s["labels"])
            stream = next((s for s in candidates if live.get(s["url"])), candidates[0])
            f = feeds.get((c["id"], feed), {})
            name = c["name"] if f.get("is_main", True) else f"{c['name']} {f.get('name', feed)}"
            logo = logos.get((c["id"], feed)) or logos.get((c["id"], None), "")
            attrs = f'tvg-id="{c["id"]}@{feed}" tvg-logo="{logo}" group-title="{group}"'
            lines.append(f"#EXTINF:-1 {attrs},{name}")
            if stream.get("referrer"):
                lines.append(f"#EXTVLCOPT:http-referrer={stream['referrer']}")
            if stream.get("user_agent"):
                lines.append(f"#EXTVLCOPT:http-user-agent={stream['user_agent']}")
            lines.append(stream["url"])
        (ROOT / "playlists" / filename).write_text("\n".join(lines) + "\n")
        print(f"playlists/{filename}: {len(picked)} entries")


if __name__ == "__main__":
    main()
