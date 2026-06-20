# Full Threshold Operator Eligibility Kernel v1

Current public status: structural architecture integrated conditional;
numerical closure open.

This sprint formalizes when a charged ledger slot is eligible for a
threshold/virtual-door dressing. It does not add new threshold factors.

## Eligibility Rule

A threshold factor is allowed only when the action/projector layer supplies a
virtual-door subspace and a projector on that subspace:

```text
D_fi = rank(P_fi|V_fi)/dim(V_fi)
K_f -> K_f + [-ln(D_fi)] |i_f><i_f|
```

```text
threshold_rank_projection_rule=DERIVED_CONDITIONAL_ON_VIRTUAL_DOOR_PROJECTOR_DATA
```

## Known Derived Conditional Case

The known threshold remains exactly:

```text
sector=up
mode=(6,0)
slot=1
Z_virt^{u,2}=1/2
operator insertion=ln 2
up_6_0_Zvirt_threshold=DERIVED_CONDITIONAL
```

This is the weak-double projection bridge. It is inserted at operator level as
`K_u -> K_u + (ln 2)|1_u><1_u|`.

## Charged Slot Scan

| sector | slot | mode | status | insertion |
| --- | ---: | --- | --- | --- |
| lepton | 0 | `(0,0)` | `REFERENCE_SLOT_NOT_THRESHOLD_TARGET` | none |
| lepton | 1 | `(1,2)` | `NO_THRESHOLD_SOURCE_FOUND` | none |
| lepton | 2 | `(3,3)` | `NO_THRESHOLD_SOURCE_FOUND` | none |
| up | 0 | `(0,0)` | `REFERENCE_SLOT_NOT_THRESHOLD_TARGET` | none |
| up | 1 | `(6,0)` | `DERIVED_CONDITIONAL` | `ln 2` |
| up | 2 | `(8,1)` | `NO_THRESHOLD_SOURCE_FOUND` | none |
| down | 0 | `(0,0)` | `REFERENCE_SLOT_NOT_THRESHOLD_TARGET` | none |
| down | 1 | `(0,3)` | `NO_THRESHOLD_SOURCE_FOUND` | none |
| down | 2 | `(4,2)` | `NO_THRESHOLD_SOURCE_FOUND` | none |

## Generator Threshold Rules

```text
THRESHOLD_RULE_NONE: no insertions
THRESHOLD_RULE_DERIVED_ONLY: insert only up (6,0) ln 2
THRESHOLD_RULE_SYMBOLIC_OPEN: eligibility table present, open slots symbolic
```

The default diagnostic threshold rule remains `THRESHOLD_RULE_DERIVED_ONLY`.

## Verdict

```text
full_threshold_operator_eligibility_v1=COMPLETED_ELIGIBILITY_AUDIT
full_threshold_operator=OPEN
numerical_closure=OPEN
```

No observed masses, CKM, PMNS, neutrino data, measured fine-structure alpha, or
empirical target ratios are used. Do not invent threshold dressings for open
slots without an explicit virtual-door/projector source.

Frozen predictions changed: no.

Official predictions changed: no.
