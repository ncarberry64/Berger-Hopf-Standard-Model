# BHSM Full Freeze Protocol and Minimal Charged K_f Generator

Current public status: structural architecture integrated conditional; numerical closure open.

This sprint adds a candidate freeze protocol and a deterministic minimal charged
sector operator generator. It does not change frozen predictions, official
predictions, tolerances, public releases, or comparison data.

## Freeze Rule

BHSM numerical claims must follow this order:

1. Derive the structural ingredient from internal BHSM boundary/action data.
2. Freeze the ingredient before external comparison.
3. Predict or screen using only the frozen ingredient.
4. Compare after the freeze.

Forbidden derivation inputs include observed masses, quark mass ratios, charged
lepton masses, CKM values, PMNS values, neutrino data, measured alpha, target
ratios, and post-comparison residuals.

## Freeze Layers

| Layer | Content | Current status |
| --- | --- | --- |
| A | Sector architecture and projectors | `STRONGLY_SUPPORTED_CANDIDATE` |
| B | Sector ledgers and zero-defect equations | `DERIVED_CONDITIONAL_ON_SECTOR_ENGINE` |
| C | `rho_ch` branches `{1,2,3}` | `OPEN_LOCALIZABLE` exact value |
| D | Charged suppression package | `STRONGLY_SUPPORTED_CANDIDATE` |
| E | Effective charged `K_f` operators | `STRONGLY_SUPPORTED_CANDIDATE` |
| F | Threshold dressings | `STRONGLY_SUPPORTED_CANDIDATE`; full threshold operator `OPEN` |
| G | Branch tracking and readout | `STRONGLY_SUPPORTED_CANDIDATE` |
| H | Spectral-gap readout | diagnostic only in this sprint |
| I | RG/scheme transport | `OPEN` |

## Sector Projectors

The bridge primitive labels are `C in {0,1}` and `sigma in {+1,-1}`:

```text
P_C = C
P_+ = (1+sigma)/2
P_- = (1-sigma)/2
P_d = P_C P_- = C(1-sigma)/2
```

The sector projectors are:

```text
P_nu = (1-C)(1+sigma)/2
P_l  = (1-C)(1-sigma)/2
P_u  = C(1+sigma)/2
P_d  = C(1-sigma)/2
```

## Unified Boundary Winding

The candidate unified winding index is:

```text
Omega(C,sigma;q,j) = (2P_C-1) q + 2(-sigma)(1+P_d) j
                   = (2C-1) q - 2 sigma [1+C(1-sigma)/2] j
```

It reproduces:

| Sector | `C` | `sigma` | `Omega` |
| --- | ---: | ---: | --- |
| neutrino | 0 | +1 | `-q - 2j` |
| lepton | 0 | -1 | `-q + 2j` |
| up | 1 | +1 | `q - 2j` |
| down | 1 | -1 | `q + 4j` |

Status:

```text
unified_Omega_projector_formula: STRONGLY_SUPPORTED_CANDIDATE
```

## Incidence Target and Orientation Trace

The incidence target is:

```text
kappa_3 = 3
A(C,sigma) = kappa_3(1+P_C)(1+P_d)
```

The oriented target is:

```text
tau(C,sigma) = C - (1-C)sigma
T(C,sigma) = tau(C,sigma) A(C,sigma)
```

| Sector | `A` | `tau` | `T` |
| --- | ---: | ---: | ---: |
| neutrino | 3 | -1 | -3 |
| lepton | 3 | +1 | +3 |
| up | 6 | +1 | +6 |
| down | 12 | +1 | +12 |

Status:

```text
sector_target_incidence_product_A: STRONGLY_SUPPORTED_CANDIDATE
orientation_trace_Gamma_T: STRONGLY_SUPPORTED_CANDIDATE
```

## Boundary Graded Defect

The candidate boundary graded defect is:

```text
Delta_IT = Omega - T
```

Admissible non-reference modes satisfy:

```text
Omega(C,sigma;q,j) = T(C,sigma)
```

Status:

```text
Boundary_Graded_Defect_Theorem: STRONGLY_SUPPORTED_CANDIDATE
```

This remains candidate-level. It is not action-derived until the BHSM action
derives `D_C`, `D_d`, `Gamma_sigma`, `Gamma_T`, `E_3`, `E_A`, and the
zero-defect constraint.

## Candidate Ledgers

The reference slot `(0,0)` is a sector reference, not an ordinary excitation in
the zero-defect tangent test.

| Sector | Reference | First nonzero | Second nonzero | Tangent |
| --- | --- | --- | --- | --- |
| neutrino | `(0,0)` | `(3,0)` | `(1,1)` | `(-2,1)` |
| lepton | `(0,0)` | `(1,2)` | `(3,3)` | `(2,1)` |
| up | `(0,0)` | `(6,0)` | `(8,1)` | `(2,1)` |
| down | `(0,0)` | `(0,3)` | `(4,2)` | `(4,-1)` |

