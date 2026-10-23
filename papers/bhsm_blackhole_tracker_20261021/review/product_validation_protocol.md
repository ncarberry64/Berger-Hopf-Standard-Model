# Blackhole Tracker product validation protocol

This protocol is fixed before evaluating the new nonlinear inference product. It separates a calibrated ordinary point-lens tracking tool from optional inference about the conditional R1 exterior. It is an internal AI-assisted validation plan, not an observational proposal or external peer review. Existing derivative checks remain useful, but a local Jacobian rank alone does not validate a nonlinear research product.

No physical R1 boundary state will be enlarged to manufacture power. In particular, the existing eta=10^(-3) state remains at its declared physical amplitude. Synthetic uncertainties are explicitly supplied test inputs, not inferred instrument capability. Failure or weak information is an acceptable scientific output when the input does not identify a parameter.

## Public interface and observation contract

The agreed new package is `product/bhtracker`. Its public interface is:

```python
load_dataset(path_or_dict) -> Dataset
predict(dataset, parameters, family="gr") -> numpy.ndarray  # N by 6
fit(dataset, family="gr", starts=2, nuisance="shear") -> dict
```

The six observable columns are `[theta_plus_x_mas, theta_plus_y_mas, theta_minus_x_mas, theta_minus_y_mas, ln_R, delay_seconds]`. The plus/minus labels continue the noncritical bright positive-parity minimum and faint negative-parity saddle. R is the ratio of absolute geometric magnifications for the same source emission; the delay is faint minus bright and is positive on the admitted reference branches. This is a primary-pair contract, not a claim that no other images exist.

Dataset schema version 1 contains physical distances in pc, redshifts, observer epochs in years, a reference epoch, an N-by-6 observation matrix and its full 6N-by-6N covariance. Parameter inputs to `predict` include `mass_msun`, `center_mas[2]`, `proper_motion_mas_yr[2]`, `source_mas[N,2]`, `shear[2]`, `compact_quad[2]`, and `convergence`. The shear potential convention is `(gamma_plus/2) r² cos 2phi + (gamma_cross/2) r² sin 2phi`. Compact quadrupole coefficients use the declared dimensionless reference phase convention. The absolute astrometric frame and its time convention are supplied calibration assumptions.

The source policy is `free_per_epoch`; two unlensed source coordinates are nuisance parameters at every epoch. A successful fit must not quietly assume a known source track. The result dictionary includes `status`, physical `estimates`, `uncertainty`, `chi2`, `dof`, `diagnostics`, `model` and physical-unit `predictions`. `nuisance="shear"` admits two shear coordinates; `"full"` additionally admits two compact quadrupole coordinates and convergence. Unknown options must be rejected rather than silently mapped to another family.

## Frozen reference fixtures

The independent prediction fixture uses an ordinary point mass of 10 solar masses, distances `(D_l,D_s,D_ls)=(1000,8000,7000)` pc and redshifts zero. These are a synthetic Galactic geometry, not a candidate object. Its irregular observer epochs run from 2025.55 to 2026.58, with reference epoch 2026, a nonzero center and two proper-motion components. The source rows keep every primary pair outside the declared unresolved interior and away from u=0. The concrete numeric arrays and seed are frozen in the test source before evaluating the root implementation.

Prediction checks derive the mass length and time scale independently from the nominal solar gravitational parameter `GM_sun=1.3271244e20 m³/s²`, exact c and the pc conversion, rather than import the product's own unit constants or lens functions. For zero ordinary multipoles, each epoch must satisfy:

`theta_E² = 4m D_ls/(D_l D_s)`,

`center(t) = center_ref + proper_motion * (t - reference_epoch)`,

`x_plus=(u+sqrt(u²+4))/2`, `x_minus=-1/x_plus`,

`ln R=4 asinh(u/2)`, and `Delta t=4GM(1+z_l)h(u)/c³`.

The physical image angles add the moving center to the signed Einstein-angle images. A common absolute translation and a shift of reference epoch have exactly known effects and provide additional calibration checks.

For covariance tests, use distinct nonzero per-column scales in mas, log flux and seconds. Construct a positive-definite dense covariance with both image-coordinate correlations and cross-epoch correlations. This deliberately prevents a code path that silently discards covariance off-diagonal entries from passing. Epoch permutations must permute observations, parameters' source rows, and both covariance axes by the same six-row blocks.

## Preregistered acceptance matrix

