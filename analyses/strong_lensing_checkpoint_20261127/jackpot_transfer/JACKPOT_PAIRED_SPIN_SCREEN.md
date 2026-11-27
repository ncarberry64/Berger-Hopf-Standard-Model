# Coordinated spin: fixed-ray pair interaction and Jackpot transfer

Test the author's same-pool idea as a conditional optical fixture. Two hypothetical regular-side responses have equal Gaussian widths, same depth, a 1.7335 arcsec projected separation from center to inter-ring midpoint, and projected axis from the earlier early-data-only full-annulus fit. None of these is a measured spin location or proof of co-rotation. Reversing one input reverses its signed regular deformation, not the masses, while the quadratic graph optical response integrates squared line-of-sight gradients. This model tests optical overlap, not the missing spin-to-flow equations.

First compute the plus-plus, minus-minus, plus-minus and minus-plus maps at fixed rays. Taking the signed four-way mean cancels all single-object terms exactly, including deliberately nonzero additive fixtures. The shared optical term survives and equals the analytic product template. For this equal-width case its line-of-sight potential is a Gaussian about the midpoint weighted by exp[-d²/(4 ell²)], about .779. Verified against direct line integration and differentiation. Do not treat cross terms generated only by image inversion as evidence for this mechanism.

Propagate only that isolated interaction, with plus/minus signs, on the same frozen Chabrier ordinary-plus-envelope lens. Predeclare two sensitivity normalizations in which the hypothetical self-bend RMS at the early knots is 3% or 10% of the existing static envelope bend RMS. These are not measured spin energies. Refit the same three nuisances on the 14 early knots, trace the third-source counterimage from A, and only then score with B. For a diagnostic preserving the circular mass constraints exactly, take the circular mean of the radial pair deflection out of the added map instead of letting it shift the mass. This projection is not a physical conservation derivation, but tests whether the distinctly angular part can explain the holdout without moving the calibrated apertures.

| Trial | Early fit RMS, mas | B error, mas |
|---|---:|---:|
| Frozen baseline | 31.4 | 346 |
| 3% raw pair, coordinated | 50.2 | 295 |
| 10% raw pair, coordinated | 103.7 | 158 |
| 3% angular-only pair, coordinated | 30.0 | 345 |
| 10% angular-only pair, coordinated | 44.2 | 345 |
| 3% angular-only pair, counterrotating | 37.3 | 346 |

At 3%, the matched circular-mean-preserving map alone moves B by about 37–38 mas at fixed baseline nuisances. After refitting the rings, only 0.7–0.9 mas remains. The apparent raw benefit does not pass the inner checks. Do not infer that all shared angular dynamics are degenerate: this is a simple overlapping equal-width fixture, with one orientation and a chosen host, not an action-derived rotating flow. No transfer. Replay: OPENBLAS_NUM_THREADS=1 python jackpot_paired_spin_screen.py.
