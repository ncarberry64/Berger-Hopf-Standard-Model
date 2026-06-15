# Full BHSM Completion v1.0 Candidate

## Executive Status

Full BHSM v1.0 Candidate is a repo-audited candidate architecture, not a completed proof of the Standard Model.

The discrete geometric skeleton is strong and test-backed.
The continuous numerical mass engine remains unresolved.
The existing BHSM prediction layer remains protected.
The new heat-kernel spectral-action mass engine was tested and demoted to ordering scaffold only.
The collective curvature threshold layer is documented as a candidate interpretation, not a solved dark-matter theory.

## Layer Architecture

```text
Full BHSM v1.0 Candidate =
local SM gauge representation layer
+ Berger-Hopf boundary channel layer
+ topographic fourth-order stability layer
+ response-selector layer
+ collective curvature threshold layer.
```

```text
S_BHSM,candidate =
S_SM,local
+ S_T
+ S_boundary
+ S_response
+ S_collective-threshold
```

`S_SM,local` preserves the infrared local gauge layer:

```text
SU(3)_c x SU(2)_L x U(1)_Y
```

`S_T` supplies:

```text
L_T = nabla^2 - B*nabla^4
fourth-order stability
two nonzero branches + zero reference
```

`S_boundary` supplies:

```text
A_rep = A_q tensor O_q + A_j tensor O_j
O_q = 3B - L
O_j = -4T3 + 2(3B)(1/2 - T3)
```

`S_response` supplies operator activity, pair-count activity, amplitude projection,
interface-block dilution, and candidate stochastic dressing.

`S_collective-threshold` supplies:

```text
K_eff = K_self + Gm + K_boundary + K_envelope
m_i = M_f [K_i_eff - K_i_crit]_+^p Z_i
```

## Representation-To-Mode Pipeline

```text
(B,L,T3)
-> (O_q,O_j)
-> Omega_f
-> Omega_f_star
-> G_f
-> H_f
-> branch role
-> response/threshold layer
```

```text
O_q = 3B - L
O_j = -4T3 + 2(3B)(1/2 - T3)
Omega_f(q,j) = O_q q + O_j j
q = k - 2j
k = q + 2j
N = q^2 + j^2
```

## Target Degree Law

```text
Omega_f_star = 3 * 2^(3B + (3B)(1/2 - T3))
```

Outputs:

```text
charged lepton: 3
neutrino magnitude: 3
up: 6
down: 12
```

Status: `SECTOR_TARGET_DEGREE_LIFT_LAW_STRUCTURAL_CANDIDATE`

## Fermion Ledger

Generated modes in `(k,j)` form:

| sector | heavy | middle | light |
| --- | --- | --- | --- |
| charged lepton | (0,0) | (5,2) | (9,3) |
| neutrino | (0,0) | (3,0) | (3,1) |
| up | (0,0) | (6,0) | (10,1) |
| down | (0,0) | (6,3) | (8,2) |

Generated modes in `(q,j)` form:

| sector | heavy | middle | light |
| --- | --- | --- | --- |
| charged lepton | (0,0) | (1,2) | (3,3) |
| neutrino | (0,0) | (3,0) | (1,1) |
| up | (0,0) | (6,0) | (8,1) |
| down | (0,0) | (0,3) | (4,2) |

Status: `FERMION_MODE_LEDGER_FROM_REP_RULES_CONDITIONAL`

## Generation Count

```text
three generations = zero-boundary reference + two stable nonzero topographic branches
```

Status: `GENERATION_COUNT_FOURTH_ORDER_STABILITY_STRUCTURAL_CANDIDATE`

## Mass Engine Status

New heat-kernel spectral action:

```text
Tier C ordering only.
Not the existing BHSM engine.
Existing BHSM bare predictions beat the heat-kernel baseline on all six charged mass rows.
```

Minimal branch-threshold reconstruction:

```text
D_log_threshold_plus_type was the best minimal reconstruction diagnostic.
RMS log error to existing bare approximately 0.510697459271581.
Max abs log error approximately 1.0380747597108453.
Ordering pass: yes.
Middle-vs-light separation pass: yes.
Hidden response remains.
Overfit risk remains.
No numerical closure.
```

