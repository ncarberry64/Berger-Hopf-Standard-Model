# PO-BH-52 - Neutral Boundary Tensors and Boundary Condition Theorem

Status: `OPEN_LOCALIZABLE`

Current public status: structural architecture integrated conditional; numerical closure open.

## Problem

PO-BH-50 localized the neutral effective action:

```text
S_eff^(nu) =
S_bulk[Phi] + S_partial^(nu)[Phi]
+ S_subsurface^(nu)[Phi; ellapse_nu, g_sub].
```

The boundary-action candidate is:

```text
S_partial^(nu) =
int_partialB [
  1/2 chi_nu^{AB} partial_A Phi partial_B Phi
  + lambda_nu(nhat) Phi nhat.grad Phi
] dA.
```

This makes three neutral boundary objects shared dependencies for `S_eff_nu`, subsurface projection geometry, `Delta_y_nu`, and `S_nu_topo`:

- `chi_nu^{AB}`: neutral anisotropic boundary response tensor;
- `lambda_nu(nhat)`: neutral scalar-normal coupling;
- neutral boundary condition from variation of `S_bulk + S_partial^(nu)`.

The goal is to localize these objects without fitting them to neutrino data or propagation anomalies.

## Route A - Variational Boundary-Condition Route

Start from:

```text
S_eff^(nu) =
S_bulk[Phi] + S_partial^(nu)[Phi] + S_subsurface^(nu).
```

with:

```text
S_partial^(nu) =
int_partialB [
  1/2 chi_nu^{AB} partial_A Phi partial_B Phi
  + lambda_nu(nhat) Phi nhat.grad Phi
] dA.
```

Varying the bulk and boundary pieces should produce a neutral boundary condition of schematic form:

```text
n_mu partial^mu Phi + B_nu[chi_nu, lambda_nu, Phi] = 0 on partialB.
```

Here `B_nu` denotes the boundary operator produced by the tangential tensor `chi_nu^{AB}`, the normal coupling `lambda_nu(nhat)`, and the chosen boundary integration-by-parts convention.

Status: `OPEN_LOCALIZABLE`.

Reason: the variational structure localizes the boundary condition, but the repo does not yet derive the full scalar/topographic boundary action, the exact variation convention, or numerical tensor values.

## Route B - Sector-Operator Source Route

The neutral sector operator is:

```text
Omega_nu = -q - 2j = -k.
```

This may identify the neutral boundary sector, but `Omega_nu` is not automatically enough to derive tensor values. A separate operator-to-tensor proof would need to map the sector operator into `chi_nu^{AB}`, `lambda_nu`, or a unique neutral boundary functional.

Status: `STRUCTURALLY_MOTIVATED_NOT_DERIVED`.

Reason: the operator is a sector label and admissibility source. It is not, by itself, a boundary-tensor derivation.

## Route C - Subsurface-Channel Inheritance Route

Using the PO-BH-51 projection geometry:

```text
g_sub, ellapse_nu, Pi_sub_to_ext
```

one can interpret neutral boundary tensors as pullbacks or restrictions of the subsurface channel geometry. Candidate forms:

```text
chi_nu^{AB} ~ f_nu(y) g_sub^{AB}
```

or

```text
chi_nu^{AB} =
chi_parallel P_parallel^{AB} + chi_perp P_perp^{AB}.
```

Status: `OPEN_LOCALIZABLE`.

Reason: this route is structurally compatible with the subsurface neutral topographic channel, but `g_sub`, `ellapse_nu`, `Pi_sub_to_ext`, the projection projectors, and the pullback/restriction rule remain open-localizable.

## Route D - Finite-Width Profile Route

The neutral finite-width profile route relates the tensors and boundary condition to the neutral profile `W_nu` and saddle equation:

```text
grad_Y S_eff^(nu)(Y_nu) = 0.
```

The tensors `chi_nu^{AB}` and `lambda_nu` can be localized as missing inputs needed to define the boundary part of `W_nu` and therefore the neutral saddle.

Status: `OPEN_LOCALIZABLE`.

