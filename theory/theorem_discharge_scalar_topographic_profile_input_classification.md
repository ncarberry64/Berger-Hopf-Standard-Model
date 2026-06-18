# PO-BH-60 - Scalar/Topographic Profile Input Classification and Threshold Ledger

Status: input classification only. Numerical closure remains open.

Current public status: structural architecture integrated conditional; numerical closure open.

## Purpose

PO-BH-59 localized two scalar/topographic level-set routes:

```text
F_STF(x,t) = T(x,t) - T_0
```

and

```text
F_int(y) = Phi(y) - Phi_0.
```

It also conditionally derived the regular-level-set normal, second fundamental
form, shape operator, trace curvature, and collar-Jacobian formulas. PO-BH-60
does not add a numerical prediction. It classifies the profile inputs and
thresholds needed to evaluate the PO-BH-59 geometry without fitting to observed
data.

PO-BH-60 is not a numerical prediction sprint.

Localized notation is not a derivation. A symbol in the framework can justify
`LOCALIZED_NOT_NUMERIC`, but it cannot justify `DERIVED_CONDITIONAL` unless the
repo supplies the equations, assumptions, and dependencies that derive it from
prior BHSM structure.

## Prior Chain Through PO-BH-59

- PO-BH-47: numerical input closure map.
- PO-BH-48: `S_nu_topo` localized.
- PO-BH-49: `Delta_y_nu` localized.
- PO-BH-50: `S_eff_nu` localized.
- PO-BH-51: subsurface projection geometry localized.
- PO-BH-52: neutral boundary tensors localized.
- PO-BH-53: scalar/topographic boundary variation derived conditionally.
- PO-BH-54: normal-coupling/collar convention localized.
- PO-BH-55: collar geometry package localized.
- PO-BH-56: complete scalar/topographic collar action audited.
- PO-BH-57: collar measure / extrinsic geometry derived conditionally.
- PO-BH-58: boundary embedding / induced metric / shape operator formulas
  derived conditionally.
- PO-BH-59: scalar/topographic level-set routes localized, with
  regular-level-set geometry derived conditionally.

## Route A - Spacetime Scalar `T(x,t)`

PO-BH-59 records the candidate spacetime route

```text
F_STF(x,t) = T(x,t) - T_0
T(x,t) = T_0.
```

The scalar framework notation is

```text
T(x,t) = T_bg(t) + A_T,dip(t)(ihat . uhat) + T_loc(x,t).
```

Classification:

```text
explicit T(x,t): LOCALIZED_NOT_NUMERIC
T_bg(t): LOCALIZED_NOT_NUMERIC
A_T,dip(t): LOCALIZED_NOT_NUMERIC
T_loc(x,t): OPEN_LOCALIZABLE
T_0: OPEN_LOCALIZABLE
gradient norm |grad T|: OPEN_LOCALIZABLE
```

Reason: the decomposition is localized as framework notation. The explicit
functions, threshold, metric values, gradient norm, and orientation are not
derived.

## Route B - Internal Profile `Phi(y)`

PO-BH-59 records the candidate internal route

```text
F_int(y) = Phi(y) - Phi_0
Phi(y) = Phi_0.
```

The internal localization is a Berger space `B^3` with radius `r`, squash
parameter `epsilon`, and universal Higgs/topographic profile `Phi(y)` peaked at
`y_0`.

Classification:

```text
explicit Phi(y): LOCALIZED_NOT_NUMERIC
internal Berger metric g_B: LOCALIZED_NOT_NUMERIC
Berger radius r: OPEN_LOCALIZABLE
Berger squash parameter epsilon: OPEN_LOCALIZABLE
distinguished point y_0: LOCALIZED_NOT_NUMERIC
Phi_0: OPEN_LOCALIZABLE
gradient norm |grad Phi|: OPEN_LOCALIZABLE
```

Reason: the profile and internal geometry are localized as framework objects,
but the explicit profile, threshold, metric values, radius, squash parameter,
gradient norm, and orientation are not derived here.

## Four Gate Decomposition

PO-BH-60 splits the profile bottleneck into four separable gates:

| gate | question | current status | consequence |
| --- | --- | --- | --- |
| Gate 1 - profile existence/localization | Does BHSM define `T` or `Phi` as framework objects? | Partially localized | `T(x,t)` and `Phi(y)` may be referenced as framework objects, but not as numerical profiles. |
| Gate 2 - threshold selection | Does BHSM derive `T_0` or `Phi_0`? | Open-localizable | The level set is not fixed. |
| Gate 3 - metric/profile evaluation | Does BHSM supply the metric, profile, gradient norm, and orientation needed to evaluate `n`, `K`, `S`, and `J`? | Open-localizable | The formulas remain conditional and unevaluated. |
| Gate 4 - neutral action evaluation | Does BHSM supply the integral/action prescription needed to compute `S_nu_topo` and `epsilon_nu_topo`? | Open-localizable | Neutral numerical suppression remains open. |

Expected result: Gate 1 is partially localized. Gates 2, 3, and 4 remain
open-localizable.

Gate 1 is partially localized; Gates 2, 3, and 4 remain open-localizable.

## Input Ledger

| input | route | status | evidence in repo | missing dependency | forbidden shortcut |
| --- | --- | --- | --- | --- | --- |
| `T_0` | spacetime threshold | `OPEN_LOCALIZABLE` | PO-BH-59 identifies `T=T_0` as a candidate level set. | threshold selection theorem | fit threshold to neutrino or anomaly/FTL data |
| `Phi_0` | internal threshold | `OPEN_LOCALIZABLE` | PO-BH-59 identifies `Phi=Phi_0` as a candidate level set. | threshold selection theorem | fit threshold to neutrino or PMNS data |
| explicit `T(x,t)` | spacetime scalar | `LOCALIZED_NOT_NUMERIC` | framework decomposition `T_bg + A_T,dip(ihat.uhat) + T_loc` | explicit functions and dynamics | choose functions from target residuals |
| explicit `Phi(y)` | internal profile | `LOCALIZED_NOT_NUMERIC` | universal profile symbol peaked at `y_0` | profile equation and solution | choose profile from neutral scale |
| `T_bg(t)` | spacetime scalar component | `LOCALIZED_NOT_NUMERIC` | framework decomposition | explicit function | tune background to target values |
| `A_T,dip(t)` | spacetime scalar component | `LOCALIZED_NOT_NUMERIC` | framework decomposition | explicit function | tune dipole to anomaly claims |
| `T_loc(x,t)` | spacetime scalar component | `OPEN_LOCALIZABLE` | framework decomposition names local term | explicit local source/dynamics | tune local term after comparison |
| internal Berger metric `g_B` | internal route | `LOCALIZED_NOT_NUMERIC` | internal Berger geometry is localized | explicit metric values/conventions | choose metric to fit suppression |
| Berger radius `r` | internal route | `OPEN_LOCALIZABLE` | radius is named in framework notation | derived radius value | tune radius to neutrino scale |
| Berger squash parameter `epsilon` | internal route | `OPEN_LOCALIZABLE` | squash parameter is named in framework notation | derived squash value | tune squash to match data |
| distinguished point `y_0` | internal profile | `LOCALIZED_NOT_NUMERIC` | `Phi(y)` is peaked at `y_0` | derivation of point from action | choose point from residuals |
| profile equation of motion | both routes | `OPEN_LOCALIZABLE` | scalar/topographic action scaffolds exist | full EOM and solution | infer EOM from desired profile |
| profile boundary conditions | both routes | `OPEN_LOCALIZABLE` | boundary variation is conditional | complete boundary-condition values | fit boundary condition to PMNS |
| gradient norm `|grad T|` | spacetime route | `OPEN_LOCALIZABLE` | regular-level-set normal requires it | metric/profile evaluation | assume nonzero gradient for prediction |
| gradient norm `|grad Phi|` | internal route | `OPEN_LOCALIZABLE` | regular-level-set normal requires it | internal metric/profile evaluation | assume nonzero gradient for prediction |
| normal orientation | both routes | `OPEN_LOCALIZABLE` | collar/normal conventions are localized | derived orientation sign | pick sign from anomaly/FTL data |
| `K(Y)` | collar trace | `OPEN_LOCALIZABLE` | trace formula conditionally derived | evaluated profile/metric/orientation | fit curvature to neutrino scale |
| `S(Y)` | shape operator | `OPEN_LOCALIZABLE` | shape-operator formula conditionally derived | evaluated `h_AB` and `K_AB` | fit shape operator |
| `J(Y,rho)` | collar Jacobian | formula `DERIVED_CONDITIONAL`; value `OPEN_LOCALIZABLE` | PO-BH-57 formula | evaluated `S(Y)` | fit Jacobian |
| `S_nu_topo` | neutral action | `OPEN_LOCALIZABLE` | Hessian/barrier route localized | action integral, positivity, profile | fit suppression |
| `epsilon_nu_topo` | neutral suppression factor | `OPEN_LOCALIZABLE` | structural relation `exp(-S_nu_topo)` | derived `S_nu_topo` | fit suppression factor |

