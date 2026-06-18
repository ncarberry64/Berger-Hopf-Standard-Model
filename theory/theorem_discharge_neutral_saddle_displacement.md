# PO-BH-49 - Neutral Saddle Displacement Theorem

## Mission

This sprint localizes the neutral saddle displacement

```text
Delta y_nu = y_nu - y_H
```

as one missing dependency in the already-localized neutral topographic
suppression action

```text
S_nu_topo = 1/2 Delta y_nu^T G_nu_topo Delta y_nu + S_barrier
G_nu_topo = 1/2 E_nu^T H_topo^(nu) E_nu.
```

The goal is not to fit neutrino data. The goal is to determine whether
`Delta y_nu` follows from existing BHSM scalar/topographic, neutral-ledger, or
finite-width structure.

## Verdict

`Delta_y_nu` remains `OPEN_LOCALIZABLE`.

The neutral saddle displacement `Delta y_nu` has been localized as a required
input for the `S_nu_topo` Hessian/barrier formula. Candidate stationary-point
and finite-width centroid definitions are documented. Numerical neutrino
closure remains open.

## Locked Context

The current neutral ledger is

```text
(0,0), (3,0), (1,1)
```

and the neutral operator is

```text
Omega_nu = -q - 2j = -k.
```

The neutral topographic suppression formula remains

```text
epsilon_nu_topo = exp(-S_nu_topo)
M_nu = epsilon_nu_topo M_nu^(0).
```

## Candidate Route A - Stationary-Point Displacement

Define the neutral and Higgs/charged saddles by

```text
grad_y S_eff^(nu)(y_nu) = 0
grad_y S_eff^(H)(y_H) = 0.
```

Linearizing around `y_H` gives the candidate formula

```text
Delta y_nu = - H_H^{-1} grad_y[delta S_eff^(nu-H)]|_{y_H}.
```

Status: `OPEN_LOCALIZABLE`.

Reason: the repo has scalar/topographic and Hessian scaffolds, but it does not
yet derive `S_eff^(nu)`, `S_eff^(H)`, `H_H`, or the neutral-minus-Higgs
gradient.

## Candidate Route B - Ledger Displacement

Candidate formula:

```text
Delta labels = (q_nu,j_nu) - (q_H,j_H).
```

Status: `STRUCTURALLY_MOTIVATED_NOT_DERIVED`.

Reason: the neutral ledger is present, but the Higgs/charged reference label
and the map from labels to topographic displacement coordinates are not
derived.

## Candidate Route C - Boundary-Operator Displacement

Candidate formula:

```text
Omega_nu = -q - 2j = -k.
```

Status: `STRUCTURALLY_MOTIVATED_NOT_DERIVED`.

Reason: the neutral boundary operator localizes the sector, but the repo does
not yet contain a theorem mapping boundary-operator mismatch to a displacement
from the charged/Higgs boundary saddle.

## Candidate Route D - Finite-Width Overlap Centroid

Candidate definitions:

```text
y_nu = integral y W_nu(y) dV / integral W_nu(y) dV
y_H  = integral y W_H(y) dV / integral W_H(y) dV
Delta y_nu = y_nu - y_H.
```

Status: `OPEN_LOCALIZABLE`.

Reason: the centroid definition is precise, but the repo does not yet derive
the neutral weight `W_nu`, the Higgs/charged weight `W_H`, a coordinate chart,
a compact-manifold centroid convention, or a gauge/coordinate invariance rule.

## Verdict Table

| candidate route | formula | dependencies | status | reason | allowed next action | forbidden shortcut |
| --- | --- | --- | --- | --- | --- | --- |
| Stationary-point displacement | `Delta y_nu = - H_H^{-1} grad_y[delta S_eff^(nu-H)]|_{y_H}` | `S_eff^(nu)`, `S_eff^(H)`, `H_H`, `delta S_eff^(nu-H)`, stationary equations | `OPEN_LOCALIZABLE` | Effective actions and the neutral-minus-Higgs gradient are not derived. | Derive the two effective actions, Hessian, and gradient from the boundary/topographic action. | Fit `Delta y_nu` to observed neutrino masses or PMNS residuals. |
| Ledger displacement | `Delta labels = (q_nu,j_nu) - (q_H,j_H)` | neutral ledger, Higgs/charged reference label, label-to-coordinate map | `STRUCTURALLY_MOTIVATED_NOT_DERIVED` | Ledger labels exist, but the reference label and distance map are not derived. | Derive the Higgs/charged reference and label-to-distance map. | Choose a label displacement because it gives the desired suppression. |
| Boundary-operator displacement | `Omega_nu = -q - 2j = -k` | `Omega_nu`, charged/Higgs boundary condition, operator-to-displacement map | `STRUCTURALLY_MOTIVATED_NOT_DERIVED` | Neutral operator is structural, not yet a displacement theorem. | Derive an operator-mismatch-to-displacement map. | Convert `Omega_nu` values into fitted coordinates. |
| Finite-width centroid | `Delta y_nu = <y>_nu - <y>_H` | `W_nu`, `W_H`, coordinate chart, centroid convention, gauge/coordinate invariance rule | `OPEN_LOCALIZABLE` | The centroid route is well-localized but lacks explicit weights and invariant convention. | Derive weights and an invariant centroid prescription from the finite-width profile. | Choose centroids after looking at neutrino data. |

## Claim Boundary

This sprint does not derive `S_nu_topo`, does not derive a numerical neutrino
mass scale, does not claim PMNS numerical prediction, and does not alter
frozen or official predictions.

Observed neutrino masses, observed neutrino mass splittings, PMNS angles, and
PMNS CP phase are forbidden inputs for choosing `Delta y_nu`.

## Missing Dependencies

- derive `S_eff^(nu)`;
- derive `S_eff^(H)`;
- derive the Higgs/charged Hessian `H_H`;
- derive `grad_y[delta S_eff^(nu-H)]|_{y_H}`;
- derive `W_nu` and `W_H`;
- derive a coordinate chart or coordinate-invariant centroid convention;
- derive the neutral label-to-distance map `E_nu`;
- keep all ingredients locked before any neutrino-scale comparison.

## Current Public Status

`structural architecture integrated conditional; numerical closure open`

