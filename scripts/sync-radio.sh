#!/usr/bin/env bash
# Bring junguler/m3u-radio-music-playlists' main into c4Entertainment/m3u-radio-music-playlists,
# merged on GitHub (no clone: the repository is about 2 GB), then rewrite playlists.json.
#
#   scripts/sync-radio.sh
#
# Needs gh logged in as c4Entertainment (gh auth login), or GH_TOKEN set to its token.
# A conflict stops it: merge by hand in a clone, with junguler as the remote upstream.
set -euo pipefail

FORK=repos/c4Entertainment/m3u-radio-music-playlists
UPSTREAM=repos/junguler/m3u-radio-music-playlists
if [ -z "${GH_TOKEN:-}" ] && gh auth token -u c4Entertainment >/dev/null 2>&1; then
  GH_TOKEN=$(gh auth token -u c4Entertainment)
  export GH_TOKEN
fi

sha=$(gh api "$UPSTREAM/commits/main" --jq .sha)
gh api -X PATCH "$FORK/git/refs/heads/upstream" -f sha="$sha" -F force=true --silent
echo "upstream: junguler main at ${sha:0:7}"

if out=$(gh api -X POST "$FORK/merges" -f base=main -f head=upstream \
    -f commit_message="Merge junguler/m3u-radio-music-playlists main" --jq '.sha // ""' 2>&1); then
  if [ -n "$out" ]; then echo "merged into main: ${out:0:7}"; else echo "main already has it"; fi
else
  echo "the merge did not go through: $out" >&2
  exit 1
fi

cd "$(dirname "$0")/.."
python3 scripts/catalogue.py
