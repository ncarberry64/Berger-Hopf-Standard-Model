# Statistical risk review: bounded follow-up of the frozen 64-draw offset

The original y-motion mean error is consistent with this sample's first-order Gaussian noise response. The independent linear control reproduces it to `3.07e−8` mas/yr; it does not identify an additional nonlinear, covariance or local convergence error. The original receipt, all 64 results, original thresholds and reported 2.75-empirical-SEM offset remain unchanged. The conclusion remains limited synthetic local-interval calibration, without an empirical bias correction.

The canonical full report is `product/validation/report.md`, the executed protocol is `product/validation/statistical_risk_protocol.md`, and every follow-up draw is retained in `product/validation/statistical_risk_receipt.json`. The implementation is `product/tests/statistical_risk_review.py`. These are at the worktree root, outside the paper directory.

## Pre-experiment audit

The initial announced protocol SHA was `bb894b022a88df206a3eb6b3fb6a598c892aaec957eb01ec3698351026ae1136` at 2026-10-22 00:00:47.543 UTC. It was revised at 00:01:42.203 UTC, before script creation at 00:03:01.501 and experiment dispatch at 00:03:13.626. The executed SHA is `b316c22240954a4dc023a3864ff4276357e6f2e83084fc03e362967c775304f5`. The revision added explicit complete-stream mean scoring, including finite returned estimates from rejected fits and making a mean unavailable if an exception/nonfinite value prevents a complete stream. Model, seeds, budget, coverage intervals and all thresholds were unchanged. Reversing exactly that clarification reproduces the announced SHA. The first announced file was revised before data generation; it was not immutable.

The single 10.883-second execution used the prescribed maximum 145 solves: one noiseless reference, eight original standard refits, eight tighter refinements and 128 independent fits. All 64 original noise hashes and the original baseline hash match. No complete original ensemble was rerun, no stream was searched or extended, and reserved seed 202610210129 remains unused.

## Numerical findings

| Check | Result | Frozen concern level |
|---|---:|---:|
| Independent whitened Jacobian rank | 25 / 25 | Full rank required |
| Relative Jacobian discrepancy | `2.50e−11` | `1e−5` |
| Maximum five-coordinate covariance-diagonal discrepancy | `2.91e−11` | `1e−4` |
| Largest original mean nonlinear-minus-linear / analytic SEM | `0.00509` | `0.1` |
| Maximum eight-refit tighter displacement / local sigma | `4.57e−8` | `0.01` |
| Maximum tighter chi-square improvement | `1.55e−12` | `1e−6` |

The original nonlinear y mean is `0.000397991778` mas/yr; the independently derived linear mean is `0.000398022444`. Their empirical-SEM ratios are 2.74811 and 2.74822. The truth-known-covariance z is 2.5875, while the linear joint five-coordinate mean reference has p=0.1630. The originally highlighted component was selected post hoc; these values do not turn it into a preregistered discovery test.

The separate PCG64 seed 202610210128 follow-up returned 126 `TRACKED` and two goodness-of-fit `FIT_REJECTED` decisions. Every optimizer converged and every returned estimate was finite. The two rejected decisions count as misses in all five 128-draw denominators. The all-finite-estimator mean diagnostic includes their returned estimates as specified; they are not admitted tracks.

| Coordinate | Original covered /64 | Independent covered /128 | Independent exact coverage p | Independent known-covariance mean z |
|---|---:|---:|---:|---:|
| Mass | 61 | 118 | 0.1513 | −0.4555 |
| Center x | 59 | 120 | 0.5383 | −0.2571 |
| Center y | 61 | 119 | 0.3045 | −0.1777 |
| Motion x | 61 | 120 | 0.5383 | −0.7367 |
| Motion y | 61 | 121 | 0.6872 | 0.8394 |

No original or follow-up exact coverage guard rejects at alpha=0.01. No follow-up local mean-error guard rejects at familywise alpha=0.01, Bonferroni per-coordinate p<0.002. The experiments are reported separately. Follow-up y mean is `9.12948e−5` mas/yr, or 0.8790 empirical SEM, and the largest paired mean correction across all five coordinates is 0.00760 analytic SEM. Failure to reject these guards is not proof of nominal coverage or unbiasedness.

The two rejected indices 106 and 116 have chi-squares 65.4439 and 70.3620 on 29 degrees of freedom, goodness p-values `1.24005e−4` and `2.70496e−5`. A labeled post-hoc audit of existing noise only gives linear minimized chi-squares 65.4492 and 70.3639 and rejects exactly the same two draws. No new fit or stream was used. Such a tail count is uncommon: ideal `P[Binomial(128,0.001)≥2]=0.007476`. It remains visible; thresholds and data are not changed. An operational false-rejection calibration claim is not supported by this experiment.

## Code identity and disposition

The experiment source hashes in the receipt exactly match HEAD `79c374d6ae3331b63fc50846ef60cabfcdd2eb9f`: `data.py`=`832b6c21...`, `forward.py`=`3dc51c57...`, `inference.py`=`f5be57d2...`. Start/end hash equality is true. Later root edits have mtimes 00:04:18.717 and 00:05:28.953 UTC, after the receipt write at 00:03:25.465; their inspected diff changes validation, provenance/configuration and argument checking, without changing the fit equations, least-squares algorithm or covariance formula. Exact full hashes and post-run source snapshots are in the product report and receipt.

No production correction is recommended from these checks. The script's later `--audit-existing` addition is a reproducible descriptive postprocessing mode; its hash is recorded separately from the original executed-script hash. The manuscript preserves its original 64-draw table and adds the independent 128-draw findings, retained rejection count and narrow interpretation. Any future correction must use a new protocol and the reserved unused stream; these two used streams cannot become fresh validation.
