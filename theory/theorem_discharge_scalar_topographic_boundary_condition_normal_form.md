# PO-BH-62 - Scalar/Topographic Boundary Condition Normal Form

Status: boundary-condition normal form derived conditionally.

Current public status: structural architecture integrated conditional; numerical closure open.

## Purpose

PO-BH-62 is a normal-form derivation sprint, not a classification sprint and
not a numerical prediction sprint.

PO-BH-61 found a partial EOM source: the existing schematic scalar bulk action
and symbolic boundary variation provide source structure, but no complete
profile EOM, threshold rule, profile solution, or neutral action value is
derived. PO-BH-62 takes the symbolic boundary variation structure and reduces
it to a clean conditional boundary-condition normal form.

The correct closure is normal-form closure, not coefficient closure.

## Prior Chain Through PO-BH-61

- PO-BH-53 conditionally derived the symbolic scalar/topographic boundary
  variation form.
- PO-BH-54 and PO-BH-55 localized the normal-coupling/collar convention.
- PO-BH-56 audited the complete scalar/topographic collar action source.
- PO-BH-57 and PO-BH-58 conditionally derived collar and embedding geometry
  formulas.
- PO-BH-59 localized spacetime and internal level-set routes.
- PO-BH-60 classified profile inputs and thresholds.
- PO-BH-61 completed a derivation-source audit and found
  `PARTIAL_EOM_SOURCE_FOUND`.

## Generic Variational Structure

For a scalar/topographic field `u`, a generic variational action has the
structure

```text
delta S = integral_B E[u] delta u + integral_partialB B[u] delta u.
```

Stationarity requires

```text
E[u] = 0 in the bulk
B[u] = 0 on the boundary
```

for the permitted boundary variations.

For a standard kinetic term, integration by parts supplies normal-derivative
boundary structure:

```text
B[u] contains n^mu partial_mu u
```

or in an internal Berger space with coordinates `y^a`,

```text
B[Phi] contains n^a partial_a Phi.
```

Boundary potentials or boundary couplings can shift the natural Neumann form
to a Robin or source-coupled Robin form:

```text
n.partial u + partial U_boundary/partial u = 0.
```

Equivalently, at normal-form level,

```text
alpha u + beta n.partial u = gamma
```

or, when a boundary source is supplied by action data,

```text
alpha u + beta n.partial u = J.
```

No numerical values for `alpha`, `beta`, `gamma`, or `J` are derived here.

## Boundary Variation Structure

The existing symbolic scalar/topographic boundary variation has the form

```text
n_mu partial^mu Phi
- D_A(chi_nu^{AB}D_B Phi)
+ R_nu[lambda_nu, Phi, n.grad Phi]
= 0 on partialB.
```

This supports conditional normal-form reduction because it contains:

- a normal derivative term;
- optional tangential boundary operator terms;
- optional source or Robin-like terms through `R_nu`;
- open tensor/collar/profile coefficients.

Therefore the form can be organized as Dirichlet, Neumann, Robin/mixed, or
source-coupled Robin families, while the values of all coefficients remain
open-localizable.

## Route A - Spacetime Scalar `T`

PO-BH-59/60 localized the spacetime route

```text
F_STF(x,t) = T(x,t) - T_0.
```

The level-set boundary notation is

```text
T |_{partial B} = T_0.
```

This is a Dirichlet level-set normal form. It does not derive `T_0`.

The natural-boundary normal derivative is

```text
n^mu partial_mu T |_{partial B} = 0.
```

The mixed/Robin normal form is

```text
alpha_T T + beta_T n^mu partial_mu T = gamma_T.
```

If a boundary source is supplied by later action data, the source-coupled
form is

```text
alpha_T T + beta_T n^mu partial_mu T = J_T.
```

Status:

```text
spacetime_boundary_condition_form_T: DERIVED_CONDITIONAL
normal_derivative_T: DERIVED_CONDITIONAL as form; value OPEN_LOCALIZABLE
boundary_condition_coefficients_T: OPEN_LOCALIZABLE
threshold_selection_T_0: OPEN_LOCALIZABLE
T_profile_solution: OPEN_LOCALIZABLE
```

