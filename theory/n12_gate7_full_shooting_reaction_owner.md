# Interval-13 full shooting derivative and reaction replay

Continued from `674c9165b8feb1e424e33669003395ce9a8a65eb` on
`theory/gate7-66d-reduced-adjoint-integration`, with initial local/remote agreement.
The old 8×8 extraction and its failed homogeneous replay remain unchanged.

**The complete center replay passes the frozen reprojection allowances.** The
descriptor discrepancy falls from 0.07882691264 to at most 8.393e-9 proof units,
against the unchanged 8.916e-7 allowance: approximately 9.39 million-fold reduction.
This is a first-order frozen-jet result with explicit signed defects, not a proof
of nonlinear slaving or exact nonlinear equivalence of boundary and shooting rows.

## Exact residual ownership

The source and line ranges below are hash-bound, with the literal source excerpts
preserved in `artifacts/flagship_integration/gate7_full_shooting_owner_20260926/report.json`.

- `scripts/audit_n12_gate7_correlated_descriptor_newton_midpoint_replay.py:49–78`
  owns endpoint assembly, midpoint incidence and the 99-component shooting residual.
- `scripts/audit_n12_gate7_constraint_descriptor_hermite_collocation_candidate.py:67–77`
  owns the augmented rate `f=(G/||G||, Delta/||G||)`. The last residual is the
  integrated descriptor-rate equation, **not** the diagnostic eigenvalue-minus-s
  fiber residual stored separately by the midpoint producer.
- `src/bhsm/interface/aether_forward_c2_exact_fixed_s_field.py:167–217` owns G,
  selected eigenline, complementary response, and Delta. In particular,
  `Delta=c_psi*b_psi+s*remainder`. Eigenline/response and normalization enter f;
  they are not additional independent rows in this 99-component residual.
- `scripts/materialize_n12_gate7_correlated_descriptor_augmented_jacobians.py:61–84`
  assembles the fixed-descriptor state Jacobian, descriptor column and last
  descriptor-rate row. These frozen Jacobians retain their numerical-predictor
  authority; the replay does not promote them to new uniform derivative certificates.
- `scripts/materialize_n12_gate7_augmented_fixed_descriptor_block_newton_predictor.py:67–87`
  owns both Newton blocks, their signs, trial/test frames and the left forcing.
- `scripts/audit_n12_gate7_current_green_componentwise_two_radius.py:102–115`
  owns the causal map `C_i=-M_i^-1 N_i`; the signed-transverse consumer loads
  these blocks and saves the maps at lines 683–689 and 740–745.

For y=(weighted state,s), h=1/4, and f_j=f(y_j), the exact assembled expression is

```
m = (y13+y14)/2 + h/8 (f13-f14)
R13 = [y14-h f14/6] + [-y13-h f13/6] - 2h f(m)/3.
```

There is **no separate additive history/current-Green term** in this assembler.
History enters through endpoint dependence. The producer's max(s,0) clamp is
inactive at the stored endpoint and midpoint centers checked here.

With J13, J14 and Jm denoting the frozen rate Jacobians,

```
B_left  = I/2 + h J13/8
B_right = I/2 - h J14/8
L13 = -I - h J13/6 - 2h Jm B_left/3
R13' = I - h J14/6 - 2h Jm B_right/3
M = Te14^T R13' Tr14
N = Te14^T L13 Tr13
dR_reduced = M dc14 + N dc13.
```

Frames are held fixed in this center derivative. Trial descriptor scale is 1e-7,
test scale 1e6. The saved residual and midpoint replay exactly in binary64. Arb
chain-rule replay errors against the stored blocks are at most 1.627e-15.

## Owned left-history lift and reaction identity

The corrected binding producer at
`scripts/checkpoint_n12_gate7_66d_tangent_binding.py:51–56,79–96` builds the 72-column
reset family F_k by causal transport, then appends the projected augmented flow
v_k. Its descriptor flow component is the physical rate divided by 1e-7.
Let A be the **saved node-14 launch coefficients**, used at both endpoints:

```
V13 = [F13,v13] A
V14 = [F14,v14] A.
```

Using node-13's independently chosen child coordinates here would be wrong.
The 72-column identity `M F14+N F13=0` holds up to stored rounding. The appended
flow is not silently assumed to satisfy it: its signed defect is saved. After
the node-14 launch pullback, the 72-column contribution has Frobenius bound
4.739e-14 and the flow contribution 2.237e-6 in full 74D residual coordinates.
Their sum, not an independent magnitude tail, is retained.

