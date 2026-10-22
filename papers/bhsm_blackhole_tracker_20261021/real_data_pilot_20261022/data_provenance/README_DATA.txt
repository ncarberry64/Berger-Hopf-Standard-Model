REAL OBSERVATIONS FOR THE BHSM BLACK HOLE TRACKER PILOT
Acquired and structurally checked: 22 October 2026

STATUS

109 downloaded files, 6,755,857 raw bytes. Every file has a recorded SHA-256.
All five Zenodo files also match the MD5 published by that archive. Raw files
are preserved byte for byte. No new scientific fits or classifications were run.
See download_manifest.json and validation_report.json for exact evidence.

The observations require an unresolved-light-curve/astrometry model. They cannot
be converted honestly into the existing resolved-two-image tracker schema merely
by renaming columns. Apparent stellar brightness, individual image brightness,
image separation and interimage delay are different observables.

1. PUBLISHED OGLE-III PARENT CATALOG AND FIXED PILOT

Source: the official archive associated with Wyrzykowski et al. (2015),
ApJS 216, 12; DOI 10.1088/0067-0049/216/1/12.
Directory: https://ftp.astrouw.edu.pl/ogle/ogle3/blg_tau/

The basic and full catalog tables each contain the same 3,560 class-A events.
These are metadata/previous fit summaries, not independent new measurements.
The optimized light curves for a declared 100-event subset are supplied.

Pilot ID: BHSM-OGLE3-pilot-20261022-v1
Selection: all 75 parent events with published tE >=150 days, plus 25 controls
from the 2,272 parent events with 10<=tE<50 days. For the controls, sort by
SHA256 of the ASCII string
  BHSM-OGLE3-pilot-20261022-v1|OGLE3-ULENS-nnnn
using the four-digit zero-padded catalog event number; tie by numeric ID.
Take the first 25. The complete selected list is in pilot_selection.json.

The SHA-256 of canonical selected IDs sorted numerically, joined by LF and
including a final LF, is:
0cf5dbf714a99567ccfc8448f53560333ed4597115a2801138ac707926a8a4a7

This selection preceded any new fitting. It is an internally frozen selection,
not a public preregistration. Retain every selected event in analysis accounting.
The controls compare ordinary-duration events; their lens types are not known
negative labels. The included published events are not newly discovered events.

Parent published timescale counts, calculated from the downloaded table:
  tE>=100 days: 216; tE>=150 days: 75; tE>=200 days: 39.
The 100-event pilot contains 39 at >=200 days, 36 at 150–200 days, and 25 controls.
The standard-event parent catalog excludes strong-parallax/exotic cases and
had a 1<tE<400-day selection requirement. This further enriched subset is not
a complete black-hole search sample and cannot support abundance estimates.

2. OGLE SCHEMAS AND PARSER DETAILS

Optimized photometry: three whitespace-separated numeric fields:
  HJD-2450000 [days], I-band magnitude [mag], magnitude uncertainty [mag].
The underlying clock scale of HJD is not explicitly stated in the README.
Preserve the heliocentric convention and offset. Do not casually rename HJD
as MJD/BJD/TCB. These optimized reductions are not nightly averaged and already
have published error corrections; do not apply the same correction again.

The supplied 100 light curves contain 76,344 numeric measurements. All numeric
values are finite and all magnitude errors positive. Structural validation is
not evidence that the data are free of blending, outliers or systematics.

Actual full-catalog physical column numbers (1-based):
  1:event number;2:RA J2000;3:Dec J2000;4:field.chip;5:star number;
  6:t0;7–8:signed t0 error offsets;9:tE;10–11:signed tE error offsets;
  12:u0;13–14:signed u0 error offsets;15:source flux fraction;
  16–17:its signed error offsets;18:baseline I magnitude;19–20:its errors;
  21:chi-square;22:degrees of freedom;23:V magnitude;24:V uncertainty;
  25:EWS alias(es);26:overlap alias.

The publisher README combines field/chip/star as one field in its description,
so its subsequent numbers differ by one. Its baseline-magnitude uncertainty
labels also appear copied from t0; retain the original README and document the
parser interpretation. V=99.999 and V-error=9.999 are missing-value sentinels
(946 paired occurrences), not meaningful measurements.

The published class-A catalog is already deduplicated. Overlap aliases identify
another field's observation, not an extra primary event to delete. Preserve
OGLE3-ULENS-0337, which has such an alias. Multiple EWS aliases in one row
likewise do not mean multiple independent events.

