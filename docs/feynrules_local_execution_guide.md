# FeynRules Local Execution Guide

Local scripts:

```text
scripts/feynrules/check_bhsm_minimal_model.m
scripts/feynrules/export_bhsm_minimal_to_ufo.m
```

Expected local commands:

```text
wolframscript -file scripts/feynrules/check_bhsm_minimal_model.m
wolframscript -file scripts/feynrules/export_bhsm_minimal_to_ufo.m
```

These commands require a local Mathematica/Wolfram runtime and FeynRules.
They should be run only after intentionally enabling and validating:

```text
models/feynrules/BHSM_Minimal_Collider_Interface.fr
```

The repository does not claim these commands were run in Phase Three-L.

Phase Three-M adds Python wrappers under `scripts/feynrules/` that refuse to
enable or export the minimal model unless live validation evidence exists. The
wrappers write local logs under `runs/feynrules_validation/`; those logs are
not committed as validation evidence unless a future sprint intentionally
records a real run.

Phase Three-N adds runtime discovery scripts under `scripts/runtime/` and a
single execution-gate wrapper. In the current environment the Wolfram/FeynRules
runtime is not detected, so the wrapper records skipped validation rather than
creating a fake validation result.