For saved trial P, W=(P^-1)_{q,:} Te14^T and P_p=P[:,0:66], define

```
U_left=Tr13 V13, U_right=Tr14 P_p
F_right = W (U_right - h J14 U_right/6)
F_left  = W (-U_left - h J13 U_left/6)
F_mid   = -2h W Jm (B_left U_left+B_right U_right)/3
F_total = F_right+F_left+F_mid
Dphi_candidate = -Q_inverse_proposal F_total.
```

Q and its inverse proposal are the frozen 8×8 objects; no extraction was repeated.
The actual chain-rule reaction coefficient differs by a retained signed deltaQ.
Its Frobenius bound is 8.069e-13; the computed equation residual
`Q Dphi_candidate+F_total` is at most 2.685e-19.

The physical center rows are independently assembled from the normalized Stage-B
interface operator A_n X^-1 and the saved causal descriptor graph s-g c_state.
The interface row owner is
`src/bhsm/interface/aether_cross_resolution_reconnaissance_v21_35.py:3199–3282`:
trace, momentum minus fixed environment momentum, and
`child_flux+momentum_rate-force+event_flux`. The saved Stage-B R23 differentiates
these with the environment fixed. The descriptor graph is only first-order
causal authority, not a new nonlinear equation.

Write these physical rows in split coordinates as [G_p,G_q]. The exact affine-jet
bridge, including every retained defect, is

```
[F_total,Q_actual] = B [G_p,G_q] + [E,deltaQ]
B = Q G_q^-1; E = F_total-B G_p; deltaQ = Q_actual-Q.
```

F_total is computed from the frozen producer chain before constructing this bridge;
no missing forcing is fitted to the desired answer. E is saved as a signed 8×66
matrix, with Frobenius bound 7.574e-9. Neither E nor deltaQ is set to zero. Thus
the result establishes center replay within declared allowances, not global
equality of zero sets or a nonlinear theorem.

## Signed decomposition and replay

The scalar projection below is `<d_term,d_expected>/||d_expected||²`. It records
signs along the expected descriptor row; the full vectors are stored and summed
before norms. Norms in the second column are not added as error bounds.

| Contribution to descriptor reaction | Row norm | Signed projection |
| --- | ---: | ---: |
| Direct right endpoint | 0.000587825 | -0.00307158216 |
| Direct left endpoint | 0.0791227774 | +1.01288332330 |
| Midpoint, both incidences | 0.00235964986 | -0.00981182055 |
| Separate external history term | 0 | 0 |
| Signed sum | approximately 0.07806854 | +0.99999992059 |

The omitted left derivative, including its midpoint incidence in the original
Newton left block, explains the former failure. Final normalized boundary-row
errors, in channel order, are approximately
`[8.87e-10, 5.35e-11, 1.17e-10, 8.84e-10, 4.86e-9, 1.32e-9, 5.48e-9]`.
Every row is below its propagated Case-B allowance (approximately 3.98e-8).
Descriptor error is at most 8.393e-9 proof units, or 8.393e-16 physical units.
The descriptor allowance is copied unchanged from the previous checkpoint;
boundary allowances apply the frozen interface rows to the same stored child
reprojection bound. No tolerance was retuned.

## Reproduction and next boundary

The artifact directory contains hashes, literal source-line provenance, both
history lifts, signed forcing and reaction terms, physical rows, bridge and
defects. Two fresh runs of `scripts/bind_n12_gate7_full_shooting_reaction.py
--out <new-directory>` reproduce reports and arrays byte-for-byte.

Focused tests include differentiation of the actual frozen assembler expression
(extracted without importing or running its producers) with an independent
nonlinear synthetic rate, as well as frozen residual/block replay, source hashes,
signs and unchanged allowances. The three checkpoint test files run with
`python -m pytest --noconftest tests/test_gate7_full_shooting_reaction.py
tests/test_gate7_eight_reaction_center.py tests/test_gate7_66d_tangent_binding.py -q`.
Result: **16 passed**. Both final materializations are byte-identical.

Next work must extend the owned endpoint/history lift and this defect-aware row
identity to the unchanged physical tube before nonlinear slaving can be claimed.
No nonlinear work was performed in this task. Stage B, the original 8×8 diagnostic
and the interval-13 local gain 0.72221510 remain frozen.
`Gate7_closed=False`; `FULL_BHSM_COMPLETE=False`.
