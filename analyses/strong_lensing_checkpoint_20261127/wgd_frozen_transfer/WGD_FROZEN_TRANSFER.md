# WGD 2038−4008: frozen R1 transfer on independently measured starlight

**Result.** The pinned PR #23 response can be transferred without retuning
to a spherical, stellar-only profile anchored to actual galaxy photometry.
In that explicitly conditional setup, it is far too small to supply the
mass missing from the imaged circular critical-scale proxy. The same
retained optics are reproduced by one nonnegative conventional effective
mass profile constructed from the frozen R1 result. This does not measure
a dark halo, fit the actual quad, or establish observational discrimination.

## Inputs and controls

- PR #23 commit 4f044a6af5757f6f1c4e99e6547b43d6c45e353c. Same archived
  V0, R1 background equations, H0=67.4, kinetic normalization and local
  screened branch, evaluated at WGD's z_l=0.230 rather than copied from
  the first lens. No shooting, coefficient retune, or fit.
- [Agnello et al. (2018)](https://academic.oup.com/mnras/article/479/4/4345/5032807)
  supplies the main luminous component's Sérsic n=1.90, major-axis effective
  radius 3.45 arcsec and axis ratio 0.77. From the optical photometry with a
  Salpeter IMF, their abstract reports log10 stellar mass 11.64 (+.20/−.43),
  while §3.1.2 reports 11.40 under nominal magnitude errors. These are
  alternative conditional inputs, not new fits or a propagated posterior.
- Assume spherical symmetry, constant stellar mass-to-light ratio, omit
  the separately visible compact bulge, and use spherical Abel deprojection
  of the circularized Sérsic. A same-scale Plummer proxy tests sensitivity
  to the stellar shape, not observational uncertainty. The input stellar
  mass was imported, not re-estimated from flux under the R1 distances.
- No timing input, observed time delays, fitted total lens mass, tuned
  dark halo, source position, galaxy environments, or shear used. The
  separate critical-mass proxy uses only the published imaging 1.30 arcsec
  scale and explicitly stated circular single-plane distance assumptions.

## Results

The original reference threshold replays as rV=212.029224977 kpc at
z_l=0.3 and M=10^11 solar masses. At z_l=.230 the frozen coefficients
give epsilon_infinity=.001837596127; the angular distance is 780.8339 Mpc
and circularized Re is 11.4604 kpc. At central log10 M*=11.64,
rV=359.4983 kpc and H_l rV/c=9.19e−5.

For the main circularized Sérsic profile, the local fractional deflection
increment relative to the bare stellar lens is:

| Physical impact / circularized Re | Fractional increment |
|---:|---:|
| 0.25 | 2.9095e−5 |
| 0.50 | 4.3256e−5 |
| 1.00 | 7.2652e−5 |
| 2.00 | 1.3929e−4 |
| 4.00 | 2.9642e−4 |

The Plummer control gives 7.2932e−5 at one Re. These are fractional
physical bending increments, not relative image shifts, time delays,
or a measured departure from gravity.

At 1.30 arcsec with the discovery article's nominal source-redshift
assumption z_s=.777, the circular critical mass is 2.46863e11 solar
masses. The circularized stellar-only and actual frozen-R1 contributions:

| log10 M*/solar mass | Bare stars / critical | R1 addition / critical |
|---:|---:|---:|
| 11.40 | 0.22173 | 1.1247e−5 |
| 11.64 | 0.38533 | 1.5130e−5 |
| 11.84 | 0.61070 | 1.9340e−5 |

Even removing screening entirely at the same frozen coupling contributes
at most 0.001123 of the critical mass over these cases. The formal source
redshift stress case z_s=2.187 gives stars 0.2800/0.4866/0.7712 and
R1 addition no more than 2.443e−5 of the circular critical mass. These
separate cases do not resolve conflicting redshift inputs. No source
redshift is needed for the main fractional-deflection transfer.

## Independent optical correspondence checks

For enclosed bare mass m(r), use M_eff=m F, where
F=2 epsilon/(1+sqrt(1+a m/r^3)). Its logarithmic slope is the pinned
positive-density formula. Integrating its density through the
projected cylinder by spherical shell containment and integrating
enclosed effective mass along the ray are independent projections.
Across all 46 cases their maximum relative discrepancy for the R1 term
is 2.56e−11. The total conventional projected mass agrees with explicit
stars plus R1 to 1.30e−12 of the input stellar mass. The exact
correspondence is at retained order; no two independent gravitational
contributions should be stacked.

The pointwise bound 0<=M_eff<=epsilon m implies the projected bound
because the cylinder shell-containment weight is nonincreasing with
shell radius: an integration by parts converts it to a positive linear
functional of enclosed mass. This bound is stronger evidence for a
non-closure of the luminous-only proxy than a numerical comparison at
one finite quadrature tolerance. For the central specified 1.30 arcsec
case, the formal contribution beyond 20 Mpc is bounded to 6.51e−6 of
the R1 correction within the branch formula; this is not a physical
exterior-matching or total error bound.

An inverse check maps a generated total back to the input bare mass
using the stable positive quadratic root and agrees to 3.33e−16 of
total stellar mass. This does not authorize applying both a
conventional fitted total mass and its R1 correction, or establish a
positive inverse density for arbitrary supplied total profiles.

Replay: run `python3 wgd_frozen_transfer.py` in this folder. Outputs:
`wgd_frozen_transfer.json`. Pinned source copies are under `pr23/`.
No repository changes, manuscript submission, or use of timing data.
