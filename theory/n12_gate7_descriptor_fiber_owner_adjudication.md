# Gate-7 descriptor identity and node-13 fiber adjudication

Base: `7d2a7db789391426dbd3b6529ab3a4e6c5ca7b7d`, branch
`theory/gate7-66d-reduced-adjoint-integration`.

**SAME_EULER_DIRAC_DESCRIPTOR_PROVED** for the historical C2 fiber and current
Gate-7 descriptor functional. **STOP_FROZEN_CENTER_OFF_DESCRIPTOR_FIBER** for
the requested center adjudication. The certified point enclosure proves that
the frozen node-13 pair does not satisfy the fiber equation. No 75th row is
appended, and no successful fiber-owner center milestone is claimed.

## Side-by-side owner ledger

| Item | Historical C2 fiber | Current Gate-7 |
| --- | --- | --- |
| Producing implementation | `certify_n12_c2_regularized_launch_segment.py:96-128`; fresh-chart `_jet` and branch selection in `certify_n12_c2_fresh_descriptor_fiber_eigenline_chart.py:60-102` | `_jet`, `_selected_line`, `exact_fixed_s_field_action`, `exact_cancelled_euler_dirac_field_action` in `aether_forward_c2_exact_fixed_s_field.py:20-38,51-87,108-145,197-217` |
| Action | `exact_full_action_jet_at_state(12,q,v,m,points=96)` | Identical function/module and call; the two `_jet` return expressions have identical ASTs |
| Operator | Raw reduced Hessian `D=L_zz=H[37:,37:]`, `z=(v,m)`, 61 by 61 | Same raw reduced Hessian; not `W^-1 H W^-1` |
| State domain | 98 components: 37 q, 37 velocity, 24 multipliers | Same ordering, dimensions and stored action weights |
| Physical arm | First 98 components of the terminal pair after the certified reset swap; now the outgoing C2 arm | The same C2 child continuation; “event” in lambda_event is the historical branch label |
| Branch | Largest absolute overlap with retained reference; zero-based index 24 in the historical chart | Same rule and index 24; point index additionally verified by outward inertia |
| Reference | Birth and fresh-chart archives | Byte-identical to both historical references |
| Eigenline | Real Euclidean unit vector in raw 61 coordinates, sign chosen for positive reference overlap | Same; frozen point proof certifies normalization and positive overlap |
| Scalar sign | Signed outgoing eigenvalue s>=0; not absolute value | Signed independently supplied s>=0; no eigenvalue sign reversal |
| Physical coordinate | s=lambda_event(Y); lambda_event^2 is a separate readout | Carried signed eigenvalue s; physical descriptor perturbation `ds=1e-7 ds_proof` |
| Residual scaling | Physical eigenvalue units | Test scale `1e6`, unrelated to changing the physical scalar |
| Treatment of floating eigenvalue | Explicitly diagnostic; signed s carried separately | Same diagnostic distinction; current s is corrected/transported separately from the state |

The historical fresh-chart record has
`physical_propagation_domain=EXACT_lambda_event_EQUALS_s_DESCRIPTOR_FIBER`.
The denominator theorem treats fixed-s errors in `ker Dlambda_event`; ambient
spectral balls certify the line and gap, not arbitrary off-fiber physical data.

In the current endpoint producer `_node`, state projection and
`descriptor=parent_descriptor+correction[98]` are separate. The parent uses a
correlated first-order descriptor transport. Thus identity of the scalar owner
does **not** imply that every numerical augmented center lies on its exact
fiber. Neither an operator redefinition nor a different physical descriptor is
needed to explain the failure below.

The comparison proves identity of this retained finite N12 action functional.
It does not claim new continuum spectral convergence or redo the frozen branch
continuation. The common reference, raw operator, selected index and certified
point normalization remove the notation-only ambiguity.

## Certified node-13 value replay

Reuse the already independently reproduced endpoint-13 point eigenpair proof
inside `.affine_eigenpair_pilot_work/endpoint_013/record.json`, located through
the frozen `gate7_shared_eigenbranch_links_20260923/certificate.json` source
ledger. Its array and record hashes are checked. Its exact rational center
matches all 98 frozen node-13 state entries with zero radii. Its binding hashes
match the current endpoint archive and the action implementation.

The selected eigenvalue is coordinate 61 of that normalized 62-variable
eigenpair proof. Its rational midpoint and radius are consumed directly in
Arb512; no point action or eigensolve is run. The existing certified machinery
encloses the same selected action eigenvalue used by the historical fiber.