Status:

```text
zero_defect_tangent_adjacency: DERIVED_CONDITIONAL_ON_SECTOR_ENGINE
```

## Charged Stiffness Branches

The charged branch cost is:

```text
N_ch(q,j;rho_ch) = q^2 + rho_ch j^2
rho_ch in {1,2,3}
```

Branch interpretations:

| `rho_ch` | Interpretation |
| ---: | --- |
| 1 | isotropic candidate |
| 2 | weak-involution weighted candidate |
| 3 | rank-three closure weighted candidate |

Status:

```text
rho_ch_exact_value: OPEN_LOCALIZABLE
rho_ch_branches={1,2,3}: STRUCTURAL_CANDIDATES
```

Down-sector windows remain:

```text
0 < rho_ch < 8
0 < rho_ch < 16/5    old down ordering window
```

## Charged Suppression Package

The candidate incidence closure is:

```text
g_ch = 1/21
Pi_l = 1/7
Pi_u = 2/7
Pi_d = 4/7
S_l = 20/21
S_u = 19/21
S_d = 17/21
eta_l = 20/3087
eta_u = 38/3087
eta_d = 68/3087
```

Status:

```text
charged_suppression_incidence_closure: STRONGLY_SUPPORTED_CANDIDATE
```

It is not promoted beyond candidate-level until `B_supp` and phase response
normalization are action-derived.

## Minimal Charged Operators

For charged sectors the candidate log-suppression operator is the real symmetric
tridiagonal matrix:

```text
K_f = [[0, beta_f, 0],
       [beta_f, lambda1_f, kappa_f],
       [0, kappa_f, lambda2_f]]
```

with:

```text
lambda_i,f = eta_f N_i,f
beta_f = g_ch Pi_f
kappa_f = g_ch / ||v_f||_ch^2
```

The tangent norms are:

```text
||v_l||^2 = 4 + rho_ch
||v_u||^2 = 4 + rho_ch
||v_d||^2 = 16 + rho_ch
```

Status:

```text
minimal_charged_Kf_generator: STRONGLY_SUPPORTED_CANDIDATE
```

The bridge seeds `beta0=kappa0=g_ch` remain a minimal bridge closure ansatz,
not a derived conditional result.

## Threshold Insertion

The existing allowed middle-up dressing is inserted at operator level:

```text
K_u_dressed = K_u + (ln 2) |1_u><1_u|
```

where the slot is the up-sector mode `(6,0)`. No post-diagonal arbitrary
dressing is introduced.

Status:

```text
operator_level_threshold_insertion: STRONGLY_SUPPORTED_CANDIDATE
Z_virt_u1: DERIVED_CONDITIONAL
full_threshold_operator: OPEN
```

## Branch Tracking

The readout rule is:

1. Start in the bare diagonal ledger basis.
2. Turn on `beta_f` and `kappa_f` continuously.
3. Apply derived threshold insertions continuously.
4. Diagonalize the final frozen operator.
5. Track eigenbranches by maximal overlap with the prior branch.
6. Assign physical mass ordering only after the full operator is frozen.

Status:

```text
Mode_Identity_Threshold_Readout_Theorem: STRONGLY_SUPPORTED_CANDIDATE
```

## Current Status Table

```text
Boundary_Graded_Defect_Theorem: STRONGLY_SUPPORTED_CANDIDATE
sector_target_incidence_product_A: STRONGLY_SUPPORTED_CANDIDATE
orientation_trace_Gamma_T: STRONGLY_SUPPORTED_CANDIDATE
unified_Omega_projector_formula: STRONGLY_SUPPORTED_CANDIDATE
zero_defect_tangent_adjacency: DERIVED_CONDITIONAL_ON_SECTOR_ENGINE
charged_suppression_incidence_closure: STRONGLY_SUPPORTED_CANDIDATE
minimal_charged_Kf_generator: STRONGLY_SUPPORTED_CANDIDATE
operator_level_threshold_insertion: STRONGLY_SUPPORTED_CANDIDATE
Mode_Identity_Threshold_Readout_Theorem: STRONGLY_SUPPORTED_CANDIDATE
Z_virt_u1: DERIVED_CONDITIONAL
rho_ch_exact_value: OPEN_LOCALIZABLE
full_threshold_operator: OPEN
RG_transport: OPEN
numerical_closure: OPEN
```

## Claim Boundary

This file records a candidate freeze protocol and minimal charged operator
generator. It uses no empirical comparison inputs and does not update frozen or
official prediction outputs. The exact public status remains:

```text
structural architecture integrated conditional; numerical closure open
```
