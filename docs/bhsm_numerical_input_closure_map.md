# BHSM Numerical Input Closure Map

Status: `STRUCTURAL_ARCHITECTURE_INTEGRATED_CONDITIONAL_NUMERICAL_CLOSURE_OPEN`

This closure map records the remaining symbolic inputs after the current BHSM theorem-discharge chain. It distinguishes structural closure from numerical closure and forbids fitting routes that would hide free knobs.

Machine-readable companion: `data/bhsm_numerical_input_closure_map.json`.

## Status Classes

- `DERIVED`
- `DERIVED_CONDITIONAL`
- `STRUCTURALLY_INTEGRATED`
- `STRUCTURALLY_MOTIVATED_NOT_DERIVED`
- `OPEN_LOCALIZABLE`
- `OPEN_UNRESOLVED`
- `FROZEN_CANDIDATE`
- `FORBIDDEN_TO_FIT`

## Ledgers

| sector | modes |
| --- | --- |
| charged lepton | `(0,0),(1,2),(3,3)` |
| neutrino | `(0,0),(3,0),(1,1)` |
| up | `(0,0),(6,0),(8,1)` |
| down | `(0,0),(0,3),(4,2)` |

The relation `k=q+2j` gives neutrino `k` values `[0,3,3]`.

## Integrated Structural Chain

BHSM now has an integrated conditional structural architecture for SM-like finite algebra, charges, Higgs/scalar mass generation, fermion hierarchy, CKM, PMNS, and CP sources. Numerical closure remains open.

## Phase Admissibility

PO-BH-41A is encoded as:

`alpha0` and `gamma0` are not standalone single-sector observables. They become physical only through sector-relative sampling.

The CKM phase source is:

`arg(Theta_12 Theta_23 Theta_13*)`

The sector displacement scaffold is:

`Delta y_ud = - H_topo^{-1} grad_y(delta S_partial^d - delta S_partial^u)|_{y0}`

## Neutral / PMNS Scaffold

The neutral topographic suppression route is:

`M_nu = epsilon_nu_topo M_nu^(0)`

`epsilon_nu_topo = exp(-S_nu_topo)`

`H_nu = epsilon_nu_topo^2 H_nu^(0)`

PO-BH-48 localizes `S_nu_topo` as the next neutral numerical-closure object.
The current candidate formula is:

`S_nu_topo = 1/2 Delta y_nu^T G_nu_topo Delta y_nu + S_barrier`

with

`G_nu_topo = 1/2 E_nu^T H_topo^(nu) E_nu`.

Status: `OPEN_LOCALIZABLE`. The candidate formula depends on deriving
`Delta y_nu`, `H_topo^(nu)`, `E_nu`, `S_barrier`, and the neutral finite-width
saddle/path from the boundary/topographic action. Numerical neutrino closure
remains open.

PO-BH-49 localizes `Delta y_nu` as a required input for the `S_nu_topo`
Hessian/barrier formula. Candidate definitions are:

`Delta y_nu = - H_H^{-1} grad_y[delta S_eff^(nu-H)]|_{y_H}`

and

`Delta y_nu = <y>_nu - <y>_H`.

Status: `OPEN_LOCALIZABLE`. The stationary-point route still requires
`S_eff^(nu)`, `S_eff^(H)`, `H_H`, and the neutral-minus-Higgs gradient. The
centroid route still requires explicit `W_nu`, `W_H`, a coordinate chart or
coordinate-invariant centroid convention, and gauge/coordinate invariance.
Numerical neutrino closure remains open.

PO-BH-50 localizes the neutral effective action `S_eff^(nu)` as the
action-level source for the neutral saddle displacement. The primary candidate
is a subsurface neutral topographic channel:

`S_eff^(nu) = S_bulk[Phi] + S_partial^(nu)[Phi] + S_subsurface^(nu)[Phi; ellapse_nu, g_sub]`

with stationary condition:

`grad_y S_eff^(nu)(y_nu) = 0`

and comparison to the Higgs/charged reference through:

`delta S_eff^(nu-H) = S_eff^(nu) - S_eff^(H)`.

