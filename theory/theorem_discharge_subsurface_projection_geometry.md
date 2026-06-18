# PO-BH-51 - Subsurface Neutral Projection Geometry Theorem

Status: `OPEN_LOCALIZABLE`

Current public status: structural architecture integrated conditional; numerical closure open.

## Problem

PO-BH-50 localized the neutral effective action as

```text
S_eff^(nu) =
S_bulk[Phi] + S_partial^(nu)[Phi]
+ S_subsurface^(nu)[Phi; ellapse_nu, g_sub].
```

This makes three projection-geometry objects explicit upstream dependencies:

- `g_sub`: an internal/subsurface effective metric or topographic metric;
- `ellapse_nu`: an exterior-projection/lapse factor for neutral modes;
- `Pi_sub_to_ext`: a projection map from subsurface neutral-channel coordinates to exterior surface observer coordinates.

The purpose of this sprint is to localize these objects mathematically without fitting them to data, without predicting neutrino masses, and without claiming local faster-than-light dynamics.

## Interpretation Boundary

Neutral modes, including neutrinos and possible ghost-like neutral modes, may be represented as coupling to a subsurface neutral topographic channel beneath the exterior spacetime surface. Exterior observers live on the outside surface. Apparent anomalous or superluminal behavior is exterior-projected apparent behavior and does not imply local causality violation in the internal/topographic metric. The candidate is locally causal in the internal/topographic metric.

BHSM does not claim local causality violation. Any FTL-like behavior is exterior-projected apparent behavior arising from a subsurface/internal topographic channel and remains conditional until `g_sub`, `ellapse_nu`, and `Pi_sub_to_ext` are derived.

## Route A - Metric Splitting Route

Define an exterior-surface metric and a subsurface neutral metric:

```text
ds_ext^2 = g_ext,ab dx^a dx^b
ds_sub^2 = g_sub,AB dY^A dY^B.
```

Define the subsurface-to-exterior projection map:

```text
x^a = Pi_sub_to_ext^a(Y).
```

The induced exterior-projected interval is:

```text
ds_proj^2 = g_ext,ab dPi^a dPi^b.
```

Candidate lapse/projection factor:

```text
ellapse_nu^2 = ds_proj^2 / ds_sub^2.
```

Status: `OPEN_LOCALIZABLE`.

Reason: this gives a concrete metric/projection/lapse scaffold, but the repo does not yet derive `g_sub`, `Pi_sub_to_ext`, or the positive scalar ratio from the full scalar/topographic boundary action.

## Route B - Topographic Lapse Route

Define `ellapse_nu(y)` as a scalar/topographic projection factor:

```text
0 < ellapse_nu(y) <= 1.
```

Candidate core/subsurface limiting behavior:

```text
ellapse_nu(y) -> 0
```

near a zero-exterior-spacetime core.

Status: `OPEN_LOCALIZABLE`.

Reason: this is compatible with the topographic picture, but the scalar/topographic profile solution and neutral boundary conditions remain open.

## Route C - Stationary Channel Route

Define the subsurface neutral channel as a support or saddle of the neutral effective action:

```text
grad_Y S_eff^(nu)(Y_nu) = 0.
```

The projection geometry supplies the exterior/topographic point:

```text
y_nu = Pi_sub_to_ext(Y_nu).
```

Then the neutral saddle displacement is:

```text
Delta y_nu = Pi_sub_to_ext(Y_nu) - y_H.
```

Status: `OPEN_LOCALIZABLE`.

Reason: the route links `S_eff_nu`, projection geometry, and the PO-BH-49 displacement formula, but both `S_eff_nu` and `Pi_sub_to_ext` remain open-localizable objects.

## Route D - Causality-Preserving Apparent FTL Route

Local internal causality is imposed as:

```text
v_sub <= c_sub.
```

Exterior-projected apparent speed may be anomalous due to projection/lapse:

```text
v_ext,proj = |d Pi_sub_to_ext(Y) / dt_ext|
```

with

```text
dt_ext = ellapse_nu dt_sub.
```

A small `ellapse_nu` can make exterior-projected motion appear fast without local internal causality violation.

