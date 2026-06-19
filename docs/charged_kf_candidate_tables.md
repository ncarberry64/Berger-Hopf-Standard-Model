# Charged K_f Candidate Tables

Current public status: structural architecture integrated conditional; numerical closure open.

These tables are structural diagnostics for `src/charged_kf_generator.py`. They
are not empirical comparisons and do not update frozen or official prediction
outputs.

Status:

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

## Charged Suppression Constants

| Constant | Value |
| --- | ---: |
| `g_ch` | `1/21` |
| `Pi_l` | `1/7` |
| `Pi_u` | `2/7` |
| `Pi_d` | `4/7` |
| `S_l` | `20/21` |
| `S_u` | `19/21` |
| `S_d` | `17/21` |
| `eta_l` | `20/3087` |
| `eta_u` | `38/3087` |
| `eta_d` | `68/3087` |

## Diagonal Costs by Branch

| `rho_ch` | Lepton ledger costs | Up ledger costs | Down ledger costs |
| ---: | --- | --- | --- |
| 1 | `0, 5, 18` | `0, 36, 65` | `0, 9, 20` |
| 2 | `0, 9, 27` | `0, 36, 66` | `0, 18, 24` |
| 3 | `0, 13, 36` | `0, 36, 67` | `0, 27, 28` |

## Bridge Entries

| Sector | `beta_f` | `kappa_f` |
| --- | ---: | ---: |
| lepton | `1/147` | `1/[21(4+rho_ch)]` |
| up | `2/147` | `1/[21(4+rho_ch)]` |
| down | `4/147` | `1/[21(16+rho_ch)]` |

## Minimal K_f Template

For each charged sector:

```text
K_f = [[0, beta_f, 0],
       [beta_f, eta_f N_1,f, kappa_f],
       [0, kappa_f, eta_f N_2,f]]
```

The template is real, symmetric, and tridiagonal. The off-diagonal bridge is a
minimal candidate closure ansatz; it is not promoted to a complete charged
action derivation.

## Operator-Level Threshold Insertion

The only allowed threshold insertion in this sprint is the existing middle-up
candidate:

```text
K_u_dressed = K_u + (ln 2) |1_u><1_u|
```

where slot `1_u` is the construction-basis up-sector mode `(6,0)`.

No other slot receives a threshold insertion, and no post-diagonal arbitrary
dressing function is introduced.

## Diagnostic Eigenvalue Readout

The machine-readable report
`data/bhsm_full_freeze_protocol_charged_kf_v1.json` contains the deterministic
bare eigenvalues, bare gaps from ground, and up-sector operator-threshold gaps
for `rho_ch in {1,2,3}`.

The small matrix spectra are diagnostic outputs of the candidate generator.
They are not a mass comparison, not a CKM comparison, and not numerical closure.
Negative diagnostic ground offsets in a candidate branch are reported rather
than hidden; the readout theorem and positivity/threshold operator remain open
beyond the stated candidate statuses.