Status: `OPEN_LOCALIZABLE`. The candidate route still requires the internal
subsurface metric `g_sub`, projection/lapse map `ellapse_nu`, neutral boundary
tensors `chi_nu^{AB}` and `lambda_nu`, neutral boundary conditions, and the
finite-width neutral profile. The subsurface-channel language allows only
exterior-projected anomalous propagation or apparent FTL from exterior-surface
viewpoint; it remains locally causal in the internal/topographic metric.
Numerical neutrino closure remains open.

PO-BH-51 localizes the subsurface neutral projection geometry required by
`S_eff^(nu)`. The current candidate objects are:

`ds_sub^2 = g_sub,AB dY^A dY^B`

`x^a = Pi_sub_to_ext^a(Y)`

`ellapse_nu^2 = ds_proj^2 / ds_sub^2`.

Status: `OPEN_LOCALIZABLE` for `g_sub`, `ellapse_nu`, and `Pi_sub_to_ext`.
The subsurface neutral projection geometry has been localized as a required
dependency for the neutral effective action. Candidate internal metric,
projection map, and exterior-lapse structures are documented. No local FTL or
numerical neutrino prediction is claimed. Missing dependencies include the
scalar/topographic profile, coordinate-invariant projection convention,
internal metric derivation, positivity/causality proof, and relation to neutral
boundary tensors.

PO-BH-52 localizes the neutral boundary tensors and boundary condition required
by `S_eff^(nu)` and the subsurface neutral channel. The current boundary-action
candidate is:

`S_partial^(nu) = int_partialB [1/2 chi_nu^{AB} partial_A Phi partial_B Phi + lambda_nu(nhat) Phi nhat.grad Phi] dA`

with schematic variational boundary condition:

`n_mu partial^mu Phi + B_nu[chi_nu, lambda_nu, Phi] = 0 on partialB`.

Status: `OPEN_LOCALIZABLE` for `chi_nu_AB`, `lambda_nu`, and
`neutral_boundary_condition`. The neutral boundary tensors and boundary
condition have been localized as required dependencies for the neutral
effective action and subsurface neutral channel. Candidate boundary-action and
variational forms are documented. Tensor values and the explicit neutral
boundary condition remain open; no numerical neutrino prediction or local FTL
claim is made.

PO-BH-53 derives the scalar/topographic boundary variation conditionally under
fixed-background boundary assumptions. The symbolic variational form is:

```text
n_mu partial^mu Phi - D_A(chi_nu^{AB}D_B Phi)
+ R_nu[lambda_nu, Phi, n.grad Phi] = 0 on partialB.
```

Status: `DERIVED_CONDITIONAL` for
`explicit_scalar_topographic_boundary_variation` and the symbolic
`neutral_boundary_condition`. The tensor values `chi_nu^{AB}` and
`lambda_nu`, the normal-coupling convention inside `R_nu`, the neutral profile
`W_nu`, and positivity/stability proof remain open. No numerical neutrino
prediction is claimed.

PO-BH-54 localizes the normal-coupling/collar convention for the neutral term
`lambda_nu Phi n.grad Phi`. A fixed-normal restricted route gives
`R_nu=lambda_nu n.grad Phi`, while collar and Robin reductions remain
open-localizable. The numerical value/function of `lambda_nu` remains open; no
numerical neutrino prediction or local FTL claim is made.

PO-BH-55 localizes the collar geometry package as the missing convention set
for the neutral normal-coupling term. The thin collar scaffold is:

`C_epsilon(partialB) = partialB x [0,epsilon]`

with coordinates `(Y^A,rho)`, measure candidate
`dV_collar = J(Y,rho) dA d rho`, orientation convention
`n=s_n partial_rho`, and inner-edge/variation data at `rho=epsilon`.

Status: `OPEN_LOCALIZABLE` for the package. The collar coordinate `rho` is
`DERIVED_CONDITIONAL` as a local collar chart, while `collar_measure`,
`normal_orientation`, `inner_collar_edge_condition`,
`admissible_collar_variation_data`, and `robin_coefficients_A_B` remain
`OPEN_LOCALIZABLE`. The collar geometry package has been localized as the
missing convention set for the neutral normal-coupling term. Collar coordinate,
measure, orientation, edge condition, and admissible variation data are now
explicit closure-map objects. Robin coefficients remain open unless a full
collar convention is derived.

