# Charged Kf Rule-A Suppression Propagation v1

Current public status: structural architecture integrated conditional;
numerical closure open.

This sprint propagates the direct charged suppression operator rule into named
charged `K_f` diagnostic branches. It does not change frozen or official
predictions and does not compare to observed masses, CKM, PMNS, neutrino data,
measured fine-structure alpha, or empirical target ratios.

## Named Suppression Rules

Rule A is the direct single-operator trace contraction from the
trace-normalized charged suppression kernel:

```text
RULE_A_SINGLE_OPERATOR_TRACE=DERIVED_CONDITIONAL_ON_B_SUPP_TRACE_KERNEL
eta_f = Tr(P_f B_supp) S_f
eta_l=20/147
eta_u=38/147
eta_d=68/147
```

Rule B remains the older double-normalized candidate:

```text
RULE_B_DOUBLE_NORMALIZED_PHASE_CANDIDATE=CANDIDATE_REQUIRES_INDEPENDENT_PHASE_RESPONSE
eta_f = Tr(P_f B_supp) g_ch S_f
eta_l=20/3087
eta_u=38/3087
eta_d=68/3087
```

The independent phase-response source remains:

```text
independent_phase_response_source=OPEN_LOCALIZABLE
```

## Kf Propagation

The diagnostic Rule A branch uses

```text
lambda_i,f = eta_f N_i,f
```

with the charged costs:

```text
N_l1=1+4 rho_ch
N_l2=9+9 rho_ch
N_u1=36
N_u2=64+rho_ch
N_d1=9 rho_ch
N_d2=16+4 rho_ch
```

The bridge layer is not rederived here:

```text
beta_f = g_bridge Pi_f
kappa_f = g_bridge / ||v_f||^2_ch
```

`beta_f` and `kappa_f` remain the existing bridge ansatz layer. Rule A changes
only suppression diagonals in the named diagnostic branch.

## Threshold Handling

The existing operator-level threshold insertion is preserved:

```text
K_u -> K_u + (ln 2)|1_u><1_u|
```

It is applied only to the up-sector `(6,0)` slot. No other threshold dressings
are added.

## Spectral Sanity Artifact

The machine-readable report
`data/charged_kf_rule_a_spectral_sanity_v1.json` includes, for every charged
sector and `rho_ch in {1,2,3}`:

- diagonal entries;
- `beta_f`;
- `kappa_f`;
- eigenvalue gaps;
- `exp[-gap]` spectral factors;
- Rule A up-sector rows with the operator-level `ln 2` insertion;
- branch-ordering notes.

No empirical comparison is performed.

## Status Summary

```text
charged_Kf_rule_A_suppression_propagation=DERIVED_CONDITIONAL_ON_B_SUPP_TRACE_KERNEL
RULE_A_SINGLE_OPERATOR_TRACE=DERIVED_CONDITIONAL_ON_B_SUPP_TRACE_KERNEL
RULE_B_DOUBLE_NORMALIZED_PHASE_CANDIDATE=CANDIDATE_REQUIRES_INDEPENDENT_PHASE_RESPONSE
minimal_charged_Kf_generator_eta_rule_A=DERIVED_CONDITIONAL_DIAGNOSTIC_BRANCH
minimal_charged_Kf_generator_eta_rule_B=LEGACY_CANDIDATE_BRANCH
independent_phase_response_source=OPEN_LOCALIZABLE
numerical_closure=OPEN
```

## Remaining Open Items

- decide whether future charged `K_f` work should adopt Rule A, Rule B, or
  another action-derived suppression rule;
- derive or reject the independent phase-response source;
- derive exact `rho_ch`;
- derive the full threshold operator;
- derive RG/scheme transport;
- keep numerical closure open until all symbolic inputs are locked before
  comparison.

Frozen predictions changed: no.

Official predictions changed: no.
