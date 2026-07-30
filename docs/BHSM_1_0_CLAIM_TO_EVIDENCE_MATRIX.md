# BHSM 1.0 claim-to-evidence matrix

The authoritative row-level matrix is
`artifacts/BHSM_1_0_claim_to_evidence_matrix_v6_30_8.json`. It records, for
every retained public or internal claim, its location, class, action and
domain provenance, independent inputs, derived coefficients, comparison
data, frozen artifact, benchmark, falsifier, \(\lambda_5\) dependency,
evidence, status, blockers, and caveat.

| Claim group | Status | Principal evidence | Principal blocker |
| --- | --- | --- | --- |
| Conditional framework status | retained | `docs/current_bhsm_status.md` | RB-01/RB-03 |
| Deterministic engine and tests | retained | `tests/`, `docs/reproducibility.md` | none |
| Frozen no-retuning screens | retained as screens | `theory/bhsm_v1_frozen_prediction_set.json` | RB-14 |
| Fixed-h D0 reduction | retained mathematical result | `artifacts/BHSM_fixed_h_canonical_interaction_v6_30_5.json` | none |
| Scalar quartic | retained parameterized result | `artifacts/BHSM_G5_action_source_ledger_v6_30_7.json` | parameter-free extension only |
| Local scalar stability | retained conditional inequality | `artifacts/BHSM_fixed_h_local_stability_v6_30_5.json` | parameter-free extension only |
| Charged flavor screens | conditional | `src/yukawa_overlap.py` | RB-03/RB-04/RB-05 |
| CKM screens | conditional | `src/ckm.py`, `src/flavor_matrix.py` | RB-06 |
| PMNS extension | candidate/effective | `src/pmns.py` | RB-07 |
| Gauge screens | conditional | `src/gauge_couplings.py` | RB-01/RB-08 |
| Higgs/scale screen | conditional, unlicensed scale | `src/higgs_scale.py` | RB-09/RB-12/RB-13 |
| Proxy gap and scalar scaffold | retired as theorem data | `artifacts/BHSM_distinct_action_derived_prediction_v7_3.json` | exact non-universal physical-sector coupling absent |
| Running masses and mixings | finite-input map complete | `artifacts/BHSM_common_scheme_observable_transport_v7_2.json` | pole conversion and empirical validation not inferred |
| Distinct physical prediction routes | exhausted; exact object blocked | `artifacts/BHSM_distinct_action_derived_prediction_v7_3.json` | RB-15 |
| Repository readiness | retained repository status only | `docs/github_landing_status.md` | RB-16 |

No retained claim depends on an unrecorded evidence row. The table is a
human-readable index; the deterministic JSON is canonical.
