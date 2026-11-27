# Cross-lens projected curvature modes (control only)

Use a circular deflection rising/falling as r^s and add a trace-free
linear stretch of fractional amplitude g at the median angular radius
of the development images. This is a simple projected gravitational
lens model. It does not say how measured matter determines the
parameters or capture separate deflection planes. No halo masses
are fitted or used as inputs.

Use within-feature Helmert contrasts on development paths; the unknown
source center cancels. For holdouts, compare each counterimage's
back-projected angle to the first image's inferred source angle.
Do not call these errors image-plane positions. Data:
- CSWA 31: Wang 2022 Table 1, S0–S3 fit, S4/S5 held out,
  https://doi.org/10.1051/0004-6361/202243600.
- Jackpot: Gavazzi 2008 Table 1, four matched S1 knots train, S2 held
  out, both in the native sky axes, https://arxiv.org/abs/0801.1555.
  S2 uses the later spectroscopic redshift 2.035 from
  https://arxiv.org/abs/2104.12790. S3 remains reserved and was not scored
  here because it comes from a different astrometric frame.
- HE 0435: Courbin 2011 Table 2, https://doi.org/10.1051/0004-6361/201015709;
  A/B/C train, A used to anchor D. No delay inferred in this screen.
  Training has only four scalar contrasts for four local parameters;
  a small training error is not corroboration.

Training on CSWA 31 gives s=0.406024 and g=0.04301295. Freeze both at
these values, fitting only one scale and one azimuth to each other
lens’s development set. This tests the transfer of shape parameters,
not absolute strength and direction; those are still locally fit.

| Evaluation | Circular only | Local stretch and slope | Frozen CSWA shape |
|---|---:|---:|---:|
| CSWA 31 S4 | 2.224 | 2.529 | — |
| CSWA 31 S5 | 2.564 | 1.631 | — |
| Jackpot S2 | 0.711 | 0.771 | 0.377 |
| HE 0435 D | 0.062996 | 0.002168 | 0.010264 |

Numbers are anchor-to-counterimage source-plane closure RMS in arcsec.
The stretch helps CASSOWARY S5 but not S4. Two-parameter shape transfer
improves the reduced circular Jackpot control, but is not closure.
Neither frozen-parameter ablation establishes a unique common rule:
stretch-only and slope-only transfers for Jackpot give 0.312 and 0.368
arcsec, respectively. HE D does best with the locally adjusted stretch
in this reduced test. Its circular/local-stretch development fits, and
the corresponding Jackpot ones, hit the chosen slope bound of 0.65.
These are not credible physical slope measurements or full GR scores.
No morphology score or new prediction of a physically derived BHSM
curvature amplitude has been made.

Replay: `OPENBLAS_NUM_THREADS=1 python -W error cross_lens_mode_control.py`.
