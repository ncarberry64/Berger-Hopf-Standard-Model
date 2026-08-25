# N12 reset-fiber radius jet and scale-center audit

Status: `TIME_QUOTIENT_CANNOT_REMOVE_ALL_RADIUS_JET_VARIATION_COMMON_SCALE_RETAINED_PHYSICAL_CENTER`.

At the certified complete-child reset, restrict the two action-owned boundary
covectors

`delta x`, `delta(D_tau x)`, with `x=log R4`,

to the 67-dimensional kernel of the fixed-event `31 x 98` reset Jacobian.
The resulting `2 x 67` map has singular values

`2.6101789046984036`, `0.18441692331001722`,

and hence rank two.  Analytic derivatives agree with direct centered
differences along both right-singular directions to better than `5.3e-11`;
the reset-tangency residuals are below `2.4e-14`.

This rank statement does not require the missing explicit hybrid time vector.
For any one-dimensional time generator `g`, quotienting the target Cauchy jet
by `span(A g)` lowers the rank by at most one.  At least one radius-history
jet therefore survives the already-retained whole-system time quotient.
Moreover the fixed scalar-channel coefficient jet

`V=exp(-2x)`, `D_tau V=-2 V D_tau x`

has determinant `4 exp(-4x)>0` as a map from `(x,D_tau x)`.  The surviving
radius jet is consequently a genuine fixed-channel coefficient-history
variation, not merely a coordinate label.

The common scale must also be classified correctly.  It is a center of the
homogeneous weight-seven balance, but the complete retained action contains
weights `5,3,1,-1` and a boundary Casimir of weight `-1`.  Its zeta functional
has a nontrivial common-scale variation.  Thus common scale is a physical
modulation/force direction in the full saddle, not an exact gauge direction
that may be quotiented away.  The exact autonomous whole-system time
translation remains a gauge equivalence; the twelve leading descriptor
lapse/velocity kernel vectors are lifted at relative order `R^-2` and are not
promoted here to twelve exact full-action gauges.

Reset kinematics, time translation, and common-scale symmetry therefore do
not prove fiber invariance of the exterior response.  Only a separate
retained-action quantum trace-cancellation theorem could still provide that
shortcut.  In its absence the actual finite-stratum parametric exterior
oracle and its first two physical geometry jets remain required.

`FULL_BHSM_COMPLETE=false`.
