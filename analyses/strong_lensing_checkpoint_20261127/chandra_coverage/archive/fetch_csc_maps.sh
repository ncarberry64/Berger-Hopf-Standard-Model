#!/usr/bin/env bash
set -euo pipefail
grep -oE 'acisf[0-9]{5}_[0-9]{3}N[0-9]{3}_s_img3.fits' csc_calibrated/siap.xml | sort -u | sed 's/_s_img3.fits$//' |
 xargs -P 8 -I{} bash -c '
  p=$1; k=${p:5:5}; k=$((10#$k)); mkdir -p "$k/csc"
  for b in s m h; do
    f="${p}_${b}_exp3.fits"; o="$k/csc/$f"
    if ! [[ -s $o ]]; then
      curl --compressed -fLsS --retry 1 --max-time 70 "https://cda.cfa.harvard.edu/csccli/retrieveFile?filename=$f&filetype=expmap&version=cur" -o "$o.part"
      head -c 9 "$o.part"|grep -q SIMPLE
      mv "$o.part" "$o"
    fi
  done' _ {}
find . -path '*/csc/*exp3.fits' -type f | sort | xargs -r sha256sum > csc_calibrated/SHA256SUMS
