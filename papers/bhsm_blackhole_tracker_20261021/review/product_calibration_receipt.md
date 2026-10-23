# Frozen nonlinear product calibration receipt

**C6, C7, C8 and C11 pass the declared checks.** This is an internal AI-assisted synthetic validation with supplied known covariance, not evidence of an observed object, horizon, R1 signal or achievable measurement precision. The complete per-draw results and hashes are in `product_calibration_receipt.json`; replay with `python product/tests/calibrate_product.py`.

## Frozen design

The design uses the existing `make_example("nearby_motion", noise=False)` truth/covariance, the fixed PCG64 seed 4932026, 64 sequential full-covariance Gaussian draws, and `fit(..., family="gr", starts=1, nuisance="shear")`. Sources remain free at every row. All 64 draws and all failures belong in the denominator. No draw was removed, no tolerance was widened, and no source code changed during the replay.

The 95% intervals are local Gaussian intervals using the supplied known covariance without chi2 rescaling. Mass uses a log interval with sigma_logM=sigma_M/M; center and motion use additive intervals. Each of the five predeclared coverage tests uses the exact two-sided binomial null p=0.95 at alpha=0.01. All five results are reported without a multiple-testing adjustment.

## Repeated-noise result (C7)

| Parameter | Covered / 64 | Exact 95% interval for coverage | Exact binomial p | Mean error | Error scatter |
|---|---:|---:|---:|---:|---:|
| mass_msun | 61/64 | 0.8691â€“0.9902 | 1 | 3.1069 | 38.2111 |
| center_x_mas | 59/64 | 0.8270â€“0.9741 | 0.2532 | -0.000661157 | 0.00793738 |
| center_y_mas | 61/64 | 0.8691â€“0.9902 | 1 | 0.000309398 | 0.00550926 |
| motion_x_mas_yr | 61/64 | 0.8691â€“0.9902 | 1 | 1.38658e-05 | 0.00125249 |
| motion_y_mas_yr | 61/64 | 0.8691â€“0.9902 | 1 | 0.000397992 | 0.00115859 |

All 64 optimizer runs converged and returned TRACKED; zero exceptions, admission failures or rejected fits were excluded. The parameter units are solar masses, mas and observer mas/year. The y-motion mean error is about 2.75 estimated standard errors of its ensemble mean; it is reported rather than suppressed. The frozen coverage criterion does not reject it, but this finite ensemble does not establish negligible bias or universal coverage.

## Nonlinear recovery and negative controls

C6 fits the noiseless baseline from the data-derived default initializer and two fixed nontrivial perturbations (mass factors 1.5 and 0.65, plus center, motion, source and shear shifts). Each run uses three internal starts. All three recover the exact mass/center/motion solution within the frozen mass relative tolerance 10^(-5) and center/motion tolerances 10^(-5) of the reference angular/span scales. The largest chi2 is 3.005e-23, below the frozen 10^(-6) limit. The initializer perturbations are data-derived and are saved in the JSON; the truth was not passed as an initializer.

C8 uses the noiseless ten-year cosmological fixture with its original supplied covariance. It returns PARTIALLY_IDENTIFIED, motion SNR 0.0048245, and one-sigma component errors 0.0121361, 0.0124452 mas/year against true motion 0.00005, -0.00003 mas/year. It does not turn a well-measured mass into a resolved proper-motion claim.

C11 uses the exact ordinary-shear fixture. Omitting shear returns FIT_REJECTED, chi2=28297.8, p=0. Admitting two ordinary shear coordinates returns TRACKED, chi2=1.954e-22, p=1, recovering the declared (0.03,-0.018) shear. Model mismatch is rejected rather than assigned a novel cause.

## Scope

These results complement the independent closed-form physical-unit and covariance contract tests. They demonstrate nonlinear recovery for the stated ordinary compact-lens fixtures and bounded gross local-interval calibration in one fixed 64-draw ensemble. They do not validate every source trajectory, strong/critical image configurations, unknown frame or distance calibration, general macro/environment nuisances, global likelihood topology or nonlinear profile intervals. Conditional R1 envelope and exact finite degeneracy checks require their separate receipts; no physical boundary state was enlarged here.

Runtime: 6.977 seconds. Source hashes were unchanged throughout the run. Frozen criteria hash: `8a467896068c4a3eb6cd86578ecba958d789321a8795ccab40001371ec8c1e0a`.
