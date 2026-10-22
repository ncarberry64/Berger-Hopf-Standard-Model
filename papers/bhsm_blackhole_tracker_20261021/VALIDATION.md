# Validation and evidence: 0.2.0rc4

Validation is separated into the reviewed physical-inference corrections, native unresolved observations, historical resolved-pair calibration, conditional theory, and installed workflows. A completed optimizer is not a scientifically adequate model. Internal agent checks are not external peer review.

## Current installed release and joint validation

The current product suite passes 233 tests; `product/validation/rc4_product_tests.xml` records the final run. The clean noneditable wheel passes the base-only and optional-astrometry installation probes. All four notebooks execute with that installed interpreter outside the checkout. Browser source-pack import, saved measured-state verification, native export/CLI replay and explicit unsuccessful-search diagnostics are checked. Current wheel/source hashes and final-head CI remain bound by release receipts rather than older historical files.

The [separate 2023 joint audit](joint_known_system_20261022/README.md) retains frozen v1 and v2 algorithms, independent dense-covariance/Schur-complement checks, noiseless and zero-parallax controls, all three measured candidate baselines, 40 parametric controls, fixed-mass profiles, original limited UTC partition diagnostics and corrected local-noon whole-night validation. None of G0/G1/G2 is accepted: 15/15/8 residual bins fail, and G2 reaches the 100-day correlation cap. Conditional profile crossings have no accepted mass-interval status. The full calibration-sensitivity campaign is not required after the frozen all-models-fail stopping rule, and is not represented as performed. Internal checks are not external validation or general classification reliability.

The following rc3 receipts remain historical evidence for the unchanged pilot and the five reviewed corrections.

## Reviewed corrections

The fresh full product suite passes **182 tests**, recorded in `product/validation/rc3_product_tests.xml` (54.02 s). The focused F1–F3 set passes **75 tests** (33.08 s), with `product/validation/rc3_resolved_correction_receipt.json` and `rc3_resolved_corrections_tests.xml`.

1. **Numerical reference invariance:** physical fit domains no longer depend on a chosen reference mass, coordinate normalization or epoch. Stellar and very massive regressions compare the same physical predictions and likelihoods across reference choices.
2. **Physical profiles:** fixed mass/motion profile points reoptimize nuisance coordinates inside the declared admitted domain. Inadmissible states and failed/unresolved points retain explicit outcomes; a grid edge is not a measured limit.
3. **Unidentified motion:** rank/null projection determines which local coordinate uncertainties exist. A pseudoinverse zero is not reported as perfect motion precision. Repeated-epoch data retain unavailable motion components.
4. **Radial mechanics:** the membrane equation requires a round spatial p-sphere, fixed Minkowski background, constant tension, c=1, coordinate-time derivatives and subluminal radial speed. A constant applied pressure needs its pressure-work term. The pure membrane gives zero traction; curved/backreacting geometry, variable tension and dynamic forcing require their actual covariant variations.
5. **Source reconciliation:** the historical d604… handoff is preserved separately from the named 149b… handoff and original front/galaxy PDFs. All four raw hashes verify. Both PDFs were read and all 23 pages inspected. Their results retain their prescribed-background/conditional domains.

F4–F5 formal theory/source revision is [705d4c7e](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/tree/705d4c7e2f9a832b457f63ff975e7d4dc8008645): **22 symbolic checks** and **10 focused tests** pass. Repeat generation gives identical ledgers, and the narrow formal audits retain their own receipts. No unrelated historical campaign is represented as rerun.

## New native-observation likelihood

The versioned unresolved schema preserves each original magnitude/error/time, instrument/filter, source hash and source-row identity. The PSPL model is fitted in native magnitudes with an explicitly assumed diagonal Gaussian noise model. Per-instrument baselines/source fractions retain blending and zero-point freedom. No resolved images, ratios, delays, distances or covariance are fabricated.

[Synthetic validation](real_data_pilot_20261022/SYNTHETIC_VALIDATION_V1.json) uses the real sampling/error patterns but synthetic values: two noiseless injections (200 and 25 days) recover truth with chi-square below 2e-23, sixteen noisy trials test recoverability/error scaling, and a faint-source nuisance profile exposes timescale/blend degeneracy. This is limited validation, without calibrated coverage, false-discovery or black-hole recovery claims.

Optional centroid/parallax primitives have analytic/convention/admission tests. Public helpers require finite inputs, strict verified metadata, and explicit orientation conventions. Gould trajectory coordinates are lens-minus-source in the rotating basis, while the centroid input is source-minus-lens in north/east coordinates; the documented conversion includes this sign. The literal Sun-vector helper requires heliocentric ICRS vectors. These checks do not certify an end-to-end mass fit to the deposited HST data.

## Frozen real-data pilot

[Protocol](real_data_pilot_20261022/protocol_v1.json) `BHSM-OGLE3-native-pilot-20261022-v1` was internally frozen before the measured-light-curve fits. Protocol SHA256:
`b1e75ea708343bad1207ac180229058f093164e877cea68ac13bedfc3feed498`.
It is not external preregistration.

