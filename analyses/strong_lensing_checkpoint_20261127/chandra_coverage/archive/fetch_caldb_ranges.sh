#!/usr/bin/env bash
set -euo pipefail
U='https://cxc.cfa.harvard.edu/conda/ciao/noarch/caldb_main-4.12.4-0.conda'
N=2270928318
SZ=67108864
export U N SZ
mkdir -p chunks
seq 0 $(((N-1)/SZ)) | xargs -P 14 -I{} bash -c '
 i=$1; a=$((i*SZ)); b=$((a+SZ-1)); ((b<N)) || b=$((N-1))
 printf -v out "chunks/seg%03d" "$i"
 if [[ ! -s $out ]]; then
  curl -fLsS --retry 1 --max-time 100 -D "$out.hdr" -r "$a-$b" "$U?part=$a" -o "$out.part"
  grep -qi "content-range: bytes $a-$b/$N" "$out.hdr"
  [[ $(stat -c%s "$out.part") -eq $((b-a+1)) ]]
  mv "$out.part" "$out"
 fi' _ {}
cat chunks/seg[0-9][0-9][0-9] > chunks/caldb_main-4.12.4-0.conda
[[ $(stat -c%s chunks/caldb_main-4.12.4-0.conda) -eq $N ]]
hash=$(awk -F '#' '/caldb_main-4.12.4-0.conda/{print $2}' calcache/env_files/final.txt)
echo "$hash  chunks/caldb_main-4.12.4-0.conda" | md5sum -c
