# Findings from the frozen current-kernel study

All **4,608 generated datasets, 4,736 fits and 1,024 generating-timescale
profile queries** finished their planned accounting. Original observations,
failed scientific decisions and historical calibration receipts are preserved.
These are synthetic observations, including the daughters using actual
observing times and reported errors. No actual lens mass is recovered by this
experiment.

The independent saved-only audit confirms the producer's counts, input lineage,
quadratic forms and all 28 frozen exact-binomial tests. It makes no model,
generator, fit or profile calls. **Three calibration tests fail**, all on the
OGLE3-ULENS-0127 cadence:

| Nominal 95% procedure | Contains truth / 512 | Fraction | Exact two-sided p |
| --- | ---: | ---: | ---: |
| Local timescale interval | 510 | 99.61% | 2.959e-9 |
| Local impact-parameter interval | 461 | 90.04% | 3.776e-6 |
| Generating-timescale profile-reference membership | 504 | 98.44% | 6.539e-5 |

All three exceed the allowed discrepancy at the frozen Bonferroni family
alpha 0.01 across 28 tests. Both excessive and insufficient coverage matter.
The profile query checks one generating ordinate; it does not produce complete
confidence endpoints. Local errors and reference thresholds remain conditional
approximations whose coverage has not been established for an arbitrary event.
There is no fitted correction, error inflation, replacement draw or changed
acceptance threshold in response to these results.

The twenty resolved mass/center/motion tests do not reject under the same
criterion at their four supplied-covariance designs. Motion remains unavailable
in every repeated-epoch control. No stationary motion exceeds the existing
two-component SNR cut in 256 controls, but the finite experiment cannot validate
a rare conventional five-sigma false-alarm probability. The ordinary-shear
controls reject the omitted-shear model and recover the admitted one.

## A nonrejected light curve does not establish its physical cause

| Fixed control | Nonrejected / 128, cadence 0033 | Nonrejected / 128, cadence 0127 |
| --- | ---: | ---: |
| Constant source | 94 | 102 |
| Specified periodic variable | 0 | 0 |
| Two-source lensing fitted as one source | 0 | 125 |
| Point lens with correlated errors fitted with diagonal errors | 121 | 112 |

These are conditional screening rates for the declared controls, not population
rates or black-hole false-positive rates. In particular, a nonrejected constant
curve is not a detected lensing transient. The tool's `PHOTOMETRIC_FIT` status
denotes a returned nonrejected fit under its working model; physical origin
requires independent evidence and model comparisons. Every photometric case
keeps lens mass and distance unavailable.

The software has no validated BH classifier, so its BH false-positive and
false-negative rates are **unavailable**. This study clears neither the known
black-hole recovery requirement nor the scientific publication hold. Existing
candidate labels and literature alternatives are not promoted by it.

The [prospective study guide](CALIBRATION_STUDY_V1.md) explains reproduction,
failure accounting and limits. Its BHSM interpretation remains explicit:
one gravitational optical exterior represents hypersurface topography and is
counted once. A fitted light curve does not measure an envelope's microscopic
boundary, a core, spin or a horizon.

Producer result SHA-256:
`9b22a47af9cdbeb2762591024845aa792e53827b4ac2433433e343c4427ba8a2`.
Independent saved-only audit SHA-256:
`3c38c6912c5a3883a826a360e8f9ef407c082f3f6f28f730c58eaa4b62664a47`.
Execution source and raw-file hashes were unchanged at completion. The transport
manifest and complete fit table accompany the versioned validation evidence.
