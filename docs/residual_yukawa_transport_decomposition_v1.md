# Residual Yukawa Transport Decomposition Theorem v1

Current public status: structural architecture integrated conditional; numerical closure open.

PR #36 conditionally canceled the same-sector gauge-universal RG component.
This sprint localizes the next piece: sector-universal residual/Yukawa identity
terms also cancel in same-sector ratios. No empirical inputs are used.

## Decomposition

For sector `f`, write the symbolic anomalous-dimension operator as:

```text
Gamma_f = gamma_gauge,f I_f + gamma_universal,f I_f + tilde_Gamma_f
```

For same-sector branches `a,b`:

```text
d ln(R_ab) / d ln(mu) = <a|Gamma_f|a> - <b|Gamma_f|b>
```

The identity components cancel:

```text
<a|gamma_gauge,f I_f|a> - <b|gamma_gauge,f I_f|b> = 0
<a|gamma_universal,f I_f|a> - <b|gamma_universal,f I_f|b> = 0
```

The remaining transport is:

```text
d ln(R_ab) / d ln(mu) = <a|tilde_Gamma_f|a> - <b|tilde_Gamma_f|b>
```

## Status

```text
same_sector_residual_identity_cancellation=DERIVED_CONDITIONAL_ON_SHARED_SECTOR_BRANCH_SPACE
residual_Yukawa_transport_decomposition=PARTIALLY_LOCALIZED
charged_branch_differential_residual_transport=OPEN_LOCALIZABLE
```

## Charged Ratios

| ratio | sector | gauge component | sector-universal residual | branch-differential residual | comparison ready |
| --- | --- | --- | --- | --- | --- |
| `mu_over_tau` | charged lepton | canceled | canceled | `OPEN_LOCALIZABLE` | no |
| `e_over_tau` | charged lepton | canceled | canceled | `OPEN_LOCALIZABLE` | no |
| `c_over_t` | up | canceled | canceled | `OPEN_LOCALIZABLE` | no |
| `u_over_t` | up | canceled | canceled | `OPEN_LOCALIZABLE` | no |
| `s_over_b` | down | canceled | canceled | `OPEN_LOCALIZABLE` | no |
| `d_over_b` | down | canceled | canceled | `OPEN_LOCALIZABLE` | no |

## Cross-Sector Diagnostics

The same-sector identity cancellation is not applicable to:

```text
tau_over_t
b_over_t
nu_over_l
```

## K_f-Aligned Candidate

A structural candidate is recorded:

```text
tilde_Gamma_f proportional_to K_f - (Tr K_f / 3) I_f
```

Its status is:

```text
Kf_aligned_residual_transport_candidate=STRUCTURALLY_MOTIVATED_CANDIDATE
Kf_residual_transport_coefficient=OPEN_LOCALIZABLE
```

No numerical predictions are emitted from this candidate.

## Remaining Blockers

```text
charged_branch_differential_residual_transport=OPEN_LOCALIZABLE
Kf_residual_transport_coefficient=OPEN_LOCALIZABLE
scheme_alignment=OPEN
comparison_ready_predictions=OPEN
numerical_closure=OPEN
```

No observed masses, CKM data, PMNS data, neutrino data, measured alpha,
measured gauge couplings, measured Yukawa couplings, or empirical target ratios
are used.

Frozen predictions changed: no.

Official predictions changed: no.
