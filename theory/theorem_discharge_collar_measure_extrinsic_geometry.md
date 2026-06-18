# PO-BH-57 - Collar Measure / Extrinsic Geometry Theorem

Status: `DERIVED_CONDITIONAL` for the standard collar Jacobian formula.

Current public status: structural architecture integrated conditional; numerical closure open.

## Problem

PO-BH-55 localized the collar geometry package and PO-BH-56 audited the
complete scalar/topographic collar action. The remaining local geometric
question is whether the collar measure can be written as

```text
dV_collar = J(Y,rho) dA d rho
```

with a curvature expansion

```text
J(Y,rho) = 1 + rho K(Y) + O(rho^2)
```

or a sign-convention equivalent. This sprint audits whether that formula is
available from standard collar/extrinsic geometry and whether BHSM already
derives the geometric input `K(Y)`.

The result is deliberately split:

- the collar Jacobian formula is conditionally derived from standard smooth
  collar geometry;
- the BHSM-specific boundary trace `K(Y)` and shape operator `S` remain open
  geometric dependencies unless a boundary embedding, induced metric, and
  scalar/topographic profile are derived elsewhere.

## Required Assumptions

- The boundary `partialB` is smooth and fixed.
- A collar neighborhood exists:

```text
C_epsilon(partialB) = partialB x [0,epsilon].
```

- Collar coordinates are `(Y^A,rho)`.
- `epsilon` is small enough that the collar chart does not self-intersect.
- The background geometry is fixed while this local formula is derived.
- A boundary induced metric `h_AB(Y)` exists.
- A normal orientation convention is tracked explicitly by `s_n in {+1,-1}`.
- `K(Y)` is a geometric trace term, not a fitted parameter.
- Observed neutrino masses, observed neutrino mass splittings, PMNS data, and
  fitted anomaly/FTL data are not used.
- No numerical neutrino prediction is claimed.
- No local FTL or experimental FTL claim is made.

## Route A - Standard Collar / Tubular-Neighborhood Jacobian

Assume a smooth boundary with induced metric `h_AB(Y)` and shape operator
`S^A_B(Y)` for the chosen normal orientation. In a small collar,

```text
dV_collar = J(Y,rho) dA d rho
```

with

```text
J(Y,0) = 1.
```

The standard local geometric candidate is

```text
J(Y,rho) = det(I + rho S(Y))
```

for one sign convention, or

```text
J(Y,rho) = det(I - rho S(Y))
```

if the opposite normal orientation or second-fundamental-form convention is
chosen. To first order,

```text
J(Y,rho) = 1 + rho tr(S)(Y) + O(rho^2)
```

or the sign-reversed equivalent. We identify

```text
K(Y) = tr(S)(Y)
```

within the chosen convention.

Status: `DERIVED_CONDITIONAL` for the standard collar formula.

Reason: this is standard smooth collar/extrinsic geometry once a boundary
embedding, induced metric, and normal convention exist. BHSM has not yet
derived the embedding or `S(Y)` from the scalar/topographic profile, so the
formula is conditional and symbolic.

## Route B - Induced-Metric Determinant Route

Use the collar metric restricted to boundary-parallel coordinates:

```text
dV_collar = sqrt(det h(Y,rho)) dY d rho
```

and

```text
dA = sqrt(det h(Y,0)) dY.
```

Then

```text
J(Y,rho) = sqrt(det h(Y,rho) / det h(Y,0)).
```

With the convention

```text
h_AB(Y,rho) = h_AB(Y,0) + 2 rho K_AB(Y) + O(rho^2)
```

one obtains

```text
J(Y,rho) = 1 + rho h^{AB}K_AB(Y) + O(rho^2).
```

Thus

```text
K(Y) = h^{AB}K_AB(Y)
```

up to the same normal-orientation sign convention.

Status: `DERIVED_CONDITIONAL` for the determinant identity and first-order
expansion; `OPEN_LOCALIZABLE` for the BHSM-specific metric data.

## Route C - Normal Divergence Route

If the unit normal `n` is derived from the boundary embedding, then the
trace curvature may be written schematically as

```text
K(Y) = div_boundary n
```

or, in an ambient notation with projection to the boundary,

```text
K(Y) = nabla_mu n^mu
```

with sign depending on the chosen normal orientation.

Status: `OPEN_LOCALIZABLE`.

Reason: the repo tracks normal orientation through `n = s_n partial_rho`, but
it does not yet derive the ambient boundary embedding, projected divergence,
or complete normal field from the BHSM scalar/topographic data.

## Route D - Topographic Level-Set Route

A scalar/topographic profile could define a boundary as a level set

```text
Phi(Y,rho) = const.
```

with candidate normalized normal

```text
n_mu = partial_mu Phi / sqrt(partial_alpha Phi partial^alpha Phi).
```

Then the same trace candidate would be

```text
K(Y) = nabla_mu n^mu.
```

Status: `OPEN_LOCALIZABLE`.

Reason: this route requires a scalar/topographic profile solution, background
metric, regular nonzero gradient, and boundary embedding. Those objects remain
open in the current BHSM chain.

## Route E - Hessian / Second-Variation Route