PO-BH-56 audits the complete scalar/topographic collar action as the source
needed to derive the PO-BH-55 collar package. The candidate complete action is:

`S_collar = int_{partialB x [0,epsilon]} L_collar[Phi, partial_rho Phi, D_A Phi, J, lambda_nu, chi_nu] J(Y,rho) dA d rho`

The audit also records the possible collar-measure expansion:

`J(Y,rho) = 1 + rho K(Y) + O(rho^2)`

Status: `OPEN_LOCALIZABLE` for `complete_scalar_topographic_collar_action`.
The existing repo localizes boundary and subsurface scalar/topographic action
scaffolds, but it does not yet derive a complete collar Lagrangian,
extrinsic-curvature measure, normal orientation, inner-edge condition,
admissible variation data, or symbolic Robin coefficients. The complete
scalar/topographic collar action has been audited as the source needed to
derive the collar measure, orientation, edge condition, admissible variations,
and Robin coefficients. Any pieces not fixed by the existing action remain
open and cannot be fitted post-comparison.

PO-BH-57 derives the collar-measure expansion conditionally from standard
collar/extrinsic geometry. Under a smooth fixed boundary, induced metric, shape
operator `S`, and explicit normal-orientation convention, the collar Jacobian
has the symbolic form:

`J(Y,rho)=det(I + rho S(Y))`

or the sign-convention equivalent `det(I - rho S(Y))`. Therefore:

`J(Y,rho)=1 + rho K(Y) + O(rho^2)`

with `K(Y)=tr(S)(Y)` up to orientation sign. Status:
`DERIVED_CONDITIONAL` for `collar_measure_extrinsic_geometry` and
`collar_jacobian_J`. PO-BH-58 localizes the boundary embedding and
conditionally derives the induced metric, unit normal, second fundamental form,
shape operator, and trace formulas needed to evaluate the collar Jacobian.
Their numerical/function values remain open unless a BHSM scalar/topographic
boundary profile and embedding are derived. These quantities are geometric
dependencies, not fitted parameters.

with

`H_nu^(0) = [[lambda0+Delta0, etaA exp(i phiA), etaB exp(i phiB)], [etaA exp(-i phiA), lambda3+DeltaA, delta exp(i varphi)], [etaB exp(-i phiB), delta exp(-i varphi), lambda3+DeltaB]]`.

Neutral off-diagonal moment costs:

| moment | cost |
| --- | ---: |
| `M_nu(1,1)` | 2 |
| `M_nu(-2,1)` | 5 |
| `M_nu(3,0)` | 9 |

PMNS source:

`U_PMNS = U_l,L^dagger U_nu,L`

PMNS phase loop:

`Phi_nu = phiA + varphi - phiB`

Equivalently:

`Phi_nu = arg[M_nu(3,0) M_nu(-2,1) M_nu(1,1)^*]`

Mass-splitting scaffold:

`Delta m_+-^2 = 2 epsilon_nu_topo^2 sqrt(((DeltaB-DeltaA)/2)^2 + |delta|^2)`

Near-degenerate mixing scaffold:

`tan 2 theta_AB = 2 |delta|/(DeltaB-DeltaA)`

## Forbidden Fit Routes

- fit `beta0` to masses;
- fit `Delta alpha/gamma` to CKM;
- fit the CKM `1/16` exponent after comparison;
- fit `chi_nu`, `lambda_nu`, or the neutral boundary condition to neutrino masses, PMNS data, or FTL/anomaly data;
- fit `R_nu`, collar convention, or Robin coefficients to neutrino masses, PMNS data, or FTL/anomaly data;
- fit collar coordinate, measure, orientation, edge condition, variation data, or Robin coefficients to neutrino masses, PMNS data, or FTL/anomaly data;
- fit the complete scalar/topographic collar action, `L_collar`, `J(Y,rho)`, `s_n`, edge data, `A_nu`, or `B_nu` to neutrino masses, PMNS data, or FTL/anomaly data;
- fit `J(Y,rho)`, `K(Y)`, the shape operator `S`, boundary embedding, or collar-measure curvature data to neutrino masses, PMNS data, or FTL/anomaly data;
- fit `S_eff_nu` to neutrino masses or PMNS data;
- fit `g_sub`, `ellapse_nu`, or `Pi_sub_to_ext` to neutrino masses, PMNS data, or FTL/anomaly data;
- fit `S_nu_topo` to neutrino scale;
- fit the PMNS phase loop to measured CP value;
- fit scalar/topographic profile parameters to hide extra light states.

