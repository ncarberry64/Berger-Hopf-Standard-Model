# Bounded statistical risk review

The original 64-draw y-motion offset is consistent with the finite sample's first-order Gaussian noise response. Independent derivatives, covariance and eight tighter refinements found no material implementation or convergence discrepancy in this fixture. A separately frozen 128-draw follow-up did not trigger the declared coverage or mean-error guards. It returned two goodness-of-fit rejections, both retained as coverage misses. These results support a limited synthetic local-interval check; they do not establish unbiasedness, universal coverage or an observational false-alarm rate.

## Preservation and protocol history

The original `product_calibration_receipt.json` remains byte-for-byte unchanged, SHA-256 `aa95fd1a6f1f5918f2a31044cd565dd590ab71794ba39ec70a140a92beb028c7`. Its seed 4932026, 64 draws, thresholds, every result and the highlighted offset are preserved. All 64 regenerated noise hashes and the noiseless dataset hash agree with that receipt. The complete original nonlinear ensemble was not rerun.

The protocol was specified before follow-up data generation, but the first announced file was **not immutable**. The timestamped session log and filesystem record show this history (UTC):

| Event | Time | SHA-256 / change |
|---|---|---|
| First protocol write | 2026-10-22 00:00:33.939 | Initial text; spacing was then cleaned up |
| Announced protocol version | 00:00:47.543 | `bb894b022a88df206a3eb6b3fb6a598c892aaec957eb01ec3698351026ae1136` |
| Pre-experiment clarification | 00:01:42.203 | `b316c22240954a4dc023a3864ff4276357e6f2e83084fc03e362967c775304f5` |
| Experiment script created | 00:03:01.501 | Executed script SHA `08ab564058fecb30377366f41c2a6655f35c50ee9ae5cfce49e8e95d5e614303` |
| Experiment tool call | 00:03:13.626 | One bounded execution, 10.883 s runtime |
| Experiment receipt written | 00:03:25.465 | Before the subsequent root source edits |

The sole change between the announced and executed protocols added an explicit rule: the mean diagnostic uses all finite returned estimates, including estimates returned with a goodness-of-fit rejection; rejected decisions remain coverage misses and invalid tracks. If an exception or nonfinite estimate prevents a complete-stream mean, that test is unavailable rather than silently conditioned on successes. Reversing exactly that clarification from the final protocol reconstructs the announced `bb894...` hash. The model, seeds, sample budget, intervals, gates and rejection thresholds did not change. No new experiment ran between these versions.

The design allowed at most 145 solves: one noiseless reference, eight standard refits of original indices 0–7, eight test-only tighter refinements and one independent 128-draw stream seeded 202610210128. That budget was used once. No seed search, extension, bias correction, empirical recentering or pooled pass claim was made. The correction-confirmation stream seeded 202610210129 remains ungenerated and unused.

## Independent mathematical control

The ordinary-lens fixture has 54 measurements and 25 parameters: log mass, two center coordinates, two motion coordinates, two shears and two independent source coordinates in each of nine rows. The independent code derives its full physical-unit Jacobian from stationary point-lens images and the SI nominal solar gravitational parameter. It uses no production lens or derivative routine.

For image Jacobian `A=I−H0`, a perturbing potential `p` and source change `δy`, it uses `δx=A⁻¹(δy+∇p)`, `δln|μ|=tr[A⁻¹(Hp+DH0[δx])]`, and `δ(τ−−τ+)=(x+−x−)·δy+p+−p−`. Center shifts also enter the observed sky coordinates directly; source and motion shifts enter `δy`. The shear potential includes its factor one half. The independent whitened least-squares map is linear in the Gaussian noise and has exactly zero expected first-order error and a known covariance.

The independent whitened Jacobian has rank 25. Its relative Frobenius discrepancy from the production Jacobian is `2.50e−11` (fixed bound `1e−5`); the largest relative discrepancy of the five physical covariance diagonals is `2.91e−11` (bound `1e−4`). Across all five original-coordinate means, the largest nonlinear-minus-linear difference is `0.00509` analytic ensemble standard errors (bound `0.1`). The corresponding follow-up maximum is `0.00760`.

For original indices 0–7, tighter test-only tolerances changed an estimate by at most `4.57e−8` of its reported local sigma and improved chi-square by at most `1.55e−12`; the frozen concern levels were `0.01` sigma and `1e−6`, respectively. All eight standard refits reproduced their saved estimates exactly. This is a local convergence check, not a proof of a global optimum in arbitrary data.

## The original offset remains visible

| Original 64-draw y-motion statistic | Nonlinear fit | Independent linear control |
|---|---:|---:|
| Mean error, mas/yr | `0.000397991778` | `0.000398022444` |
| Empirical standard error of mean, mas/yr | `0.000144823614` | `0.000144829246` |
| Mean / empirical standard error | `2.74811` | `2.74822` |
| Mean / known-covariance standard error | `2.58751` | `2.58771` |

