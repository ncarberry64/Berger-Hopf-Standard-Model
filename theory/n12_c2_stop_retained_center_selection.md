# N=12 retained global stop-center selection

Status: `QUARTER_STEP_CENTER_SELECTED_FOR_KRAWCZYK; INTERVAL_RADII_OPEN`.

Both compared centers start at the same certified reset datum and integrate
the same retained denominator-free action-arclength field.  The exact
combined-direction identity is used for the quarter-step realization.  Both
stored descriptor polynomials have exact rational Bernstein first-hit
certificates.

A proof center must be judged by the correlated Green image of its defect,
not by the largest pointwise residual alone.  With matched twelve-point Gauss
residual sampling and fine-grid graph Jacobians:

| center | pointwise residual max | correlated correction max | terminal state correction | macro tangent leakage |
|---|---:|---:|---:|---:|
| step `0.5` | `2.609140837701298e-5` | `1.814522961013384e-5` | `1.8145229610133837e-5` | `1.6070913898564564e-6` |
| step `0.25` | `1.5496153409065845e-5` | `3.486903140325637e-6` | `1.983149361661596e-6` | `4.1315518794963806e-7` |

Thus the quarter-step center reduces the global correlated correction by a
factor `5.203823817268202` and the terminal state correction by a factor
`9.14970398141405`.  Gauss-8 and Gauss-12 values of the quarter-step global
correction differ by only about `0.18%`.  It is the retained numerical center
for the global Krawczyk enclosure.

This choice is a proof-coordinate optimization, not a physical member
selector.  It does not assert that the center is an exact orbit and does not
close Gate 7.  Promotion still requires outward-rounded `Y`, `Z1`, and `Z2`,
plus transfer of the certified first hit and every retained domain margin.
