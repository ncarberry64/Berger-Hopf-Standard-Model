#!/bin/bash
set -eu
id="$1"; u="https://cxc.cfa.harvard.edu/cdaftp/byobsid/${id: -1}/$id/primary/"
f=$(curl -fLsS --max-time 25 "$u" | grep -oE 'acisf[^"]+_fov1\.fits\.gz' | sort -u | head -1)
test -n "$f"; curl -fLsS --max-time 30 "$u$f" -o "$f"; gzip -t "$f"; printf '%s %s\n' "$id" "$u$f"