Four files have an exact trailing source annotation:
  ERROR: data not sorted in HJD!
Their mappings and source line numbers are:
  OGLE3-ULENS-2756 photBLG216.1.I.51236.dat   743 numeric rows;line744.
  OGLE3-ULENS-2773 photBLG216.3.I.161902.dat  750 numeric rows;line751.
  OGLE3-ULENS-2781 photBLG216.4.I.210984.dat  748 numeric rows;line749.
  OGLE3-ULENS-2787 photBLG216.5.I.97549.dat   747 numeric rows;line748.
The delivered numeric rows in all four are strictly increasing with no repeated
timestamps or identical rows. Preserve the warning as a source annotation and
all numeric measurements. No sorting/deduplication is needed for these files.
Do not guess why the upstream warning was emitted. The parser recognizes this
exact line; other malformed content is not silently ignored.

3. SEPARATE HISTORICAL KNOWN-SYSTEM BENCHMARK

Source: Lam et al. author-deposited observations, Zenodo 6607578,
version 1.0.0, released 10 June 2022; DOI 10.5281/zenodo.6607578.
Physical event: OGLE-2011-BLG-0462 / MOA-2011-BLG-191.

Included actual measurement files:
  OGLE-2011-BLG-0462.dat: 15,545 rows; HJD 2455260.85488–2458787.50868.
  MOA-2011-BLG-191.dat: 46,040 rows; HJD 2453824.09254–2459441.11699.
  OB110462_HST_F606W.dat: 8 rows.
  OB110462_HST_F814W.dat: 8 rows.
The author README is included. Posterior FITS files and simulations were not
downloaded or supplied as observations.

OGLE/MOA columns: hjd,mag,mag_err. OGLE is OGLE-IV I-band; MOA magnitudes are
calibrated to OGLE-III. Use instrument-specific source/blend flux parameters.

HST columns: t,x,x_err,y,y_err,mag,mag_err. Positions/errors are relative
RA/Dec in milliarcseconds; magnitudes are Vega. The time values range from
55781.358304794485 to 59487.895291095905 in both filters. These are 8 shared
epochs, not 16 independent visits. Each file has strictly increasing times,
finite numeric values and positive errors.

The author README calls t "UTC" but does not define its numeric epoch origin.
Its separate reference to MJD describes posterior t0, not measurement t.
Verify observation-time conventions through original reduction/export code
or exposure metadata before precision joint inference. Do not assign an MJD
origin, add a day or convert clocks by guesswork. HJD's clock scale also needs
documentation for precision parallax inference. A relative-time rectilinear
photometric screen can state its limited timing assumptions and proceed.

The HST positions may already contain cross-filter alignment corrections.
Check before applying historical offsets again. A supplied full covariance
matrix is absent; diagonal noise, frame uncertainty and inter-filter dependence
are modeling assumptions/issues, not measured covariance supplied by the archive.

This is a versioned historical recovery benchmark. The 2023 and 2025 reanalyses
changed reductions/observations; their mass estimates are not required fit
targets for these 2022 bytes. Never tune the model solely to recover a desired mass.

4. WHAT A SEARCH CAN CONCLUDE

Photometric duration depends on lens mass, geometry and relative motion.
Without additional information these quantities are degenerate. An interesting
long event is a follow-up target, not a measured black hole. Astrometric angular
scale plus microlensing parallax can constrain mass under a suitable model;
the relevant uncertainties, degeneracies and systematics still matter.

The current package establishes that real measurements are available and
reproducibly selected. It does not establish a new black-hole candidate or
validate a BHSM-specific mechanism. The Codex task defines analysis, candidate
checks and the separation of those claims.

5. PROVENANCE, REPLAY AND ATTRIBUTION

download_manifest.json retains each URL, retrieval time, HTTP metadata, byte
count and hash. pilot_selection.json preserves the parent-table hash, selection
rule and event identities. validation_report.json records actual checks.
scripts/data_tools.py verifies these files offline and can refetch identical
bytes into a separate folder. Refetching is optional; actual files are present.

Preserve source-specific acknowledgments and citations in SOURCE_CITATIONS.txt
and the author READMEs. Public accessibility is not an inferred blanket CC or
software license. Before public redistribution, check the source terms for
that distribution. No researcher, journal or collaboration was contacted.
