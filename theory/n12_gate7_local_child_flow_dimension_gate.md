# Interval-13 parameterized child flow: center dimension gate

Base: `310035e63baab59d8cf2a941792782cc8f6e0715` on
`theory/gate7-66d-reduced-adjoint-integration`.

**STOP_LOCAL_INTERNAL_SYSTEM_NOT_SQUARE.** Replacing the unavailable nonlinear
history map by a local interval implicit problem is a legitimate change of proof
formulation. The supplied local equations, however, still need a scalar condition
selecting the left descriptor. The center test exhibits that freedom explicitly.
No failed physical stability or tube-inclusion claim is made.

## Variable and equation ledger

Keep 66 left complete-child coordinates external. In the full augmented endpoint
description, a favorable internal ledger is:

| Internal variables | Dimension |
| --- | ---: |
| Left constraint-normal and boundary complement | 25+7=32 |
| Left carried descriptor | 1 |
| Right augmented state, including child, boundary, descriptor and normals | 99 |
| Total | 132 |

Granting the seven fixed-environment interface equations at the left, the owner
equations used by the existing reduced Newton construction are:

| Equations | Count |
| --- | ---: |
| Left state constraints | 25 |
| Left interface equations | 7 |
| Right state constraints | 25 |
| Reduced full-incidence shooting equations | 74 |
| Total | 131 |

This grants the availability and invertibility of the endpoint state graphs for
the purpose of the dimension test; it does not certify those nonlinear graphs.
Even after those eliminations there are 75 unknowns (left descriptor plus all
74 right reduced coordinates) and only 74 equations. Adding midpoint or
eigenline/response variables with their defining equations does not remove this
one-dimensional deficit.

If all 99 ambient shooting equations are imposed together with both endpoint
constraint sets, the count becomes 156 equations for 132 unknowns. The existing
predictor records 25 normal shooting residuals; it does not supply identities
allowing them to be dropped as exactly redundant. This overdetermined system is
not asserted inconsistent, but is not the requested square implicit system.

## Exact ownership of the missing scalar

- `scripts/audit_n12_gate7_within_seam_constraint_center_obstruction.py`,
  `_constraint_geometry`, defines the 25 equations from 24 multiplier-gradient
  rows and the energy constraint. Its input is the 98-component state; the
  carried descriptor does not appear.
- `src/bhsm/interface/aether_cross_resolution_reconnaissance_v21_35.py`,
  `_child_rows_at_order`, supplies trace, canonical momentum and dynamic flux
  interface equations in that state and the fixed environment. These also do
  not fix the separately carried descriptor.
- `scripts/materialize_n12_gate7_augmented_fixed_descriptor_newton_endpoint_candidate.py`,
  `_node`, sets `descriptor=parent_descriptor+correction[98]` separately from
  `_project`. The pointwise descriptor-gradient diagnostic is not an additional
  nonlinear projection equation.
- `scripts/audit_n12_gate7_correlated_descriptor_newton_midpoint_replay.py`
  transports the descriptor in the last shooting row. Its
  `numerical_midpoint_descriptor_fiber_residual_diagnostic_only` is stored
  separately, not imposed as a zero equation.
- `theory/n12_gate7_augmented_fixed_descriptor_newton.md` explicitly fixes the
  reset endpoint in the original causal problem. Cutting history at node 13
  removes that supplied descriptor datum unless another owned boundary/fiber
  condition replaces it. The first-order transport described in
  `theory/n12_gate7_correlated_descriptor_newton.md` is not such a nonlinear
  condition.

No globally absent physical equation is inferred from this trace. The precise
gap is its binding to the proposed local child family. Promoting the numerical
eigenvalue-minus-descriptor diagnostic to an exact equation, holding s13 constant,
or reusing a center descriptor row as a nonlinear graph would add an unproved
condition and would require the mandatory center and tube checks.

## Cheap center assembly and null direction

Reuse the frozen M13 and the already-owned N13 from the full shooting packet.
After granting state-graph elimination and holding the external p fixed, form

```
K_cut = [ N13 e_s | M13 ],       shape 74 x 75,
v_null = (1, -M13^-1 N13 e_s).
```

The source M13 is invertible, so this matrix has exact full row rank 74 for its
stored coefficients and a one-dimensional kernel. The saved binary64 null-vector
residual has Arb512 Frobenius upper bound 5.306e-17. The exact algebraic null
formula is independently evaluated with Arb, and its replay bound is retained.

The 74 positive singular values have minimum approximately 0.14110794 and maximum
4.45654663, with ratio 31.58254. That ratio is **not an invertibility condition
number**: the minimum gain on the 75-dimensional internal domain is zero. A
two-sided internal inverse and its replay do not exist.

Normalize the null direction by one left descriptor proof unit (1e-7 physical
descriptor units). The right descriptor component is approximately 1.00892332
proof units and its state tangent-coefficient norm approximately 0.92156548.
This is a direction that can be scaled arbitrarily, not an assertion that a unit
step lies inside the physical tube.

The previous 8×8 block and its passing full-history center replay remain frozen.
They do not remove this newly externalized initial-descriptor freedom. A larger
square internal system does not yet exist, so its requested 8×8 Schur and 8×66
reaction replay are not performed or claimed. The non-square stop condition
occurs first; no further source search or nonlinear computation followed.

## Deliverable and next mathematical requirement

`artifacts/flagship_integration/gate7_local_child_flow_dimension_20260926/` stores
the variable/equation ledger, source hashes, K_cut, null vector and outward replay.
`scripts/diagnose_n12_gate7_local_child_flow_dimension.py` consumes only the frozen
blocks; it calls no action producer. Two fresh processes reproduce identical
bytes. This is a diagnostic checkpoint, not the requested local theorem.
Validation: `python -m pytest --noconftest tests/test_gate7_local_child_flow_dimension.py -q`
passed **2 tests**, checking the null replay, source hashes, equation counts and
fail-closed status flags.

The next requirement is an owner-bound scalar condition selecting the left
descriptor, together with a justified treatment of the normal shooting rows if
the full ambient residual is required. Only then can a square internal Jacobian
and the mandatory Schur replay be tested. No physical parameters or equations
were invented, no radii changed, and no nonlinear proof was attempted.
`Gate7_closed=False`; `FULL_BHSM_COMPLETE=False`.
