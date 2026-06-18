# PO-BH-55 - Collar Geometry Package Theorem

Status: `OPEN_LOCALIZABLE`

Current public status: structural architecture integrated conditional; numerical closure open.

## Problem

PO-BH-53 conditionally derived the symbolic neutral boundary condition:

```text
n_mu partial^mu Phi
- D_A(chi_nu^{AB}D_B Phi)
+ R_nu[lambda_nu, Phi, n.grad Phi]
= 0 on partialB.
```

PO-BH-54 localized the normal-coupling ambiguity in:

```text
lambda_nu Phi n.grad Phi.
```

PO-BH-55 localizes the missing collar geometry package needed to decide whether the normal term remains a fixed-normal remainder or reduces to a Robin-type boundary contribution:

```text
R_nu -> A_nu Phi + B_nu n.grad Phi.
```

This sprint does not derive numerical neutrino data, `lambda_nu`, or numerical Robin coefficients.

## Route A - Thin Collar Coordinate

Introduce a local collar neighborhood:

```text
C_epsilon(partialB) = partialB x [0,epsilon]
```

with collar coordinates:

```text
(Y^A, rho).
```

In this coordinate chart the normal derivative is represented as:

```text
n.grad Phi = partial_rho Phi
```

up to the orientation sign fixed in Route B.

Status: `DERIVED_CONDITIONAL` for the local collar coordinate `rho`.

Reason: a thin local collar chart is a standard fixed-boundary geometric scaffold. The BHSM finite-width collar interpretation and its coupling to the scalar/topographic action remain conditional.

## Route B - Collar Measure

The collar measure is written:

```text
dV_collar = J(Y,rho) dA d rho
```

with normalized boundary condition:

```text
J(Y,0)=1.
```

Status: `OPEN_LOCALIZABLE`.

Reason: the local measure form can be written once a collar chart exists, but the Jacobian `J(Y,rho)` is not derived from the Berger-Hopf scalar/topographic boundary geometry. It must remain symbolic unless derived from the boundary/subsurface metric.

## Route C - Orientation Convention

The collar coordinate can point inward/subsurface or outward/exterior. Track this by:

```text
n = s_n partial_rho
```

with:

```text
s_n in {+1,-1}.
```

Then:

```text
lambda_nu Phi n.grad Phi = s_n lambda_nu Phi partial_rho Phi.
```

Status: `OPEN_LOCALIZABLE`.

Reason: the sign effect on the normal-coupling term is explicit, but BHSM has not yet derived the inward/outward orientation convention from the subsurface/internal geometry.

## Route D - Inner Edge at rho=epsilon

The collar has an inner edge at:

```text
rho=epsilon.
```

Candidate edge conditions include:

- Dirichlet data such as `delta Phi|epsilon=0`;
- Neumann data such as `partial_rho Phi|epsilon=0`;
- subsurface matching to the neutral topographic channel;
- decay/localization of the collar profile.

Status: `OPEN_LOCALIZABLE`.

Reason: these are admissible mathematical possibilities, but no existing theorem in the repo selects the BHSM inner-edge condition from the complete scalar/topographic boundary action.

## Route E - Admissible Collar Variation Data

The variation of the collar term must state what is fixed or free at the outer and inner edges:

```text
delta Phi at rho=0
delta partial_rho Phi at rho=0
delta Phi at rho=epsilon
delta partial_rho Phi at rho=epsilon
```

PO-BH-53 leaves `delta Phi` free on the exterior boundary for the symbolic neutral boundary condition. PO-BH-54 keeps the fixed-normal-derivative route as a restricted convention only. PO-BH-55 therefore records the collar variation data as an explicit closure-map object rather than silently choosing it.

Status: `OPEN_LOCALIZABLE`.

Reason: the variation data can be classified consistently with PO-BH-53 and PO-BH-54, but the BHSM-admissible choice is not yet derived from the complete boundary action.

## Route F - Robin Coefficient Extraction