## Route B - Internal Berger Profile `Phi`

PO-BH-59/60 localized the internal route

```text
F_int(y) = Phi(y) - Phi_0.
```

The level-set boundary notation is

```text
Phi |_{partial B_int} = Phi_0.
```

This is a Dirichlet level-set normal form. It does not derive `Phi_0`.

The internal regular-level-set normal is

```text
n_a = partial_a Phi / sqrt(|g_B^{bc} partial_b Phi partial_c Phi|)
```

and the internal normal derivative is

```text
n^a partial_a Phi |_{partial B_int}.
```

The natural-boundary normal form is

```text
n^a partial_a Phi |_{partial B_int} = 0.
```

The mixed/Robin normal form is

```text
alpha_Phi Phi + beta_Phi n^a partial_a Phi = gamma_Phi.
```

If a boundary source is supplied by later internal action data, the
source-coupled form is

```text
alpha_Phi Phi + beta_Phi n^a partial_a Phi = J_Phi.
```

Status:

```text
internal_boundary_condition_form_Phi: DERIVED_CONDITIONAL
normal_derivative_Phi: DERIVED_CONDITIONAL as form; value OPEN_LOCALIZABLE
boundary_condition_coefficients_Phi: OPEN_LOCALIZABLE
threshold_selection_Phi_0: OPEN_LOCALIZABLE
Phi_profile_solution: OPEN_LOCALIZABLE
```

## Dirichlet Normal Form

Dirichlet data fix the field value on the boundary:

```text
T |_{partial B} = T_0
Phi |_{partial B_int} = Phi_0.
```

This form is compatible with level-set notation. The thresholds `T_0` and
`Phi_0` are not derived.

The thresholds `T_0` and `Phi_0` are not derived.

## Neumann Normal Form

Neumann data fix the normal derivative on the boundary:

```text
n^mu partial_mu T |_{partial B} = 0
n^a partial_a Phi |_{partial B_int} = 0.
```

This is the natural boundary condition for the standard kinetic term when no
additional boundary potential/source is present and the boundary variation is
free.

## Robin/Mixed Normal Form

Robin or mixed data combine field value and normal derivative:

```text
alpha_T T + beta_T n^mu partial_mu T = gamma_T
alpha_Phi Phi + beta_Phi n^a partial_a Phi = gamma_Phi.
```

This is conditionally supported by the symbolic boundary variation and collar
terms. The coefficients remain open-localizable.

## Source-Coupled Normal Form

If later BHSM action data supply boundary sources, the same normal-form
family becomes

```text
alpha_T T + beta_T n^mu partial_mu T = J_T
alpha_Phi Phi + beta_Phi n^a partial_a Phi = J_Phi.
```

This is a conditional source-coupled form. PO-BH-62 does not derive source
values.

## Coefficient and Threshold Ledger

| object | PO-BH-62 status | reason |
| --- | --- | --- |
| `boundary_condition_normal_form` | `DERIVED_CONDITIONAL` | follows from variational bulk-plus-boundary structure |
| `spacetime_boundary_condition_form_T` | `DERIVED_CONDITIONAL` | Dirichlet, Neumann, Robin/mixed, and conditional source-coupled forms are localized |
| `internal_boundary_condition_form_Phi` | `DERIVED_CONDITIONAL` | same normal-form families apply with internal Berger normal derivative |
| `boundary_condition_coefficients_T` | `OPEN_LOCALIZABLE` | no `alpha_T`, `beta_T`, `gamma_T`, or `J_T` values are derived |
| `boundary_condition_coefficients_Phi` | `OPEN_LOCALIZABLE` | no `alpha_Phi`, `beta_Phi`, `gamma_Phi`, or `J_Phi` values are derived |
| `threshold_selection_T_0` | `OPEN_LOCALIZABLE` | `T_0` is not derived |
| `threshold_selection_Phi_0` | `OPEN_LOCALIZABLE` | `Phi_0` is not derived |
| `normal_derivative_T` | form `DERIVED_CONDITIONAL`; value `OPEN_LOCALIZABLE` | normal derivative structure is formal; profile value is open |
| `normal_derivative_Phi` | form `DERIVED_CONDITIONAL`; value `OPEN_LOCALIZABLE` | internal normal derivative structure is formal; profile value is open |
| `T_profile_solution` | `OPEN_LOCALIZABLE` | no spacetime profile solution is derived |
| `Phi_profile_solution` | `OPEN_LOCALIZABLE` | no internal profile solution is derived |
| `S_nu_topo_functional` | `OPEN_LOCALIZABLE` | normal form is prerequisite only |
| `S_nu_topo_value` | `OPEN_LOCALIZABLE` | no neutral action value is computed |
| `epsilon_nu_topo` | `OPEN_LOCALIZABLE` | no suppression value is computed |

