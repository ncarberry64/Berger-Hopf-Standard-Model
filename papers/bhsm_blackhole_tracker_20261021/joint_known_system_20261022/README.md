# Separate 2023 joint known-system benchmark

This audit belongs to the formal [BHSM reviewer repository](https://github.com/ncarberry64/Berger-Hopf-Standard-Model). Its observations and protocol are separate from the frozen 100-event pilot and the historical 2022 benchmark. **Every frozen joint candidate fails baseline adequacy. No mass or black-hole identification is accepted.** Published classification of OB110462 is independent literature evidence.

The version2 timing/frame/blend sensitivity stage has a predeclared baseline-adequacy entry gate, which no candidate passes. That stage is therefore not executed and no systematic robustness is claimed; this is a conditional stop, rather than a passing test or an unreported result. Earlier version1 diagnostic sensitivities remain historical evidence.

Read [the plain-language result](PLAIN_LANGUAGE_RESULT.txt), [conditional baseline table](baseline_summary.csv), [whole-night prediction table](prediction_summary.csv), [residual bins](residual_bin_summary.csv), and [diagnostic figure](joint_noise_diagnostics.png). A numerical fit, global quadratic or passing plug-in prediction score does not override failed structure. Native-error quantile-cut bins contain tied rounded uncertainties and have unequal counts; they are not equal-size quartiles.

The [protocol](protocol/JOINT_MASS_BENCHMARK_PROTOCOL_V2.md) freezes the post-v1-diagnostic candidate set and stopping rules. The [source freeze](protocol/JOINT_PROTOCOL_V2_FREEZE.json) and [prediction-partition correction](protocol/JOINT_VALIDATION_PARTITION_V2_1_FREEZE.json) preserve chronology. Independent agent checks are internal computational reviews, not external peer review; their receipts are under `review/`.

The corrected partition holds out entire Chilean observing nights using a fixed local-noon boundary. It was frozen before prediction outcomes. The original midnight-boundary score remains a conditional diagnostic with its disclosed short train/validation gaps. Both versions retain exact GP covariance across the partition.
The [original UTC-boundary diagnostics](original_UTC_prediction_diagnostic.csv) are retained beside the corrected prediction table; a favorable scalar result from either partition cannot override failed baseline adequacy.

The [provenance manifest](PROVENANCE_MANIFEST.json) pins scientific sources, canonical inputs, source-pack bytes, drivers and large external outputs. Full fitted vectors and all 40 generated sample files are represented by hashes rather than committed copies. [Control summaries](control_summary.json) retain failures, profile status and the coarse Monte Carlo limit. All 62 [conditional profile rows](conditional_mass_profile.csv) are retained. G1's [refined conditional supports](conditional_refined_support.json) remain diagnostic likelihood supports under an inadequate model; they are not accepted confidence intervals. Every G2 grid row is cap-limited. The original serial grid is authoritative; auxiliary parallel comparisons preserve matching admission states but disclose thread-environment numerical differences in `review/JOINT_V2_G2_SERIAL_PARALLEL_COMPARISON.json`.

The portable source pack named in the manifest contains exact author observations and 82 minimal complete primary-header prefixes, with licenses and a verification/refetch helper. See [attribution and rights](sourcepack/CITATIONS_AND_RIGHTS.md) and [the byte inventory](sourcepack/ACQUISITION_MANIFEST.json). Historical Windows paths in receipts are provenance only. The versioned importer resolves relative pack paths using platform-independent path handling. The wrapper checks numerical input identity and environment explicitly; identical numerical behavior on another operating system is not certified by the path tests. No unreleased Keck observations are fetched or assumed.

The product supplies `products/blackhole_tracker/research/reproduce_joint_campaign.py` in the formal BHSM checkout, with instructions in `README_JOINT_REPRODUCTION.md` beside it. It verifies scientific hashes and source-pack data, retains the fixed candidates, seeds, modes, continuation budgets, profiles, partition versions and controls, and refuses silent scientific migration. Replay is independent of rerunning an optimization. From a formal checkout, first verify the pack without fitting:

```text
python products/blackhole_tracker/research/reproduce_joint_campaign.py --sourcepack /path/to/BHSM_OB110462_2023_SourcePack_v1.zip --output /path/to/new_external_output --verify-only
```

Remove `--verify-only` to run the fixed campaign. The source pack is a draft release asset under `museum/public/research/blackhole-tracker/`; its planned Pages URL in the manifest is explicitly **not yet a verified live publication**. The final formal source revision and publication status must be bound by the release coordinator before release.

To regenerate only these compact derived tables and the figure from an existing complete external campaign (no fits):

```text
python build_compact_audit.py --results-root /path/to/frozen/campaign
```

The [manual calibration-data request](MANUAL_CALIBRATION_DATA_REQUEST_TEMPLATE.txt) is prepared for author review and has **not been sent**. It specifies missing photometric clocks/variance components, seeing/detector checks, astrometric covariance/frame/epoch metadata and independent lens-flux evidence. A future calibration/data version requires a new frozen analysis; it cannot replace this failed campaign retrospectively.

A separate [robust-estimator feasibility assessment](review/ROBUST_ESTIMATOR_FEASIBILITY_ASSESSMENT.txt) explains why these failed Gaussian hypotheses do not rule out every estimator. It derives the assumptions a cluster/block estimating-equation route would require and reviews saved-state night dependence and uneven HST visit leverage without fitting it. No robust mass interval, bootstrap or new acceptance result is produced.

BHSM interpretation remains one compact-lens optical exterior counted once. The engine supplies no new core potential, measured membrane state, horizon classification, lens distance, absolute motion or black-hole discovery from these outputs.