| Quantity | Result |
| --- | ---: |
| s13, frozen physical coordinate | 4.27486392211581918044e-10 |
| lambda_event(Y13), certified point value | 4.27392731468065055923e-10 |
| R_fiber=lambda_event(Y13)-s13 | -9.36607435168621208930e-14 |
| Same residual divided by 1e-7 | -9.366074351686212e-7 |
| Original certified eigenvalue witness radius | 6.869413205938866e-123 |
| Selected zero-based index | 24 |
| Numerical point gap, diagnostic | 2.6077429332534634e-7 |
| Certified lower separation on the connected endpoint/midpoint link | 8.116990278265437e-9 |

Exact outward lower and upper endpoints are saved in the new report. The
residual enclosure is strictly negative and excludes zero. Its tiny radius is
the numerical uncertainty of the frozen point certificate, not an assertion
that the whole physical tube has that radius. The larger link gap has a distinct
uniform-domain role and is not substituted for the point value error.

No previously frozen tangent/reprojection allowance is a center-value tolerance
for this equation. Nor does a historical enclosure of a nearby exact history
make its stored predictor center an exact fiber point. The user-required frozen
center membership therefore fails. A nearby admissible correction may exist,
but none is constructed or claimed here; s13 and Y13 are unchanged.

## Fiber covector and tangent diagnostics

For the physical scalar owner,

```
D R_fiber = Dlambda_action dY_action - ds_physical.
```

On the exact unit null, `dY13=0`; the sign and scaling therefore give

```
D R_fiber[u]                 = -5.9056854121223064e-8 physical units
D (R_fiber/1e-7)[u]          = -0.5905685412122307 proof units.
```

The exact signed interval inherits the previous unit-null rational enclosure.
This evaluation needs no numerical eigenvalue-gradient approximation.

For the remaining row evaluations, the stored diagnostic action gradient and
physical tangent B13 give `[Dlambda B13/1e-7, -1]`. On the saved augmented 66D
child graph its residual row norm is `9.396019469218658e-7` proof units. This is
a diagnostic only: no new certified Dlambda radius or allowance is supplied,
and child compatibility is not promoted to a theorem.

For the seven node-13 boundary directions, use the same owned complement
convention as the frozen split: normalize final Stage-B R23 by its saved row
scales, form `H_T=T^T H_action T`, and use

```
L13 = H_T^-1 A_n^T (A_n H_T^-1 A_n^T)^-1
boundary13 = [X13 L13; 0].
```

Only frozen H, T, X and R23 are consumed. No action producer or 8-by-8 reaction
extraction is rerun. The saved-center duality defect is bounded by `6.830e-14`.
The fiber row on these seven state-only directions is, in proof units,

```
(0.7390532351, -0.6589251479, 0.7798278192, 2.189610997,
 -0.2686649322, 25.65729309, -3.147544001).
```

These coordinate-dependent responses do not change the established boundary
subspace and are not physical budget debits. They show the row's action on the
reaction directions; they do not supply a successful enlarged-system replay.

## Center stop and continuation requirement

Because the value replay fails, the requested conjunction of provenance,
center membership and tangent compatibility does not pass. There is no
75-by-75 system, rank/inverse claim, Schur recovery or repeated reaction replay
in this checkpoint. The existing 8-by-8 block and center replay stay frozen.

The historical interpretation is now unambiguous: an exact physical state is
on the selected Euler--Dirac fiber, while an independently carried numerical
descriptor and an approximate state can violate that fiber. Raw binary64
eigenvalues are still diagnostics. The high-precision certified point value
detects the actual frozen-center defect without replacing the signed coordinate.

The next prerequisite is an owner-bound treatment of this nonzero center fiber
defect, including any proposed recentering and propagation of its effect into
the frozen tangent/response data. That work was not authorized in this center
test and is not attempted. Do not relabel the result
`EULER_DIRAC_DESCRIPTOR_FIBER_OWNER_RECOVERED` or return to a broad scalar search.

Reproducer: `scripts/adjudicate_n12_gate7_descriptor_fiber.py`. Packet:
`artifacts/flagship_integration/gate7_descriptor_fiber_owner_20260926/`.
Two fresh processes reproduced the arrays and report byte-identically.
`python -m pytest --noconftest tests/test_gate7_descriptor_fiber_owner.py tests/test_gate7_local_null_classification.py -q`
passed **8 tests**, covering the signed interval exclusion, null derivative,
child/boundary evaluations, source integrity and fail-closed status.
`Gate7_closed=False`; `FULL_BHSM_COMPLETE=False`.