All **109 raw hashes**, the exact **100-event** selection and **76,344 numeric rows** are verified. Four source-warning annotations and event 0337 remain retained. There is no clipping, thinning, averaging, duplicate deletion, event replacement or repeated published error correction. The source convention is native HJD relative-day arithmetic with underlying clock scale unspecified; it is not silently promoted to precision ephemeris time.

Every event receives twelve-start baseline optimization, a nuisance-reoptimized timescale profile, signed-blend sensitivity and error-scale 1.25 sensitivity. Bounds, stopping criteria, rank threshold, diagnostics and follow-up ordering are frozen in the protocol. Alternative sensitivities do not replace the baseline. Profiles return likelihood reference levels without calibrated coverage: 91 have both level 1 crossings, nine have unresolved grid intervals. Inadequate-model profiles are not physical confidence intervals.

[All 100 accounting](real_data_pilot_20261022/derived_v1/summary.json):

| Stratum | Inadequate PSPL model | Not rejected by chi-square screen |
| --- | ---: | ---: |
| Long duration | 67 | 8 |
| Controls | 22 | 3 |
| Total | 89 | 11 |

Eleven screen passes are not eleven fully adequate scientific models. Only 0585 and 3092 pass the stricter frozen archival-follow-up criteria. Their mass, distances, angular Einstein radius, parallax and absolute motion remain unavailable. No mass-supported or new black-hole interpretation is produced.

The [literature annotation receipt](real_data_pilot_20261022/LITERATURE_ANNOTATION_RECEIPT.json) preserves the original frozen numerical fields and ranking. Four exact crossmatches with the published 59-event parallax sample include the previously interpreted 0264/PAR-07. The two-target audit confirms 3092's OGLE/MOA aliases; bounded searches do not establish 0585's novelty. No published mass is used as a fitting datum.

## Version-specific known-system benchmark

The corresponding 2022 Zenodo 6607578 v1.0.0 data contain 61,585 ground-based photometric rows and 16 HST rows at 8 shared visits. All five photometry-only fits converge with multistart confirmation, yet every one fails adequacy and has temporal/seasonal residual flags. Native reduced chi-square is 2.4515 jointly, 3.6754 OGLE-only, 2.0259 MOA-only, 2.4532 under the equal-instrument objective, and 2.4515 under signed blending.

The equal-instrument photometric sensitivity is not Lam et al.'s published joint photometric/astrometric equal-weight likelihood. No mass recovery is claimed. Original HST export-time mapping/frame/calibration conventions remain unresolved; a naive MJD interpretation misses the matching F606W exposure windows. No guessed time shift or second filter correction is applied. Later reductions do not substitute for the supplied older inputs. The rc4 analysis above uses a separately versioned primary 2023 reduction and source pack.

## Frozen sources and later documentation

The exact frozen kernels, protocol and driver are retained with [replay instructions](real_data_pilot_20261022/README.md). Later optional-astrometry docstring corrections preserve the executable AST; photometry.py and observations.py remain byte-identical. The [post-pilot receipt](real_data_pilot_20261022/POST_PILOT_OPTIONAL_DOCS_PATCH.json) records pre/post hashes. Final rc3 theory-source pins change provenance to 705d4c7e; the historical pilot keeps its original interpretation bytes and unchanged PSPL objective.

## Installed app and export/replay

The clean installed rc3 wheel retains the resolved GR/R1 workflows and imports the 734-row 0585 native file. Its native fit agrees with the frozen pilot (tE 268.172741 days), keeps BHSM interpretation explicit, and leaves every mass-derived quantity null. The actual browser-downloaded export replays through the installed CLI with maximum prediction difference 0.0 sigma, identical source-row identities and the same unavailable-mass fields.

The [native app API receipt](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/tree/9f1768a7fbac1d16e0e25713f87b8191cbe02249/products/blackhole_tracker/validation/rc3_native_app_api_receipt.json) records nine focused interface checks. Final delivery receipts bind the actual installed wheel, notebook executions, PDF renders and final-head CI; earlier release receipts are historical and do not certify later bytes.

## Historical resolved-pair and theoretical evidence

The preserved64-draw calibration uses a ten-year, three-source synthetic design with full supplied covariance and free source positions. Nominal local 95% interval coverage was 61/64 for mass and each motion component, 59/64 and61/64 for center coordinates; bias and finite-sample limits remain in the original receipt. The separate 128-draw follow-up retains two rejected outcomes and its tail-count limitation. These were not rerun on the revised rc3 kernel and do not calibrate native-photometry intervals.

Historical weak-motion and omitted-shear controls retain partial/rejected outcomes. The conditional R1 calculation preserves the exterior-wide sufficient quadrupole state cap, zero-flux treatment, source pairing and source-pinned provider checks. Its retained local principal-sign guarantees are not full coupled stability, horizon regularity or a selected physical amplitude. The screened leading delay null, shear ambiguity and two projected STF nulls remain explicit. The earlier 54-observable/30-nuisance experiment is an information design, not realistic observing feasibility.

The updated paper states all these distinctions. Compilation and visual verification must bind the final PDF bytes; old PDF receipts do not certify changed pages.
