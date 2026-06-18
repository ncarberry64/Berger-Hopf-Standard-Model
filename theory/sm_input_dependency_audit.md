# SM Input Dependency Audit

| object | formula_or_usage | uses_sm_input | input_type | bhsm_status | replacement_needed_for_full_derivation | candidate_bhsm_primitive | risk_if_unreplaced |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B | O_q = 3B - L and target degree law | True | SM representation label | preserved_as_input | derive B as topological sector counter | B-L/topological sector count | boundary operators remain downstream of SM labels |
| L | O_q = 3B - L | True | SM representation label | preserved_as_input | derive L as topological sector counter | B-L/topological sector count | lepton/quark split remains imported |
| T3 | O_j = -4T3 + 2(3B)(1/2 - T3) | True | weak-isospin input | preserved_as_input | derive T3 as boundary-interface eigenvalue | weak interface orientation | base coefficient remains SM-fed |
| Y | hypercharge and electric charge screens | True | SM charge assignment | preserved_as_input | derive admissible U(1) boundary phase closure | boundary phase closure | hypercharge remains imported |
| Q | Q = T3 + Y/2 | True | SM charge relation | preserved_as_input | derive electric charge from boundary closure | boundary closure eigenvalue | electric charge remains downstream |
| SU(3)_c | local color gauge factor | True | local gauge input | preserved_as_input | derive color algebra from boundary automorphisms | three-channel internal degeneracy | local color remains input |
| SU(2)_L | local weak gauge factor | True | local gauge input | preserved_as_input | derive weak algebra from interface channels | two-state boundary orientation | weak layer remains input |
| U(1)_Y | hypercharge gauge factor | True | local gauge input | preserved_as_input | derive U(1) from boundary phase closure | admissible phase closure | trace/U(1) layer remains input |
| fermion chirality | chiral multiplet ledger | True | SM chiral structure | preserved_as_input | derive chirality from boundary orientation/asymmetry | boundary orientation | mirror exclusion remains conditional |
| left/right multiplets | field content ledger | True | SM multiplet input | preserved_as_input | derive L/R split from boundary domain | boundary domain asymmetry | field content remains imported |
| color triplet/singlet split | quark/lepton branch structure | True | SM representation input | preserved_as_input | derive from active three-channel degeneracy | color channel automorphism | sector split remains imported |
| weak doublet/singlet split | T3 and chirality use | True | SM representation input | preserved_as_input | derive from boundary interface orientation | two-state interface orientation | weak split remains imported |
| Higgs doublet | Yukawa and electroweak screens | True | SM scalar input | preserved_as_input | derive from boundary deformation mode | boundary deformation mode | scalar sector remains scaffolded |
| Yukawa coupling layer | mass hierarchy screens | True | SM free-parameter layer | failed_or_limited_candidate | derive collective threshold mass law | collective curvature fixed point | mass numerical closure remains open |
| CKM | mixing screens | True | SM empirical mixing structure | open_derivation_obligation | derive interface kernels | boundary interface kernel | mixing remains structural candidate |
| PMNS | effective neutrino extension | True | effective extension input/comparison | open_derivation_obligation | derive conjugate-cover kernels | boundary interface kernel | neutrino mixing remains candidate |
| anomaly cancellation | hypercharge consistency checks | True | SM consistency condition | preserved_as_input | derive from boundary closure consistency | global boundary closure | anomaly cancellation remains downstream |

## Conclusion

The strongest current BHSM layer is downstream of the preserved local SM representation data. Replacement by derivation requires moving B, L, T3, chirality, color, weak isospin, and hypercharge from inputs to outputs of the Berger-Hopf/topographic boundary system.