Status: `STRUCTURALLY_MOTIVATED_NOT_DERIVED`.

Reason: this is a conservative interpretation scaffold, not a derived propagation theorem. It becomes mathematical only after `g_sub`, `ellapse_nu`, and `Pi_sub_to_ext` are derived.

## Verdict Table

| candidate route | formula | dependencies | status | reason | allowed next action | forbidden shortcut |
| --- | --- | --- | --- | --- | --- | --- |
| Metric splitting | `ds_ext^2=g_ext,ab dx^a dx^b`; `ds_sub^2=g_sub,AB dY^A dY^B`; `x^a=Pi_sub_to_ext^a(Y)`; `ellapse_nu^2=ds_proj^2/ds_sub^2` | `g_ext`, `g_sub`, `Pi_sub_to_ext`, positive interval-ratio convention, coordinate chart | `OPEN_LOCALIZABLE` | Metric/projection/lapse scaffold exists, but the metric and projection are not derived. | Derive `g_sub` and `Pi_sub_to_ext` from the internal topographic metric and boundary profile. | Choose a metric ratio or projection map from neutrino residuals or anomaly claims. |
| Topographic lapse | `0 < ellapse_nu(y) <= 1`; `ellapse_nu(y)->0` near a zero-exterior-spacetime core | scalar/topographic profile solution, neutral boundary conditions, positivity of lapse, core definition | `OPEN_LOCALIZABLE` | Compatible with the topographic picture, but profile and boundary conditions remain open. | Derive `ellapse_nu(y)` from the scalar/topographic profile and boundary conditions. | Fit `ellapse_nu` to neutrino masses, PMNS residuals, or apparent speed claims. |
| Stationary channel | `grad_Y S_eff^(nu)(Y_nu)=0`; `y_nu=Pi_sub_to_ext(Y_nu)`; `Delta y_nu=Pi_sub_to_ext(Y_nu)-y_H` | `S_eff_nu`, `Pi_sub_to_ext`, stationary channel coordinates, Higgs/charged reference saddle `y_H` | `OPEN_LOCALIZABLE` | Connects projection geometry to PO-BH-49 but leaves the action and projection map open. | Derive the neutral stationary channel and projection map before any neutrino comparison. | Pick `Y_nu` or `Pi_sub_to_ext` to make `Delta_y_nu` numerically useful. |
| Causality-preserving apparent FTL | `v_sub<=c_sub`; `v_ext,proj=|d Pi_sub_to_ext(Y)/dt_ext|`; `dt_ext=ellapse_nu dt_sub` | `g_sub` causal cone, `ellapse_nu`, `Pi_sub_to_ext`, projection theorem | `STRUCTURALLY_MOTIVATED_NOT_DERIVED` | Explains exterior-projected apparent FTL without local causality violation, but is not derived. | Prove the projection statement from `g_sub`, `ellapse_nu`, and `Pi_sub_to_ext`. | Claim literal local FTL, experimental FTL, or tune projection data to anomalies. |

## Closure-Map Status

The preferred status is:

```text
g_sub: OPEN_LOCALIZABLE
ellapse_nu: OPEN_LOCALIZABLE
Pi_sub_to_ext: OPEN_LOCALIZABLE
```

Missing dependencies:

- scalar/topographic profile solution;
- coordinate chart or coordinate-invariant projection convention;
- internal metric derivation;
- positivity/causality proof;
- relation to neutral boundary tensors and neutral boundary conditions.

## Claim Boundary

The subsurface neutral projection geometry has been localized as a required dependency for the neutral effective action. Candidate internal metric, projection map, and exterior-lapse structures are documented. No local FTL or numerical neutrino prediction is claimed.

Observed neutrino masses, observed neutrino mass splittings, PMNS angles, PMNS CP phase, fitted FTL/anomaly data, and post-comparison choices of `g_sub`, `ellapse_nu`, or `Pi_sub_to_ext` are forbidden inputs.

## Next Action

Derive or reject `g_sub`, `ellapse_nu`, and `Pi_sub_to_ext` from the scalar/topographic profile, coordinate-invariant projection convention, positivity/causality proof, and neutral boundary tensors before any neutrino comparison.
