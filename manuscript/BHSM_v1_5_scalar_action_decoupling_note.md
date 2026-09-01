# BHSM v1.5 Scalar/Topographic Action-Decoupling Note

BHSM v1.5 builds an action-level scalar/topographic decoupling scaffold. It distinguishes the SM Higgs projection from heavy, screened, virtual, and forbidden scalar/topographic modes. It does not claim full scalar decoupling from the complete action.

## Status

| Item | Result |
| --- | --- |
| Scalar/topographic status | `SCALAR_ACTION_SCAFFOLD_PASSES` |
| Theorem complete | `False` |
| Corrected H_T dependency | `DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL` |
| Open scalar risks in current inventory | `0` |
| Dangerous proxy modes in current inventory | `0` |
| Frozen BHSM predictions changed | `False` |

## Action Channels

| Channel | Role | Status |
| --- | --- | --- |
| `HIGGS_PROJECTED_LIGHT_MODE` | Allows exactly one light SM Higgs projection `H(x) Phi_0(y)` | `ACTION_SCAFFOLD` |
| `HOPF_GAP_LIFTED` | Lifts orthogonal scalar complement above `4*pi^2*v` | `HOPF_GAP_SCAFFOLD` |
| `HT_COMPLEMENT_LIFTED` | Links complement lifting to corrected formal-kernel `H_T` scaffold | `HT_FORMAL_KERNEL_LINKED` |
| `DERIVATIVE_SCREENED` | Treats derivative-filtered topographic modes as conditional screened modes | `SCREENING_SCAFFOLD` |
| `CURVATURE_SCREENED` | Treats curvature-filtered topographic modes as conditional screened modes | `SCREENING_SCAFFOLD` |
| `VIRTUAL_ONLY` | Classifies virtual/off-shell scalar-topographic exchange as not an on-shell light particle | `STATE_ONTOLOGY_LINKED` |
| `FORBIDDEN_UNSCREENED_LIGHT_SCALAR` | Falsifier channel for direct-coupled light scalar fifth-force risks | `FALSIFIER_RULE` |

## Sufficient Scaffold Condition

The scalar/topographic sector passes this v1.5 scaffold if one Higgs projection is light, all scalar complements are Hopf/H_T lifted or screened, derivative/curvature screened modes do not mediate unscreened fifth forces, and no `OPEN_SCALAR_RISK` remains in the current inventory.

The current scaffold satisfies these checks. The forbidden unscreened scalar channel is retained as a falsifier, not removed from the audit.

## Claim Boundary

This note does not prove scalar decoupling from the full Berger-Hopf action. The remaining proof obligations are:

- prove uniqueness of the Higgs projection from the complete scalar action;
- prove derivative and curvature screening at action level;
- complete the full `H_T` theorem rather than relying on `DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL` scaffold status;
- show globally that no direct-coupled unscreened light scalar/topographic mode is present.

No BHSM v1.0/v1.1/v1.4 frozen prediction, tolerance, mode ledger, canonical geometry, overlap width, or virtual dressing rule is changed by this v1.5 scaffold.
