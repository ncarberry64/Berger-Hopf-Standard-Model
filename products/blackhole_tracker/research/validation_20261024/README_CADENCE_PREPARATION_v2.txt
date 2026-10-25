Portable two-cadence preparation kit — no observations included

This kit supplies exact frozen selection/download metadata and a small standard-
library acquisition helper for OGLE3-ULENS-0033 and OGLE3-ULENS-0127. These are the
two prospectively selected cadence parents of the synthetic calibration study.
The kit does not include native brightness or prepared parents, grant a data
license, fit measured brightness, create a new BH identification, or clear the
paper's publication hold. Provider availability and terms remain external.

1. Verify the metadata / inspect the exact two URLs, with no network:
   python -I -B fetch_calibration_cadences_v2.py

2. Explicitly acquire the two original files into a NEW external directory:
   python -I -B fetch_calibration_cadences_v2.py --download --data-root NEW_DATA
   The helper makes at most two HTTPS requests to the pinned original provider,
   follows no redirects, accepts only exact recorded bytes and SHA256, preserves
   partial downloads and failures, and never replaces an existing data root.
   Timeout defaults10s; each file's deadline60s is checked before AND after each
   bounded read. Late bytes/EOF are retained but refused. A blocking read can
   extend failure reporting past that deadline by at most its socket timeout.
   Unexpected/changed content is unresolved, never silently substituted.

3. Recheck already acquired data, with no network and no writes:
   python -I -B fetch_calibration_cadences_v2.py --verify-existing --data-root NEW_DATA
   Existing data roots must contain both metadata files and the two raw paths.

The helper finds cadence_metadata_v1 next to itself; if installed as a source
script under product/scripts, it also supports the sibling location
product/research/validation_20261024/cadence_metadata_v1. --metadata-root explicitly
selects a relocated copy. Identity is checked against embedded SHA256 pins.
All runtime arguments are portable paths; no original C: path is needed.

4. From a matching unpacked product source distribution, install declared package
   dependencies into a fresh environment. Use the same preserved calibration
   sources if reproducing this study; later kernels define another study.
   python -I -B product/scripts/calibrate_rc7.py prepare --data-root NEW_DATA --output NEW_PREPARATION
   This ONLY parses/hash-pins the two cadence parents and prepares a NEW freeze;
   it does not run the 4,608 synthetic datasets or fit native brightness.
   Check exact argparse help if the enclosing distribution renames product/.

Expected parent payload SHA256 under the preserved study parser/serializer:
  CADENCE_PARENT_0.json  f8a5dfeb6f7be238387ef07d110c16aaf6e1ca6f3fd1ae6372814d9823d0ec93
  CADENCE_PARENT_1.json  20888274ab66dedae333c42b1503076f7dc00539eb7072535ae93cf9f2c761ca
The preserved observation loader uses the raw filename, not its absolute path,
in the parent payload. Relocation alone should preserve these two payload hashes
under the same parser and serializer. The new execution freeze does record new
absolute source/raw/parent paths and runtime, so its full hash must differ. If a
parent hash differs, retain it as unresolved and inspect parser/serialization
changes; never edit the old parent/freeze to make it agree. A NEW execution
freeze/admission is required before any new study campaign. Native files need
remain external; never add the fetched files or native parents to public Git.

Provider/source records: CADENCE_SOURCE_MAP_v1.json preserves the exact original
download entries and selected catalog rows. The supplied download_manifest.json
explicitly states: no blanket data license is inferred from public accessibility;
preserve attribution and source-specific terms. These are optimized OGLE-III
2015-release light curves, not manufactured resolved positions or flux ratios.

PUBLIC evidence transport retains all synthetic generated inputs/outcomes,
failures, plots, source pins and source snapshot except six declared copies of
four native entities (two originals/two prepared parents). LOCAL complete
transport retains all original bytes separately. The public archive is therefore
synthetic-evidence-complete, not original-native-complete. Hash verification is
content integrity, not independent scientific validity or provider authenticity.
