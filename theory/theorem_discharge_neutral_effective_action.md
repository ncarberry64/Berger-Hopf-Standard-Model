# PO-BH-50 - Neutral Effective Action Theorem

Status: `OPEN_LOCALIZABLE`

Current public status: structural architecture integrated conditional; numerical closure open.

## Problem

PO-BH-49 localized the neutral saddle displacement as

```text
Delta y_nu = - H_H^{-1} grad_y[delta S_eff^(nu-H)]|_{y_H}
```

with

```text
delta S_eff^(nu-H) = S_eff^(nu) - S_eff^(H).
```

This makes the neutral effective action `S_eff^(nu)` an upstream numerical-closure object. The stationary-point condition is

```text
grad_y S_eff^(nu)(y_nu) = 0.
```

The goal of this sprint is to localize `S_eff^(nu)` without fitting neutrino masses, neutrino mass splittings, PMNS angles, or the PMNS CP phase.

## Required Downstream Role

The neutral effective action supplies the action-level source for the neutral saddle displacement. The displacement then feeds the neutral topographic suppression action:

```text
S_nu_topo = 1/2 Delta y_nu^T G_nu_topo Delta y_nu + S_barrier.
```

Since `S_eff^(nu)`, `S_eff^(H)`, `H_H`, the neutral-minus-Higgs gradient, and the neutral finite-width profile are not derived, `S_nu_topo` remains not numerically closed.

## Route A - Exterior Surface vs Subsurface Neutral Channel Action

Candidate:

```text
S_eff^(nu) =
S_bulk[Phi] + S_partial^(nu)[Phi]
+ S_subsurface^(nu)[Phi; ellapse_nu, g_sub].
```

Interpretation: neutral modes are treated as a subsurface neutral topographic channel. Exterior observers live on the outside surface, while neutral excitations may project to exterior observers with anomalous path length or timing. The needed open structures are:

- internal/subsurface metric `g_sub`;
- neutral lapse/projection map `ellapse_nu`;
- relation between subsurface paths and exterior-surface coordinates;
- neutral boundary action `S_partial^(nu)`.

Status: `OPEN_LOCALIZABLE`.

## Apparent FTL / Causality Guardrail

This route permits language such as exterior-projected anomalous propagation or apparent FTL from exterior-surface viewpoint. That phrase is interpretive and projection-level only. The candidate is locally causal in the internal/topographic metric. It does not assert experimentally established faster-than-light neutrino propagation, and it does not turn an exterior projection effect into a local dynamical causality claim.

FTL-like language remains provisional until `g_sub`, `ellapse_nu`, and the subsurface-to-exterior projection map are derived from the internal/topographic action.

## Route B - Boundary Action Inherited From Scalar/Topographic Terms

Candidate:

```text
S_eff^(nu) =
S_bulk[Phi]
+ int_partialB [
  1/2 chi_nu^{AB} partial_A Phi partial_B Phi
  + lambda_nu(nhat) Phi nhat.grad Phi
] dA.
```

Open objects:

- neutral boundary tensor `chi_nu^{AB}`;
- normal coupling `lambda_nu(nhat)`;
- neutral boundary condition;
- compatibility with the scalar/topographic action.

Status: `OPEN_LOCALIZABLE`.

## Route C - Neutral Operator Source

Candidate source label:

```text
Omega_nu = -q - 2j = -k.
```

This localizes a neutral sector operator, but it is currently only a sector label unless an operator-to-action theorem is supplied. It does not by itself produce the neutral effective action.

Status: `STRUCTURALLY_MOTIVATED_NOT_DERIVED`.

## Route D - Finite-Width Neutral Profile Action

Candidate:

```text
S_eff^(nu)[W_nu] =
int_B W_nu(y) V_eff^(nu)(y) dV
+ regularization/width term.
```

This route would define `y_nu` as a saddle or centroid of the finite-width neutral profile. It still requires `W_nu`, `V_eff^(nu)`, a regularization term, and an invariant saddle/centroid prescription.

Status: `OPEN_LOCALIZABLE`.

## Verdict Table

| route | formula | dependencies | status | reason | allowed next action | forbidden shortcut |
| --- | --- | --- | --- | --- | --- | --- |
| A subsurface neutral channel | `S_bulk + S_partial^(nu) + S_subsurface^(nu)[ellapse_nu,g_sub]` | `g_sub`, `ellapse_nu`, projection map, neutral boundary action | `OPEN_LOCALIZABLE` | localizes the action source but does not derive metric/projection data | derive metric and projection from boundary/topographic action | fit apparent propagation or action parameters to neutrino data |
| B boundary scalar/topographic | `S_bulk + int_partialB[...]dA` | `chi_nu^{AB}`, `lambda_nu`, boundary condition | `OPEN_LOCALIZABLE` | boundary action form is plausible but tensors are open | derive neutral tensors and boundary condition | choose tensors from observed masses or PMNS residuals |
| C neutral operator source | `Omega_nu=-q-2j=-k` | operator-to-action map | `STRUCTURALLY_MOTIVATED_NOT_DERIVED` | sector label does not force an action | derive operator-to-action theorem | convert labels into fitted action scale |
| D finite-width profile | `int_B W_nu V_eff^(nu)dV + width term` | `W_nu`, `V_eff^(nu)`, regularization, centroid/saddle convention | `OPEN_LOCALIZABLE` | profile action is localizable but not computed | derive neutral profile and invariant saddle | choose profile width from neutrino scale |

## Claim Boundary

The neutral effective action `S_eff^(nu)` has been localized as the action-level source for the neutral saddle displacement. A subsurface neutral-channel candidate is documented, but the internal metric, projection/lapse map, neutral boundary tensors, and neutral profile remain open. Numerical neutrino closure remains open.

This sprint does not derive a neutrino mass prediction, a PMNS numerical prediction, a neutrino ordering prediction, or any locally superluminal dynamics claim.

## Next Action

Derive or reject `g_sub`, `ellapse_nu`, `chi_nu^{AB}`, `lambda_nu(nhat)`, `W_nu`, `V_eff^(nu)`, and the neutral projection map from the internal boundary/topographic action before any neutrino comparison.
