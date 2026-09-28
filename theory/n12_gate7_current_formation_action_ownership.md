# Current incoming formation action: ownership before summation

Base: `2e0a5fbd001df789e3b0ac0f9dd85659e2f0beb1`, branch-23 incoming
half of the saved current reset candidate. This ledger specifies accounting;
it does not claim an evaluated history functional or stationary root.

The 32 independent reset rows leave the complete 66-dimensional admissible
incoming formation tangent. These directions are retained as formation
unknowns. Their existence is not a rank defect; their gauge/time ownership
and stationary response must be determined by the same action.

## Action and reduction

The retained accounting is

```
Gamma_form = Gamma_attached^zeta + Gamma_heat - Gamma_SM^zeta
Gamma_heat = -1/2 STr E1(ell^2 P_joint)
Gamma_red(a,P) = Gamma_form(a,P,n(a,P)),  F_n(a,P,n)=0.
```

Here `a` denotes the incoming state in the existing weighted action
coordinates, and `P` denotes the 73 launch parameters, not the heat operator
`P_joint`. The functional includes the owned history and endpoint domain;
evaluating the local Lagrangian at a terminal state does not evaluate it.
The reference law is recorded in
[the finite-endpoint force owner](n12_finite_endpoint_zero_source_force_functional.md).

## Term ledger

“Retained” in a derivative column means that the corresponding derivative
must enter the complete current reduction. It does not assert a nonzero
numerical contribution at the as-yet-unsolved history. `ALREADY_INCLUDED`
means no additional summand is added. `INTERNAL_ELIMINATED` specifies the
required accounting route; the current numerical elimination is not complete.

| Sector | Classification | Covector | Hessian | Launch forcing | Owner / accounting |
|---|---|---|---|---|---|
| Classical incoming bulk / formation | ACTIVE | Retained | Retained | Retained | Attached action integrated on the current incoming history, with its owned moving endpoints |
| Parent-side history | ALREADY_INCLUDED | Retained | Retained | Retained | Domain of the bulk and replacement functionals, not a second copy of either action |
| Seam / attachment | ACTIVE | Retained | Retained | Retained | AE2 attachment and common operator domain; moving attachment and material seeds retained |
| Reset pullback | ALREADY_INCLUDED | Retained | Retained | Retained | Existing reset constraint and boundary reaction pullback; Lagrange multiplier curvature retained; reset residual is not a penalty action |
| Heat-minus-zeta graded replacement | ACTIVE | Retained | Retained | Retained | Signed joint operator heat trace minus the zeta term already present in the attached action |
| Transverse gauge contact | ACTIVE | Retained | Retained | Retained | Wentzell `K_F c_group sqrt(Delta1)`, assembled in the common operator once |
| Scalar / topographic contact | ACTIVE | Retained | Retained | Retained | Nonaffine scalar potential and owned source incidence; no separate delta term inferred from the sector name |
| Pair / mixed contact vertices | ALREADY_INCLUDED | Retained operator variation | `Tr(DQ[dP]dP)+Tr(Q d2P)` | Same mixed contractions | Derivatives of the common heat operator; not independent forces added after the heat derivative |
| Canonical momentum | ALREADY_INCLUDED | Boundary variation | Momentum response | Momentum response | Derived from the same attached/reduced action and canonical lift; do not add momentum itself to the scalar action |
| Dynamic flux | ALREADY_INCLUDED | Material boundary variation | Material response | Material response | `F-Gamma_conormal-DPi[X]`; the regularized arc derivative alone is not the physical-time term |
| Descriptor / normalization / internal response | INTERNAL_ELIMINATED | Common objective adjoint | Contracted Lagrange Hessian | Common mixed adjoint | Retain full internal equations before projection; no frozen internal variables or sectorwise norm substitution |
| Independent reset-frame source | ZERO | Zero independent source | Zero independent source | Zero independent source | AE2 `nabla U_R=0`; transported physical variations remain included |
| Independent fermion delta contact | ZERO | Zero | Zero | Zero | AE2 owns `S_Sigma_F=0`; does not zero gauge/scalar response |
| External birth source | ZERO | Zero external source | Zero external source | Zero external source | The retained zero-external-source problem; internal contact/history terms remain active |
| Second outgoing C2 action copy | NOT_PRESENT | No extra copy | No extra copy | No extra copy | The common boundary/reaction functional already accounts for C2; fixed-C2 annihilation does not imply zero launch forcing |

