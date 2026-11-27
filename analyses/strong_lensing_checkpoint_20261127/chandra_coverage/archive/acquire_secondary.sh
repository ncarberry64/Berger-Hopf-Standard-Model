#!/usr/bin/env bash
set -eo pipefail
for id in 7761 11550 11551 11552 14489 14490 14491 14492 14493 14494 23798; do
  b=https://cxc.cfa.harvard.edu/cdaftp/byobsid/${id: -1}/$id
  mkdir -p "$id/secondary"
  (
    curl -fLsS --retry 1 --max-time 20 "$b/secondary/" -o "$id/secondary_index.html"
    mapfile -t files < <(grep -oE 'href="[^"]+\.fits\.gz"' "$id/secondary_index.html"|cut -d'"' -f2|grep -E '(evt1|flt1|msk1|mtl1|stat1|pbk0)\.fits\.gz')
    for f in "${files[@]}"; do
      out="$id/secondary/$f"
      [ -s "$out" ] || { curl -fLsS --retry 1 --max-time 110 "$b/secondary/$f" -o "$out.part"; gzip -t "$out.part"; mv "$out.part" "$out"; }
    done
    du -sh "$id/secondary"
  ) &
  if (( $(jobs -pr|wc -l) >= 4 )); then wait -n; fi
done
wait
find . -path '*/secondary/*.fits.gz' | sort | xargs -r sha256sum > SHA256SUMS.secondary