Reason: the route connects boundary tensors to `W_nu`, but `W_nu`, `V_eff^(nu)`, profile regularization, and the finite-width neutral action remain open.

## Causality / FTL Guardrail

Neutral boundary tensors may define access to a subsurface topographic channel. exterior-projected anomalous propagation remains interpretive and conditional. No claim of local causality violation is made. No claim of experimental FTL is made.

The tensor and boundary-condition candidates do not turn apparent exterior-surface behavior into a local internal/topographic causality violation.

## Verdict Table

| candidate route | formula | dependencies | status | reason | allowed next action | forbidden shortcut |
| --- | --- | --- | --- | --- | --- | --- |
| Variational boundary condition | `S_partial^(nu)=int_partialB [1/2 chi_nu^{AB} partial_A Phi partial_B Phi + lambda_nu(nhat) Phi nhat.grad Phi] dA`; `n_mu partial^mu Phi + B_nu[chi_nu,lambda_nu,Phi]=0 on partialB` | `S_bulk`, `S_partial^(nu)`, variation convention, `chi_nu_AB`, `lambda_nu`, integration-by-parts rule | `OPEN_LOCALIZABLE` | The variational form is localized, but the explicit action and variation convention are not fully derived. | Derive the boundary variation and tensor values from the scalar/topographic action. | Choose tensors or a boundary condition from neutrino masses or PMNS residuals. |
| Sector-operator source | `Omega_nu=-q-2j=-k` | `Omega_nu`, operator-to-tensor theorem, neutral boundary functional | `STRUCTURALLY_MOTIVATED_NOT_DERIVED` | `Omega_nu` labels the sector but does not automatically derive tensor values. | Derive or reject an operator-to-tensor theorem. | Treat the sector label as a fitted tensor value or complete boundary condition. |
| Subsurface-channel inheritance | `chi_nu^{AB} ~ f_nu(y) g_sub^{AB}` or `chi_parallel P_parallel^{AB}+chi_perp P_perp^{AB}` | `g_sub`, `ellapse_nu`, `Pi_sub_to_ext`, projection projectors, pullback/restriction rule | `OPEN_LOCALIZABLE` | Compatible with PO-BH-51, but the projection geometry remains open-localizable. | Derive the pullback/restriction rule from the subsurface projection geometry. | Choose anisotropic tensor components to tune the neutral sector. |
| Finite-width profile | `grad_Y S_eff^(nu)(Y_nu)=0` with tensors supplying profile inputs for `W_nu` | `W_nu`, `V_eff^(nu)`, profile regularization, neutral saddle equation, boundary tensors | `OPEN_LOCALIZABLE` | Connects tensors to the neutral profile but does not derive the profile. | Derive `W_nu` and profile regularization from the boundary condition and topographic action. | Fit profile width or tensor values to the neutrino scale. |

## Closure-Map Status

Preferred status:

```text
chi_nu_AB: OPEN_LOCALIZABLE
lambda_nu: OPEN_LOCALIZABLE
neutral_boundary_condition: OPEN_LOCALIZABLE
```

Missing dependencies:

- explicit scalar/topographic boundary action;
- variation convention;
- internal/subsurface metric;
- neutral profile `W_nu`;
- explicit neutral boundary condition derivation;
- positivity/stability proof.

## Claim Boundary

The neutral boundary tensors and boundary condition have been localized as required dependencies for the neutral effective action and subsurface neutral channel. Candidate boundary-action and variational forms are documented. Tensor values and the explicit neutral boundary condition remain open; no numerical neutrino prediction or local FTL claim is made.

Observed neutrino masses, observed neutrino mass splittings, PMNS angles, PMNS CP phase, fitted FTL/anomaly data, and post-comparison choices of `chi_nu`, `lambda_nu`, or the neutral boundary condition are forbidden inputs.

## Next Action

Derive or reject `chi_nu_AB`, `lambda_nu`, and the neutral boundary condition from the explicit scalar/topographic boundary action, variation convention, subsurface metric/projection geometry, neutral profile `W_nu`, and positivity/stability proof before comparison.
