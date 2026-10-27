# m3ustreamz

Curated M3U playlists of free, legal streams, built from [iptv-org](https://github.com/iptv-org/iptv).

| Playlist | What it carries |
| --- | --- |
| [`playlists/trace-afrobeat.m3u`](playlists/trace-afrobeat.m3u) | Every Trace channel iptv-org lists (one entry per feed), and Afrobeat TV |

## Rebuilding

```sh
python3 scripts/build.py
```

The script reads the iptv-org API and keeps one stream per channel feed: the first that answers
with an HLS playlist, otherwise the first one listed. The probe sends no User-Agent of its own:
the official `channels.trace.plus` streams answer 403 to a bare `Mozilla/5.0` one.
