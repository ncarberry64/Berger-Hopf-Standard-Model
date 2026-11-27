#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
P="$PWD"
s="$P/ciao/ciao-4.18/bin/ciao.sh"
[[ -r $s ]] || { echo 'Install CIAO with the CXC CALDB before running.' >&2; exit 2; }
set +u; source "$s" -o; set -u
for id in "$@"; do
  d="$P/$id"; mkdir -p "$d/maps" "$d/pfiles"
  export PFILES="$d/pfiles;$ASCDS_INSTALL/param"
  shopt -s nullglob
  e=("$d"/primary/*evt2.fits.gz)
  a=("$d"/primary/*asol1.fits.gz)
  b=("$d"/primary/*bpix1.fits.gz)
  m=("$d"/secondary/*msk1.fits.gz)
  [[ ${#e[@]} -eq 1 && ${#a[@]} -eq 1 && ${#b[@]} -eq 1 && ${#m[@]} -eq 1 ]]
  # Archived event calibration for map verification; replace evt2 with
  # flare-filtered chandra_repro events for the final calibrated analysis.
  fluximage "${e[0]}[ccd_id=7]" "$d/maps/" bands="0.5:2.0:1.0,3.0:7.0:4.0" asolfile="${a[0]}" badpixfile="${b[0]}" maskfile="${m[0]}" binsize=4 expmapthresh=0.5% background=none psfecf=0.95 parallel=no clobber=yes
done
