# Frozen real-observation pilot, 22 October 2026

The software ingested and processed all **100 previously published OGLE-III
events and 76,344 native measurements**, with no clipping, thinning, event
replacement or fabricated resolved-image data. All 109 raw-file hashes and
the frozen sample hash were checked before and after fitting. Four literal
publisher warning annotations and OGLE3-ULENS-0337 were retained.

The simple rectilinear point-source/point-lens model with the native diagonal
magnitude-noise assumption was inadequate for **89 events**. Eleven passed
the predeclared chi-square screen; passing that screen alone did not clear
blending, sampling, residual correlation or numerical-bound concerns. Every
event remains in the results, including all inadequate and unresolved cases.

Two historical events passed all conservative, predeclared photometric
follow-up screens. **Neither is a measured black hole or a new event.**

| Historical event | Fitted tE, days | Local quadratic sigma, days | Conditional profile level-1 crossings, days | Native chi-square / dof |
| --- | ---: | ---: | --- | --- |
| OGLE3-ULENS-0585 | 268.173 | 74.326 | 202.907–344.964 | 748.247 / 729 |
| OGLE3-ULENS-3092 | 187.730 | 19.808 | 170.065–208.639 | 805.423 / 734 |

The profile endpoints are nuisance-reoptimized reference-level crossings,
not intervals with calibrated coverage. Ninety-one events had both crossings
within the declared search grid; nine remained unresolved. Local errors and
all profiles condition on the model and assumed independent native errors.

**What is identified:** the light-curve peak epoch, relative Einstein crossing
time, dimensionless impact parameter and instrument brightness/blend parameters
can be constrained under an adequate model. Some events still have severe
timescale/blending or sampling degeneracies. Mass, lens/source distance, angular
Einstein radius, microlens parallax, absolute proper motion, physical boundary
radius and horizon status remain unavailable in every pilot fit. Long duration
alone measures no lens mass.

**What follow-up means:** these are historical peaks, so the shortlist concerns
archival calibration/modeling and feasibility of high-resolution source/lens
association. It does not predict an ongoing outburst. The ranking follows the
frozen quality/precision/timescale rule and is not a black-hole probability.
No mass-supported or potentially new black-hole interpretation was established.

## Results and evidence

- [Complete 100-event table with literature annotations](literature_annotations_v1/all_100_results.csv), [JSON](literature_annotations_v1/all_100_results.json).
- [Two-event annotated follow-up ranking](literature_annotations_v1/followup_ranking.csv), [JSON](literature_annotations_v1/followup_ranking.json).
- [Original frozen analysis table](derived_v1/all_100_results.csv), [summary](derived_v1/summary.json), [unchanged ranking](derived_v1/followup_ranking.json).
- [100 residual plots](derived_v1/residuals/) and [100 compact diagnostics, profiles and sensitivities](derived_v1/diagnostics/).
- [Separate 2022 known-system benchmark](derived_v1/historical_benchmark/summary.json), with five instrument/objective residual plots in that directory.
- [Frozen protocol](protocol_v1.json), [exact hash](protocol_v1.sha256), [driver](run_pilot.py) and [derived-output manifest](derived_v1_manifest.json).
- The native-schema and likelihood contract is `UNRESOLVED_OBSERVATIONS.md` under development `product/` or formal `products/blackhole_tracker/`.
- [Synthetic validation at actual cadence](SYNTHETIC_VALIDATION_V1.json): independent analytical checks, two noiseless recoveries, 16 noisy trials and a faint-source nuisance profile. These trials do not establish calibrated coverage.
- [Post-analysis literature annotation receipt](LITERATURE_ANNOTATION_RECEIPT.json): no refitting or reranking, original numerical fields preserved.

Full native inputs, all original source-row identities, predictions/residuals,
all 300 pilot fit JSON files and the benchmark replay inputs were kept outside
source Git at the recorded private output location in `derived_v1/summary.json`.
The public derived artifacts contain no table of native per-point observations.
Raw bytes remain external; acquisition URLs, hashes, selection and citations
are in [data provenance](data_provenance/).

## Prior literature and aliases

The [all-event primary-cohort crossmatch](literature_annotations_v1/prior_cohort_crossmatch.json)
identifies four overlaps with the published 59-event OGLE-III parallax cohort:
0264=PAR-07/OGLE-2005-BLG-474; 0568=PAR-21/OGLE-2006-BLG-005;
2122=PAR-37; and 3404=PAR-17/OGLE-2008-BLG-157. The match uses database IDs,
aliases and coordinates, not event duration. PAR-07 already has a historical
prior-dependent remnant interpretation and later reanalysis; those published
mass estimates were not imported as measurements into this pilot.

