# Interval-13 nonlinear slaving: first missing representation

The center owner checkpoint `35b37277c5e5590eee992ae2b51dc89cc0a0234b` remains
frozen. Its center reaction replay passes. No tangent, Stage-B, descriptor-scale,
8×8 extraction, shooting ownership or local-contraction calculation was reopened.

**Stop: the inspected frozen dependency chain does not yet provide an owned
nonlinear child/reaction endpoint-history lift.** Uniform reaction invertibility
and self-map have not been tested; this is not a failed invertibility theorem or
evidence of physical instability. No expensive producer is authorized or invoked
by this finding.

## What is available and what is missing

The full-owner packet saves V13 and V14, two center first-derivative matrices.
Its physical row bridge is explicitly an affine-jet identity with a signed
defect. It does not define an off-center physical family.

`scripts/regenerate_n12_gate7_shared_site_models.py:31–76` constructs the frozen
shared rate model in endpoint parameters. Its 450 symbols are 150 state symbols
theta and 300 direction symbols u,v. Each endpoint theta block has one
longitudinal interval and one 74D transverse Euclidean ball. u and v are
derivative directions, not independent physical states. Its complete field
derivatives remain useful on their original domains.

`scripts/materialize_n12_gate7_shared_history_cells.py:69–88` builds the dense
Hermite image from those affine endpoint states and their linked physical rates.
It preserves endpoint dependence through midpoint incidence, but supplies no
new 66+8 physical-child parameterization. Dense interpolation in time is different
from the nonlinear dependence of the endpoints on child/reaction coordinates.

The first required object is

```
Gamma: (p,q) -> (Y13(p,q), Y14(p,q)),
p in the declared 66D child domain, q in an owned 8D reaction domain,
```

with common parameter identifiers, endpoint values and first/mixed jets, an
outward inclusion into the existing endpoint product balls, and the off-center
physical boundary/descriptor row identity with signed defects. It must extend
the frozen center history/flow lift. An arbitrary affine extension of V13/V14
would define a proposed family; its equality to the intended physical family
and its tube inclusion would still need proof.

The original physical radii, in order longitudinal/transverse, remain exactly

```
4325777291715173/4722366482869645213696  (~9.160189721418071e-7)
4683284956119277/2417851639229258349412352 (~1.9369612593815614e-9).
```

These are the frozen endpoint group radii. They cannot simply be relabeled as
a radius for p or for each boundary/descriptor coordinate. The inspected center
packet does not contain a certified reaction product domain obtained by such a
pullback. No new radii are proposed here.

## Derivative obligation, retaining both endpoints

For the already-owned residual, write J0=Df(Y13), J1=Df(Y14), Jm=Df(m), h=1/4,
and A0=D_q Y13, A1=D_q Y14. With frozen reaction projection W,

```
m = (Y13+Y14)/2 + h(f(Y13)-f(Y14))/8
D_q m = (A0+A1)/2 + h(J0 A0-J1 A1)/8
K = W [A1-A0 - h/6 (J0 A0 + 4 Jm D_q m + J1 A1)].
```

For a proved triangular history lift, A0 may vanish in the reaction directions;
its vanishing must be owned on the domain, not inferred from the center. The
p derivative retains both endpoints exactly as in the successful replay.
Existing full-shooting tests already guard the left and midpoint signs.

Even an adequate enclosure of the ambient field Hessian does not supply the
missing lift derivatives. For example,

```
J(Y) A - J(Y0) A0 = (J(Y)-J(Y0)) A + J(Y0)(A-A0).
```

The second term requires variation of the endpoint/history lift. The same issue
occurs in midpoint incidence and the physical row bridge. Consequently there is
no justified numerical bound for K0^-1 DeltaK from the inspected representation.
This is an input gap, not a computed large variation bound.

The frozen numerical Q also differs from the actual center chain by the already
recorded signed deltaQ (Frobenius upper bound 8.069e-13). Any future
`K=Q+DeltaK` must include that center defect; it must not assert exact equality
between Q and the physical center derivative or discard the defect.

## Self-map and next task

Inclusion additionally requires an owned reaction domain and a signed enclosure
of F_q(p,q_predictor(p)) on the same common child parameters. A center descriptor
row or its reprojection allowance is not a nonlinear residual radius. Neither
uniform inverse bounds nor reaction self-map bounds are claimed here.

The next task is to construct and certify Gamma and its product-domain inclusion
from the retained causal/reset, flow and boundary equations. Only then can the
existing shared rate graphs be pulled back with common p dependence to form
DeltaK and evaluate a reaction self-map. Whether a new scientific producer is
needed cannot be decided before this representation is specified.

The companion `scripts/checkpoint_n12_gate7_nonlinear_lift_gap.py` records source
hashes, exact inherited radii and center inverse diagnostics without re-extraction.
Its report uses null for uncomputed variation, uniform inverse and self-map
bounds. The inherited sigma_min is approximately 0.09939261502; the stored inverse
proposal has operator norm approximately 10.06110967. A rigorous Frobenius-based
upper bound for the inverse of the stored binary64 Q is 10.40241084 (rounded up).
This is not a uniform inverse bound on the tube.

Two fresh runs reproduced byte-for-byte, and assertions verified that all
uncomputed bounds remain null and all completion flags false. The two focused
tests `test_chain_rule_against_actual_producer_expression` and
`test_signed_contributions_preserve_left_forcing` passed with `--noconftest`.
No mixed-curvature reduction
or comparison with the frozen 0.27778490 margin is justified at this stop.
`Gate7_closed=False`; `FULL_BHSM_COMPLETE=False`.
