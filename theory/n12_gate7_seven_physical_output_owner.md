# Seven physical outputs: exact definition and Outcome C

Continuation of `6c1ec7dc`. The seven native outputs are now an explicit
assembly, with their original row positions and signs bound to source.
The complete joint-history derivative cannot yet be evaluated: the exact
missing numerical owner is the **current-center N12 joint graded
heat-minus-zeta operator jet**. This is an existing action functional whose
numerical realization is missing, not a request for an environment law.

## G7 is the actual complete-child output

At N12, `_child_rows_at_order` in
`aether_cross_resolution_reconnaissance_v21_35.py:3199` returns 32 rows:
three trace, 25 constraints, two momentum, two dynamic flux. The seven
native outputs select zero-based rows `(0,1,2,28,29,30,31)`. The 25 omitted
output rows remain internal equations in `F_joint`.

Writing `z` for the event variables and `y` for the internally solved child
and history variables, the existing equation is

```
R7(z,y) = [ T(q_child-q_event)
            P_child-P_event
            Gamma_child + DP_child[X_child] - F_child + Gamma_event ].
```

`native_seven_outputs.py` assembles exactly these residuals, or their jets in
common parameter columns. It contains no random/test projections. The
three rows of T are owned by `_trace_jacobian_at_order:2751`; the momenta,
force and configuration/velocity lifts by `_canonical_pair_at_order:2998`;
the dynamic sign by `_child_rows_at_order:3274`. Source text, lines and
hashes are included in the packet.

The material outputs and child-required outputs are defined separately:

```
G7_event = [Tq_event; P_event; Gamma_event],
G7_child_required = [Tq_child; P_child; F_child-DP_child[X_child]-Gamma_child],
R7 = diag(I5,-I2) (G7_child_required-G7_event).
```

Thus the same seven native equations require equality of these two output
maps. The event arm enters the residual with `diag(-I5,+I2)`. The G7 to
differentiate for a material-response comparison is the unsigned reaction
map, not the complete-child residual. A derivative of the entire
residual along a solved boundary graph vanishes by definition; that zero
must not be mislabeled the nonzero material reaction of its event arm.
The child momentum-rate terms are not duplicated on the event side.

## The first unavailable physical input

The exact dependency is

```
CURRENT_CENTER_N12_JOINT_GRADED_HEAT_MINUS_ZETA_OPERATOR_JET
```

It supplies the actual closed finite-history graded operator `P_joint`
and its action-owned coefficient/geometry jets in the recentered node-13
realization, or an equivalent controlled full spectral/Weyl realization.
The functional owner is
`forward_finite_endpoint_heat_force.py::heat_regulator_value_and_force`.
Its docstring and signature require the caller to supply the positive
operator and geometry jets; it does not construct that history.

The frozen
`BHSM_N12_GATE7_JOINT_HEAT_COTANGENT_REVERSE_SEED.json::matching_audit`
explicitly records both
`actual_complete_joint_operator_value=ACTUALLY_MISSING` and
`actual_complete_joint_operator_first_jet=ACTUALLY_MISSING`.
The force-functional packet likewise records the finite-history operator,
temporal form and geometry jet as unavailable. These exact records are
hash-bound here; their numerical witnesses are not rerun.

The closest seam packet,
`BHSM_N12_AE2_COVARIANT_SEAM_ENCLOSURE_Z_MINUS_1.json`, encloses covariant
load jets at **one resolvent point**, z=-1. It explicitly leaves
`complete_heat_spectral_family=OPEN`. That cannot be substituted for

```
Q(P) = (1/2) exp(-ell^2 P) P^-1,
D Gamma_heat[P_a] = Re Tr(Q(P)^dagger P_a).
```

For a physical reaction derivative, already at fixed heat length the next
chain-rule level contains

```
D_b D_a Gamma_heat = Re Tr(DQ(P)[P_b] P_a + Q(P) P_ab),
```

with the retained grading/multiplicities, zeta subtraction and any moving
boundary/lift terms applied in the same action coordinates. A norm bound
on a scalar force or a z=-1 load does not supply these signed boundary/history
mixed contractions. The absence occurs before a physical seven-output
right-hand side can be supplied to the adjoint solve.

## Consequence for the requested seven adjoints

The existing reduction remains

```
F_y^T Lambda = G7_y^T,
R_joint = G7_xi - Lambda^T F_xi.
```

Once its physical seeds exist, the owned coefficient-history recurrence
reverse-transports each of the seven covectors. No 73-column forward-history
campaign is needed and no autonomous external source is added. But the
local 125 border is not `F_y` for the complete heat/contact stationarity
problem, and frozen flow transitions do not generate missing output seeds.
The prior exact local cancellation and historical split remain unchanged.

Accounting A is `LOCAL_ALREADY_INCLUDED`. For B-J, the retained internal
terms remain active, but none of the requested numerical classifications
can be selected for the **complete** reduced rows from the missing jet.
They are not set to zero, marked inactive, or declared distinct corrections.
The packet uses null for these undecided entries. In particular the earlier
local descriptor/constraint cancellation is not generalized to all joint
descriptor, normalization, contact or history variables.

The existing two-sided seam assembly retains `M_f`, transported `M_C2`,
`U_R`, `W_phys` and the owned gauge/scalar/AE2 contacts once. Only `J_ext=0`.
No internal block is removed and no extra `Lambda_E` is introduced.

## Outcome

**Outcome C:** the numerical realization of the current-center joint
graded heat-minus-zeta operator and its boundary/history jet is absent from
the recovered owner chain. Its action law and reverse formula already exist.
This identifies the first unavailable owner input without repeating the
seam search or the historical test-covector split.

`Delta_history`, complete rank, correction rank/norms, largest correction
entry, and the seven physical adjoint residuals are unevaluated; no zeros
or error bounds are fabricated for them. The local 7x73 is not promoted.
No tolerance changes, local derivative reruns, Stage-B or history campaigns.
`Gate7_closed=False`; `FULL_BHSM_COMPLETE=False`.

Reproduce this binding with
`scripts/bind_n12_gate7_seven_physical_outputs.py --out <new-directory>`.
Packet: `artifacts/flagship_integration/gate7_seven_outputs_20260927/`.

Validation: seven new focused tests bind row selection, orientation using the
actual frozen native jet, source/packet hashes, and repeat determinism. The
report repeats byte-identically. The initial orientation assertion used Arb
interval equality incorrectly; it was corrected to compare stored midpoint
and radius exactly, without altering data or tolerance. Together with the
53 checkpoint tests, the focused suite has 60 tests.
