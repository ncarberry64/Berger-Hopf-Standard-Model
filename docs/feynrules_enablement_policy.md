# FeynRules Enablement Policy

Machine-readable artifact:

```text
artifacts/BHSM_feynrules_model_enablement_decision_v1_5.json
```

Committed disabled model:

```text
models/feynrules/BHSM_Minimal_Collider_Interface.fr.disabled
```

Enabled model path, allowed only after live validation:

```text
models/feynrules/BHSM_Minimal_Collider_Interface.fr
```

Policy:

- static syntax-contract checks do not authorize enablement;
- live FeynRules syntax validation must pass;
- live model-load validation must pass;
- the minimal Lagrangian symbol must be checked;
- unresolved vertices must remain excluded;
- forbidden fake numerical masses, widths, and readiness claims must remain
  absent.

Current result:

```text
enablement_allowed = false
enablement_performed = false
```

The model remains disabled.

