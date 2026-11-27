#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")"
for b in f390w f606w f814w; do
 curl -LfS --retry 2 "https://hla.stsci.edu/cgi-bin/fitscut.cgi?red=hst_12267_01_wfc3_uvis_${b}&RA=51.8633&DEC=-13.4397&SIZE=1800&format=fits" -o "hla_${b}.fits"
done
sha256sum -c hla_inputs.sha256
