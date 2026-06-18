# PO-BH-58 - Boundary Embedding / Induced Metric / Shape Operator Theorem

Status: `DERIVED_CONDITIONAL` for the standard differential-geometry formulas.

Current public status: structural architecture integrated conditional; numerical closure open.

## Problem

PO-BH-57 conditionally derived the collar-measure formula

```text
J(Y,rho)=det(I + rho S(Y))
```

or its sign-equivalent convention, with first-order expansion

```text
J(Y,rho)=1 + rho K(Y) + O(rho^2).
```

The remaining question is whether BHSM supplies the geometric objects needed
to evaluate `S(Y)` and `K(Y)`. This sprint localizes the boundary embedding,
induced metric, unit normal, second fundamental form, shape operator, and
trace formulas. The formulas are standard and conditionally derived; their
BHSM-specific function values remain open unless a scalar/topographic boundary
profile and embedding are derived.

## Required Assumptions

- `partialB` is a smooth boundary.
- A boundary embedding exists:

```text
X: partialB -> B.
```

- The embedding is represented in local coordinates by `X^mu(Y^A)`.
- The induced metric is nondegenerate.
- A fixed background metric `g_mu_nu` and compatible connection `nabla` exist.
- A unit normal exists and its sign/orientation convention is explicit.
- If a scalar/topographic level-set route is used, the gradient is nonzero on
  the boundary.
- No observed neutrino masses, neutrino mass splittings, PMNS values, or
  fitted anomaly/FTL data are used.
- No numerical neutrino prediction is claimed.
- No local FTL or experimental FTL claim is made.

## Route A - Embedding Pullback Route

Let

```text
X^mu(Y^A)
```

be a boundary embedding and define tangent vectors

```text
e_A^mu = partial_A X^mu.
```

The induced boundary metric is the pullback

```text
h_AB = g_mu_nu e_A^mu e_B^nu.
```

Status: `DERIVED_CONDITIONAL` for the pullback formula.

Reason: once `X` and `g_mu_nu` are supplied, the induced metric follows by
standard differential geometry. The BHSM-specific embedding `X` and background
metric data remain open-localizable.

## Route B - Unit-Normal Route

The unit normal is constrained by

```text
n_mu e_A^mu = 0
```

and

```text
g^{mu nu} n_mu n_nu = 1
```

or the sign-equivalent normalization for a different metric signature or
orientation convention.

Status: `DERIVED_CONDITIONAL` for the algebraic conditions; `OPEN_LOCALIZABLE`
for the BHSM-specific normal field and orientation sign.

Reason: orthogonality and normalization define the normal once the embedding,
metric, and orientation are supplied. The repo does not yet derive those data
from the scalar/topographic profile.

## Route C - Second Fundamental Form Route

With tangent vectors and normal in place, define

```text
K_AB = e_A^mu e_B^nu nabla_mu n_nu.
```

The shape operator is

```text
S^A_B = h^{AC} K_CB.
```

The trace is

```text
K = tr(S) = h^{AB} K_AB.
```

All three equations may acquire an overall sign depending on whether the
normal orientation or second-fundamental-form convention is reversed.

Status: `DERIVED_CONDITIONAL` for the standard formulas; function values remain
open until `X`, `g_mu_nu`, `n`, and the scalar/topographic profile are derived.

## Route D - Level-Set / Topographic Boundary Route

If the boundary is a level set

```text
F(x)=0
```

or

```text
Phi(x)=Phi_0,
```

then a candidate normal is

```text
n_mu = partial_mu F / sqrt(g^{alpha beta} partial_alpha F partial_beta F)
```

or, for a scalar/topographic profile,

```text
n_mu = partial_mu Phi / |grad Phi|.
```

The trace can then be written as

```text
K = nabla_mu n^mu
```

up to sign and projection conventions.

Status: `OPEN_LOCALIZABLE`.

Reason: this route is the most BHSM-specific route, but it requires the
scalar/topographic profile, regular nonzero gradient, background metric, and
level-set embedding. Those objects are not yet derived.

## Route E - Hessian / Projected Curvature Route

For a regular scalar level set, a projected Hessian can contribute to the
second fundamental form:

```text
K_AB ~ P_A^mu P_B^nu nabla_mu nabla_nu Phi / |grad Phi|
```

where the exact sign and projection depend on the normal and metric
conventions.

Status: `STRUCTURALLY_MOTIVATED_NOT_DERIVED`.

Reason: the repo has topographic Hessian scaffolds and second-variation
diagnostics, but does not prove that those candidate Hessians equal the
extrinsic curvature tensor of the collar boundary.

## Route F - Collar-Measure Consistency Route

The formulas above supply the geometric objects needed by PO-BH-57:

```text
J(Y,rho)=det(I + rho S(Y))
```

and

```text
K=tr(S).
```