The [two-target audit](literature_annotations_v1/target_prior_literature.json)
preserves queries, primary URLs, archived-source hashes and scope limits.
0585 is the published database object BLG122.6.83113; bounded identifier,
database-ID and coordinate searches did not locate a specific lens-interpretation
paper. Search absence does not establish novelty. 3092 is OGLE-2007-BLG-057,
also MOA-2007-BLG-027 / MOA-2007-BLG-27, discussed in
[Yock (2008)](https://arxiv.org/abs/0805.1775). Its official EWS and optimized
reduction have different star IDs, retained with their reduction provenance.
Neither target has a black-hole mass from this run. Crowded-field physical
associations and complete novelty clearance remain unresolved.

## The historical known-system benchmark

The separate OGLE-2011-BLG-0462 / MOA-2011-BLG-191 benchmark used the actual
2022 Zenodo v1.0.0 observations: 15,545 OGLE and 46,040 MOA photometric rows.
The joint native-noise fit gives tE=282.796 days and chi-square/dof=2.4515;
OGLE-only gives 270.791 days, MOA-only 299.061 days, the equal-instrument
objective sensitivity 276.472 days and signed-blend sensitivity 282.796 days.
All five screens are inadequate, with temporal/seasonal residual flags.
Convergence and ingestion therefore do not establish successful physical
recovery on this benchmark.

These photometry-only screens are **not** the original publication's joint
astrometric default-weight/equal-weight analyses. The equal-instrument run is
labelled as its own objective sensitivity; it is not tuned to a published mass.
Later changed reductions are not recovery targets for these older bytes.

The 16 HST rows represent eight shared epochs in two filters. Native positions
and times were ingested, but the README does not define the numeric epoch
origin or complete frame/alignment provenance. Independent exposure metadata
also show that simply naming these numbers MJD does not recover the observing
times. No guessed offset, clock conversion or historical cross-filter shift
was applied. Precision annual parallax, composed joint astrometry and mass
inference remain specifically unresolved pending the original export-time
mapping, calibration and an appropriate shared-frame/noise model.

## Reproduce without changing the checkout

The internally frozen protocol preceded the real fits. It uses development
version 0.2.0rc3 and exact hashes of the three scientific kernels plus the driver;
later user-interface/package-provenance edits do not pretend to be those earlier
package bytes. The frozen driver has its original development-tree layout and
must retain its exact bytes. The wrapper constructs that layout in a checked
temporary workspace, restores only the four small own-code snapshots and
verifies the protocol/kernel hashes. It leaves the current product untouched.

Install the release and its dependencies first, or pass `--product-root` pointing
to the current directory containing `bhtracker`. From this directory:

```powershell
python reproduce_frozen_pilot.py --verify-only --data-root C:/path/to/data
python reproduce_frozen_pilot.py --data-root C:/path/to/data --output C:/path/to/fresh_reproduction
```

The verification-only path was exercised against all supplied raw files and
reproduced the exact 100-event selection without another scientific fit. A full
reproduction writes the same complete accounting into the fresh external output
directory, including a copy of its derived artifacts. It refuses an existing
started analysis directory. Set the data root to the folder containing
`download_manifest.json`, `pilot_selection.json` and `raw/`.

To refetch the exact pinned raw observations into a separate folder:

```powershell
python data_provenance/data_tools.py --data-root data_provenance refetch --destination C:/path/to/data
python data_provenance/data_tools.py --data-root C:/path/to/data verify
```

The bounded helper refuses changed bytes. Retain the source acknowledgments and
rights statements; public download access is not a blanket software license.
No native OGLE measurements were bundled into the public software release.

After the completed run, the optional angular/parallax **docstrings** were
qualified to distinguish Gould lens-relative-source trajectory coordinates from
source-minus-lens sky coordinates, and to require a consistent heliocentric
ephemeris origin. [The receipt](POST_PILOT_OPTIONAL_DOCS_PATCH.json) records
before/after hashes and exact executable-AST identity excluding docstrings;
the PSPL likelihood and native parser remained byte-identical. The original
small code files are retained in [frozen sources](frozen_v1_sources/MANIFEST.json)
for exact reproduction. No optional joint fit is claimed.

## BHSM meaning

The same ordinary compact-lens optical response retains the explicit BHSM
Einstein/GHY interpretation and is counted once. This route infers no BHSM core
state, physical boundary deformation, encapsulation threshold or galaxy
dark-matter mechanism from a light curve. Boundary energy is withheld when the
mass and radius are unresolved. The sample is enriched for published long
events and is not a completeness, abundance or black-hole population estimate.
