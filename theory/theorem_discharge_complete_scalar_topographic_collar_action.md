# PO-BH-56 - Complete Scalar/Topographic Collar Action Theorem

Status: `OPEN_LOCALIZABLE`

Current public status: structural architecture integrated conditional; numerical closure open.

## Problem

PO-BH-55 localized the collar geometry package needed by the neutral normal-coupling term:

```text
lambda_nu Phi n.grad Phi.
```

The remaining question is whether the complete scalar/topographic boundary action already determines:

- the collar measure `J(Y,rho)`;
- the normal orientation sign `s_n`;
- the inner-edge condition at `rho=epsilon`;
- admissible collar variation data;
- symbolic Robin coefficients `A_nu`, `B_nu`;
- and therefore the full form of `R_nu[lambda_nu, Phi, n.grad Phi]`.

This theorem-discharge audit finds that the repo contains localized scalar/topographic boundary-action scaffolds, but not a complete collar action that fixes these data.

## Route A - Existing Scalar/Topographic Action Extraction

The candidate complete collar action would have the schematic form:

```text
S_collar =
int_{partialB x [0,epsilon]}
L_collar[Phi, partial_rho Phi, D_A Phi, J, lambda_nu, chi_nu]
J(Y,rho) dA d rho.
```

The existing repo supports:

```text
S_bulk[Phi]
S_partial^(nu)[Phi]
S_subsurface^(nu)[Phi; ellapse_nu, g_sub]
```

and the localized boundary term:

```text
S_partial^(nu) =
int_partialB [
1/2 chi_nu^{AB} partial_A Phi partial_B Phi
+ lambda_nu(nhat) Phi nhat.grad Phi
] dA.
```

Status: `OPEN_LOCALIZABLE`.

Reason: the action scaffolds identify the ingredients, but the repo does not yet define a full `L_collar` on `partialB x [0,epsilon]` that fixes the measure, orientation, edge condition, variation data, or Robin coefficients.

## Route B - Measure Derivation Route

PO-BH-55 writes:

```text
dV_collar = J(Y,rho) dA d rho
```

with:

```text
J(Y,0)=1.
```

A possible geometric expansion would be:

```text
J(Y,rho) = 1 + rho K(Y) + O(rho^2)
```

where `K(Y)` is an extrinsic-curvature or boundary-trace term.

Status: `OPEN_LOCALIZABLE`.

Reason: this expansion is a plausible collar-geometry route, but the repo does not yet derive the required extrinsic curvature, boundary trace, or boundary metric data from BHSM scalar/topographic geometry. Therefore `J(Y,rho)` remains open.

## Route C - Orientation Derivation Route

The collar sign is tracked by:

```text
n = s_n partial_rho
```

with:

```text
s_n in {+1,-1}.
```

Equivalently, the normal coupling carries:

```text
lambda_nu Phi n.grad Phi = s_n lambda_nu Phi partial_rho Phi.
```

Status: `OPEN_LOCALIZABLE`.

Reason: existing boundary and subsurface-channel documents preserve the sign dependence but do not fix whether `rho` points inward/subsurface or outward/exterior. The sign cannot be chosen from residuals.

## Route D - Inner-Edge Condition Route

The collar has an inner edge:

```text
rho=epsilon.
```

Candidate edge conditions include:

- matching to the subsurface neutral channel;
- decay/localization;
- Neumann data such as `partial_rho Phi|epsilon=0`;
- Dirichlet data such as `delta Phi|epsilon=0`;
- transparent/matching boundary data.

Status: `OPEN_LOCALIZABLE`.

Reason: existing docs list structurally reasonable options, but the repo does not derive which one follows from the complete scalar/topographic action, neutral profile `W_nu`, or subsurface metric data.

## Route E - Admissible Variation Data

The collar variation must specify whether the following are fixed or free:

```text
delta Phi at rho=0
delta partial_rho Phi at rho=0
delta Phi at rho=epsilon
delta partial_rho Phi at rho=epsilon
```

PO-BH-53 leaves `delta Phi` free at the exterior boundary for the symbolic boundary condition. PO-BH-54 records fixed-normal derivative data only as a restricted convention. PO-BH-56 therefore keeps the admissible collar variation data explicit.

Status: `OPEN_LOCALIZABLE`.

Reason: the existing action does not determine the fixed/free variation class at both collar edges.

## Route F - Robin Coefficient Derivation Route

If a full collar action and admissible variation convention were derived, the normal-coupling term could reduce to:

```text
R_nu -> A_nu Phi + B_nu n.grad Phi
```

with symbolic dependencies:

```text
A_nu = A_nu[lambda_nu, J, epsilon, edge condition, orientation]
B_nu = B_nu[lambda_nu, J, epsilon, edge condition, orientation]
```

Status: `OPEN_LOCALIZABLE`.

Reason: the dependencies are localized, but `A_nu` and `B_nu` cannot be extracted without the complete collar action, the measure, the sign convention, the inner-edge condition, and admissible variation data. No numerical values for `lambda_nu`, `A_nu`, or `B_nu` are claimed.

