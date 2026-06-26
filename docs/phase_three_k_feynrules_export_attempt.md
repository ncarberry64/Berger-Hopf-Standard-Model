# Phase Three-K FeynRules Export Attempt

BHSM Phase Three-K is the first bounded software-track export attempt for the
minimal collider-interface subset.

The sprint exports a disabled FeynRules syntax draft:

```text
models/feynrules/BHSM_Minimal_Collider_Interface.fr.disabled
```

The file is disabled because Mathematica/FeynRules syntax validation was not
run in this sprint. It is not a production FeynRules file and not a UFO model.

Included subset:

- canonical production-basis kinetic structure;
- standard target gauge/current conventions;
- BHSM CKM charged-current target;
- BHSM PMNS charged-current target;
- BHSM CP phase only through CKM/PMNS mixing sources;
- `BHSM_COLLIDER_INTERFACE` runtime parameter mode.

Excluded:

- charged boundary response, pending `X_ch`;
- neutral kernel, pending neutrino basis/scale and Dirac-Majorana theorem;
- standalone CP holonomy, pending `O_int`;
- `BHSM_PURE_NOFIT` mass-width closure;
- full renormalization closure.

UFO export, MadGraph validation, LHE/HepMC generation, and detector-software
interfaces remain gated.

## Phase Three-L Follow-On

Phase Three-L adds a FeynRules syntax contract, local Mathematica/FeynRules
runner scripts, software environment preflight, UFO export runner contract, and
MadGraph smoke-test runner contract for this same bounded minimal subset.

The follow-on package does not promote the disabled draft to a production
`.fr` file. FeynRules syntax validation, model loading, UFO export/loadability,
MadGraph smoke testing, LHE/HepMC generation, Athena readiness, and CMSSW
readiness remain false unless actually executed and validated in the required
external software environment.
