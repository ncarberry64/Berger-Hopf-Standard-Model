# rho_ch Branch Pressure Test v1

Current public status: structural architecture integrated conditional;
numerical closure open.

This sprint pressure-tests the three no-fit charged stiffness branches under the
Rule A charged `K_f` diagnostic. It performs no empirical mass, CKM, PMNS,
neutrino, measured-alpha, or target-ratio comparison.

## Rule A Context

The diagnostic uses the direct trace-normalized charged suppression rule:

```text
RULE_A_SINGLE_OPERATOR_TRACE
eta_l=20/147
eta_u=38/147
eta_d=68/147
```

Rule B is not used as the default diagnostic branch in this sprint.

## Branches

```text
rho_ch=1: isotropic stiffness
rho_ch=2: weak-involution stiffness
rho_ch=3: rank-three closure stiffness
```

The exact value remains:

```text
rho_ch_exact_value=OPEN_LOCALIZABLE
```

## Internal Diagnostics

For each branch and charged sector, the report computes:

- Rule A spectral gaps;
- gap separation ratios;
- pair split;
- reference gap minimum;
- branch-order labels from the dominant eigenvector component;
- up-sector gaps with the existing operator-level `ln 2` insertion on `(6,0)`;
- whether the up threshold insertion causes branch reordering;
- down-sector pair-degeneracy measure.

The machine-readable report is
`data/rho_ch_branch_pressure_test_v1.json`.

## Classification

```text
rho_ch_1_isotropic_branch=BRANCH_CANDIDATE
rho_ch_2_weak_involution_branch=BRANCH_CANDIDATE
rho_ch_3_rank_three_branch=STRUCTURALLY_INTERESTING_BRANCH
down_near_degeneracy_rho_ch_3=STRUCTURALLY_INTERESTING_NOT_SELECTION_RULE
up_threshold_branch_reordering=DIAGNOSTIC_REPORTED_NO_EMPIRICAL_SELECTION
charged_Kf_Rule_A_spectral_sanity=INTERNALLY_STABLE_DIAGNOSTIC
numerical_closure=OPEN
```

The down-sector split is smallest at `rho_ch=3`, making it structurally
interesting. This is not a selection rule by itself.

The up `(6,0)` threshold insertion does not reorder the branches in this
diagnostic.

## Conclusion

All three `rho_ch` branches remain internally viable under the Rule A charged
`K_f` diagnostic. No branch is invalidated by internal spectral sanity, and no
winning branch is selected. The exact `rho_ch` value remains open-localizable
until an action-level selection theorem is supplied.

Frozen predictions changed: no.

Official predictions changed: no.