## Assumptions

- Background collar geometry is fixed unless derived otherwise.
- `J(Y,rho)` is unknown and remains open.
- Normal orientation is tracked by `s_n` and remains open.
- The inner-edge condition at `rho=epsilon` remains open.
- `lambda_nu` is treated as a background coefficient.
- Variations may be free or fixed at each collar boundary only after an admissible convention is derived.
- Observed neutrino masses, observed neutrino mass splittings, PMNS angles, PMNS CP phase, and fitted anomaly/FTL data are forbidden inputs.
- No numerical neutrino prediction is claimed.
- No claim of local causality violation is made.
- No claim of experimental FTL is made.

## Verdict Table

| candidate route | formula | assumptions | dependencies | status | reason | allowed next action | forbidden shortcut |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Existing action extraction | `S_collar=int_{partialB x [0,epsilon]} L_collar[...] J(Y,rho)dA d rho` | existing scalar/topographic action can be extended to a collar | `S_bulk`, `S_partial^(nu)`, `S_subsurface^(nu)`, collar package | `OPEN_LOCALIZABLE` | Existing scaffolds identify terms, but not a complete collar Lagrangian. | Derive `L_collar` from the complete scalar/topographic boundary action. | Write `L_collar` after comparison. |
| Measure derivation | `J(Y,rho)=1+rho K(Y)+O(rho^2)` | boundary extrinsic curvature or trace exists | boundary metric, extrinsic geometry, collar coordinate | `OPEN_LOCALIZABLE` | `K(Y)` is not derived in the repo. | Derive the collar Jacobian from boundary/subsurface geometry. | Fit `J` or `K`. |
| Orientation derivation | `n=s_n partial_rho`, `s_n in {+1,-1}` | inward/outward convention exists | boundary orientation, subsurface channel, exterior convention | `OPEN_LOCALIZABLE` | The sign is tracked but not fixed. | Derive sign from internal/subsurface orientation. | Choose sign from residuals. |
| Inner-edge condition | matching, decay/localization, Neumann, Dirichlet, or transparent data at `rho=epsilon` | finite collar has an admissible inner boundary | `W_nu`, `g_sub`, subsurface matching theorem | `OPEN_LOCALIZABLE` | Edge options are listed but not selected. | Derive edge condition from neutral profile/subsurface action. | Select an edge condition post-comparison. |
| Admissible variations | fixed/free `delta Phi` and `delta partial_rho Phi` at `rho=0,epsilon` | variation convention is supplied by action | PO-BH-53, PO-BH-54, inner-edge condition | `OPEN_LOCALIZABLE` | Existing action does not fix all boundary variation data. | Derive the fixed/free variation class. | Fix variation data to hide terms. |
| Robin extraction | `A_nu[lambda_nu,J,epsilon,edge,orientation]`, `B_nu[lambda_nu,J,epsilon,edge,orientation]` | full collar package is derived | `lambda_nu`, `J`, `s_n`, edge condition, variation data | `OPEN_LOCALIZABLE` | Dependencies are known, coefficients are not extracted. | Derive symbolic Robin coefficients after fixing collar data. | Fit `A_nu` or `B_nu`. |

## Closure-Map Status

Preferred status:

```text
complete_scalar_topographic_collar_action: OPEN_LOCALIZABLE
collar_measure: OPEN_LOCALIZABLE
normal_orientation: OPEN_LOCALIZABLE
inner_collar_edge_condition: OPEN_LOCALIZABLE
admissible_collar_variation_data: OPEN_LOCALIZABLE
robin_coefficients_A_B: OPEN_LOCALIZABLE
R_nu_normal_coupling: OPEN_LOCALIZABLE
```

The complete scalar/topographic collar action has been audited as the source needed to derive the collar measure, orientation, edge condition, admissible variations, and Robin coefficients. Any pieces not fixed by the existing action remain open and cannot be fitted post-comparison.

## Claim Boundary

This theorem audits the existing scalar/topographic boundary-action scaffolds as the possible source for the PO-BH-55 collar geometry package. It does not derive `J(Y,rho)`, `s_n`, the inner-edge condition, admissible variation data, `A_nu`, `B_nu`, `lambda_nu`, neutrino masses, or PMNS values.

No numerical neutrino prediction is claimed. No claim of local causality violation is made. No claim of experimental FTL is made.

Observed neutrino masses, observed neutrino mass splittings, PMNS angles, PMNS CP phase, fitted FTL/anomaly data, and post-comparison choices of `L_collar`, `J(Y,rho)`, `s_n`, edge data, variation data, `A_nu`, `B_nu`, `lambda_nu`, `S_eff_nu`, `Delta_y_nu`, `S_nu_topo`, or `epsilon_nu_topo` are forbidden inputs.

## Next Action

Derive or reject the complete collar Lagrangian, collar Jacobian, orientation sign, inner-edge condition, admissible variation data, and symbolic Robin coefficients from the full scalar/topographic boundary action before comparison.
