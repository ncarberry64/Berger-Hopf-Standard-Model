# PO-BH-53 - Scalar/Topographic Boundary Variation Theorem

Status: `DERIVED_CONDITIONAL`

Current public status: structural architecture integrated conditional; numerical closure open.

## Problem

PO-BH-52 localized the neutral boundary tensors and schematic neutral boundary condition:

```text
S_partial^(nu) =
int_partialB [
  1/2 chi_nu^{AB} partial_A Phi partial_B Phi
  + lambda_nu(nhat) Phi nhat.grad Phi
] dA
```

and

```text
n_mu partial^mu Phi + B_nu[chi_nu, lambda_nu, Phi] = 0 on partialB.
```

The purpose of PO-BH-53 is narrower: vary `S_bulk[Phi] + S_partial^(nu)[Phi]` and decide whether the symbolic neutral boundary operator can be conditionally derived without fitting any neutral-sector data.

## Route A - Standard Variational Boundary Route

Take the scalar bulk action:

```text
S_bulk =
int_B [
  1/2 g^{mu nu} partial_mu Phi partial_nu Phi
  - V(Phi)
] dV.
```

For fixed background geometry, variation and bulk integration by parts give:

```text
delta S_bulk =
int_B [bulk Euler-Lagrange term] delta Phi dV
+ int_partialB n_mu partial^mu Phi delta Phi dA.
```

Thus:

```text
delta S_bulk|boundary =
int_partialB n_mu partial^mu Phi delta Phi dA.
```

Adding the localized neutral boundary action gives:

```text
delta(S_bulk + S_partial^(nu))|partialB =
int_partialB [
  n_mu partial^mu Phi
  + B_nu[chi_nu, lambda_nu, Phi]
] delta Phi dA
+ possible derivative-of-deltaPhi terms.
```

Status: `DERIVED_CONDITIONAL`.

Reason: the bulk boundary term and schematic boundary contribution follow from standard variation, but exact signs and the normal-coupling reduction depend on explicit boundary conventions.

## Route B - Boundary Integration-By-Parts Route

Vary the tangential-gradient term:

```text
S_chi =
int_partialB 1/2 chi_nu^{AB} D_A Phi D_B Phi dA.
```

Assuming `chi_nu^{AB}` is symmetric or replaced by its symmetrized part, and assuming the boundary has no boundary or edge terms vanish:

```text
delta S_chi =
int_partialB chi_nu^{AB} D_A Phi D_B(delta Phi) dA
```

and boundary integration by parts gives the conditional contribution:

```text
delta S_chi =
- int_partialB D_A(chi_nu^{AB} D_B Phi) delta Phi dA.
```

Therefore the tangential tensor contributes:

```text
B_chi[Phi] = -D_A(chi_nu^{AB} D_B Phi).
```

Status: `DERIVED_CONDITIONAL`.

Reason: the divergence form follows from the localized boundary action once the boundary derivative, measure, and boundary-of-boundary convention are fixed. This does not derive the numerical or geometric value of `chi_nu^{AB}`.

## Route C - Normal Coupling Route

The localized normal-coupling term is:

```text
S_lambda =
int_partialB lambda_nu Phi n.grad Phi dA.
```

Its variation is:

```text
delta S_lambda =
int_partialB [
  lambda_nu (n.grad Phi) delta Phi
  + lambda_nu Phi n.grad(delta Phi)
] dA
```

if `lambda_nu` and the background normal are held fixed.

The second term depends on a boundary collar or normal-derivative variation convention. It may reduce to a Robin-like contribution, modify the normal derivative coefficient, or require an auxiliary boundary-of-boundary/collar condition. Therefore PO-BH-53 records the conservative placeholder:

```text
R_nu[lambda_nu, Phi, n.grad Phi].
```

Status: `OPEN_LOCALIZABLE`.

Reason: the term is localized and its first variation is written, but the exact Robin-like reduction is not derived until the normal/collar convention is fixed.

## Route D - Conservative Schematic Closure Route

Combining the bulk boundary term, the tangential-gradient variation, and the localized normal-coupling ambiguity gives:

```text
n_mu partial^mu Phi
- D_A(chi_nu^{AB} D_B Phi)
+ R_nu[lambda_nu, Phi, n.grad Phi]
= 0 on partialB.
```

Equivalently:

```text
B_nu[Phi] =
-D_A(chi_nu^{AB}D_B Phi)
+ R_nu[lambda_nu, Phi, n.grad Phi].
```

