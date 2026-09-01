# Reviewer Attack Guide: How to Break BHSM

This guide is for technical reviewers who want direct pressure points.

## 1. Check Frozen Outputs

Inspect:

- `theory/bhsm_v1_frozen_prediction_set.md`
- `theory/bhsm_prediction_ledger.md`
- `tests/test_final_release_package.py`

Break condition: frozen values drift, or the dressed branch changes anything
other than `c/t`.

## 2. Check Complete Operator Identification

Inspect:

- `theory/full_bhsm_theorem_completion_report.md`
- relevant complete-operator modules under `src/`

Break condition: the final operator is not the operator used in the theorem
chain, or the coordinate-first kernel sneaks back into the final status.

## 3. Check Action Uniqueness

Inspect:

- `theory/bhsm_theorem_completion_decision.md`
- action-origin and uniqueness reports under `theory/`

Break condition: another admissible action scaffold produces the same ledger
without being excluded by the current axioms.

## 4. Check Projector Commutator Control

Inspect projector commutator reports and guard tests.

Break condition: `[P_perp,V]` is not controlled on the required domain, or a
conditional commutator node is still used to claim theorem completion.

## 5. Check Projector Graph-Domain Stability

Inspect projector graph-domain reports and tests.

Break condition: the projector does not preserve the complete graph domain, or
the proof silently relies on a finite coordinate-only shortcut.

## 6. Check H_T Lower-Bound Transfer

Inspect:

- `theory/full_bhsm_theorem_completion_report.md`
- H_T lower-bound transfer modules and tests.

Break condition: the lower-bound transfer depends on an open or conditional
node, or fails to exclude protected zero modes correctly.

## 7. Check Index Theorem

Inspect index theorem hardening reports and tests.

Break condition: `dim ker D_twist = 3` fails, or the protected states are not
exactly one each in lepton, up, and down.

## 8. Check Mirror Exclusion

Inspect mirror exclusion reports and tests.

Break condition: any coordinate-first kernel, chirality-flipped partner,
Higgs-U1 mirror channel, boundary mirror channel, or topographic/mixed-sector
mirror channel remains protected.

## 9. Check Hidden Empirical Fitting

Search for prediction-ledger, residual-audit, CKM, PMNS, or empirical mass
machinery imported into theorem closure modules.

Break condition: theorem closure uses empirical residuals or fit data.

## 10. Check QCD/RG Precision Limitations

Inspect:

- `theory/qcd_precision_closure_report.md`
- `theory/quark_ratio_precision_comparison.md`

Break condition: precision QCD/RG matching is claimed complete without
validated precision inputs and uncertainty propagation.

## 11. Check Claim Boundaries

Break condition: the repository claims experimental confirmation, accepted
replacement of the Standard Model, QCD confinement, new particle discovery, or
guaranteed correctness.
