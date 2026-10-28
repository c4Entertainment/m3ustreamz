# m3ustreamz

Curated M3U playlists of free, legal streams, built from [iptv-org](https://github.com/iptv-org/iptv) and other public lists.

| Playlist | What it carries |
| --- | --- |
| [`playlists/trace-afrobeat.m3u`](playlists/trace-afrobeat.m3u) | Every Trace channel iptv-org lists (one entry per feed), and Afrobeat TV |
| [`playlists/bbc-radio.m3u`](playlists/bbc-radio.m3u) | BBC Radio's 64 national, nations and local stations over HLS, from [bpsib's gist](https://gist.github.com/bpsib/67089b959e4fa898af69fea59ad74bc3) (HTTPS; UK Only stations play only in the UK) |
| [`playlists/bbc-radio-lsn.m3u`](playlists/bbc-radio-lsn.m3u) | The same stations through lsn.lv, from the same gist |

The site also lists playlists hosted elsewhere, opened at their own address so they stay as their
source keeps them: the 31 You Radio playlists in
[laurentjuma/m3u-radio-music-playlists](https://github.com/laurentjuma/m3u-radio-music-playlists/tree/main/you_radio/m3u/stations).

## The site

`index.html` lists every playlist, searchable by playlist and channel, each with **Open in Mediagg**
(`https://mediagg.app/open/?url=<the playlist's raw address>`) and a copy icon for its address. It
reads `playlists.json`, which `scripts/catalogue.py` writes from `playlists/` and the titles,
categories and descriptions in `playlists/catalogue.json`. GitHub Pages serves it from the root of
`main`. To look at it locally:

```sh
python3 scripts/catalogue.py && python3 -m http.server 8000   # http://localhost:8000
```

A new playlist: add the `.m3u` to `playlists/`, its entry to `playlists/catalogue.json`, run
`scripts/catalogue.py` and commit `playlists.json` with it. A playlist hosted elsewhere needs only its entry,
with its address as `url`; `catalogue.py` fetches it to list its channels.

## Rebuilding

```sh
python3 scripts/build.py
```

It also rewrites `playlists.json`.

The script reads the iptv-org API and keeps one stream per channel feed: the first that answers
with an HLS playlist, otherwise the first one listed. The probe sends no User-Agent of its own:
the official `channels.trace.plus` streams answer 403 to a bare `Mozilla/5.0` one.