## Missing Inputs

- coefficient derivation for `alpha_T`, `beta_T`, `gamma_T`, and `J_T`;
- coefficient derivation for `alpha_Phi`, `beta_Phi`, `gamma_Phi`, and
  `J_Phi`;
- threshold-selection theorem for `T_0`;
- threshold-selection theorem for `Phi_0`;
- explicit spacetime profile EOM and solution;
- explicit internal Berger profile EOM and solution;
- metric/profile values, gradient norms, and orientations;
- neutral action evaluation producing `S_nu_topo`;
- suppression value `epsilon_nu_topo`.

## Status Table

```text
boundary_condition_normal_form: DERIVED_CONDITIONAL
spacetime_boundary_condition_form_T: DERIVED_CONDITIONAL
internal_boundary_condition_form_Phi: DERIVED_CONDITIONAL
boundary_condition_coefficients_T: OPEN_LOCALIZABLE
boundary_condition_coefficients_Phi: OPEN_LOCALIZABLE
threshold_selection_T_0: OPEN_LOCALIZABLE
threshold_selection_Phi_0: OPEN_LOCALIZABLE
normal_derivative_T: DERIVED_CONDITIONAL as form; value OPEN_LOCALIZABLE
normal_derivative_Phi: DERIVED_CONDITIONAL as form; value OPEN_LOCALIZABLE
T_profile_solution: OPEN_LOCALIZABLE
Phi_profile_solution: OPEN_LOCALIZABLE
S_nu_topo_functional: OPEN_LOCALIZABLE
S_nu_topo_value: OPEN_LOCALIZABLE
epsilon_nu_topo: OPEN_LOCALIZABLE
neutral_action_evaluation_gate: OPEN_LOCALIZABLE
profile_solution_gate: OPEN_LOCALIZABLE
threshold_selection_gate: OPEN_LOCALIZABLE
```

## Guardrails

Observed masses, CKM values, PMNS values, neutrino data, anomaly/FTL data,
propulsion/anomaly data, and target values are forbidden inputs for choosing
open boundary coefficients, thresholds, profile solutions, neutral action
values, or suppression factors.

This sprint makes no numerical neutrino prediction. It makes no PMNS
prediction. It makes no CKM prediction. It makes no local FTL claim, no
experimental FTL claim, no anomaly validation claim, and no propulsion
validation claim. It does not compute `S_nu_topo` or `epsilon_nu_topo`. It
does not solve the scalar profile or topographic profile. It does not derive
`T_0`, derive `Phi_0`, or derive boundary coefficients.

## Final Conservative Conclusion

PO-BH-62 converts the symbolic boundary variation source identified in
PO-BH-61 into a conditional scalar/topographic boundary-condition normal form.
It records Dirichlet, Neumann, Robin/mixed, and conditional source-coupled
forms for the spacetime topographic scalar `T` and internal Berger/topographic
profile `Phi`. The normal-form structure is derived conditionally, but
coefficients, thresholds `T_0` and `Phi_0`, profile solutions, `S_nu_topo`
value, and `epsilon_nu_topo` remain open-localizable. No numerical neutrino,
PMNS, CKM, FTL, anomaly, propulsion, frozen prediction, or official prediction
claim is introduced.
