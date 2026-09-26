# Two prospective rejection gates

The frozen structural protocol is [the JSON manifest](../preregistration/bhsm_geometry_first_make_or_break_v1.json), with an adjacent SHA-256 file. The [implementation](../code/bhsm_make_or_break_prediction.py), [tests](../tests/test_bhsm_make_or_break_prediction.py), and [synthetic artifact](../artifacts/BHSM_MAKE_OR_BREAK_PREDICTION_v1.json) have distinct roles. No target-data result is reported here.

## Gate A: shared state

All deterministic measurements obey `d = F X_2 + epsilon` with the same two-component state. Fixed source and conventional mean contributions are removed as specified before fitting. The GLS minimum `chi2_perp` tests the component outside the two-column response space. Under fixed rank-two kernels, known SPD Gaussian covariance, and no fitted nuisances, the reference distribution is chi-square with `N-2` degrees of freedom. Require `N>2`, reject at **p < 0.01**.

Cholesky whitening and least squares avoid explicit matrix inverses. The API rejects nonfinite data, wrong dimensions, rank-deficient designs and non-SPD covariance. It reports conditioning. Estimated covariance, fitted nuisance terms, nonlinear parameters or data-selected kernels require a different, preregistered calibration. Counting bins alone does not establish independent combinations.

This profiles two shared state coordinates to test compatibility. It does not use a second measurement to claim the formerly underdetermined one-amplitude prediction is closed. If theory independently fixes the direction, a distinct one-parameter test can be frozen before targets.

## Gate B: minimal coherent covariance

For `O=Mq` with a fixed finite response, `C_topo=M C_q M^dagger`, so rank is at most `m`. For one random amplitude it is at most one, equal to one only for nonzero response and variance. The zero-signal case has undefined eigenvalue ratios.

**One local noise type is not one global random amplitude.** Independent increments at two path segments can have nonparallel responses and produce rank two. A rank-one prediction after propagation requires a fixed separable shape or equivalent global rank-one source covariance. This physical coherence assumption is not action-derived in the current package.

The primary statistic is the signed second-largest eigenvalue of the unprojected residual covariance after scaling by independently fixed observable units. Report every signed eigenvalue, rho21 and all principal 2x2 minors. Rank is unit invariant; eigenvalue ratios require fixed units. Diagnostics do not create extra unadjusted tests.

Reject at **p < 0.01**, using the predeclared finite-sample calibration. The benchmark implements a known iid Gaussian total covariance `C_std+N+vv^T`, with the loading fixed independently, 9999 draws, seed 20260919, and the conservative Monte Carlo tail `(1+exceedances)/(B+1)`. It tests that fixed null. It does **not** calibrate the composite null of arbitrary unknown rank-one covariance, or a masked/correlated survey with fitted nuisances. A survey simulator must repeat the entire estimator/selection/nuisance pipeline and establish coverage and power.

## No retrospective rescue

No per-observable states or amplitudes, post-result changes to kernels, axis, state dimension, bins, observables or channel count. No standard covariance fitted to enforce low rank. No PSD clipping/projection to manufacture rank one. The previous low-rank protocol and helper remain unchanged as historical provenance and are excluded from this decisive test. A higher-channel model is a separate action-derived proposal frozen before decisive targets, not a repair to this one.

The hypotheses are logically separate, not assumed statistically independent. Their per-gate size is 1%; either-gate false rejection has union bound 2%. Do not report a combined 1% result.

## Required target design

The manifest enumerates release IDs/checksums and prior exposure, disjoint calibration/targets, bins/masks/source matching, axis/frame, kernel hashes/state basis, source subtraction, standard/noise/cross-survey covariance, nuisance treatment, unit scales, estimator, finite-sample simulator, multiplicity and power. These are **not yet frozen**. Structural preregistration is complete; executable observational preregistration is not. Existing Pantheon+/2MRS data cannot be relabeled blind targets.

## Reproduce the benchmark

From the repository root:

```powershell
python -m pytest -q tests/test_bhsm_make_or_break_prediction.py
python code/bhsm_make_or_break_prediction.py --output manuscript/build/make-or-break-synthetic.json
```

The synthetic checks illustrate both a compatible shared state and an incompatible one. They are software validation, not cosmological evidence.
