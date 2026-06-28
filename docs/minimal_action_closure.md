# BHSM Minimal Action Closure

The v0.8 evaluator uses
`artifacts/BHSM_author_ontology_v0_8.json` as its controlling theory
dictionary. BHSM modes are physical boundary-local fields; sector projectors
act on those fields to select admissible couplings and responses.

```text
S_BHSM,min = S_boundary + S_sector + S_phase + S_charged + S_neutral
```

| Target | Result | Scope |
| --- | --- | --- |
| CP/Z6 holonomy | `ARTIFACT_BACKED` | Holonomy and CKM/PMNS phase attachment are supported by local no-fit artifacts |
| Standalone CP `O_int` vertex | `RETIRED_TARGET` | Not required by the controlling ontology and not production eligible |
| `X_ch` | `CONDITIONAL_ACTION_THEOREM` | Physical boundary field -> `P_ch` -> `X_ch` -> charged-current response |
| Neutrino BHSM mass | `CONDITIONAL_PROPAGATION_THEOREM` | Neutral propagation -> curvature-threshold response -> effective mass observable |

The X_ch and neutrino results follow from the author ontology plus local
boundary-source artifacts; they are not established by the older artifacts
alone. Numerical X_ch normalization and numerical neutrino curvature response
remain open. Dirac/Majorana convention is secondary to the propagation theorem.
No FeynRules, UFO, MadGraph, or empirical-validation status changes.

```bash
python -m bhsm.interface minimal-action-status
python -m bhsm.interface minimal-action-report --format markdown
```
