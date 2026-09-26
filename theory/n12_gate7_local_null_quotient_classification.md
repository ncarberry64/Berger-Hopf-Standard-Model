# Interval-13 local null: quotient and environment classification

Base: `d44d75bf60a1a783777795fcd395f6d95d259e7e`, branch
`theory/gate7-66d-reduced-adjoint-integration`.

**UNRESOLVED_OWNER_SCALAR**, vocabulary classification **UNRESOLVED**.
Neither gauge removal nor environment exclusion is owner-bound. This does not
prove that the true coupled symmetry cannot account for the direction, and does
not require inventing a scalar equation. It corrects the previous dimension
note's premature next-step priority: first recover the quotient/environment
binding. No new equation, quotient, nonlinear proof, or physical failure is claimed.

## Frozen unit null and blocks

For the stored coefficients, the exact positively oriented unit direction is

```
v = (1, -M13^-1 N13 e_s)
u = v / sqrt(v^T v).
```

Normalization uses Euclidean reduced proof coordinates. A descriptor trial unit
is `1e-7` physical units; the historical test scale remains `1e6`. The packet
stores Arb512 rational endpoint enclosures of every component of u, its binary64
center, the original left-descriptor normalization, and source hashes. Its exact
stored-matrix unit-null replay is bounded by `4.982e-153`; the saved binary64
unit-vector replay is bounded by `1.755e-17`. These are algebraic center bounds,
not physical-tube certificates. A unit displacement is not asserted admissible.

| Block of unit null | Value or norm |
| --- | ---: |
| Left state, including child/boundary/normal directions | exactly 0 |
| Left descriptor, proof units | 0.5905685412122307 |
| Left descriptor, physical units | 5.9056854121223064e-8 |
| Right 73 state coefficients, norm | 0.5442475816210054 |
| Right descriptor, proof units | 0.5958383740832282 |
| Right descriptor, physical units | 5.958383740832281e-8 |
| Right seven boundary coordinates, norm | 0.00166055639815758 |
| Both descriptor axes, proof-coordinate norm | 0.8389246509071522 |

The seven boundary coordinates in the frozen action-Hessian complement are

```
(1.956755999885406e-4, 1.408073376640726e-5, -1.370127971276699e-5,
 1.677213821490635e-4, 1.022548750489034e-3, 3.539536924060459e-4,
 1.232782622110434e-3).
```

The full right state in action and raw coordinates is saved. There are no
independent midpoint/eigenline/response variables in this 75-coordinate problem.
The dependent midpoint incidence is saved as
`du_mid=(du_left+du_right)/2+h(J_left du_left-J_right du_right)/8`, `h=1/4`,
using the frozen endpoint Jacobians. No derivative producer was called.

## Time owner: what is available and what is missing

`theory/n12_continuum_singular_hitting_reset_relation.md:75-105` owns the
fixed-event 31-by-98 Jacobian, raw fiber dimension 67, and retained 66 count.
The more specific owner audit
`theory/n12_reset_time_quotient_generator_audit.md:1-30` and its stored JSON state
`WHOLE_SYSTEM_TIME_QUOTIENT_COUNT_RETAINED_EXPLICIT_HYBRID_GENERATOR_OPEN`.
They explicitly reject local child flow as the coupled hybrid time generator:
the stored reset-flow relative residual is about `0.01135975`, and distance from
the fixed-event kernel about `0.00358421`. Those old calculations were not rerun.

The intrinsic force-root equivalence in
`theory/n12_intrinsic_time_quotient_force_root.md` does not supply this generator
or a basis for its Hessian quotient. It cannot identify the current null by the
dimension count. The actual coupled-generator angle, its event evaluation, and
an action metric owning its quotient are consequently **unavailable**, not zero.

The available endpoint archive stores normalized cancelled-field rates
`f=(G/||G||, Delta/||G||)`. This parameter is arc, not proper time. The exact
fixed-s field owner gives `F_s=G/Delta`, `Dlambda[F_s]=1`
(`src/bhsm/interface/aether_forward_c2_exact_fixed_s_field.py:108-129`).
We compare these stored rates diagnostically without renaming them the coupled
generator. Their least-squares state-frame residuals at 13/14 are
`1.962e-11` and `2.116e-11`.

There is **no exact lift of this local flow into the 75-dimensional slice**:
the slice fixes the left state, whereas the local flow's left action-state rate
has norm 1. Its 75-coordinate projection simply discards that motion. We save
this diagnostic projection and the full 148-coordinate endpoint pair so that
discarding it cannot silently become a gauge operation.

| Diagnostic comparison | Principal angle | Signed overlap | Unit projection residual |
| --- | ---: | ---: | ---: |
| Full 148 reduced endpoint pair, arc rates | 89.95536474 degrees | 0.0007790321391 | 0.9999996966 |
| 75-coordinate projected flow, not an exact lift | 89.93687623 degrees | 0.001101717462 | 0.9999993931 |
| Full pair of F_s endpoint rates | 89.95523453 degrees | 0.0007813046863 | 0.9999996948 |
| Action-weighted state pairs only | 89.98881890 degrees | 0.0001951469681 | 0.9999999810 |

