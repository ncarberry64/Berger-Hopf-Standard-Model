Local numerical derivative evidence --2026-10-24
Reviewer source: https://github.com/ncarberry64/Berger-Hopf-Standard-Model

Both admitted diagnostics evaluated the SAME ALL32 frozen final states:16
authentic2023 states and16 generated-control states. Each used four fixed steps,
5920 normalized model calls, no optimization or new data/random draw. Every
state/level/coordinate remains. Coarse and fine jobs completed in64.125s and
61.532s with no failed calls, source changes, audit loss or timeout.

The old Newton polish used scaled Hessian step1e-4. That step reported negative
free-space curvature at15/16 native states, even though finer evaluation gives
positive spectra in14/16 native states at ALL four fine steps. This establishes
an operational coarse-stencil problem; it does not certify the exact Hessian.
Native states10 and11 retain negative minima across every tested fine step.
The generated control has15 positive states; its state3 stays negative, with
minimum near-18.90634 across the fine sequence. No state is omitted or relabeled.

At native state15 the weakest free eigenvalues at3e-7 and1e-7 are approximately
20.0880046 and20.0880021. The fine-step results support a smaller Hessian step
as a numerical correction. They do not show that a positive-Hessian-only Newton
method will resolve the remaining states with stably negative floating spectra.
No new fit is performed or admitted by this compact comparison.

Scalar finite differences also expose truncation/roundoff limits. Native maximum
relative discrepancy falls from~1.078 at3e-6 to~0.006965 at1e-7. For native15 u0,
the analytic scaled gradient is~.0032095, compared with coarse finite differences
-318.9405 at1e-4,-29.8514 at3e-5 and~.0026921 at1e-7. Near-h-squared coarse
convergence supports truncation as a major cause, rather than automatic rejection
of the analytic score. These are observed floating comparisons, not an exact
derivative proof or a calibrated statistical acceptance test.

The fine t0 table preserves the kernel's unchanged JD=origin+offset operation.
At the smallest scaled step, decoded-JD versus offset step mismatch reaches
~.00024045 (0.0240 percent); no decoded step is erased. The stencil remains in
offset coordinates. No clock, physical time, stencil denominator or kernel is
silently corrected. This floating origin effect limits interpretation of the
finest scalar differences and is distinct from unknown observational clocks.
Profile active faces and clipped-brightness regimes remain unchanged across
every stencil in both jobs; the native noise-domain contact still remains.

Files:
- ALL256_HESSIAN_LEVELS_v1.csv: all coarse/fine step spectra, skew and gradient
  discrepancy summaries.
- ALL5888_DERIVATIVE_COLUMNS_v1.csv: every coordinate/stencil outcome and actual
  steps; the analytic and finite-difference scaled gradients are both visible.
- ALL128_FINE_T0_ROUNDING_LEVELS_v1.csv: every fine-step t0 rounding diagnostic.
- COMPARISON32_STATES_v1.json: paired states, complete roster and qualifications.
- COARSE_DERIVED_OUTCOME_v1.json.gz and FINE_DERIVED_OUTCOME_v2.json.gz: complete
  derived diagnostic outputs, with exact uncompressed hashes checked by the
  portable build_derivative_review_v1.py script. No original observations,
  observation-level predictions or row residual arrays are included.

These diagnostics do not change the four failed point-campaign outcomes in the
parent review directory. A stable conditional point near7 solar masses is not
an accepted known-BH recovery. Numerical resolution of all modes, calibrated
Student adequacy/reference/coverage, noise-domain treatment and observational
calibration/identity evidence are still required. Publication hold remains.
BHSM uses one exterior optical geometry with surface/envelopment interpretation,
counted once. No microscopic interface/core/horizon state or new BH is measured.
