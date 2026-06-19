# Charged Suppression Operator Kernel v1

Current public status: structural architecture integrated conditional; numerical
closure open.

This sprint addresses the charged suppression normalization ambiguity left by
the charged `K_f` and boundary-action-source audits. It does not add official
predictions, does not change frozen outputs, and does not use empirical
comparison data.

## Why This Exists

The prior charged suppression package used

```text
eta_f = Pi_f g_ch S_f
```

with

```text
R_ch=21
g_ch=1/21
Pi_l=1/7, Pi_u=2/7, Pi_d=4/7
S_l=20/21, S_u=19/21, S_d=17/21
```

That gives the older candidate package:

```text
eta_l=20/3087, eta_u=38/3087, eta_d=68/3087
```

The possible issue is double normalization. If `B_supp` is already a
trace-normalized charged suppression operator, then `Tr(P_f B_supp)` already
contains the active `1/R_ch` normalization.

## Trace-Normalized Kernel

The total charged incidence module is

```text
E_ch = E_A,l direct_sum E_A,u direct_sum E_A,d
```

with ranks

```text
rank(E_A,l)=3
rank(E_A,u)=6
rank(E_A,d)=12
R_ch=3+6+12=21
```

The minimal symmetry/trace-normalized suppression kernel is

```text
B_supp=I_ch/21
```

so

```text
Tr(B_supp)=1
```

and each charged incidence state has diagonal primitive weight `1/21`.

The sector projections give

```text
Tr(P_l B_supp)=3/21=1/7
Tr(P_u B_supp)=6/21=2/7
Tr(P_d B_supp)=12/21=4/7
```

## Self-Screening

The incidence self-screening counts are retained as

```text
chi_l=1
chi_u=2
chi_d=4
```

Under the single trace-normalized operator, the effective primitive response is
the diagonal weight `1/21`, giving

```text
S_l=1-1/21=20/21
S_u=1-2/21=19/21
S_d=1-4/21=17/21
```

## Contraction Rules

### Rule A: Single-Operator Trace Contraction

```text
eta_f = Tr(P_f B_supp) S_f
```

This is the rule directly derived by the implemented trace-normalized
`B_supp=I_ch/21` kernel. It gives

```text
eta_l=20/147
eta_u=38/147
eta_d=68/147
```

Status:

```text
charged_suppression_single_operator_trace_rule=DERIVED_CONDITIONAL_ON_B_SUPP_KERNEL
```

### Rule B: Double-Normalized Independent Phase Coupling

```text
eta_f = Tr(P_f B_supp) g_ch S_f
```

This reproduces the older package

```text
eta_l=20/3087
eta_u=38/3087
eta_d=68/3087
```

but requires an additional independent phase-response coupling before it can be
promoted.

Status:

```text
charged_suppression_double_normalized_rule=STRONGLY_SUPPORTED_CANDIDATE_REQUIRES_INDEPENDENT_PHASE_COUPLING
g_ch_independent_phase_response=OPEN_LOCALIZABLE
```

### Rule C: Local-Sector Normalization

```text
eta_f = g_ch S_f
```

This local-sector route is structurally possible but not selected by the global
trace-normalized charged incidence kernel.

## Correction

The older eta_f={20,38,68}/3087 package is the double-normalized candidate.
The single-operator trace contraction gives eta_f={20,38,68}/147 and is the
rule directly derived by a trace-normalized B_supp kernel. The
double-normalized rule requires an additional independent phase-response
coupling before it can be promoted.

## Status Summary

```text
B_supp_universal_suppression_operator=DERIVED_CONDITIONAL_ON_TRACE_NORMALIZED_KERNEL
B_supp_trace_normalization=DERIVED_CONDITIONAL_ON_TRACE_NORMALIZED_KERNEL
Pi_f_incidence_projection_fractions=DERIVED_CONDITIONAL_FROM_B_SUPP_TRACE
chi_f_incidence_self_screening_counts=DERIVED_CONDITIONAL_ON_INCIDENCE_KERNEL
charged_suppression_single_operator_trace_rule=DERIVED_CONDITIONAL_ON_B_SUPP_KERNEL
charged_suppression_double_normalized_rule=STRONGLY_SUPPORTED_CANDIDATE_REQUIRES_INDEPENDENT_PHASE_COUPLING
charged_suppression_local_sector_rule=STRUCTURALLY_POSSIBLE_NOT_SELECTED
g_ch_independent_phase_response=OPEN_LOCALIZABLE
charged_suppression_eta_values=RULE_A_DERIVED_CONDITIONAL_RULE_B_CANDIDATE
minimal_charged_Kf_generator_eta_dependency=NOT_OVERWRITTEN_REQUIRES_EXPLICIT_RULE_SELECTION
numerical_closure=OPEN
```

## What Remains Open

- derive or reject an independent primitive phase-response operator;
- decide whether the charged `K_f` generator should later use Rule A, Rule B,
  or another action-derived rule;
- derive exact `rho_ch`;
- derive the full threshold operator;
- derive RG/scheme transport;
- close numerical predictions only after all symbolic inputs are locked before
  comparison.

No observed charged-lepton masses, observed quark masses, CKM values, PMNS
values, neutrino data, measured fine-structure alpha, empirical target ratios,
or post-comparison branch selection are used.

Frozen predictions changed: no.

Official predictions changed: no.