The last row uses the owned state weights, but supplies no descriptor extension
or metric for the coupled quotient. These are numerical comparisons of stored
centers, not outward quotient certificates. No frozen tolerance is modified.

## Event covector and environment

`Dlambda` acts on the state. It is not `ds` on an independently varied carried
descriptor. The stored diagnostic eigenvalue-gradient evaluations give:

| Covector | Node 13 | Node 14 |
| --- | ---: | ---: |
| Dlambda[u] | exactly 0 | 5.26959364345241e-10 |
| ds[u] | 5.9056854121223064e-8 | 5.958383740832281e-8 |
| Dlambda[F_s], stored center replay | 0.9999999992359555 | 0.9999999992808836 |
| (Dlambda-ds)[u]/1e-7 | -0.5905685412122307 | -0.5905687804397758 |

The symbolic transversality identity is exact in the field owner; the displayed
gradient replay is a binary64 diagnostic. In particular the zero left state
makes Dlambda[u_left]=0 independent of eigenvalue-gradient uncertainty.

The fixed Stage-B environment is explicit:
`source/bhsm_gate7_stageB_direct_interface.py:91-136` holds event q, momentum and
flux fixed and differentiates `_child_rows_at_order` in the 98-state. That owner
(`aether_cross_resolution_reconnaissance_v21_35.py:3199-3282`) contains trace,
constraint, momentum and flux equations, with no independent carried s input.
At the left their derivative on the null is exactly zero. They do not supply a
scalar E with E(u) nonzero that identifies the extra descriptor as excluded.

The typed environment descriptor in
`theory/bhsm_environmental_child_compatibility_selection.md:36-44` is
`(alpha_s,tau_s,I_s,Lambda_s,B_s)`. Its support restrictions do not select a
member within a supported sector (lines 265-304); the explicit boundary datum
remains missing in `bhsm_environment_conditioned_reset_selector_recovery.md`.
No source-level mapping from that tuple to the independently carried s13 was
found in these implicated owners. Thus **E(u) is unavailable**. The declaration
that environment directions are held fixed cannot manufacture this mapping.

After neither removal was justified, the targeted scalar-owner check found the
already-written fiber `lambda(Y)=s` in the fixed-s field (lines 73-75).
Its candidate derivative above detects the null strongly. The local shooting
candidate, however, assigns s separately from state projection; its midpoint
fiber discrepancy is stored diagnostically. The fiber is not an established
environment condition or a proved nonlinear local initial/history graph. We
neither impose it nor set s13 to zero. This identifies an existing owner family
for later binding, without proposing new physics or searching more broadly.

## Child and boundary projections

Use the already-frozen `P=diag(X[Z,L],1)`; solve `P c=u_right` without
re-extracting the 8-by-8 block. L is the action-Hessian boundary complement.
The split has a large condition number, so coefficient norms are not physical
budgets. At the stored center:

| Projection/component of right state | Norm |
| --- | ---: |
| Oblique child component, action norm | 5.78994066165536 |
| Oblique boundary component, action norm | 5.69402355914403 |
| Their signed sum, action norm | 0.5442475816210053 |
| Orthogonal projection onto child state subspace | 0.5442314105658407 |
| Residual from that child state subspace | 0.004195456331354981 |
| Orthogonal projection onto boundary subspace | 0.4519210139100942 |
| Projection onto the full augmented 66D child graph, proof norm | 0.5463523916810766 |
| Residual from the full augmented child graph, proof norm | 0.5939089679696924 |

The oblique components cancel substantially. The two orthogonal projections are
separate subspace diagnostics, not additive components. The normalized right
interface response has norm `0.0016605563981576875`. The entire null cannot be
classified PERSISTENCE_FREE from its large state-child projection: it also has
boundary response and independent descriptor displacement. NORMAL_SLAVED,
GAUGE, ENVIRONMENT_EXCLUDED, and TRANSITION_ONLY are not established either.

## Checkpoint and stop

`scripts/classify_n12_gate7_local_null.py` consumes only frozen arrays and source
text. `artifacts/flagship_integration/gate7_local_null_classification_20260926/`
contains the report, exact rational unit-null enclosures, arrays, SHA256 source
ledger, literal source-line provenance, and two-process byte-identical replay.
Validation: `python -m pytest --noconftest tests/test_gate7_local_null_classification.py tests/test_gate7_local_child_flow_dimension.py -q`
passed **6 tests**, including the frozen dimension gate, source hashes, null
replay, flow-projection distinction, covector ownership and oblique reconstruction.

No 74-by-74 quotient system is formed: its rank/condition and Schur/reaction
replay are inapplicable until Case A or B has an owner. The old 8-by-8 extraction
and passing center replay remain frozen. The exact next task is to bind the
coupled hybrid generator and induced node-13 coordinate lift, or an explicit
environment/fiber initial-datum covector, before removing this direction.

`Gate7_closed=False`; `FULL_BHSM_COMPLETE=False`. Stop after this classification.
