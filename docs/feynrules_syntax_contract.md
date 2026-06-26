# FeynRules Syntax Contract

Machine-readable artifact:

```text
artifacts/BHSM_feynrules_syntax_contract_v1_4.json
```

The contract statically checks that the disabled model draft:

- contains `BHSM_MINIMAL_COLLIDER_INTERFACE` labeling;
- warns that it is not the complete BHSM 4D Lagrangian;
- warns that unresolved standalone vertices are excluded;
- contains no numerical PDG mass markers;
- contains no fake width assignments;
- contains no LHE/HepMC readiness claims;
- contains no Athena/CMSSW readiness claims.

These are repository text checks only. They are not Mathematica syntax checks,
not FeynRules load checks, not Lagrangian validation, and not UFO export
checks.