## Open Numerical Inputs

Open inputs include charged-sector metrics and prefactors, CKM mixing metrics and finite-width moments, sector-relative displacement coordinates, CKM `1/16` exponent, neutral suppression action, neutral operator parameters, scalar/topographic profile solution, scalar decoupling, stability proof, coupling bounds, and higher-loop thresholds.

The neutral topographic suppression action has been localized as the next numerical-closure object. A candidate Hessian/barrier formula is identified, but numerical neutrino closure remains open unless explicitly derived and locked.

The neutral saddle displacement `Delta y_nu` has been localized as a required input for the `S_nu_topo` Hessian/barrier formula. Candidate stationary-point and finite-width centroid definitions are documented. Numerical neutrino closure remains open.

The neutral effective action `S_eff^(nu)` has been localized as the action-level source for the neutral saddle displacement. A subsurface neutral-channel candidate is documented, but the internal metric, projection/lapse map, neutral boundary tensors, and neutral profile remain open. Numerical neutrino closure remains open.

The subsurface neutral projection geometry has been localized as a required dependency for the neutral effective action. Candidate internal metric, projection map, and exterior-lapse structures are documented. No local FTL or numerical neutrino prediction is claimed.

The neutral boundary tensors and boundary condition have been localized as required dependencies for the neutral effective action and subsurface neutral channel. Candidate boundary-action and variational forms are documented. Tensor values and the explicit neutral boundary condition remain open; no numerical neutrino prediction or local FTL claim is made.

The scalar/topographic boundary variation has been derived conditionally as a symbolic neutral boundary-condition form. The tensor values `chi_nu^{AB}` and `lambda_nu` remain open; no numerical neutrino prediction is claimed.

The collar geometry package has been localized as the missing convention set for the neutral normal-coupling term. Collar coordinate, measure, orientation, edge condition, and admissible variation data are now explicit closure-map objects. Robin coefficients remain open unless a full collar convention is derived.

The complete scalar/topographic collar action has been audited as the source needed to derive the collar measure, orientation, edge condition, admissible variations, and Robin coefficients. Any pieces not fixed by the existing action remain open and cannot be fitted post-comparison.

The collar-measure expansion has been derived conditionally from standard collar/extrinsic geometry as a symbolic formula. The boundary embedding, induced metric, unit normal, second fundamental form, shape operator, and trace formulas have been localized or derived conditionally as geometric structures needed to evaluate the collar Jacobian. Their numerical/function values remain open unless a BHSM scalar/topographic boundary profile and embedding are derived. These quantities are geometric dependencies, not fitted parameters.

PO-BH-59 localizes two scalar/topographic level-set boundary routes: a spacetime route `F_STF(x,t)=T(x,t)-T_0` and an internal Berger route `F_int(y)=Phi(y)-Phi_0`. The regular-level-set normal, second fundamental form, shape operator, trace, and collar-Jacobian formulas are conditionally derived. Their thresholds, explicit profiles, metric values, orientation, and numerical/function values remain open. `S_nu_topo` and `epsilon_nu_topo` remain open-localizable. No numerical neutrino prediction, PMNS numerical prediction, CKM numerical prediction, local FTL, experimental FTL, anomaly validation, or propulsion validation is claimed.

PO-BH-60 classifies the scalar/topographic profile inputs required after PO-BH-59. It separates the remaining bottleneck into four gates: profile existence/localization, threshold selection, metric/profile evaluation, and neutral action evaluation. Gate 1 is partially localized; Gates 2, 3, and 4 remain open-localizable. `T_0`, `Phi_0`, explicit profile functions, gradient norms, metric/profile values, orientation, `S_nu_topo`, and `epsilon_nu_topo` remain open/localizable. No numerical neutrino prediction, PMNS prediction, CKM prediction, FTL claim, anomaly validation, or propulsion validation is introduced.