| ID | Input/control | Required outcome before claiming validation |
|---|---|---|
| C1: units and forward physics | Independent closed-form moving point lens, no multipoles | All six physical-unit outputs agree with the independent formula within a documented numerical tolerance; shape is N by 6, values finite, delay and branch flux ordering preserved. The test does not import the implementation's lens formula. |
| C2: coordinate calibration | Translate all absolute angular quantities; change reference epoch with the compensating center shift | Relative lens physics, flux and delay are unchanged, while predicted absolute angles transform exactly. Proper motion is observer mas/year, not an unlabelled physical velocity. |
| C3: permutation | Nontrivial epoch/block permutation and dense covariance | Predictions reorder by the same permutation. The Gaussian quadratic form is unchanged. A fit must either preserve ordering or explicitly canonicalize every corresponding array; silent partial sorting is a failure. |
| C4: full covariance | Recompute the fitted residual quadratic form as `r.T @ solve(C,r)` | Reported chi2 agrees with this independent value. Covariance is not replaced by its diagonal. No tolerance is relaxed after seeing a failure. |
| C5: admission | Wrong dimensions, nonfinite values, nonpositive mass/distances, nonsymmetric or non-positive-definite covariance, unsupported family/policy | Explicit informative failure before inference; no silent clipping, zero-noise replacement or pseudoinverse that hides invalid measurement covariance. Equal zero Galactic redshifts are allowed; a flat-distance identity is not imposed on cosmological distances. |
| C6: baseline nonlinear recovery | Noiseless ordinary point-lens primary pairs with source positions free in the fit | Multiple initializations reach mutually consistent predictions/objective and recover the identifiable physical mass/center/motion solution to the declared solver accuracy. A fitted prior or a known source track may not be added invisibly. This is a nonlinear fit check, not another Jacobian test. |
| C7: repeated-noise calibration | Independent Gaussian draws from the declared covariance, fixed truth and frozen seeds | Empirical bias, coverage and fit failures are reported for mass and both center/motion components. A finite ensemble can expose gross miscalibration but cannot certify universal coverage. No seed or realization may be removed because it is inconvenient. |
| C8: weak-motion negative control | The original ten-year cosmological compact-source geometry at its actual small angular displacement | Product reports broad/weak or non-identifiable proper-motion information when appropriate. It may not force a successful tracking claim from the broad abstract spatial scan or shrink intervals through hidden priors. |
| C9: exact finite nuisance degeneracy | Two parameters generating the same ordinary compact `r^(-2)` potential, or the zero-flux harmonic envelope and compact quadrupole with equivalent normalization | Nonlinear predictions are unchanged along the exact compensating parameter direction. Individual amplitudes are flagged non-identifiable; the implementation must not emit finite likelihood-only uncertainties by silently inverting a null. A prior-constrained result must name the prior. |
| C10: baseline-only envelope negative control | Pure baseline data; optional envelope amplitudes truly zero, declared covariance | An optional fit may improve chi2 by fitting noise, but must not label that improvement a physical R1 detection. Boundary/nonregular likelihoods require their own null calibration; a naive fixed chi-square detection threshold is not licensed. |
| C11: ordinary mismatch | Data from a fixed ordinary shear/compact quadrupole omitted from the fit | Poor fit or model sensitivity is identified. A mass drift/envelope fit is not automatically assigned a novel physical cause. Refit with the admitted ordinary nuisance and show the change. |
| C12: unrestricted-cause ambiguity | Distinct source interpretations with the same Weyl potential on sampled rays | Product reports equivalent predictions; it cannot identify a horizon or a gravity theory from the shared exterior alone. |
| C13: actual small R1 state | Existing admissible worldtube state and actual normalization; no amplitude inflation | Forward output reproduces the physical tiny contribution. If inference has no power at the supplied covariance, output is a limit, weak information or non-identifiability. Numerical derivative test amplitudes are not physical states. |
| C14: local-model admission | Ray enters worldtube, critical/ordering crossing, or R1 branch violates its declared domain | Reject or mark outside model scope. An optimizer is not allowed to turn a successful numerical step into physical admission. |

The first delivered contract test file prioritizes C1–C5 as requested. It will use the public API after the root package lands; no root forward-model or inference source is edited by the independent tester. Additional nonlinear recovery/calibration tests follow only once the agreed API returns uncertainty and identifiability metadata needed to assess them.

## Nonlinear recovery and uncertainty evaluation

For C6, compare predictions and objective from several substantially different starts, not merely parameter proximity from one favorable start. Check the physical mass estimator and per-epoch point-lens center as independent controls. For the ideal point lens,

`center_i = (theta_plus_i + sqrt(R_i)*theta_minus_i)/(1+sqrt(R_i))`,

