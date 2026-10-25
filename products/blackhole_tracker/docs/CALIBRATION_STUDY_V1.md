# Current-kernel calibration: prospective study v1

This separately versioned experiment evaluates the corrected resolved-image
inference and the native rectilinear photometry workflow. It retains the old
64-draw calibration as history rather than relabeling it as current evidence.
The complete specification is `research/validation_20261024/PROTOCOL_v1.json`;
the independently written generators and scorer are alongside it. The driver
is `scripts/calibrate_rc7.py`.

The study is **synthetic**, including when it uses authentic observing times
and reported magnitude errors. It does not refit the original brightness in
those cadence files, manufacture resolved measurements of a real event, or
establish a black-hole identification. The authentic known-system analysis is
a different experiment with its own observational version and calibration.

## What is measured

| Component | Fixed experiment and accounting |
| --- | --- |
| Resolved local uncertainty | Four blocks of 512 realizations: regular 10-solar-mass, the same track reported at a distant reference epoch with a different numerical mass scale, 0.05-solar-mass, and a high-mass exterior. Distances and dense measurement covariance are explicitly supplied hypothetical inputs. |
| Motion and ordinary-model controls | 256 stationary tracks; two repeated-epoch blocks of 64; 128 ordinary-shear datasets each fitted with and without shear. |
| Native-magnitude uncertainty | 512 matching point-source/point-lens realizations on each of two fixed actual cadence/error patterns, plus the generating-timescale profile ordinate in every such case. |
| Model/noise competitors | On each cadence: 128 constant sources, 128 periodic variables, 128 two-source microlensing cases, and 128 point-lens cases with correlated Gaussian noise. Their parameters are engineering controls, not a population sample. |

The total is **4,608 distinct generated datasets, 4,736 fits and 1,024
generating-timescale profile evaluations**. All planned cases remain in the
accounting, including generation, search, profile, serialization and budget
failures. A repeated generation at the identical seed verifies reproducibility
and counts as one realization. Generating truth is kept in a sidecar and is
not passed as a free-fit initializer.

The two cadence parents are the first identifiers in each stratum of the
previously frozen 100-event selection: OGLE3-ULENS-0033 and OGLE3-ULENS-0127.
Selection ignores the measured brightness, new fit results and shortlist.
All parent times, positive errors and row identities are retained. Every
daughter brightness is generated, its identifiers are explicitly synthetic,
and its original row identity is retained as a cadence-parent reference.
Underlying photometric clocks remain `UNSPECIFIED`; relative-time fitting is
not a precision parallax calculation.

Coverage of local estimator intervals **before** goodness-of-fit selection is
reported separately from the joint outcome of being usable and covering truth
**after** that selection. Exact binomial uncertainty and unresolved completion
bounds accompany the counts. Twenty resolved local-parameter tests, six native
local-parameter tests and two timescale reference-set tests form the frozen
28-test family, with Bonferroni family alpha 0.01. Profile membership at the
generating value is not an estimate of finite interval endpoints, and an
unresolved or boundary ordinate is not silently accepted.

The motion cut is a two-component Mahalanobis signal-to-noise magnitude of 5.
This threshold does not by itself establish the conventional one-dimensional
five-sigma false-alarm probability. The stationary controls report their actual
finite-sample rate and uncertainty; a modest zero-count experiment cannot
verify an extremely rare tail. Similarly, a supplied-data optical mass
comparator above 3 solar masses is an engineering diagnostic, not a universal
neutron-star mass boundary or a black-hole classifier.

Native nonrejection rates for constants/variables and misspecified lens/noise
models are shown separately. The pipeline does not implement a validated BH
classifier, so BH false-positive and false-negative rates remain unavailable;
zero classification flags would not establish specificity.

## Reproduce in an independent workspace

Use the complete researcher source archive or matching formal BHSM checkout,
with the product installed in a dedicated environment. The source distribution
also carries the driver, specification and helper. From the product directory:

```text
python scripts/calibrate_rc7.py prepare --data-root /absolute/path/to/data --output /absolute/path/to/fresh_preparation
```

The data root must contain `pilot_selection.json`, `download_manifest.json`
and the original `raw/` hierarchy. The previous pilot's hash/citation records
and bounded refetch helper remain in the formal paper's
`real_data_pilot_20261022/data_provenance/` directory. Preparation verifies the
two raw cadence files against that manifest and records source, runtime,
protocol and parent-document hashes. It performs no scientific fit or draw.
The original observing files are never overwritten.

Review the specification, source and preparation record before execution.
Record the decision in a new JSON file containing `execution_admitted: true`
and the exact `freeze_sha256`; include the reviewer's name and intended scope.
This is a local prospective research record, not a server permission, external
registration, scientific certificate or request for additional licensing.
Calculate SHA-256 values from the actual files. Then run:

```text
python scripts/calibrate_rc7.py run --freeze /absolute/path/to/fresh_preparation/STUDY_EXECUTION_FREEZE_v1.json --freeze-sha256 FREEZE_SHA256 --admission /absolute/path/to/review_decision.json --admission-sha256 ADMISSION_SHA256 --output /absolute/path/to/fresh_results
```

Execution refuses a changed source/parent/runtime or an existing result folder.
It retains generated inputs before fitting, full outcomes, an append-only
attempt ledger, all-planned-fit CSV, block summaries and the preselected first
realization's residual plots. The one-hour wall and 2-GiB payload budgets are
checked between cases; an individual fit can finish after a boundary. Budget
exhaustion records `NOT_COMPLETED` and every unattempted case. Never replace a
failed case, reuse its seed as a fresh independent trial, or adjust criteria
after seeing favorable or unfavorable results.

`COMPLETE` means the planned accounting finished. It does not mean every
model was adequate or every confidence procedure was calibrated. Conditional
coverage at these fixed designs does not certify other cadences, nuisance
domains, native calibrations or actual-object mass estimates. Report findings
and limitations with the exact source/runtime/freeze hashes.

The BHSM description interprets a supported exterior as gravitational
hypersurface topography, with one Einstein/GHY optical response counted once.
This calibration introduces no second optical potential, new boundary law,
microscopic core coordinate, spin measurement or horizon inference.