Therefore

```text
J(Y,rho)=1 + rho K(Y) + O(rho^2)
```

with sign determined by the normal convention.

Status: `DERIVED_CONDITIONAL` for the consistency chain; numerical/function
values remain open.

## Verdict Table

| candidate route | formula | assumptions | dependencies | status | reason | allowed next action | forbidden shortcut |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Embedding pullback | `e_A^mu=partial_A X^mu`, `h_AB=g_mu_nu e_A^mu e_B^nu` | smooth embedding and fixed background metric | `boundary_embedding_X`, `g_mu_nu` | `DERIVED_CONDITIONAL` for formula; `X` open | Pullback metric is standard geometry once `X` is supplied. | Derive `X` from BHSM boundary/topographic profile. | Choose embedding from neutrino residuals. |
| Unit normal | `n_mu e_A^mu=0`, `g^{mu nu}n_mu n_nu=1` | nondegenerate metric, orientable boundary | `X`, `h_AB`, `g_mu_nu`, orientation sign | `DERIVED_CONDITIONAL` for conditions | Normal is fixed by geometry plus sign when inputs exist. | Derive the normal and orientation from profile/embedding. | Pick normal sign from anomaly/FTL data. |
| Second fundamental form | `K_AB=e_A^mu e_B^nu nabla_mu n_nu` | compatible connection and unit normal | `e_A`, `n`, `nabla`, `g_mu_nu` | `DERIVED_CONDITIONAL` for formula | Standard extrinsic curvature definition. | Derive its function value from BHSM geometry. | Fit `K_AB` to make `J` work. |
| Shape operator and trace | `S^A_B=h^{AC}K_CB`, `K=tr(S)=h^{AB}K_AB` | invertible induced metric | `h_AB`, `K_AB` | `DERIVED_CONDITIONAL` for formula | Algebraic consequence of `h_AB` and `K_AB`. | Evaluate after deriving `h_AB` and `K_AB`. | Fit `S` or `K`. |
| Topographic level set | `n_mu=partial_mu Phi/|grad Phi|`, `K=nabla_mu n^mu` | regular level set, nonzero gradient | scalar/topographic profile, metric, embedding | `OPEN_LOCALIZABLE` | Profile and embedding remain open. | Solve or bound scalar/topographic boundary profile. | Tune profile to neutrino or FTL data. |
| Hessian / projected curvature | `K_AB ~ P_A^mu P_B^nu nabla_mu nabla_nu Phi/|grad Phi|` | level-set theorem and projection convention | full Hessian, profile, projection theorem | `STRUCTURALLY_MOTIVATED_NOT_DERIVED` | Existing Hessian diagnostics do not prove the curvature identity. | Derive Hessian-to-curvature theorem. | Assert Hessian trace as curvature without proof. |
| Collar-measure consistency | `J=det(I+rho S)`, `J=1+rho K+O(rho^2)` | PO-BH-57 collar formula and shape operator | `S`, `K`, orientation sign | `DERIVED_CONDITIONAL` with open values | Links PO-BH-58 objects to PO-BH-57. | Derive values from BHSM geometry. | Fit collar Jacobian or trace. |

## Closure-Map Status

Preferred status:

```text
boundary_embedding_X: OPEN_LOCALIZABLE
induced_boundary_metric_h_AB: DERIVED_CONDITIONAL
unit_normal_n: DERIVED_CONDITIONAL
second_fundamental_form_K_AB: DERIVED_CONDITIONAL
shape_operator_S: DERIVED_CONDITIONAL
boundary_trace_K: DERIVED_CONDITIONAL
collar_jacobian_J: DERIVED_CONDITIONAL
```

The boundary embedding, induced metric, unit normal, second fundamental form,
shape operator, and trace formulas have been localized or derived
conditionally as geometric structures needed to evaluate the collar Jacobian.
Their numerical/function values remain open unless a BHSM scalar/topographic
boundary profile and embedding are derived.

## Claim Boundary

This theorem derives standard geometric formulas only under explicit
assumptions. It does not derive the BHSM boundary embedding, background metric,
scalar/topographic profile, normal orientation sign, numerical/function values
of `K`, `S`, or `J`, Robin coefficients, `lambda_nu`, neutrino masses, PMNS
values, local FTL, or experimental FTL.

Observed neutrino masses, observed neutrino mass splittings, PMNS angles, PMNS
CP phase, fitted anomaly/FTL data, and post-comparison choices of `X`, `h_AB`,
`n`, `K_AB`, `S`, `K`, `J`, `lambda_nu`, `A_nu`, or `B_nu` are forbidden
inputs.

## Next Action

Derive or reject the scalar/topographic level-set profile and boundary
embedding `X`. That is the next required step before the geometric formulas
can evaluate `K(Y)` inside BHSM rather than merely localizing it.
