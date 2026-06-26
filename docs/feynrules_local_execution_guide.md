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