and the known delay/flux formula independently yields M. These are controls for the baseline only; applying them to a general macro/R1 lens does not produce ground truth.

Known redshifts/distances and the absolute frame are part of the input contract. Releasing a free astrometric frame drift creates a corresponding center/proper-motion gauge freedom. The product should either estimate frame-relative motion with that label or flag loss of absolute motion information. A transverse velocity additionally requires a distance/redshift conversion; it is not the same reported parameter as observer proper motion.

For a bounded initial calibration, use 64 independent baseline noise realizations from a frozen seed stream. Report all 64 outcomes, including optimizer/admission failures. For each physical parameter report empirical bias, scatter, interval coverage and whether an uncertainty is prior- or boundary-limited. Compare nominal 95% coverage with its exact binomial uncertainty; use an exact binomial test at alpha=0.01 only as a gross-miscalibration guard. Do not change the ensemble, coverage level or alpha after inspecting outcomes. This is a small synthetic calibration experiment, not proof of universal 95% coverage. If the available uncertainty method is only a local Hessian approximation, state that and distinguish it from a nonlinear profile interval.

For any reported Gaussian chi2, independently recompute the quadratic form using the complete supplied covariance. Degrees of freedom must reflect fitted identifiable directions and documented constraints. Rank truncation and active parameter bounds must be reported. A successful optimizer termination is not sufficient evidence for a calibrated physical uncertainty, nor does a singular Hessian justify an unlabelled pseudoinverse confidence interval.

## Degeneracy, mismatch and optional R1 inference

The exact duplicate-potential control is deliberately finite and nonlinear. It avoids incorrectly demanding a finite degeneracy from the merely first-order `(r²−1)cos 2phi` estimator null. The latter remains a useful differential control, but can have quadratic departures. A likelihood cannot recover separate coefficients whose complete potentials enter only through their sum.

Ordinary mismatch controls are fixed source models before looking at recovered R1 amplitudes. Their role is to test whether the tool distinguishes a failed data model from an inferred physical cause. A richer model's lower residual is not by itself evidence for its ontology. General line-of-sight and source-position freedoms remain outside a finite nuisance catalogue unless explicitly modeled.

R1 output must disclose the effective action, fixed background, supplied scalar flux, matching radius, boundary-state normalization, scalar-to-metric map and omitted time-dependent/horizon physics. The existing physical state is extremely faint. Product usefulness can therefore be demonstrated by ordinary mass/center/motion recovery and honest optional limits without inventing a detectable envelope. High optical amplitudes used only to verify derivatives must remain identified as numerical tests.

## Release record and change policy

Record dataset and code hashes, package/runtime versions, seed stream, optimizer settings, starts, bounds, covariance convention, nuisance family and every test result. Keep failed tests and their reasons. Fixing an implementation and rerunning the unchanged criterion is permitted; widening a threshold or deleting difficult realizations after seeing results is not. A scientifically justified change to the data model requires an explicit protocol revision, preserving the previous result.

The product is accepted only for the model and input domain actually validated. C1–C5 passing establishes a useful interface/physics/noise contract, not by itself nonlinear calibration or observational performance. A release may honestly mark C6–C14 pending or limited while exposing its existing scientific value; it must not describe pending inference calibration as completed.

## Executed validation record

The independent 36-case public-interface replay is recorded in `product_contract_test_receipt.md` and its JSON receipt. The subsequent frozen seed-4932026, 64-draw calibration executes C6, C7, C8 and C11 through `product/tests/calibrate_product.py`; `product_calibration_receipt.json` retains every draw, initializer, failure, criterion and source hash, with a readable account in the companion Markdown receipt. All four checks pass their fixed criteria. Coverage is 61/64 for mass and both motion components, 59/64 for center x and 61/64 for center y; all 64 fits converge, and no draw is excluded. The exact binomial guard rejects none of the five coverage tests at alpha=0.01. These are bounded ordinary-lens results, not universal calibration or completion of the separate optional-R1 checks.

The separate `check_finite_harmonic_degeneracy.py` replay verifies C9's exact finite zero-flux harmonic/compact operator identity and the expected two null directions. Nonadmitted coefficients are confined to the formal `LensEngine.potential` operator check, while public `predict` separately rejects the inflated state. The readable and machine receipts are `product_finite_degeneracy_receipt.md` and `.json`. The current nonlinear fit does not expose a joint free compact-plus-boundary fit, so this establishes the exact cause ambiguity and admission behavior, not calibration of separate degenerate amplitudes.