## Threshold Ledger

| threshold | equation | status | why open |
| --- | --- | --- | --- |
| `T_0` | `T(x,t)=T_0` | `OPEN_LOCALIZABLE` | no BHSM threshold-selection theorem is present |
| `Phi_0` | `Phi(y)=Phi_0` | `OPEN_LOCALIZABLE` | no internal profile threshold-selection theorem is present |

`T_0` is not derived. `Phi_0` is not derived.

## Profile Equation-of-Motion Status

The repo has scalar/topographic action and boundary-variation scaffolds, but
PO-BH-60 does not find a complete profile equation of motion plus boundary
conditions that uniquely solve `T(x,t)` or `Phi(y)`.

```text
profile_equation_of_motion: OPEN_LOCALIZABLE
profile_boundary_conditions: OPEN_LOCALIZABLE
```

## Metric/Profile Dependency Table

| derived formula | required inputs | current evaluation status |
| --- | --- | --- |
| `n=grad F/|grad F|` | explicit profile, metric, nonzero gradient, orientation | formula conditional; value open |
| `K_AB=e_A^mu e_B^nu nabla_mu n_nu` | embedding, metric, connection, normal | formula conditional; value open |
| `S^A_B=h^{AC}K_CB` | induced metric and second fundamental form | formula conditional; value open |
| `K=tr(S)=nabla.n` | profile, metric, connection, orientation | formula conditional; value open |
| `J=det(I+rho S)` | evaluated shape operator | formula conditional; value open |

## Status Map

```text
T_0: OPEN_LOCALIZABLE
Phi_0: OPEN_LOCALIZABLE
topographic_scalar_T_explicit_profile: LOCALIZED_NOT_NUMERIC
internal_topographic_profile_Phi_explicit_profile: LOCALIZED_NOT_NUMERIC
T_bg: LOCALIZED_NOT_NUMERIC
A_T_dip: LOCALIZED_NOT_NUMERIC
T_loc: OPEN_LOCALIZABLE
internal_Berger_metric_g_B: LOCALIZED_NOT_NUMERIC
Berger_radius_r: OPEN_LOCALIZABLE
Berger_squash_parameter_epsilon: OPEN_LOCALIZABLE
distinguished_point_y_0: LOCALIZED_NOT_NUMERIC
profile_equation_of_motion: OPEN_LOCALIZABLE
profile_boundary_conditions: OPEN_LOCALIZABLE
gradient_norm_T: OPEN_LOCALIZABLE
gradient_norm_Phi: OPEN_LOCALIZABLE
normal_orientation: OPEN_LOCALIZABLE
K_of_Y: OPEN_LOCALIZABLE
S_of_Y: OPEN_LOCALIZABLE
J_of_Y_rho: DERIVED_CONDITIONAL formula; OPEN_LOCALIZABLE value
S_nu_topo: OPEN_LOCALIZABLE
epsilon_nu_topo: OPEN_LOCALIZABLE
```

## Guardrails

Observed masses, CKM values, PMNS values, neutrino data, anomaly/FTL data,
propulsion/anomaly data, and target values are forbidden inputs for choosing
any open profile, threshold, metric, orientation, curvature, action, or
suppression factor.

This sprint makes no numerical neutrino prediction. It makes no PMNS
prediction. It makes no CKM prediction. It makes no local FTL claim, no
experimental FTL claim, no anomaly validation claim, and no propulsion
validation claim. It does not compute `S_nu_topo` or `epsilon_nu_topo`.

## Final Conservative Outcome

PO-BH-60 classifies the scalar/topographic profile inputs required after
PO-BH-59. It separates the remaining bottleneck into four gates: profile
localization, threshold selection, metric/profile evaluation, and neutral
action evaluation. It confirms that `T(x,t)` and `Phi(y)` are localized as
framework objects, but `T_0`, `Phi_0`, explicit profile functions, gradient
norms, metric/profile values, orientation, `S_nu_topo`, and
`epsilon_nu_topo` remain open/localizable.

The public status remains:

```text
structural architecture integrated conditional; numerical closure open
```