If the collar coordinate, measure, orientation, inner-edge condition, and admissible variation data are derived, the normal-coupling term may reduce symbolically to:

```text
R_nu -> A_nu Phi + B_nu n.grad Phi
```

with:

```text
A_nu,B_nu = F(lambda_nu, epsilon, J, s_n, edge data).
```

Status: `OPEN_LOCALIZABLE`.

Reason: the symbolic dependency list is now localized, but `A_nu` and `B_nu` cannot be extracted until the collar package is fixed. No numerical values are derived.

## Verdict Table

| object | formula candidate | status | reason | forbidden shortcut |
| --- | --- | --- | --- | --- |
| `collar_coordinate_rho` | `C_epsilon(partialB)=partialB x [0,epsilon]`, `(Y^A,rho)` | `DERIVED_CONDITIONAL` | Local collar chart is available under fixed-boundary assumptions. | Choose a collar width from neutrino data. |
| `collar_measure` | `dV_collar=J(Y,rho)dA d rho`, `J(Y,0)=1` | `OPEN_LOCALIZABLE` | The measure form is localized, but `J` is not derived from BHSM geometry. | Fit the Jacobian or measure to residuals. |
| `normal_orientation` | `n=s_n partial_rho`, `s_n in {+1,-1}` | `OPEN_LOCALIZABLE` | The sign is tracked, not derived. | Pick the sign from neutrino or anomaly data. |
| `inner_collar_edge_condition` | Dirichlet, Neumann, subsurface matching, or decay/localization at `rho=epsilon` | `OPEN_LOCALIZABLE` | Edge options are explicit, but none is selected. | Select an edge condition after comparison. |
| `admissible_collar_variation_data` | fixed/free `delta Phi` and `delta partial_rho Phi` at `rho=0,epsilon` | `OPEN_LOCALIZABLE` | Variation choices are listed but not derived. | Fix variation data to erase unwanted terms. |
| `robin_coefficients_A_B` | `A_nu,B_nu = F(lambda_nu, epsilon, J, s_n, edge data)` | `OPEN_LOCALIZABLE` | Coefficients require the full collar package. | Fit Robin coefficients to neutrino, PMNS, or anomaly data. |

## Closure-Map Status

Preferred status:

```text
collar_coordinate_rho: DERIVED_CONDITIONAL
collar_measure: OPEN_LOCALIZABLE
normal_orientation: OPEN_LOCALIZABLE
inner_collar_edge_condition: OPEN_LOCALIZABLE
admissible_collar_variation_data: OPEN_LOCALIZABLE
robin_coefficients_A_B: OPEN_LOCALIZABLE
R_nu_normal_coupling: OPEN_LOCALIZABLE
normal_collar_convention: OPEN_LOCALIZABLE
lambda_nu: OPEN_LOCALIZABLE
```

The collar geometry package has been localized as the missing convention set for the neutral normal-coupling term. Collar coordinate, measure, orientation, edge condition, and admissible variation data are now explicit closure-map objects. Robin coefficients remain open unless a full collar convention is derived.

## Claim Boundary

This theorem localizes the collar package required for the neutral normal-coupling term. It does not derive collar measure, orientation, inner-edge condition, admissible variation data, Robin coefficients, `lambda_nu`, neutral masses, or PMNS values.

No numerical neutrino prediction is claimed. No claim of local causality violation is made. No claim of experimental FTL is made.

Observed neutrino masses, observed neutrino mass splittings, PMNS angles, PMNS CP phase, fitted FTL/anomaly data, and post-comparison choices of collar coordinate, measure, orientation, edge condition, variation data, Robin coefficients, `lambda_nu`, `S_eff_nu`, `Delta_y_nu`, `S_nu_topo`, or `epsilon_nu_topo` are forbidden inputs.

## Next Action

Derive or reject the collar measure, normal orientation, inner-edge condition, admissible variation data, and Robin coefficients from the complete scalar/topographic boundary action before comparison.
