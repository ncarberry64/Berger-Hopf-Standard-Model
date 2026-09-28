# Gate-7 current calculation scope: existing obligations only

This is an implementation-scope reconciliation of `8dc85376`, following the
user's instruction of 28 September 2026. It adds no completion gate and
changes no completion criterion, physical domain, tolerance, action term,
or Gate-7 status. The definition of done and gate ledger remain authoritative.
Earlier checkpoint phrases requiring a **full incoming history** mean an
action-sufficient realization or its equivalent contracted response; they
must not be read as requiring exact reconstruction of every historical state.

## Existing completion obligations and the work that serves them

These names are references to existing obligations, not new gates.

| Existing obligation and owner | Current calculations that support it | Required result; stronger work not required |
|---|---|---|
| Joint operator/variational-domain realization: [definition of done, lines 3–13](BHSM_1_0_DEFINITION_OF_DONE.md#authoritative-current-completion-state); [operator-data owner](../theory/n12_joint_finite_history_operator_data_gate.md) | Coefficient/duration response, incoming M11 or compliance, existing C2 response, reset transport, contacts, graded heat and zeta | An action-owned realization sufficient to evaluate the consumed contractions with controlled error. A direct operator/response oracle is explicitly an alternative to path reconstruction. |
| Projected same-action force: [finite-endpoint force](../theory/n12_finite_endpoint_zero_source_force_functional.md); [projected Cauchy criterion](../theory/n12_c2_projected_adjoint_cauchy_criterion.md) | Frozen local terms plus signed history/heat-minus-zeta/contact pullback; Q66; coefficient/duration cotangents | The combined physical covector. Neither the ambient covector nor each sector must vanish separately. Only the retained projected tail must converge if that route needs a tail. |
| Same-action nonlinear root: [forward–adjoint KKT owner](../theory/n12_finite_endpoint_forward_adjoint_kkt.md); [existing existence alternatives](../theory/n12_forward_adjoint_kkt_existence_gate.md) | Reset/descriptor residuals, internal elimination, stationarity, current normal/launch incidence | A certified root on one admissible regular stratum, using the existing reduced or coupled formulation. No universal reachability, separately selected incoming duration, or exact-history pre-solve is imposed. |
| Constrained geometry Hessian and root response: [formation KKT implementation](../src/bhsm/interface/formation_stationarity_kkt.py) | H66, moving-reset curvature, normal lift, B66x73, implicit adjoints | Correct reduced Hessian/mixed forcing, or their complete linear actions, on the physical tangent. A generic ambient Hessian or all internal second jets are not required. |
| Physical pair-plus-contact **source** Hessian: [KKT owner's distinction](../theory/n12_finite_endpoint_forward_adjoint_kkt.md); [mixed operator contractions](../src/bhsm/interface/heat_zeta_mixed_boundary_launch.py) | Retained source vertices, pair term, genuine mixed/contact term, graded internal response | The source-Hessian blocks already required by the claimed physical readouts. H66 and the material 4x73 are not substitutes for all of these blocks. Do not expand the declared observable/source set. |
| Same-action interface and persistent physical tangent: [co-moving interface owner](../theory/n12_gate7_comoving_slaved_interface.md); [native 3+4 owner](../theory/n12_gate7_geometric_material_port.md) | Three geometric traces, two momenta, two dynamic fluxes, seven-row response, coupled interface elimination | The action-derived state/interface response at fixed external data. Seven outputs are slaved quantities, not seven new external inputs. A triangular output graph alone does not establish feedback. |
| Nonlinear physical-history/persistence bounds: [current reproduction guide](GATE7_CURRENT_REPRODUCTION.md); [uniform remainder owner](../theory/n12_gate7_uniform_remainder_formulation.md); [existing budget](../artifacts/flagship_integration/gate7_global_checkpoint_20260923/current_history_budget.json) | Existing Layers A–D, moving branch/domain coverage, normalized physical rate contractions, HS incidence, signed causal remainder | The existing self-map/contraction and physical admissibility conclusions on their declared domains. Point jets or a symmetric H66 alone do not prove persistence. Direct required remainder bounds can replace stronger tensor enclosures. |
| Existing continuum, observable and reproduction obligations: [definition of done](BHSM_1_0_DEFINITION_OF_DONE.md) | Previously owned continuum proofs, declared readouts, benchmark and reproduction records | Unchanged. Finishing the incoming contraction is not automatically full BHSM completion. Retention registration is not a new numerical formation equation. |

The machine-readable crosswalk inventories **all 32 dated calculation
packages in the active 26–28 September continuation**, every tracked report
inside them, their source-listed producers, and the inherited global
remainder/chart/stop/continuum obligations. Older diagnostics are mapped as
reusable evidence or superseded routes, not promoted into fresh requirements.
This is not an instruction to rerun those packages or every historical
Gate-7 experiment in the repository.

## Minimum completion-facing numerical object

For the present incoming contribution, the target is an **evaluator of the
contracted, internally reduced same-action response on the existing regular
domain**, not a stored exact incoming trajectory. Its force/root interface is

```
q(xi,P),       H(xi,P) u,       B(xi,P) v,
xi in R66,     u in R66,        P,v in the current R73 chart.
```

Here q is the derivative of the complete pulled-back reduced action; H and B
are its physical and mixed derivatives. The arrays q66, H66 and B66x73 are
one convenient materialization of this interface. Matrix-free actions are
equivalent when they cover the directions the existing root/response solver
uses and carry the required operator-error control. Storing all 73 internal
history columns is not necessary to produce all 73 output columns.

The interface also supplies, or remains composable with, the **existing**
canonical material values/derivatives and geometric traces needed by the
fixed-environment persistence calculation. It must preserve any separately
requested physical source-Hessian contractions. It retains domain, branch,
normalization, reference and error evidence sufficient for the existing root
and persistence proofs. This does not require a new certificate format.

The absolute scalar action value is not an additional requirement of q/H/B
unless an existing residual or the chosen root proof uses it. Action values
already consumed by constraints/energy or relative normalization remain
included. The current descriptor/reset residual is likewise retained; an
arbitrarily tiny residual is not silently made zero.

This is a minimum **output contract for the current obligations**, not a
proof of the globally smallest state dimension. No new independent physical
input or reduced input count is inferred from the 66-dimensional tangent.

Exact trajectories are unnecessary even for a rigorous root proof. For
example, on the existing valid reduced chart, suppose a compressed evaluator
supplies `q_hat` with error `e_q` at the center and `H_hat` with uniform
operator error `e_H` on the proposed root neighborhood. With the proof's
preconditioner C, the existing Newton bounds can use

```
Y <= ||C q_hat|| + ||C|| e_q,
Z <= sup ||I-C H_hat|| + ||C|| e_H.
```

Those errors enter the existing self-map/contraction calculation; no new
tolerance is chosen here. The corresponding stationary response estimate,
on an invertible physical block or its already-owned border, is

```
||Y_true-Y_hat|| <= ||H^-1|| *
    (||H_hat Y_hat+B_hat|| + e_H ||Y_hat|| + e_B).
```

Root-location uncertainty must also be included when rebinding H/B. Thus a
compressed representation needs certified errors in the **consumed norms**,
not an exact trajectory. Pointwise finite differences or finitely many
matrix-vector samples alone supply neither the uniform error nor an
operator inverse/spectral certificate.

## Why an exact full history is stronger than necessary

Let n represent a history realization's internal variables and let
`F(xi,P,n)=0` be its owned equations. The representation may be a causal
shooting scheme, variational boundary-value scheme, transfer/compliance
system, or an equivalent operator realization. A regular constrained chart
can include the reset-normal elimination in n; alternatively use the existing
bordered KKT equations directly. A frozen pointwise Q66 alone is not a
nonlinear chart.

At a common internal solution put

```
A = F_n,  X = F_xi,  Z = F_P,
A^T eta = Gamma_n^T,
L = Gamma - eta^T F,
q = Gamma_xi^T - X^T eta,
U = -A^-1 X,
C = L_xi,n + U^T L_nn,
A^T Lambda = C^T,
H = L_xi,xi + U^T L_n,xi - Lambda^T X,
B = L_xi,P  + U^T L_n,P  - Lambda^T Z.
```

These are the general implicit-objective identities already implemented in
[the mixed reducer](../src/bhsm/interface/heat_zeta_mixed_boundary_launch.py).
The displayed full U is explanatory: directional solves and adjoints can
stream the needed contractions. No explicit inverse, stored full internal
first jet, internal second-jet tensor, or separate history per sector is
necessary. The L blocks include the contracted residual curvature
`-eta^T F_ab`; omitting it changes the Hessian when the objective is not
stationary in every internal variable. Compose signed sectors before bounds.

On the stationary constrained base, the existing reset formula is

```
N_P = -J^T solve(J J^T, R_P),
H66 = Q^T L_yy Q,
B66x73 = Q^T (L_yP + L_yy N_P),
L_yy = Gamma_red,yy + sum mu_i R_i,yy.
```

Off shell, use a consistent nonlinear pullback or the complete bordered
residual. Do not apply the stationary formula as an off-shell moving-frame
identity. A root proof may solve the existing coupled state/operator/adjoint
system directly; a separately certified full history is not a mandatory
prerequisite to starting that equivalent solve.

## Smallest justified history representation

The next representation retains only the following **consumed information**:

1. The classical attached-action integrals and their required projected
   derivative contractions, with owned endpoint terms. Spatial fields can be
   streamed or eliminated once their contribution and error are retained.
   Endpoint density alone is insufficient.
2. The incoming terminal response `M_f(z)` or regular compliance `C_f(z)`,
   its required contracted variations, and the **interior spectral
   contribution** needed for the same graded functional. Glue it to the
   retained child and contacts once. Only the spectral evaluations and
   remainder control required by the functional calculus are needed; one
   arbitrary negative-axis sample is insufficient.
3. The signed heat-minus-zeta force/Hessian/material contractions themselves,
   including duration, lapse and moving-boundary terms. If these can be
   evaluated directly, neither a stored transfer family nor stored
   coefficient and duration paths are separate deliverables.
4. The root/persistence residual and output-error bounds consumed by the
   existing proofs. Retain unresolved physical directions unless their
   effect on these outputs is proved absent or enclosed within the existing
   error budget.

The interior qualification is essential, not a new dependency. For a block
pencil with interior D and boundary block C,

```
det(P-z) = det(D-z) det(C-z-E^T(D-z)^-1 E).
```

The boundary Schur response alone discards the first factor. Decoupled
interior modes can leave that response unchanged while changing a heat
trace. Therefore a boundary-only representation must preserve the relevant
interior graded spectral term, or prove its cancellation for the existing
action and requested derivatives. This is not a demand to compute every
interior eigenpair. The direct joint trace contraction is an alternative.

Two representations are action-sufficiently equivalent for this work only
when they preserve the above requested derivatives and proof predicates on
the domain being certified. Exact factorization, an existing Schur/adjoint
identity, or certified output-error bounds can establish this. A small local
residual or agreement at one point cannot establish neighborhood equivalence.

## Necessity of retained dependencies

| Candidate dependency | Existing mathematical reason to retain information | Narrow form permitted |
|---|---|---|
| Coefficient variation | `D Gamma_heat = STr(Q(P) DP)`; classical integrand variation | Only projected coefficient cotangents/vertices, or their total action contractions |
| Proper duration and lapse | For an element `Gamma=h*l`, `D Gamma=l*Dh+h*Dl`; `d tau=N dt` | Duration/clock contractions in the same signed action; no independent duration selector |
| Local eigenline/hard response | `q=Gamma_xi^T-F_xi^T eta`; internal response can enter consumed coefficients | Needed solves/adjoints and contractions; the saved 124x66 is reusable evidence, not a completion requirement |
| Internal curvature | Differentiating the implicit objective gives `L_ab=Gamma_ab-eta^T F_ab` | Only contracted residual curvature appearing in H/B/material outputs |
| Moving reset/normal response | `B=Q^T(L_yP+L_yy N_P)` and multiplier curvature | Existing normal/mixed contractions; no new reset matching campaign |
| Genuine mixed/contact operator term | `D^2 Gamma_heat=STr(DQ[DP_v]DP_u+Q D^2P[u,v])` | Pair plus required mixed/contact traces, not a generic operator tensor |
| Incoming 73-direction dependence | `B=D_P q` and the material port's `D_P` | Adjoint contractions in the owned current chart; no separate full history Jacobian |
| Momentum-rate response | Dynamic flux derivative is `DF-DG-D2Pi[X,u]-DPi[DX u]` | These material contractions only; configuration force cannot replace flux |
| Positive physical domain and event consistency | Existing operator domain and nonlinear constraints must hold at the certified solution | Coupled residual/enclosure or regular chart; no requirement for an exact binary candidate first |
| Unresolved tails or discretization error | An omitted term can change q, H, B, a source Hessian or an existing persistence inequality | Bound only the consumed projected quantities; finite-stop and infinite-route requirements must not be accumulated |
| Nonlinear persistence variation | Existing self-map/contraction bounds concern the whole allowed neighborhood | Direct remainder/operator bounds; point H66 does not imply them and a generic high-order tensor is not mandatory |

These identities establish why the **effect** must be retained absent a
proved cancellation. They do not prove that every listed summand is nonzero
in BHSM, nor that a particular algorithm or internal variable is necessary.
To pursue a new dependency, first identify the existing obligation, the
specific non-eliminated term above or another owned equation, and why an
already retained contraction/bound cannot supply it. An uncomputed operand
alone is not a proof that a larger representation is necessary.

## Corrections to the last checkpoint's interpretation

- Fixed endpoint radius removes its independent first-order input; it does
  not by itself remove interior, launch, or mixed-reset effects. No Q66 column
  is discarded.
- The nonzero **formal clock** witness does not prove a nonzero contribution
  to the final signed reduced action. It prevents a kinematic shortcut; it
  does not create an independent amplitude input or completion gate.
- The candidate's small nonzero descriptor is an existing event-constraint
  defect. Carry it into the current coupled root/domain check. It does not
  justify demanding a separate exact-event reconstruction before evaluating
  any force. An off-domain positive-duration calculation must still fail
  rather than clamp the sign or substitute a proof cutoff.
- A value-only, current source-bound local solve does not complete the
  history response. Conversely, completeness of the response does not
  require exporting every internal state.
- No standalone exact duration family, entire 73-column history, full
  ambient spectrum, or generic unused second jet is required unless a
  specific existing contraction cannot otherwise be evaluated and bounded.
- The existing one-seam external-source supersession remains in force:
  E0 is Dirichlet generating data, `M_f=M11` is internal, and there is no new
  pre-E0 arm, B_birth input, reflected history or external environment law.

## Bounded next work

Reuse the frozen local/Q66/reset/C2 evidence. Assemble one signed
incoming/joint **action-contraction evaluator** for q, H actions, B actions,
and the required material responses, using the existing implicit adjoint
and operator formulas. Allocate coefficient, clock, transfer or residual
work only where that evaluator exposes a needed unsupplied contraction.
Use the existing coupled KKT route if a separate parametric history solve
would duplicate work or require an unowned endpoint selection.

After those numerical contractions and their required error bounds exist,
use the existing same-action root and persistence proofs. The physical
source Hessian and downstream completion obligations keep their original
scope. This reconciliation does not claim that q66, H66, B66x73, the root,
or Gate 7 have now been numerically completed.