The nonlinear-minus-linear y mean is `−3.07e−8` mas/yr, or `−0.0001994` analytic ensemble standard errors. Thus the highlighted offset is already present in a zero-expected-error first-order response to the original noise. The original component was selected after looking at the results; its single-coordinate Gaussian reference `p≈0.00966` is descriptive. The linear joint five-coordinate mean diagnostic has `p=0.1630`. This does not make the observed offset vanish or prove that all nonlinear bias is negligible.

## Independent follow-up: all 128 retained

Every optimizer converged and returned finite estimates. There were 126 `TRACKED` results and two `FIT_REJECTED` results at the unchanged goodness-of-fit guard `p<0.001`. Both rejections remain in all five coverage denominators as misses. No exception or domain failure was removed. The mean diagnostics below include the finite returned estimates from both rejected decisions, as prescribed before generation; they are diagnostic estimates, not admitted tracks.

| Coordinate | Original coverage /64 | Follow-up coverage /128 | Follow-up exact coverage p | Follow-up mean z using known local covariance |
|---|---:|---:|---:|---:|
| Mass | 61 | 118 | 0.1513 | −0.4555 |
| Center x | 59 | 120 | 0.5383 | −0.2571 |
| Center y | 61 | 119 | 0.3045 | −0.1777 |
| Motion x | 61 | 120 | 0.5383 | −0.7367 |
| Motion y | 61 | 121 | 0.6872 | 0.8394 |

The two ensembles are not pooled. The five follow-up exact coverage tests use the original null 0.95 and per-coordinate level 0.01; none rejects. Their observed fractions range from 0.9219 to 0.9453, with wide exact 95% binomial intervals; these are not precise measurements of nominal 95% coverage. The five prespecified local mean-error diagnostics use a Bonferroni familywise level 0.01, each two-sided `p<0.002`; none rejects. These Gaussian references are exact for the linear control and a local approximation for the nonlinear estimator. The follow-up y mean is `9.12948e−5` mas/yr, `0.8790` empirical ensemble standard errors; its scatter is `0.9549` times the truth linear sigma. The joint five-coordinate mean reference has `p=0.9056`.

The two rejected draws are 106 and 116, with nonlinear chi-squares 65.4439 and 70.3620 on 29 degrees of freedom, and goodness p-values `1.24005e−4` and `2.70496e−5`. A **post-hoc descriptive** audit reconstructed only the already-used noise, checked every saved hash, and projected it with the independent linear model. Its corresponding chi-squares are 65.4492 and 70.3639; it rejects exactly the same two draws. No additional nonlinear fits or random stream were used. The probability of at least two rejections in 128 under an ideal independent size-0.001 linear guard is `0.007476`. This uncommon tail count is retained as a limitation, not discarded, reclassified as solver failure or used to relax a threshold. This follow-up does not validate the operational false-rejection rate.

## Code provenance and scope

At experiment time, the recorded bytes of `data.py`, `forward.py` and `inference.py` exactly match Git HEAD `79c374d6ae3331b63fc50846ef60cabfcdd2eb9f`. The experiment's start/end hash check is true:

| File | Experiment SHA-256 |
|---|---|
| `bhtracker/data.py` | `832b6c210cf4eb4f18383ff7a3f47a12e6e7d9c87a767488e5db31affd633d04` |
| `bhtracker/forward.py` | `3dc51c57e56ff00633ca3d5e0766a37cd0eb7639d58a294373ac1e30df810e5d` |
| `bhtracker/inference.py` | `f5be57d250e63c81458505da31c6f0816eb409e591072f52effb273dacbc9e67` |

Root's later `data.py` and `inference.py` modifications had recorded mtimes 00:04:18.717 and 00:05:28.953 UTC, after this experiment. Reviewing the diff found strict JSON/input checks and actionable messages, provenance/configuration recording, the `max_nfev` argument-range guard and a profile input-identity check; the optimizer, residual equations and covariance calculation are unchanged. The risk review made no production inference edit and did not rerun ensembles for these metadata/admission changes. The receipt records the actual experiment hashes separately from post-run source hashes. The script was subsequently extended with an `--audit-existing` mode for the descriptive residual and provenance audit; its new hash is separately recorded and does not overwrite the executed-script hash.

Reproduce the frozen numerical experiment with `python tests/statistical_risk_review.py` from the product directory. To audit the existing receipt without refitting or generating any new random stream, use `python tests/statistical_risk_review.py --audit-existing`. The JSON receipt contains every draw, interval, error, diagnostic, threshold, noise hash, source hash, protocol revision and post-hoc classification. A repeated run is a replay, not new independent validation.

The supported conclusion is consistency with finite-sample fluctuation in this fixed synthetic fixture, with no material covariance or local convergence error found by these checks. Unknown calibration, non-Gaussian noise, different source configurations, model mismatch, critical images and real observations require their own validation. No detectability, horizon identification or universal BHSM-state inference follows from this statistical review.
