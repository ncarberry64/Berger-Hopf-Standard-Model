# Closure Spectrum Selection Rule Audit

## 1. Motivation

The admissible closure-spectrum gate documented `D_adm = {1,2,3}` as a diagnostic bridge. This audit tests candidate selection principles that support those dimensions as the minimal low-energy fundamental boundary spectrum.

## 2. Previous Gate Achieved: Diagnostic `D_adm={1,2,3}`

```text
D_adm = {1,2,3}
End(C^1)=C
End(C^2)=M2(C)
End(C^3)=M3(C)
```

## 3. Why A Real Selection Rule Is Needed

The diagnostic spectrum must eventually be derived from boundary action, admissible phase closure, and the full stability/Hessian problem. This audit does not close that proof obligation.

## 4. Candidate Selection Principles

- identity/reference closure selects `d=1`;
- orientation-pair closure selects `d=2`;
- minimal cyclic channel closure selects `d=3`;
- reducible higher closures are screened as composite or higher excitations;
- fourth-order branch count supports reference plus two nonzero branches;
- anomaly-compatible minimality requires the `1,2,3` ingredients.

## 5. Irreducibility And Reducibility Screen

Dimensions above `3` are not selected as low-energy primitive closures unless an independent action term requires them. Composite/reducible closures are interpreted as higher organization rather than fundamental low-energy sectors.

## 6. Fourth-Order Topographic Branch Screen

```text
L_T = nabla^2 - B*nabla^4
```

Candidate interpretation: zero/reference closure plus two stable nonzero branches.

## 7. Anomaly-Compatible Minimality Screen

The current charge/anomaly bridge requires a single-channel closure, a weak orientation pair, and a three-channel active closure. The smallest closure dimensions supplying those ingredients are `1`, `2`, and `3`.

## 8. Small-Dimension Audit `(d=1..8)`

| d | primitive status | reducibility status | topographic status | anomaly minimality status | selected | notes |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | primitive reference/single closure | irreducible_under_current_screen | reference | minimal_leptonic_single_channel_ingredient | true | identity/reference closure |
| 2 | primitive orientation-pair closure | irreducible_under_current_screen | stable_nonzero_orientation_candidate | minimal_weak_orientation_pair_ingredient | true | minimal Z2 orientation-pair closure |
| 3 | primitive cyclic three-channel closure | irreducible_under_current_screen | stable_nonzero_channel_candidate | minimal_three_channel_charge_anomaly_ingredient | true | minimal nontrivial cyclic channel closure beyond orientation pairing |
| 4 | composite/product-like closure | composite/reducible under current primitive set | higher_or_composite_unsupported | composite_not_needed_for_minimal_charge_anomaly_bridge | false | screened as composite or higher excitation candidate |
| 5 | higher prime unsupported | not reducible but unsupported by current low-energy minimality screens | higher_or_composite_unsupported | higher_prime_unsupported_by_current_charge_anomaly_minimality | false | unsupported, not impossible |
| 6 | composite/product-like closure | composite/reducible under current primitive set | higher_or_composite_unsupported | composite_not_needed_for_minimal_charge_anomaly_bridge | false | screened as composite or higher excitation candidate |
| 7 | higher prime unsupported | not reducible but unsupported by current low-energy minimality screens | higher_or_composite_unsupported | higher_prime_unsupported_by_current_charge_anomaly_minimality | false | unsupported, not impossible |
| 8 | composite/product-like closure | composite/reducible under current primitive set | higher_or_composite_unsupported | composite_not_needed_for_minimal_charge_anomaly_bridge | false | screened as composite or higher excitation candidate |

## 9. Candidate Result

```text
selected_low_energy_spectrum = [1, 2, 3]
```

The audit supports {1,2,3} as the minimal diagnostic closure spectrum compatible with the current BHSM charge/anomaly bridge, boundary-orientation structure, and fourth-order branch-count interpretation. It does not uniquely prove that no higher fundamental closures exist in the full Berger-Hopf theory.

## 10. Negative Result / Limitation

Higher prime closures such as `d=5` and `d=7` are unsupported by the current low-energy minimality screens, not mathematically impossible. Unique first-principles closure derivation remains open.

## 11. What This Achieves

This audit strengthens the candidate case for `(1, 2, 3)` as the minimal diagnostic low-energy closure spectrum.

Claim labels:

- `CLOSURE_SPECTRUM_SELECTION_RULE_AUDIT_CANDIDATE`
- `MINIMAL_CLOSURE_SPECTRUM_123_SUPPORTED_DIAGNOSTIC`
- `IRREDUCIBLE_CLOSURE_SCREEN_CANDIDATE`
- `TOPOGRAPHIC_BRANCH_SCREEN_CANDIDATE`
- `ANOMALY_MINIMALITY_SCREEN_CANDIDATE`
- `HIGHER_CLOSURES_COMPOSITE_OR_UNSUPPORTED_DIAGNOSTIC`
- `UNIQUE_FIRST_PRINCIPLES_CLOSURE_DERIVATION_REMAINS_OPEN`
- `FULL_HESSIAN_PROOF_REMAINS_OPEN`
- `FULL_SM_DERIVATION_NOT_CLAIMED`

## 12. What This Does Not Prove

This audit does not fully derive the Standard Model. It tests candidate selection principles that support the minimal closure spectrum {1,2,3} as the low-energy fundamental boundary spectrum. The result remains candidate-only unless the selection conditions are derived directly from the Berger-Hopf boundary action and the full topographic Hessian problem.

It does not claim BHSM has replaced the Standard Model. It does not claim the full gauge group is derived. It does not claim the closure spectrum is uniquely derived from first principles.

## 13. Next Proof Obligations

- derive the reference, orientation, and cyclic channel rules from the Berger-Hopf boundary action;
- derive the reducibility screen from admissible closure composition;
- derive the topographic branch screen from the full Hessian;
- prove or reject whether higher prime closures are excluded, excited, or physically irrelevant.

## Related Action/Hessian Scaffold

- [Boundary action Hessian scaffold gate](boundary_action_hessian_scaffold_gate.md)
- [Boundary action term realization audit](boundary_action_term_realization_audit.md)
