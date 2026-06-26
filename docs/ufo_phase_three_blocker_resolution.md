# BHSM UFO Phase Three Blocker Resolution v0.3

Machine-readable readiness artifact:

```text
artifacts/BHSM_ufo_phase_three_readiness_v0_3.json
```

Phase Three-A resolves no production UFO gate. It makes the blockers more
specific.

Resolved at documentation/ledger level:

- candidate effective Lagrangian ledger exported;
- field-normalization ledger exported;
- vertex-normalization ledger exported;
- mass/width scheme status exported;
- renormalization scheme status exported;
- FeynRules translation gate exported.

Still blocked:

- complete 4D collider-ready Lagrangian;
- gauge fixing;
- canonical field normalization;
- vertex normalization;
- mass/width scheme;
- renormalization scheme;
- complete production vertex table;
- production parameter card;
- loadable UFO model;
- MadGraph validation;
- LHE/HepMC generation;
- Athena/CMSSW integration.

Phase Three-C resolves field-dictionary and vertex-target identification at
the candidate-ledger level only. It does not resolve production UFO export.

Phase Three-D clarifies canonical target conventions and CKM/PMNS current
attachments, but mass-width and renormalization gates remain open.

Phase Three-E sharpens the normalization and scheme blockers into explicit
v0.7 artifacts. Vector and fermion target normalizations remain standard HEP
interface conventions, while gauge fixing, production coupling, mass-width, and
renormalization schemes remain candidate or open. No loadable UFO model is
exported.

Phase Three-F clears the interface normalization blocker by defining a
canonical production basis. It does not resolve the complete 4D Lagrangian,
production vertex table, mass-width, renormalization, loadable UFO, or event
generation blockers.

Phase Three-G exports candidate vertex and Lagrangian assembly ledgers. It
does not resolve the complete production vertex table, FeynRules export,
loadable UFO, MadGraph, LHE/HepMC, Athena, or CMSSW blockers.

Phase Three-H partially resolves bounded CKM/PMNS target blockers and leaves
the charged boundary response, neutral kernel, and standalone CP holonomy
vertices blocked. No loadable UFO model is exported.

Phase Three-I performs direct theorem-closure attempts after the bounded
Phase Three-H blocker audit. It does not promote the remaining standalone
blockers; instead it records `X_ch`, neutrino basis/scale/Dirac-Majorana, and
`O_int` as exact missing theorem objects.

Phase Three-J exports a minimal bounded collider-interface Lagrangian subset
for future translation. It does not export a production UFO model and does not
resolve loadability, MadGraph, LHE/HepMC, Athena, or CMSSW blockers.

Phase Three-K exports a disabled bounded FeynRules draft for the minimal
subset and a UFO export contract. It does not export a UFO model and does not
resolve MadGraph, LHE/HepMC, Athena, or CMSSW blockers.

Phase Three-L adds syntax-runner, software-preflight, UFO-runner, and
MadGraph-smoke runner artifacts for the bounded minimal subset. These artifacts
document the local execution path only. They do not resolve the remaining
production blocker that no validated loadable UFO exists in the repository.
