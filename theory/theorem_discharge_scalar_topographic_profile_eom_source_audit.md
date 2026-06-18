# PO-BH-61 - Scalar/Topographic Profile Equation-of-Motion Source Audit

Status: derivation-source audit completed; partial EOM source found.

Current public status: structural architecture integrated conditional; numerical closure open.

## Purpose

PO-BH-61 is a derivation-source audit, not a numerical prediction sprint.
It asks whether the existing BHSM scalar/topographic, collar, boundary,
level-set, and neutral-action files already contain enough structure to derive
the profile equations of motion, boundary conditions, thresholds, profile
solutions, and neutral topographic action values needed for numerical closure.

The result is conservative:

```text
profile_EOM_source_audit: COMPLETED
profile_EOM_source_result: PARTIAL_EOM_SOURCE_FOUND
```

The repo contains partial variational structure: a schematic scalar bulk
action, a symbolic boundary variation, collar/boundary scaffolds, and
level-set geometry. It does not yet contain a complete explicit spacetime
topographic EOM, internal Berger profile EOM, threshold-selection theorem,
profile solution, neutral action evaluation, or value of
`epsilon_nu_topo`.

In short: it does not yet contain a complete explicit spacetime topographic EOM.

## Prior Chain

- PO-BH-53 conditionally derives a symbolic scalar/topographic boundary
  variation.
- PO-BH-54 and PO-BH-55 localize the normal-coupling/collar convention and
  collar geometry package.
- PO-BH-56 audits the complete scalar/topographic collar action source.
- PO-BH-57 and PO-BH-58 conditionally derive standard collar and boundary
  embedding geometry formulas.
- PO-BH-59 localizes spacetime and internal level-set routes.
- PO-BH-60 classifies scalar/topographic profile inputs and leaves threshold
  selection, metric/profile evaluation, and neutral action evaluation open.

## Route 1 - Existing Scalar/Topographic Action

Evidence found:

```text
S_bulk =
int_B [
  1/2 g^{mu nu} partial_mu Phi partial_nu Phi
  - V(Phi)
] dV.
```

This supports a schematic scalar Euler-Lagrange route of the usual form
`Box_g Phi - dV/dPhi = 0`, up to conventions and any additional source
terms. It does not derive a BHSM-specific `V(Phi)`, metric values, sources,
thresholds, or solution.

Status:

```text
internal_Berger_profile_EOM: OPEN_LOCALIZABLE
spacetime_topographic_EOM: OPEN_LOCALIZABLE
```

Finding: partial EOM structure exists, but no complete profile equation is
derived.

## Route 2 - Collar/Boundary Variation

Evidence found: the scalar/topographic boundary variation gives a symbolic
boundary condition of the form

```text
n_mu partial^mu Phi
- D_A(chi_nu^{AB}D_B Phi)
+ R_nu[lambda_nu, Phi, n.grad Phi]
= 0 on partialB.
```

This is a genuine symbolic boundary-variation result, conditional on the
remaining tensor, collar, profile, and normal-coupling data. It does not fix
the tensor values, Robin coefficients, edge data, profile values, or solution.

Status:

```text
profile_boundary_conditions_from_variation: DERIVED_CONDITIONAL
profile_boundary_conditions: OPEN_LOCALIZABLE for evaluated data
```

Finding: boundary-condition form is conditionally derived, but not enough to
solve `T(x,t)` or `Phi(y)`.

## Route 3 - Level-Set Threshold Selection

Evidence found:

```text
F_STF(x,t) = T(x,t) - T_0
F_int(y) = Phi(y) - Phi_0
```

PO-BH-59 localizes both level-set routes and conditionally derives standard
regular-level-set geometry. It does not derive the threshold values `T_0` or
`Phi_0`.

Status:

```text
threshold_selection_T_0: OPEN_LOCALIZABLE
threshold_selection_Phi_0: OPEN_LOCALIZABLE
threshold_selection_gate: OPEN_LOCALIZABLE
```

Finding: the route is localized, but threshold selection is not derived.

## Route 4 - Internal Berger Profile Equation

Evidence found: the internal route identifies an internal Berger geometry,
a profile symbol `Phi(y)`, a distinguished point `y_0`, and level-set geometry
dependencies. It does not provide the explicit internal Berger metric values,
profile potential, profile source, or boundary data needed to write and solve
the complete internal profile EOM.

Status:

```text
internal_Berger_profile_EOM: OPEN_LOCALIZABLE
Phi_profile_solution: OPEN_LOCALIZABLE
metric_profile_evaluation_gate: OPEN_LOCALIZABLE
```

Finding: the profile is localized as a framework object, not solved.

## Route 5 - Neutral/Topographic Action Functional

Evidence found: prior files localize a neutral topographic suppression route,
including a Hessian/barrier candidate for `S_nu_topo`.

The repo does not yet supply all dependencies needed to evaluate the neutral
functional: explicit profile solution, metric/profile data, neutral
displacement, Hessian, embedding map, barrier term, threshold, and positivity
proof.

Status:

```text
S_nu_topo_functional: OPEN_LOCALIZABLE
S_nu_topo_value: OPEN_LOCALIZABLE
epsilon_nu_topo: OPEN_LOCALIZABLE
neutral_action_evaluation_gate: OPEN_LOCALIZABLE
```

Finding: the neutral action route is localized, but neither the functional
evaluation nor the exponential suppression value is derived.

## Route 6 - No-Source Result

A strict no-source result would say no action, boundary, or level-set
structure exists. That is too strong for the current repo.

The correct outcome is partial:

```text
existing_EOM_source: PARTIAL
complete_EOM_source: NOT_FOUND
threshold_source: NOT_FOUND
profile_solution_source: NOT_FOUND
neutral_action_value_source: NOT_FOUND
```

## Evidence Table

| route | evidence present | current result |
| --- | --- | --- |
| Existing scalar/topographic action | schematic scalar bulk action and variational language | partial EOM structure only |
| Collar/boundary variation | symbolic boundary condition from variation | `DERIVED_CONDITIONAL` form; evaluated data open |
| Level-set threshold selection | `T=T_0` and `Phi=Phi_0` routes | thresholds open |
| Internal Berger profile equation | internal profile and Berger geometry symbols | EOM and solution open |
| Neutral/topographic action functional | Hessian/barrier route localized | value and suppression open |
| No-source result | false as a total claim | partial source found, but not complete |

## Missing Derivation Source Table

| object | status after PO-BH-61 | missing source |
| --- | --- | --- |
| `spacetime_topographic_EOM` | `OPEN_LOCALIZABLE` | explicit spacetime scalar/topographic action, metric, potential/source, and admissible variations |
| `internal_Berger_profile_EOM` | `OPEN_LOCALIZABLE` | explicit internal Berger metric, profile potential/source, and boundary/collar data |
| `profile_boundary_conditions_from_variation` | `DERIVED_CONDITIONAL` | tensor values, Robin coefficients, collar edge data, and profile data |
| `threshold_selection_T_0` | `OPEN_LOCALIZABLE` | threshold-selection theorem |
| `threshold_selection_Phi_0` | `OPEN_LOCALIZABLE` | internal threshold-selection theorem |
| `T_profile_solution` | `OPEN_LOCALIZABLE` | complete spacetime EOM plus boundary/initial data |
| `Phi_profile_solution` | `OPEN_LOCALIZABLE` | complete internal EOM plus boundary data |
| `S_nu_topo_functional` | `OPEN_LOCALIZABLE` | complete neutral topographic action dependencies |
| `S_nu_topo_value` | `OPEN_LOCALIZABLE` | derived profile/integration data |
| `epsilon_nu_topo` | `OPEN_LOCALIZABLE` | derived `S_nu_topo` value |
| `neutral_action_evaluation_gate` | `OPEN_LOCALIZABLE` | action evaluation before comparison |
| `metric_profile_evaluation_gate` | `OPEN_LOCALIZABLE` | metric, profile, gradient, and orientation values |
| `threshold_selection_gate` | `OPEN_LOCALIZABLE` | derived thresholds |

## Status Map

```text
profile_EOM_source_audit: COMPLETED
profile_EOM_source_result: PARTIAL_EOM_SOURCE_FOUND
spacetime_topographic_EOM: OPEN_LOCALIZABLE
internal_Berger_profile_EOM: OPEN_LOCALIZABLE
profile_boundary_conditions_from_variation: DERIVED_CONDITIONAL
threshold_selection_T_0: OPEN_LOCALIZABLE
threshold_selection_Phi_0: OPEN_LOCALIZABLE
T_profile_solution: OPEN_LOCALIZABLE
Phi_profile_solution: OPEN_LOCALIZABLE
S_nu_topo_functional: OPEN_LOCALIZABLE
S_nu_topo_value: OPEN_LOCALIZABLE
epsilon_nu_topo: OPEN_LOCALIZABLE
neutral_action_evaluation_gate: OPEN_LOCALIZABLE
metric_profile_evaluation_gate: OPEN_LOCALIZABLE
threshold_selection_gate: OPEN_LOCALIZABLE
```

## Guardrails

Observed masses, CKM values, PMNS values, neutrino data, anomaly/FTL data,
propulsion/anomaly data, and target values are forbidden inputs for choosing
open EOM terms, thresholds, profiles, metrics, orientations, action values,
or suppression factors.

This sprint makes no numerical neutrino prediction. It makes no PMNS
prediction. It makes no CKM prediction. It makes no local FTL claim, no
experimental FTL claim, no anomaly validation claim, and no propulsion
validation claim. It does not compute `S_nu_topo` or `epsilon_nu_topo`.

## Conclusion

PO-BH-61 finds a partial scalar/topographic EOM source: the repo has schematic
bulk variational structure and a conditionally derived symbolic boundary
condition. It does not find a complete EOM source, threshold-selection theorem,
profile solution, neutral action evaluation, or suppression value. Numerical
closure remains open, and all open profile inputs remain forbidden to fit
after comparison.
