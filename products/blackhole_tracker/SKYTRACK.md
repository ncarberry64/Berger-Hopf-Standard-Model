# Measured lens angular tracks

This route fits the angular motion of one supplied foreground lens in a declared inertial tangent plane. It requires lens-position astrometry and its covariance. Catalog source/event directions, unresolved source centroids, a long event duration, and a visually straight sequence are insufficient inputs. An inferred lens position is admissible only when its identified joint model and covariance source are declared; these declarations remain the caller's evidence, not independent verification by this routine.

Under BHSM, an established gravitational imprint is interpreted as surface topography of the common exterior geometry. The exterior is counted once; this route adds no second force or mass and requires no departure from the ordinary exterior lens relation. A conditional angular track does not by itself establish gravitational origin, a black-hole identity, a mass, a distance, a horizon, a microscopic interface, or a distinct dynamical deformation. Those unavailable quantities remain null. The investigation label **Potential black hole** is not a measured mass or a confirmed identity.

## Observations and assumptions

The versioned input is `bhtracker.measured_lens_skytrack_observations.v1`. Run `python -m bhtracker skytrack example --output synthetic.json` for the complete schema. The example is explicitly synthetic and is not a recovery of a known black hole.

Supply a common `lens_id`, `position_role: LENS_ANGULAR_POSITION`, an explicit direct/inferred lens-position origin, association evidence, the inertial frame and east/north tangent origin, mas units, calibration source, and parallax treatment. Annual parallax must either have a supplied correction or remain explicitly unmodeled and conditional. The code does not turn a relative frame or an unspecified clock into absolute proper motion or a new clock standard.

Each row preserves its native epoch, native file SHA-256, source-row identity, source reference, lens identity, and measured east/north position. Duplicate epochs remain separate rows; duplicate row identities are refused. Native time is in days or Julian years; one Julian year is exactly 365.25 days. `numeric_origin`, convention, clock scale, and source are explicit metadata. An unspecified clock needs an explicit qualification. No UTC/TDB conversion or date inference occurs.

The supplied Gaussian covariance is either one positive-definite full `2N x 2N` matrix, ordered east/north by row, or a positive-definite `2 x 2` matrix per row. The latter route additionally requires a documented cross-epoch independence assumption. The full route requires that independence field to be null and forbids a second per-row covariance. No covariance is fabricated, repaired, rescaled by residuals, or silently diagonalized. Gaussian noise, correct covariance, frame calibration, and common-object association remain assumptions requiring observational support.

Unknown JSON fields and explicit nulls are retained. Exact original JSON text, including its line endings, and its UTF-8 hash are retained in every result. Hashes establish content identity, not authenticity of the supplied observations or their declarations. Strict duplicate-key/nonfinite/numeric-boolean checks apply. Input size and row-count resource limits refuse the whole input; they never thin or discard rows.

## Linear GLS and reference invariance

For row i, let `u_i = (t_i - c)/h`, with `c = (min(t)+max(t))/2` and positive half-span h. The four centered coefficients are `gamma = (E_c, N_c, a_E, a_N)`, relative to a retained position pivot. The two design rows are `[1,0,u_i,0]` and `[0,1,0,u_i]`. For supplied covariance `C = L L^T`, solve `min ||L^-1(y - A gamma)||^2`.

Time centering and scaling use exact rational arithmetic on the supplied represented binary64 epochs before conversion. An unrepresentable or underflowing numerical transform is refused. The weighted design `B=L^-1 A` must have numerical rank four under the reported SVD threshold `max(B.shape) * epsilon * largest_singular_value`. A full-rank reduced QR and triangular solves compute the coefficients and covariance `R^-1 R^-T`; there is no pseudoinverse or ridge. Rank certification here is an explicit floating-point rank policy, not a theorem about exact astronomical inputs.

At reporting epoch r, define `v=(r-c)/h` and `s=h` in Julian years. The transform is

```
T = [[1,0,v,0], [0,1,0,v], [0,0,1/s,0], [0,0,0,1/s]].
theta_r = T gamma + (pivot_E,pivot_N,0,0)
Cov(theta_r) = T Cov(gamma) T^T.
```

The full covariance, including position-motion cross terms, accompanies the result. Changing a reporting epoch transforms position and covariance; it does not refit a different physical model. Native clock shifts with a corresponding metadata-origin shift preserve the same physical epochs. The centered fit is retained as well as the reported basis. Extremely remote reporting epochs that lose representable positive-definite covariance are refused as numerical failures, not excluded physical models.

## Diagnostics and interpretation

At least two unique epochs are required for rank and fitting. At least three unique epochs are required for goodness-of-fit or motion-screen classification, even when repeated rows would give formal residual degrees of freedom. Two-epoch results remain untested fits.