The contact identities are implemented and sourced in
`scripts/derive_n12_gate7_mixed_boundary_launch_contract.py`. The fixed-C2
annihilation statement belongs to
`artifacts/flagship_integration/BHSM_N12_C2_FIXED_SEED_UPSTREAM_FORCE_OWNER.json`.
It concerns only the fixed-C2 kernel, not all 73 moving launch columns.

## Frozen current frame

`scripts/freeze_n12_gate7_formation_action_basis.py` consumes the saved
current projector and basis. It projects and orthonormalizes all 66 columns
in 512-bit Arb arithmetic without changing the reset or selecting a member
of the formation family. The owned raw-coordinate metric is `W^T W`, with
the unchanged candidate `state_weights`. Both coordinate representations
are saved:

```
Q66_current       in a = W delta_state_raw coordinates
Q66_current_raw = W^-1 Q66_current
q_form = Q66_current^T g_action = Q66_current_raw^T g_raw.
```

This is a pointwise frame enclosure at the saved candidate, not a moving
frame over a solved history. Constraint curvature still belongs in the
stationarity Hessian. The existing certified rank and full-column-rank
frame establish that no compatible direction was discarded.

The current outward Frobenius bounds are `1.021172e-66` for `J_reset Q66`
and `7.628859e-68` for `Q66^T Q66-I`. Arrays and report reproduce
byte-identically in two separate runs under
`artifacts/flagship_integration/gate7_formation_action_basis_20260928/`.

## Exact reduced launch assembly

The existing stationarity module now contracts its assembled Lagrangian
system into the reset tangent. At a stationary base, with `J=R_a`,

```
H = Gamma_red,aa + sum_i mu_i R_i,aa
M = Gamma_red,aP + sum_i mu_i R_i,aP
N_P = -J^T solve(J J^T, R_P)
H_form_66 = Q66^T H Q66
B_launch = Q66^T (M + H N_P)
delta_a = N_P delta_P + Q66 delta_y.
```

The normal lift is a coordinate decomposition of the moving constraint;
it does not pin any of the 66 physical formation unknowns. This retains the
launch forcing from moving reset geometry, which would be lost by using
`Q66^T M` alone. The saved basis is not assumed constant over a history.
Constraint curvature in the Lagrangian is the stationary-base moving-normal
correction; these formulas are not asserted as an off-shell Newton chart.

Focused tests compare this reduction against the complete bordered solve,
including a curved constraint and a nonzero moving normal. The existing
73-test suite plus four new tests gives **77 passing tests**. These algebraic
witnesses are test fixtures, never BHSM numerical inputs.

## Numerical inputs still to instantiate

The current reset packet supplies neither the current incoming temporal
operator nor its complete coefficient/duration family and internal solve.
The current spectral/history packets describe the C2 side. The reusable
incoming amplitude/compliance packets have a historical base and must not
be relabeled as current. The relevant current inputs therefore remain:

1. Current incoming coefficient history, durations, material clock, and
   common positive operator/domain, including retained contacts.
2. The complete internal residual and its current normal inverse or owned
   quotient, together with the objective covector and contracted residual
   curvature needed by the general objective adjoint.
3. Their dependence on the 98 incoming action coordinates and 73 current
   launch parameters, including the moving reset and endpoint incidence.

No local gradient, outgoing C2 coefficient row, historical affine history,
or zero-filled array is substituted for these inputs. Consequently this
frame/ownership step does not yet emit the action covector, constrained
formation Hessian, launch forcing, stationary root, or formation first jet.
`Gate7_closed=False`; `FULL_BHSM_COMPLETE=False`.
