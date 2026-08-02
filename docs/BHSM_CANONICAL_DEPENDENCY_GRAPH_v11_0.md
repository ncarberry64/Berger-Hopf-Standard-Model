# BHSM v11.0 Canonical Dependency Graph

The machine-readable graph is
`artifacts/BHSM_canonical_dependency_graph_v11_0.json`. Its declared order is
acyclic and has one highest-upstream open object.

| ID | Object | Depends on | Status |
| --- | --- | --- | --- |
| D00 | Canonical ontology registry | - | `CLOSED` |
| D01 | Multiplicative-support Haar kinematics | D00 | `CLOSED` |
| D02 | Support representation functor with fixed Haar scale | D01 | `OPEN_HIGHEST_UPSTREAM` |
| D03 | Complete supported parent action and restoring response | D02 | `BLOCKED` |
| D04 | Core phase space and transfer operator at `q_D=infinity` | D03 | `BLOCKED` |
| D05 | Common S8/S5/S4 reduction and three-mode Hessian | D03, D04 | `BLOCKED` |
| D06 | Buoyancy, Higgs, charge, and weak-field derivations | D05 | `BLOCKED` |
| D07 | Stable particle cycles and physical Floquet spectra | D05, D06 | `BLOCKED` |
| D08 | Order-three monodromies and frozen-slot intertwiners | D07 | `BLOCKED` |
| D09 | Unique global geometry and curvature-radius anchor | D03, D05 | `BLOCKED` |
| D10 | Physical masses, CKM/PMNS, and core transitions | D07-D09 | `BLOCKED` |
| D11 | Normalized effective M4 Standard Model | D06, D10 | `BLOCKED` |
| D12 | Quantum measurement, probability, and no-signalling | D04, D07, D11 | `BLOCKED` |
| D13 | Empirical replacement | D11, D12 | `NOT_ELIGIBLE_FROM_REPOSITORY_WORK` |

The exact D02 object is
`ACTION_DERIVED_SUPPORT_REPRESENTATION_FUNCTOR_ON_STRATIFIED_SECTORS_WITH_FIXED_HAAR_SCALE`.
Downstream calculation is fail-closed until its dependencies close.
