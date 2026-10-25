# Photometry uncertainty evidence: fixed-design confirmation

The native fit supplies point estimates, residual checks and local-curvature
standard errors. Those errors are not calibrated confidence intervals. The
separate [MC workspace](../PHOTOMETRY_MC.md) supplies approximate fitted-nuisance
decisions at requested `tE_days` and `u0` nodes. Its completed confirmation
supports **two fixed cadence/error/truth designs only**. General user-input and
composite-null calibration remain pending.

## Preserved historical failures

The historical nominal 95% local timescale interval covered 510/512 truths; the
local impact-parameter interval covered 461/512; generating-timescale
profile-reference membership was 504/512. All three failed their predeclared
criterion. The [historical findings](CALIBRATION_FINDINGS_20261024_V1.md), original
numerical outputs, protocols and failed decisions remain preserved. The new
procedure does not retroactively validate them.

## Completed replacement pointwise confirmation

The frozen procedure used the original magnitude likelihood, constrained-null
nuisance fits, `NULL12_FREE1`, `NULL_RAW_PEAK_WIDTH12_V1`, 12 null starts and 199
predetermined bootstrap slots with exact partial-rank bounds. It processed 2,048
independently drawn datasets at each fixed design: **4,096 datasets and 8,192
pointwise tests**, with **326,304 saved bootstrap fits** checked by the independent
saved-evidence audit. The two parameter tests share each generated dataset; they
are not 8,192 independent data draws.

| Frozen design | Native cadence/error sampling | Synthetic generating truth |
| --- | --- | --- |
| 0 | OGLE3-ULENS-0033 / 2004-BLG-281; `photBLG100.3.I.144687.dat` | `t0 = 3155.835691`, `tE = 200 days`, `u0 = 0.3`, source fraction `0.65`, baseline magnitude `18` |
| 1 | OGLE3-ULENS-0127 / 2003-BLG-002; `photBLG101.4.I.196393.dat` | `t0 = 2727.69093`, `tE = 25 days`, `u0 = 0.3`, source fraction `0.65`, baseline magnitude `18` |

Both use numeric origin `2450000`; that origin arithmetic is not a clock-scale
conversion. Only cadence and reported errors come from those native light curves.
All trial brightnesses are synthetic, drawn with independent Gaussian magnitude
noise at scale `1`. Published event timescales `281` and `24.779` days are not the
generating timescales `200` and `25` days used in this confirmation.

The frozen parent hashes are:

- Design 0: `f8a5dfeb6f7be238387ef07d110c16aaf6e1ca6f3fd1ae6372814d9823d0ec93`.
- Design 1: `20888274ab66dedae333c42b1503076f7dc00539eb7072535ae93cf9f2c761ca`.

Scope remains unchanged: this confirmation supports these two fixed designs and
generating ordinates, with general user-input/composite coverage pending. It does
not validate actual lensing origin, physical mass or a black-hole identification.

| Frozen design | Parameter | Truth included / planned | Unavailable, counted as misses | Both primary gates |
| --- | --- | ---: | ---: | --- |
| 0 | `tE_days` | 1,947 / 2,048 | 0 | Pass |
| 0 | `u0` | 1,948 / 2,048 | 0 | Pass |
| 1 | `tE_days` | 1,939 / 2,048 | 2 | Pass |
| 1 | `u0` | 1,939 / 2,048 | 5 | Pass |

All **seven unavailable tests remained misses**, with no denominator reduction.
The two prospectively fixed gates were simultaneous 99% Clopper–Pearson intervals
inside `[0.92, 0.98]` for the four metrics, and the retained two-sided nominal-0.95
gross-miscalibration test at `0.01/28`. Together they required 1,921–1,979 included
truths out of every 2,048 planned tests; all four counts passed. No independence
between the four metrics is assumed by the simultaneous criterion.

These results concern generating-ordinate membership under the two fixed
cadence/error/truth designs. They do not validate other source/blend truths,
correlated or misspecified errors, all nuisance states, `t0` intervals, continuous
endpoints or gaps between requested nodes. Fitted-nuisance bootstrap remains an
approximation; exact fully specified simple-null rank reasoning alone does not
make a composite-null procedure exact.

## Review evidence identifiers

The versioned completion and independent review records are identified by their
filenames and SHA-256 values, without workstation-dependent links:

| Review record | SHA-256 |
| --- | --- |
| `primary4_confirmation_v1/CONFIRMATION_COMPLETED.json` | `95b4686e8744a338dd0b12ac2adc8a78d7850665284772e99785ac706561e84f` |
| `primary4_terminal_independent_audit_v2/INDEPENDENT_RECEIPT.json` | `b037d6bc4e9b44381a6bed79d79b283e0078d524cc91269790f4aabdb9895af9` |
| `PRIMARY4_CONFIRMATION_PROSPECTIVE_FREEZE_v3.json` | `14198730df304d306390e7ab87c411c22a7d1d4260944f330d1184d95a822507` |

The independent audit checked all 8,192 final records and all 326,304 retained
generated-input identities, fits and rank calculations from saved evidence,
without new forward-model, covariance, fit or random-draw calls. Hashes support
provenance and consistency; they are not substitutes for the stated scientific
scope. The producer and audit retain publication hold and known-BH recovery false.

The formal reviewer/project record is the
[Berger–Hopf Standard Model repository](https://github.com/ncarberry64/Berger-Hopf-Standard-Model),
under `products/blackhole_tracker`. In BHSM, a supported gravitational exterior is
interpreted as spacetime-side hypersurface topography, with one image-summed
optical response counted once. A conditional light curve does not independently
establish gravitational origin or black-hole identity. Mass, lens distance,
angular Einstein scale, parallax, absolute lens motion, horizon and core state
remain unavailable from this unresolved-photometry route.
