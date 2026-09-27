# Fixed environment and co-moving interface: local derivative checkpoint

Continuation of `ddc84f9e026df8cc8bc759adf5140590106e878a`.

The user defines the Gate-7 physical problem by fixed external environment
and boundary-class labels (`delta e=0`), with seven interface quantities
slaved by the complete action-owned boundary equations. They are neither
constants nor independent inputs. An action-derived co-moving tangent is
preferred if it differs from the saved fixed-label chart.

N12 is one persistent closed-envelope realization. Its seven retained rows,
scale, and response are not a universal definition of BHSM envelopes. The
user's supplied progeny hierarchy distinguishes null transfer, propagation-
supported envelopes, persistent enclosures, nested and composite children.
This scope clarification does not add an exterior constitutive equation.

## Completed child-side derivative

The existing `_child_rows_at_order` owner has, besides constraint rows,

```
T q - b_trace = 0,                                      3 rows
P(Y) - b_momentum = 0,                                  2 rows
Lq(Y)^T radial(Y) + DP(Y)[X(Y)] - Lq(Y)^T grad_q A
    + b_flux = 0.                                      2 rows
```

X is the owner's raw Euler-Dirac dynamics, P its lifted canonical momentum,
and Lq its constrained canonical configuration lift. The exact child output
map is now evaluated with Arb512 on the certified replacement boxes at both
nodes 13 and 14:

```
beta(Y) = [Tq, P(Y), Lq^T(grad_q A-radial)-DP(Y)[X(Y)]],
B_match(Y,b) = S (b-beta(Y)),  S=diag(-I5,+I2),
D beta_flux[u] = -D(Lq^T(radial-grad_q A))[u]
                 -D2P[X,u] - DP[DX u].
```

Canonical KKT lifts and dynamics are verified by interval inverse/equation
replay. D3/D4 contractions are streamed and signed. No finite difference or
raw numerical eigenvalue enters these packets. Direct and adjoint momentum
derivatives agree within their enclosures. Both complete endpoint packets
reproduce byte-identically.

Composing Dbeta with the saved phase-chart jet gives nonzero reaction rows.
Node-13 raw row norm bounds are approximately
`[5.96549e-4,3.92393e-5,2.43907e-5,0.00240452,0.00621341,3319.724,871.690]`.
These have different physical units, not dimensionless stability budgets.
Their size is not evidence of physical instability.

## Reclassified output-graph comparison

Appending two copies of B_match to the saved 125-row core produces

```
K_out = [ J                 0 ],
        [-S Dbeta Y_x       S ]
F_p   = [ F_core,p; -S Dbeta Y_p ],
x_p   = -J^-1 F_core,p,
b_p   = Dbeta (Y_p+Y_x x_p).
```

This 139-row output graph is invertible with 66 declared parameter columns.
Its state tangent agrees with the saved chart by a triangular Schur identity.
The numerical paired action-coordinate maximum angle is `2.44366e-13`
degrees; midpoint projector difference is zero. The independently enclosed
projector difference is `<=1.00584e-6`, reflecting loss of shared dependence
on interval subtraction. The exact state identity is stronger, but applies
only to this output-graph extension.

**RECLASSIFIED:** this is not the requested complete physical tangent
comparison. B_match,b=S proves unique outputs given Y, not unique state and
interface reactions at fixed environment. The original 125-core leaves part
of the left state complement fixed by chart choice. Appending outputs does
not solve that complement. Identical tangents here cannot establish a new
physical authority.

## Existing coupled feedback owner

The narrow trace found `_child_history_boundary_reaction_solve` and
`event_child_two_sided_reaction_match_audit` in
`aether_cross_resolution_reconnaissance_v21_35.py`. They use

```
Hzz nu - [B^T;0] rho_child = [gq-radial;0] - Hzq v,
B nu_q + attachment_curvature(q,v) = attachment_ddot,
rho_child + rho_env = 0.
```

B here is the two-coordinate attachment Jacobian. The caller solves the
child attachment acceleration from two-sided reaction matching. Thus the
existing action includes feedback into state dynamics. It is not the
triangular output graph above. Exact source texts and line ranges are
recorded with the new local feedback packet.

`derive_n12_gate7_boundary_feedback.py` derives the child response affinely
in a held-fixed exterior conormal value, without choosing or fitting that
value. The three columns are constant, rho_env,1 coefficient and rho_env,2
coefficient. They are not new physical input directions. For fixed sampled
rho_env, its signed first derivative is

```
Hzz Dnu[u] = D([gq-radial;0]-Hzq v)[u]
             - D[B^T;0][u] rho_env - DHzz[u] nu.
```

At node 13 the 63-row bordered inverse and 2x2 reaction/acceleration
compliance inverse are verified with Arb. Affine owner replay is bounded
by `6.68920e-34`. This conditional local operator does not replace the frozen
Gate-7 normalized flow or certify a different center.

## Exact remaining binding and signed reduction

**OPEN:** identify the fixed-environment conormal functional evaluated at the
moving interface, rho_env(b;e0), and its derivative in the same attachment
frame, then bind them to interval 13. The traced caller supplies the reaction
from a frozen event; it does not establish that moving-interface continuation.
This is a precise local binding issue, not a general claim that no such BHSM
source exists. The user's hierarchy response specifies the physical scope
but does not supply this functional.

Fixed external data imply delta e=0. They do not imply D rho_env=0: the
sampling location, normal and attachment frame can move. The general signed
derivative therefore includes `-[B^T;0] D rho_env`. Neither dropping it nor
identifying the exterior response with the child output map is justified.

For complete equations F(x,b,p;e0)=0 and G(x,b,p;e0)=0, eliminate with signs:

```
J_red = F_x - F_b G_b^-1 G_x,
f_red = F_p - F_b G_b^-1 G_p,
x_p = -J_red^-1 f_red,
b_p = -G_b^-1 (G_x x_p + G_p).
```

All seven state/interface directions must enter the q complement before
elimination. The eight-reaction/descriptor frame remains reusable once G
and the moving-interface environment evaluation are bound. Then compare
action-metric 66D projectors and use the action-derived tangent; agreement
with the saved tangent is not required. Mixed derivatives and Layer-C
rebinding remain conditional on that step.

## Reproduction and scope

Artifacts: `artifacts/flagship_integration/gate7_comoving_interface_20260927/`.
Producers: `derive_n12_gate7_slaved_interface.py`,
`bind_n12_gate7_comoving_interface.py`, `derive_n12_gate7_boundary_feedback.py`.
The receipt distinguishes endpoint computation, output-graph compilation and
local weak feedback. Focused tests: `tests/test_gate7_comoving_interface.py`.

Validation: 15 tests passed across that file and
`tests/test_gate7_coupled_fiber_center.py` using `--noconftest`. All eight
report/array outputs in the four new packets reproduce byte-identically.

No seven quantities were frozen or made independent. The complete co-moving
66D tangent has not been certified or rebound to Layer C. Prior centers,
Stage-B evidence, frozen producers and predictions are unchanged.
The transfer tolerance remains `8.915423761304125e-7`.
`Gate7_closed=False`; `FULL_BHSM_COMPLETE=False`.
