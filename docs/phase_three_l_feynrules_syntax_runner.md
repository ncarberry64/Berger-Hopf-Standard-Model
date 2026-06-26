# Phase Three-L FeynRules Syntax Runner

BHSM Phase Three-L hardens the software execution path for the bounded
minimal collider-interface subset.

It adds:

- a FeynRules syntax contract;
- local Mathematica/FeynRules runner scripts;
- a software environment preflight;
- a UFO export runner contract;
- a MadGraph smoke-test runner contract.

Static repository checks passed for the disabled draft, but static checks are
not FeynRules validation. Mathematica/FeynRules/MadGraph execution was not
performed in this sprint.

The disabled model remains:

```text
models/feynrules/BHSM_Minimal_Collider_Interface.fr.disabled
```

No UFO model, MadGraph smoke result, LHE file, or HepMC file is generated.

