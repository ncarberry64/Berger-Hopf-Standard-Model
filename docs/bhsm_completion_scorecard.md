# BHSM Completion Scorecard

Status rows are candidate/audit classifications, not official release changes.

| Item | Status | Official/Candidate | Derived Status | Audit Result | Failure Risk | Next Action |
| --- | --- | --- | --- | --- | --- | --- |
| release integrity | `CLEAN_SURVIVAL` | official | `verified by tests` | frozen branches preserved | low | keep freeze guards active |
| c/t mass dressing | `CAVEATED_SURVIVAL` | official candidate | `STRUCTURALLY_MOTIVATED_NOT_DERIVED` | Z=1/2 preserved; no residual fit performed here | derivation gap | derive half-projection rule |
| CKM 2-3 mixing dressing | `CANDIDATE_SURVIVAL` | candidate | `OPEN_DERIVATION_REQUIRED` | Z^(1/16) improves Vcb/Vts with no damage flags | candidate exponent not derived | derive or reject 1/16 |
| full CKM matrix | `CANDIDATE_SURVIVAL` | candidate | `OPEN_DERIVATION_REQUIRED` | matrix reconstructed and residuals reported | future input drift | freeze rule before future comparisons |
| charged leptons | `OPEN_DERIVATION_REQUIRED` | candidate | `ETA_L_STRUCTURALLY_MOTIVATED_NOT_DERIVED` | one-parameter mode rule improves both rows but eta_l is not derived | candidate remains non-official | derive eta_l and charged-lepton scope independently |
| quark RG/common-scale | `OPEN_DERIVATION_REQUIRED` | audit | `EXTERNAL_INPUT_REQUIRED` | mixed-scale screens not precision verdicts | scheme dependence | supply validated common-scale inputs |
| gauge couplings | `CAVEATED_SURVIVAL` | audit | `GAUGE_COARSE_SURVIVAL` | matching convention recorded; no retuning | precision convention/scale | complete threshold/RG convention audit |
| boundary operators | `OPEN_DERIVATION_REQUIRED` | audit | `ACTION_LINKED` | operators recover ledger but full action derivation remains | action-origin gap | derive boundary functional from full action |
| scalar/Higgs/gap | `CAVEATED_SURVIVAL` | audit | `STRONG_PROXY_SURVIVAL` | no dangerous light scalar in scaffold audit | full spectrum open | complete spectral proof inputs |
| claim discipline | `CLEAN_SURVIVAL` | official guardrail | `verified by tests` | candidate package denies confirmation/replacement claims | low | keep candidate labels visible |

BHSM is not confirmed. This scorecard is a falsification and completion-candidate target.

## v7.2 finite official benchmark manifest

This table supersedes the historical candidate scorecard only for the live
v7.2 completion gate. It contains no comparison values.

| ID | Item | Classification |
| --- | --- | --- |
| `B72-01` | stratified-action covariance | structural identity |
| `B72-02` | representation and anomaly identities | structural identity |
| `B72-03` | common-scheme gauge identities | structural identity |
| `B72-04` | electroweak mass relations | input-dependent calculation |
| `B72-05` | CKM construction from Yukawa inputs | input-dependent calculation |
| `B72-06` | charged-lepton running-mass example | input-dependent calculation |
| `B72-07` | quark running-mass example | input-dependent calculation |
| `B72-08` | fixed-h D0 result | structural identity |
| `B72-09` | parameterized scalar quartic | parameterized relation |
| `B72-10` | universal calibration consistency | calibration check |

No row is classified as a distinct action-derived physical prediction.

## v7.3 prediction-route result

| Route | Result |
| --- | --- |
| Exact twisted Dirac, kernel, and gap | `BLOCKED_BY_EXACT_MISSING_OBJECT` |
| Full scalar/topographic Hessian | `BLOCKED_BY_EXACT_MISSING_OBJECT` |
| Internal-geometry selection | `BLOCKED_BY_EXACT_MISSING_OBJECT` |
| Mode and generation selection | `PHYSICAL_BUT_INPUT_TAUTOLOGY` |
| Input-cancelling sum rules | `STRUCTURAL_BUT_NOT_PHYSICAL` |
| Fixed-h physical consequence | `STRUCTURAL_BUT_NOT_PHYSICAL` |

The exact common obstruction is
`NONUNIVERSAL_BHSM_TO_LOCALIZED_PHYSICAL_SECTOR_ACTION_COUPLING`.
