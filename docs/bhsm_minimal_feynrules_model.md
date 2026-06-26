# BHSM Minimal FeynRules Model Draft

Model draft:

```text
models/feynrules/BHSM_Minimal_Collider_Interface.fr.disabled
```

The file header states:

```text
BHSM_MINIMAL_COLLIDER_INTERFACE
Generated from Phase Three-J bounded FeynRules-prep subset.
This is not the complete BHSM 4D Lagrangian.
This excludes charged boundary response, neutral kernel, and standalone CP holonomy vertices.
This is not a validated UFO model unless UFO export/loadability tests pass.
```

The draft contains only symbolic/runtime placeholders for the bounded CKM/PMNS
charged-current interface subset. It contains no numerical masses or widths.

It remains disabled until a real Mathematica/FeynRules syntax validation pass
is performed.

## Phase Three-L Runner Package

The Phase Three-L runner package adds local scripts for checking and exporting
the minimal draft after a user deliberately enables a validated production
copy. The current repository state still keeps
`BHSM_Minimal_Collider_Interface.fr.disabled` disabled, and no production
`BHSM_Minimal_Collider_Interface.fr` file is exported.

Static repository checks are syntax-contract checks only. They do not replace
Mathematica/FeynRules loading, `FeynmanRules[...]` validation, `WriteUFO[...]`
execution, or UFO loadability checks.

## Phase Three-M Live Attempt

Phase Three-M adds an enablement decision artifact for this draft. Since live
FeynRules validation did not run in the current environment, the enabled
production `.fr` file is still not committed.