PO-BH-61 audits the scalar/topographic profile equation-of-motion source routes. It finds partial EOM source structure in the existing schematic scalar bulk action and conditionally derived symbolic boundary variation, but no complete spacetime topographic EOM, internal Berger profile EOM, threshold-selection theorem, profile solution, neutral action evaluation, `S_nu_topo` value, or `epsilon_nu_topo` value. The audit is completed as a derivation-source audit; numerical closure remains open and no profile input may be fitted after comparison.

PO-BH-62 converts the symbolic boundary variation source identified in PO-BH-61 into a conditional scalar/topographic boundary-condition normal form. It records Dirichlet, Neumann, Robin/mixed, and conditional source-coupled forms for the spacetime topographic scalar `T` and internal Berger/topographic profile `Phi`. Boundary-condition coefficients, thresholds `T_0` and `Phi_0`, profile solutions, `S_nu_topo` value, and `epsilon_nu_topo` remain open-localizable. No numerical neutrino prediction, PMNS prediction, CKM prediction, FTL claim, anomaly validation, or propulsion validation is introduced.

PO-BH-63 audits existing BHSM structures for sources of scalar/topographic boundary-condition coefficients and threshold values. It confirms that the coefficient families follow conditionally from the PO-BH-62 normal forms and that scaling/equivalence and dimensional-analysis constraints can be recorded, but no coefficient values, coefficient ratios, source terms, `T_0`, `Phi_0`, profile solutions, `S_nu_topo` value, or `epsilon_nu_topo` are derived. No numerical neutrino prediction, PMNS prediction, CKM prediction, FTL claim, anomaly validation, or propulsion validation is introduced.

PO-BH-64 records a finite sector projector compression and charged Hessian fork audit. The unified `Omega(C,sigma)` projector formula and target-amplitude formula are documented as structural candidates, not fully action-derived claims. The charged Hessian cost is forked to `N_ch(q,j)=q^2+rho_ch j^2`, with old exact costs conditional on `rho_ch=1` and cyclic-anisotropy candidate costs conditional on `rho_ch=3`. The `8/9` eta route is downgraded, the eta projection/self-screening route is documented as candidate-only, and `Z_virt^{u,2}=1/2` is strengthened as a dimension-ratio candidate. No frozen or official prediction is changed.

PO-BH-65 audits existing BHSM charged-Hessian sources for the localizable anisotropy `rho_ch`. The minimal diagonal route `rho_ch=1` remains a `MINIMAL_ACTION_CLOSURE_CANDIDATE`, while the cyclic-base route `rho_ch=3` remains `STRUCTURALLY_MOTIVATED_NOT_DERIVED`. No charged action/Hessian source currently decides `rho_ch`, so `rho_ch_action_value` and `charged_Hessian_anisotropy_rho_ch` remain `OPEN_LOCALIZABLE`. Charged `qj` cross-terms are forbidden unless action-derived; neutral/topographic `qj` mixing remains open but cannot leak into the charged Hessian without an explicit charged coupling. The exact `eta_l` value remains open because it depends on the unresolved `rho_ch`. No mass, CKM, PMNS, neutrino, measured-alpha, or target-value input is used to choose `rho_ch`.

PO-BH-54 localizes the normal-coupling/collar convention for the neutral
boundary term:

```text
lambda_nu Phi n.grad Phi.
```

The fixed-normal restricted route gives:

```text
R_nu = lambda_nu n.grad Phi.
```

but the general collar/Robin convention remains open-localizable:

```text
S_collar = int_{partialB x [0,epsilon]}
lambda_nu(rho,Y) Phi partial_rho Phi d rho dA
```

and

```text
R_nu -> A_nu Phi + B_nu n.grad Phi.
```

Status: `OPEN_LOCALIZABLE` for `R_nu_normal_coupling` and
`normal_collar_convention`. The numerical value/function of `lambda_nu`
remains open. No neutrino numerical prediction or local FTL claim is made.

## Claim Boundary

This closure map does not claim full numerical Standard Model derivation, full replacement readiness, numerical mass ratios, numerical CKM prediction, numerical PMNS prediction, neutrino mass ordering, PMNS CP value, scalar/topographic decoupling proof, or higher-loop threshold completion.
