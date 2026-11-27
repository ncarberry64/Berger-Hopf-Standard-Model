#!/usr/bin/env bash
set -eo pipefail
for id in 7761 11550 11551 11552 14489 14490 14491 14492 14493 14494 23798; do
  b=https://cxc.cfa.harvard.edu/cdaftp/byobsid/${id: -1}/$id
  mkdir -p "$id/primary"
  (
    curl -fLsS --retry 1 --max-time 20 "$b/primary/" -o "$id/index.html"
    mapfile -t files < <(grep -oE 'href="[^"]+\.fits\.gz"' "$id/index.html"|cut -d'"' -f2|grep -E '(evt2|asol1|bpix1)\.fits\.gz')
    for f in "${files[@]}"; do
      out="$id/primary/$f"
      [ -s "$out" ] || { curl -fLsS --retry 1 --max-time 110 "$b/primary/$f" -o "$out.part"; gzip -t "$out.part"; mv "$out.part" "$out"; }
    done
    du -sh "$id/primary"
  ) &
  if (( $(jobs -pr|wc -l) >= 4 )); then wait -n; fi
done
wait
find . -path '*/primary/*.fits.gz' | sort | xargs -r sha256sum > SHA256SUMS