For at least three unique epochs, `chi_square` uses `2N-4` degrees of freedom under the declared Gaussian known-covariance linear model. Both CDF and survival probability are returned. An optional, explicitly supplied `significance_alpha` in `(0,0.5)` applies the two-sided rule `min(1,2*min(CDF,SF)) <= alpha`. An upper-tail failure reports a model/noise inadequacy; a lower-tail failure reports underdispersion. Without alpha the output reports statistics only. Nonrejection is conditional model compatibility, not proof of lensing or a black hole. Multiple-object or adaptive searches require a separate declared multiplicity/selection calibration.

The stationary null has two unrestricted position parameters; the moving alternative adds two unrestricted angular-motion components. Their difference in chi-square uses a separate upper-tail chi-square probability with two degrees of freedom and the caller's alpha. It is a conditional test of stationarity, not a black-hole test. No automatic default detection threshold is supplied. Nonlinearity can reflect annual parallax, acceleration, source association, frame error, covariance error, or other effects; it does not exclude a black hole.

## Replay and export

```
python -m bhtracker skytrack validate observations.json
python -m bhtracker skytrack fit observations.json --output result.json --reference-native-time 6000 --alpha 0.01
python -m bhtracker skytrack replay result.json
python -m bhtracker skytrack export result.json --output fresh-export-directory
```

The public Python APIs are `validate_skytrack`, `fit_skytrack`, `synthetic_example`, `replay_skytrack`, and `export_skytrack` in `bhtracker.skytrack`. Validation does not fit or validate gravitational identity. Export creates a fresh directory containing exact dataset bytes, result JSON, replay check, and instructions. It never overwrites existing outputs.

Replay requires matching method source, original input bytes and parsed values, source-row identities, frame/time and fit settings, statuses, unknowns, and BHSM interpretation. Runtime versions are recorded as informational claims; changing Python/NumPy/SciPy/BLAS does not itself fail replay. Original synthetic cross-runtime bitwise failures are retained in the research review. Exact floating equality is not a portable numerical criterion.

The prospective engineering comparison uses `tau=64*max(2N,4)*epsilon*(1+kappa(B)^2)`. It refuses comparison if tau exceeds `1e-6` or any derived budget is nonfinite. The factor 64 is a declared conservative accumulation margin and the cap a precision/resource policy; neither is a rigorous floating-point enclosure or a new statistical uncertainty. Coefficients are compared in a covariance/whitened measurement metric, predictions and residuals in the supplied measurement metric, and covariance through maximum fractional variance error. The centered fit is checked as well as the reporting basis. The stationarity diagnostic has a separate design-norm-scaled comparison allowance. Probabilities and other diagnostics must still lie in their natural ranges independently of the comparison budget; the raw pre-clip stationary difference may retain a small negative roundoff value. Raw diagnostic values remain retained. The full mathematical policy is pinned in the external method review. Passing establishes content and numerical linear-solve consistency only. It neither changes covariance nor validates the observations, model, association, or black-hole identity.

Replay also recomputes the tail probabilities from the saved chi-square statistics and degrees of freedom. Positive tails must agree within the relative engineering tau budget; a recomputed zero requires an exact saved zero. A comparison crossing a machine-underflow boundary is refused rather than assigned an absolute tail allowance. Saved statuses must follow the saved probabilities and declared alpha, and the clipped stationary difference must match its saved raw value. These semantic checks apply independently of the cross-runtime chi-square allowance, which can be coarse for very large signals. The original synthetic contradiction that motivated this guard remains preserved in the research review.

## Future multiple-event association route

Direct or model-inferred lens positions are the first implemented route, not the only possible future track evidence. For a rectilinear event, put `q_i=|u0_i| tE_i`, let J rotate a tangent-plane vector by a declared 90-degree orientation, and enumerate both signs `sigma_i`. At closest approach, a candidate lens track obeys

```
L(t_i) = S_i(t_i) + sigma_i q_i J (mu_L - mu_Si)
S_i(t_i) - sigma_i q_i J mu_Si
  = L_ref + [(t_i-t_ref) I - sigma_i q_i J] mu_L.
```

This is a separately derived future association likelihood, not an admitted route in the present method. It needs propagated source frames and proper motions, event `t0,u0,tE`, their full joint covariance and correlations, every sign mode, common-lens evidence, and calibrated false alignments. An event direction cannot simply be substituted for `L(t_i)`. Missing lens distance and angular-motion measurements remain unavailable in the catalog filter.

Nearby fast lenses can sweep across background sources and produce event sequences; mesolensing applies to several mass classes, including planets and ordinary stars ([Di Stefano, 2005](https://arxiv.org/abs/astro-ph/0511633)). Nearby/fast therefore does not identify a black hole. OGLE-2007-BLG-224 provides a published brown-dwarf counterexample ([Gould et al., 2009](https://arxiv.org/abs/0904.0249)). Later adaptive-optics flux limits support that interpretation; this was not a direct lens-position detection ([Shan et al., 2020](https://arxiv.org/abs/2011.06013)). These sources motivate follow-up and controls, not an inferred mass in this software run.

The formal researcher repository is [BHSM](https://github.com/ncarberry64/Berger-Hopf-Standard-Model). This route has synthetic validation scope; known-black-hole recognition with native data is not established by it.
