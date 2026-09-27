# Coupled interval-13 fiber center and signed physical-chart derivatives

Subsequent physical clarification: fix the external environment and its
boundary-class labels, while allowing action-slaved interface reactions.
Do not interpret the alternatives below as a request for seven free external
inputs or for manually fixed interface values. The local derivative work and
remaining coupled binding are recorded in
`n12_gate7_comoving_slaved_interface.md`; the original numerical certificate
below is preserved unchanged.

Continuation of `752fff23b4809572b292c5a25deb1f8675ef32c1` on
`theory/gate7-66d-reduced-adjoint-integration`.

The selected Euler–Dirac fiber equation now participates in a nonlinear
interval-13 center solve. A local replacement neighborhood certifies a
unique root of the **declared coupled equations**. This is a new center
result, not a projection or promotion of the old center.

The numerical residual fell from `9.36745e-7` to `1.38522e-61` in eight
updates. The left physical fiber residual is at most `2.78619e-81`;
the scaled constraint residuals are at most `2.86699e-75` at node 13 and
`4.47351e-66` at node 14. Every endpoint/midpoint evaluation verifies the
normalized, positively oriented index-24 line with Arb512; a binary64
eigenvalue never supplies the descriptor. The existing numerical Jacobian
only proposes iterations. All residuals are reevaluated from the action.

## Equations and coordinates

Write `z=(W Y,s)`, `h=1/4`, and use the existing normalized augmented rate f.
The coupled equations are

```
C(Y13)=0, C(Y14)=0,                         25 + 25 rows
Te14^T [z14-z13-h(f13+4 f(m)+f14)/6]=0,     74 rows
lambda_event(Y13)-s13=0,                    1 row
m=(z13+z14)/2+h(f13-f14)/8.
```

Unknowns are 25 left constraint-normal coordinates, the left descriptor,
98 right state coordinates, and the right descriptor: 125 in total.
The 73 remaining left coordinates are parameters. The trial/test descriptor
scales remain `1e-7` and `1e6`. No post-solve constraint projection is used.

Eliminating constraint normals gives a 75×75 center matrix. At the resolved
point its numerical rank is 75, smallest singular value approximately
`0.089658827`, and condition number `49.7045533`. The complete signed
Jacobian, inverse defects, 8×8 reaction block, Schur complement, and implicit
forcing/reaction matrices are saved. These quantities are recomputed from
the local action derivatives, not copied from the frozen predictor.
The uniform 75×75 left/right inverse defects are bounded by `5.927e-23`
and `7.803e-23`; the 8×8 reaction block has diagnostic condition `10.16097`.

## Replacement neighborhood

The neighborhood radius is `2^-180` in the declared normal/descriptor
coordinates. This tiny neighborhood certifies the center; it does not
replace the requested full physical parameter tube by a smaller claim.
With a fixed inverse proposal R, the calculation proves

```
Y = ||R F(0)||_infinity,
Z = sup_box ||I-R DF||_infinity,
Y + Z*r < r,  Z < 1.
```

The report records outward rational bounds, approximately `Y=9.147e-62`
and `Z=3.477e-22` for the descriptor-graph chart. Both that chart and the
fixed-label phase chart pass. The midpoint image is enclosed using signed
Hermite–Simpson incidence and the endpoint mean-value derivatives before
support. Separately enclosing endpoint rates was too wide; it was replaced
locally, without changing any physical tolerance.

The full unprojected 99-component shooting defect remains `3.63940e-12`;
the right-endpoint fiber defect remains `1.60755e-18`. These discretization
defects are retained. This certificate does not assert that all 99 shooting
components vanish, or identify the projected shooting equations with seven
nonlinear boundary-value equations.

## Two tangent interpretations, kept explicit

The descriptor-graph jet solves the full coupled first-order problem and
has 66 input directions with `ds=g*dY`; s is slaved, not independent.

For a fixed label, replace the left descriptor unknown by the existing C2
flow-aligned phase coordinate **inside the same coupled Jacobian**. The
phase direction is fixed as an exact rational proposal and transversality
is verified; its fiber slope is about `8.25348e-11`. The implicit solve
gives rank 66 with exactly `ds13=0` and an outward enclosure of `g*dY13=0`.
This is a local flow-aligned action/fiber chart, not a claim that its affine
phase lines are exact nonlinear flow orbits.

The new chart differs substantially from A (old Stage B) and B (previous
owner correction): paired action-metric maximum angles are about
`3.04920` degrees, with projector operator differences about `0.0531935`.
The report retains all angles, signed coefficients and interval residuals.
The new paired projector's coefficient uncertainty has Frobenius upper bound
`5.030e-7`; this is reported separately from the frozen A/B transfer errors.

**The physical interface parameterization must be specified before C is
called the authoritative Stage-B child tangent.** The seven old normalized
interface rows act on this phase chart with row norms approximately
`[5.157e-4,3.712e-5,3.613e-5,9.686e-5,2.646e-3,5.951e-3,1.727e-2]`.
They are not zero. A 66D interpretation therefore requires the corresponding
transport of interface/environment data with phase. Holding both the seven
old interface data and the descriptor fixed instead imposes an additional
scalar restriction on the old 66D space. No new boundary condition or
environment response has been invented to decide between them. A direct
question requesting this BHSM parameterization was sent to the user.

## Saved work and continuation

Artifacts: `artifacts/flagship_integration/gate7_coupled_fiber_center_20260927/`.
The center, uniform action inputs, neighborhood proof and signed jet are
separate packets. `inverse_proposal/` contains numerical proposals only;
their validity is supplied by the subsequent uniform defect calculation.
The reproducibility receipt distinguishes fresh nonlinear center solves
from fresh compilation of frozen local derivative packets.
All six primary center/neighborhood/jet outputs reproduce byte-identically.
The seven focused tests pass with `python -m pytest --noconftest
tests/test_gate7_coupled_fiber_center.py -q`.

The previous domain result is preserved separately in
`gate7_fiber_domain_exclusion_20260927`: its complete frozen endpoint-13
fiber residual interval was `[-1.10605e-13,-7.67166e-14]`, excluding zero.
That result motivated this replacement neighborhood and did not stop the
coupled solve. It has no global nonexistence or instability interpretation.

Reproducers are `solve_n12_gate7_fiber_constrained_center.py`,
`certify_n12_gate7_coupled_center_neighborhood.py`, and
`differentiate_n12_gate7_fiber_constrained_center.py`. Focused checks are in
`tests/test_gate7_coupled_fiber_center.py`.

The next mathematical operation is to bind the intended environment phase
response (or fixed-interface restriction) to the signed coupled jet, then
extend its parameterized normal graph and compose reduced curvature with
the existing fixed-adjoint machinery. The local center is available for
that work. The unresolved boundary interpretation must not be hidden by a
projector comparison or a change of tolerance.

`Gate7_closed=False`; `FULL_BHSM_COMPLETE=False`. No frozen prediction,
Stage-B artifact, previous local certificate, or tolerance was altered.