Status: `DERIVED_CONDITIONAL`.

Reason: this is the most conservative symbolic boundary operator supported by the localized scalar/topographic boundary action and stated assumptions. It is not a numerical neutrino prediction, and it does not derive tensor values.

## Assumptions

- The boundary has no boundary, or boundary-of-boundary terms vanish.
- `chi_nu^{AB}` is symmetric or replaced by its symmetrized part.
- The background boundary geometry, normal, and measure are fixed during this variation.
- `chi_nu^{AB}` and `lambda_nu` are treated as background coefficients in this sprint.
- The boundary covariant derivative `D_A` and sign convention are fixed but not globally derived from the complete internal action.
- The normal-derivative term `lambda_nu Phi n.grad Phi` requires a collar/normal-variation convention; this is stored in `R_nu`.
- Local causality is not addressed by this theorem except by the prior guardrails.

## Verdict Table

| candidate route | formula | assumptions | dependencies | status | reason | allowed next action | forbidden shortcut |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Standard variational boundary route | `delta S_bulk|boundary = int_partialB n_mu partial^mu Phi delta Phi dA`; `delta S_partial^(nu)=int_partialB B_nu delta Phi dA + possible derivative-of-deltaPhi terms` | fixed background geometry; allowed integration by parts | `S_bulk`, `S_partial^(nu)`, boundary variation convention | `DERIVED_CONDITIONAL` | Bulk boundary term and symbolic boundary contribution follow conditionally. | Derive all sign and normal/collar conventions from the complete scalar/topographic action. | Fit the boundary condition to neutrino data. |
| Boundary integration-by-parts route | `-D_A(chi_nu^{AB}D_B Phi)` | symmetric `chi_nu`; no edge terms | `chi_nu_AB`, `D_A`, boundary measure | `DERIVED_CONDITIONAL` | The divergence contribution follows after boundary integration by parts. | Derive `chi_nu_AB` and `D_A` from the neutral boundary geometry. | Fit tensor components after comparison. |
| Normal coupling route | `R_nu[lambda_nu, Phi, n.grad Phi]` | fixed normal; collar/normal-variation convention needed | `lambda_nu`, normal derivative convention | `OPEN_LOCALIZABLE` | Variation is localizable but exact Robin-like reduction is convention-dependent. | Derive the normal-coupling convention from the boundary/collar action. | Choose `lambda_nu` or its sign from residuals. |
| Conservative schematic closure route | `n_mu partial^mu Phi - D_A(chi_nu^{AB}D_B Phi) + R_nu[lambda_nu, Phi, n.grad Phi] = 0` | Routes A-C assumptions | `explicit_scalar_topographic_boundary_variation`, `chi_nu_AB`, `lambda_nu` | `DERIVED_CONDITIONAL` | A symbolic neutral boundary-condition form follows conditionally. | Derive tensor values and the `R_nu` convention before comparison. | Treat the symbolic condition as a numerical neutrino prediction. |

## Closure-Map Status

Preferred status:

```text
explicit_scalar_topographic_boundary_variation: DERIVED_CONDITIONAL
neutral_boundary_condition: DERIVED_CONDITIONAL
chi_nu_AB: OPEN_LOCALIZABLE
lambda_nu: OPEN_LOCALIZABLE
```

The upgrade is only symbolic and conditional. It localizes the variational operator but does not close numerical neutrino inputs.

## Claim Boundary

The scalar/topographic boundary variation has been derived conditionally as a symbolic variational boundary operator:

```text
n_mu partial^mu Phi
- D_A(chi_nu^{AB}D_B Phi)
+ R_nu[lambda_nu, Phi, n.grad Phi]
= 0 on partialB.
```

The tensor values `chi_nu^{AB}` and `lambda_nu`, the normal-coupling convention inside `R_nu`, the neutral profile `W_nu`, and the positivity/stability proof remain open. No numerical neutrino prediction is claimed. No claim of local causality violation is made. No claim of experimental FTL is made.

Observed neutrino masses, observed neutrino mass splittings, PMNS angles, PMNS CP phase, fitted FTL/anomaly data, and post-comparison choices of `chi_nu`, `lambda_nu`, `S_eff_nu`, `Delta_y_nu`, `S_nu_topo`, or the neutral boundary condition are forbidden inputs.

## Next Action

Derive or reject the `R_nu` normal-coupling convention, tensor values `chi_nu_AB` and `lambda_nu`, the neutral profile `W_nu`, and positivity/stability conditions from the complete scalar/topographic boundary action before comparison.