Status labels:

```text
BARE_YUKAWA_SPECTRAL_ACTION_CANDIDATE
RAW_BARE_ACTION_TIER_C_ORDERING_ONLY_CONFIRMED
SPECTRAL_ACTION_NOT_EXISTING_ENGINE
LOG_THRESHOLD_SIGNAL_INDICATED
HIDDEN_RESPONSE_REMAINS_INDICATED
NO_NUMERICAL_CLOSURE
```

## Collective Curvature Threshold Layer

Mass is interpreted as a collective curvature threshold response, not isolated spectral decay.

```text
L_T T = S_total
L_T = nabla^2 - B*nabla^4
S_total = S_visible + S_internal_modes + S_boundary + S_interaction
K_i_eff = K_i_self + sum_j G_ij m_j + K_i_boundary + K_i_envelope
m_i = M_f [K_i_eff - K_i_crit]_+^p Z_i
```

Status:

```text
COLLECTIVE_CURVATURE_THRESHOLD_LAYER_CANDIDATE
MASS_AS_COLLECTIVE_THRESHOLD_RESPONSE_CANDIDATE
LOG_THRESHOLD_BRIDGE_DOCUMENTED
NO_NUMERICAL_CLOSURE
```

## Dark Matter Interpretation

```text
K_obs = K_visible + K_collective
K_DM_eff = K_obs - K_visible
rho_DM_eff = (1/(4*pi*G)) nabla^2 Phi_collective
```

This is an effective collective curvature residue interpretation. It does not claim that dark matter is solved. It does not claim that particle dark matter is disproven. It requires empirical gravity tests.

Status:

```text
COLLECTIVE_CURVATURE_DARK_MATTER_INTERPRETATION_CANDIDATE
EFFECTIVE_DARK_MATTER_AS_CURVATURE_RESIDUE_CANDIDATE
NO_DARK_MATTER_SOLUTION_CLAIM_GUARDRAIL
EMPIRICAL_GRAVITY_TESTS_REQUIRED_GUARDRAIL
```

## Mixing And Neutrinos

```text
CKM candidate:
nested cover interface Z6 subset Z12
small mixing structural candidate

PMNS candidate:
equal-degree conjugate lepton covers Z3 <-> Z3
large mixing structural candidate

neutrino:
Omega_nu = -k
ledger: (0,0), (3,0), (3,1)
normal ordering preference candidate
m1 approximately zero at leading rank-two order candidate
A_l - A_nu = 4 A_j
PMNS CP phase base-holonomy dominated candidate
```

Status:

```text
BOUNDARY_INTERFACE_MIXING_KERNEL_STRUCTURAL_CANDIDATE
NEUTRINO_CONJUGATE_COVER_MASS_ENGINE_CANDIDATE
NEUTRINO_NORMAL_ORDERING_PREFERENCE_CANDIDATE
PMNS_BASE_HOLONOMY_PHASE_CANDIDATE
```

## Gauge Layer

```text
alpha_G = C_G/(6*pi^2)
C_U1 = 1
C_SU2 = 2
C_SU3 = 7
ratio = 1:2:7
```

Status: `GAUGE_COUPLING_ACTIVE_GENERATOR_COUNT_STRUCTURAL_CANDIDATE`

Guardrail: This is not a derivation of the full local gauge group.

## Status Cross-Links

- [Current BHSM status](../docs/current_bhsm_status.md)
- [Master equation map](full_bhsm_master_equation_map.md)
- [Claim status matrix](full_bhsm_claim_status_matrix.md)
- [Open proof obligations](full_bhsm_open_proof_obligations.md)
- [Empirical gate plan](full_bhsm_empirical_gate_plan.md)
- [Candidate release notes](full_bhsm_candidate_release_notes.md)
- [SM low-energy limit derivation gate](sm_low_energy_limit_derivation_gate.md)
- [SM input dependency audit](sm_input_dependency_audit.md)
