# PO-BH-64 - Finite Sector Projector Ledger Theorem

Current public status: structural architecture integrated conditional; numerical closure open.

## Scope

This document records a conservative finite-sector projector compression of
the BHSM charged and neutral sector ledger. It is a structural theorem/audit
layer. It asserts no proof/completion/replacement status and no empirical
validation or numerical closure.

## Sector Labels

```text
C in {0,1}
sigma in {-1,+1}
```

Interpretation:

```text
C = 0 leptonic channel
C = 1 colored/quark channel
sigma = +1 upper weak partner
sigma = -1 lower weak partner
```

## Sector Projectors

```text
P_nu = (1-C)(1+sigma)/2
P_l  = (1-C)(1-sigma)/2
P_u  = C(1+sigma)/2
P_d  = C(1-sigma)/2
```

Down-sector incidence:

```text
P_d = C(1-sigma)/2
M(C,sigma) = 1 + P_d
```

Status:

```text
down_extra_boundary_incidence: STRONGLY_SUPPORTED_CANDIDATE
```

Remaining proof obligation: derive the extra incidence from the boundary
action/projector algebra.

## Unified Sector Operator Candidate

```text
Omega(C,sigma) =
(2C - 1) q - 2 sigma [1 + C(1-sigma)/2] j
```

This reproduces:

```text
Omega_l  = -q + 2j
Omega_nu = -q - 2j
Omega_u  =  q - 2j
Omega_d  =  q + 4j
```

Status:

```text
unified_Omega_projector_formula: STRUCTURALLY_MOTIVATED_DERIVATION_CANDIDATE
```

This is not marked fully action-derived.

## Target Amplitude Candidate

```text
A(C,sigma) = 3 * 2^C * [1 + C(1-sigma)/2]
```

This reproduces:

```text
neutrino target amplitude = 3
charged lepton target amplitude = 3
up target amplitude = 6
down target amplitude = 12
```

Statuses:

```text
base_cyclic_factor_3: STRUCTURALLY_MOTIVATED_DERIVATION_CANDIDATE
color_factor_2_power_C: STRUCTURALLY_MOTIVATED_CANDIDATE
down_multiplicity_M: STRUCTURALLY_MOTIVATED_DERIVATION_CANDIDATE
sector_target_amplitude_A: STRUCTURALLY_MOTIVATED_CANDIDATE
```

The target formula is useful, but it is not claimed as fully derived from the
action.

## Three-State Ladder

Internal rule:

```text
finite boundary closure sector ladder =
reference mode + two excitation slots
```

Each sector ledger has one base/reference slot plus two nonzero excitation
slots. This is not justified by saying nature has three generations.

Status:

```text
three_state_ladder_structure: STRONGLY_SUPPORTED_CANDIDATE
```

Remaining proof obligation: derive rank-three closure from finite boundary
algebra/action.

## Guardrails

Do not use observed masses, CKM values, PMNS values, neutrino data, measured
generation counts, anomaly/FTL data, propulsion/anomaly data, or target values
to choose any open structure.

No frozen prediction or official prediction is changed.
