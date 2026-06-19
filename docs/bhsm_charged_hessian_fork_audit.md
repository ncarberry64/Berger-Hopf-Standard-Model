# PO-BH-64 - Charged Hessian Fork Audit

Current public status: structural architecture integrated conditional; numerical closure open.

## Scope

This audit separates charged-sector Hessian logic from neutral/topographic
metric mixing. It does not solve mass ratios and does not choose a Hessian
metric by fitting.

## Charged/Neutral Split

Charged sectors:

```text
q and j remain separate.
No charged-sector qj cross-term unless explicitly derived.
```

Neutral/topographic sectors:

```text
q and j mixing may be allowed.
Neutral/topographic metric mixing remains separate from charged-sector Hessian logic.
```

Statuses:

```text
charged_cross_term_s_ch: FORBIDDEN_CONDITIONAL
neutral_cross_term_s_neutral: OPEN_ALLOWED
neutral_topographic_metric_mixing: OPEN_LOCALIZABLE
```

Do not let neutral/topographic Berger anisotropy leak into charged-sector
ledgers unless explicitly derived.

## General Charged Diagonal Anisotropy Family

The exact cost `q^2+j^2` is not forced by the ledgers.

General charged family:

```text
N_ch(q,j) = q^2 + rho_ch j^2
rho_ch > 0
```

For preserving down-sector ordering where `(0,3)` is lower than `(4,2)`:

```text
0 < rho_ch < 16/5
```

If only membership is required:

```text
0 < rho_ch < 8
```

Ledger membership is robust; exact cost numbers require a metric choice.

## Isotropic Candidate

```text
rho_ch = 1
N_iso(q,j)=q^2+j^2
```

Costs:

```text
lepton: 0,5,18
up: 0,36,65
down: 0,9,20
```

Status:

```text
isotropic_metric_rho_1: MINIMAL_ISOTROPIC_CANDIDATE
exact_old_costs_0_5_18_etc: CONDITIONAL_ON_RHO_CH_EQUALS_1
```

## Cyclic-Anisotropy Candidate

```text
rho_ch = 3
N_cyclic(q,j)=q^2+3j^2
```

Costs:

```text
lepton: 0,13,36
up: 0,36,67
down: 0,27,28
```

Status:

```text
cyclic_anisotropy_rho_3: CYCLIC_ANISOTROPY_CANDIDATE
cyclic_candidate_costs_0_13_36_etc: CONDITIONAL_ON_RHO_CH_EQUALS_3
```

## Open Metric Choice

```text
charged_Hessian_anisotropy_rho_ch: OPEN_LOCALIZABLE
```

The action must decide whether `rho_ch=1`, `rho_ch=3`, or another value is
derived. Do not choose `rho_ch` by fitting masses, CKM, PMNS, neutrino data,
or observed generation data.