Existing boundary-action and topographic Hessian scaffolds suggest a possible
route in which a projected Hessian trace controls local boundary curvature:

```text
K(Y) ~ Tr_boundary(H_topo)
```

or a projected second-variation trace of the scalar/topographic action.

Status: `STRUCTURALLY_MOTIVATED_NOT_DERIVED`.

Reason: the repo contains Hessian scaffolds and second-variation diagnostics,
but not a theorem equating those candidate Hessians with the extrinsic
curvature trace entering the collar measure. This route must not be promoted
without a boundary embedding/profile proof.

## Route F - Conservative Open-Dependency Route

Until the BHSM boundary embedding and scalar/topographic profile are derived,
the safe working formula is

```text
J(Y,rho) = 1 + rho K(Y) + O(rho^2)
```

where `K(Y)` is an exposed geometric dependency.

Status: `DERIVED_CONDITIONAL` for the symbolic standard-collar expansion;
`OPEN_LOCALIZABLE` for `K(Y)` and `S(Y)`.

## Verdict Table

| candidate route | formula | assumptions | dependencies | status | reason | allowed next action | forbidden shortcut |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Standard collar Jacobian | `J(Y,rho)=det(I + rho S(Y))` or sign-equivalent | smooth collar, induced metric, shape operator, normal convention | boundary embedding, `h_AB`, `S`, orientation | `DERIVED_CONDITIONAL` | Standard collar geometry supplies the formula once geometric inputs exist. | Derive `S` and orientation from BHSM boundary/topographic geometry. | Fit `J`, `K`, or `S` to neutrino or anomaly data. |
| Induced metric determinant | `J=sqrt(det h(Y,rho)/det h(Y,0))` | collar metric exists | `h_AB(Y,rho)`, `K_AB`, sign convention | `DERIVED_CONDITIONAL` for identity; `OPEN_LOCALIZABLE` for BHSM data | Determinant relation is geometric; BHSM metric data remain open. | Derive induced metric and second fundamental form. | Choose metric coefficients after comparison. |
| Normal divergence | `K=div_boundary n` or projected `nabla_mu n^mu` | unit normal field exists | normal field, boundary projection, ambient connection | `OPEN_LOCALIZABLE` | Normal is tracked but not derived as a full field. | Derive normal from embedding/profile. | Pick normal sign or trace from residuals. |
| Topographic level set | `n_mu=partial_mu Phi/|partial Phi|`, `K=nabla_mu n^mu` | regular level set and nonzero gradient | scalar profile, background metric, boundary embedding | `OPEN_LOCALIZABLE` | Scalar/topographic profile solution remains open. | Solve or bound the profile and embedding. | Use observed neutrino data to choose profile. |
| Hessian / second variation | `K ~ Tr_boundary(H_topo)` | Hessian trace maps to extrinsic curvature | full topographic Hessian, projection theorem | `STRUCTURALLY_MOTIVATED_NOT_DERIVED` | Existing Hessian scaffolds do not prove the curvature-trace identity. | Prove Hessian-to-curvature relation from the action. | Assert a Hessian trace as `K` without proof. |
| Conservative exposed dependency | `J=1+rho K+O(rho^2)` | local collar formula only | open `K(Y)` and `S(Y)` | `DERIVED_CONDITIONAL` with open geometric inputs | Formula is localizable and conditional; evaluation data remain open. | Keep `K` exposed until derived. | Treat `K` as a fitted damping/scale parameter. |

## Closure-Map Status

Preferred status:

```text
collar_measure_extrinsic_geometry: DERIVED_CONDITIONAL
collar_jacobian_J: DERIVED_CONDITIONAL
boundary_trace_K: OPEN_LOCALIZABLE
shape_operator_S: OPEN_LOCALIZABLE
collar_measure: OPEN_LOCALIZABLE
normal_orientation: OPEN_LOCALIZABLE
```

The collar-measure expansion has been derived conditionally from standard
collar/extrinsic geometry as a symbolic formula. The boundary trace/extrinsic
curvature data needed to evaluate `K(Y)` remain open unless derived elsewhere
in BHSM. These quantities are geometric dependencies, not fitted parameters.

## Claim Boundary

This theorem derives only the standard smooth-collar Jacobian identity and its
first-order curvature expansion under explicit assumptions. It does not derive
a BHSM-specific boundary embedding, induced metric, shape operator, normal
orientation, scalar/topographic profile solution, Robin coefficients,
`lambda_nu`, neutrino masses, PMNS values, or local/experimental FTL.

K(Y) is a geometric trace term, not a fitted parameter. The scalar value of
`K(Y)` is not assigned in this sprint.

Observed neutrino masses, observed neutrino mass splittings, PMNS angles, PMNS
CP phase, fitted anomaly/FTL data, and post-comparison choices of `J(Y,rho)`,
`K(Y)`, `S(Y)`, normal orientation, `lambda_nu`, `A_nu`, `B_nu`,
`Delta_y_nu`, or `S_nu_topo` are forbidden inputs.

## Next Action

Derive or reject the boundary embedding, induced boundary metric, shape
operator, normal orientation, and scalar/topographic level-set profile. Only
after those objects are derived can `K(Y)` be evaluated inside BHSM and used in
Robin or neutral-action closure.
