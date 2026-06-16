# BHSM Boundary Axiom Ledger

| code | name | status | role | what would discharge it | downstream dependencies |
| --- | --- | --- | --- | --- | --- |
| AX-BH-1 | Berger-Hopf boundary geometry | STRUCTURAL_CANDIDATE | Defines the geometric arena for the boundary theorem program. | Construct the boundary state space from a geometric Berger-Hopf action. | THM-BH-1, THM-BH-5 |
| AX-BH-2 | Hopf fiber phase closure | DIAGNOSTIC_SUPPORTED | Sources the phase closure functional and local stiffness. | Derive global single-valuedness from admissible boundary sections. | THM-BH-1 |
| AX-BH-3 | Boundary orientation involution | DIAGNOSTIC_SUPPORTED | Sources the orientation pair and candidate weak-interface grading. | Derive the involution from Berger-Hopf boundary geometry. | THM-BH-2, THM-BH-6 |
| AX-BH-4 | Cyclic channel closure | DIAGNOSTIC_SUPPORTED | Sources the cyclic channel branch. | Derive order 3 from boundary automorphism, phase closure, or stability. | THM-BH-3, THM-BH-6 |
| AX-BH-5 | Fourth-order topographic stability | PARTIALLY_DERIVED | Provides the branch-count and stability scaffold. | Derive the operator from the underlying geometric variational principle. | THM-BH-4, THM-BH-5 |
| AX-BH-6 | Excess-sector gap | DIAGNOSTIC_SUPPORTED | Separates low-energy branches from excess sectors. | Derive the excess gap from the full Hessian spectrum. | THM-BH-4, THM-BH-6 |
| AX-BH-7 | Finite-algebra bridge | DERIVED_CONDITIONAL | Links closure dimensions to finite algebra blocks. | Prove the physical boundary channel space equals the closure space V_d. | THM-BH-7 |
| AX-BH-8 | Charge bridge | DIAGNOSTIC_SUPPORTED | Links projector algebra to charge operators. | Derive C, ell, sigma, w from boundary geometry without importing SM labels. | THM-BH-8 |
| AX-BH-9 | Anomaly bridge | DIAGNOSTIC_SUPPORTED | Checks downstream consistency of the charge skeleton. | Derive anomaly cancellation from global boundary consistency. | THM-BH-8 |
