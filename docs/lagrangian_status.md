# BHSM Lagrangian Status v0.1.0

No complete collider-ready 4D physical Lagrangian is exported in BHSM v1.0.1.

BHSM v1.0.1 exports boundary/operator-level no-fit artifacts, not a production
event-generator model.

| Object | Current BHSM status | Exported artifact/source | Needed for collider event generation? | Missing item, if any |
| --- | --- | --- | --- | --- |
| Internal boundary no-fit package | `COMPLETE_EXPORTED` | `artifacts/BHSM_boundary_no_fit_prediction_package_v1.json` | Indirect input only | Collider Lagrangian bridge |
| Profile scale | Exported | `artifacts/profile_scale_closure_values_v1.json` | Indirect input only | Mapping into collider parameters |
| Charged boundary outputs | Exported | `artifacts/charged_outputs_at_boundary_tau_A_local_v1.json`, `artifacts/charged_outputs_at_boundary_tau_A_background_identity_v1.json` | Indirect input only | Mass/width and interaction-vertex convention |
| Neutral operator output | Exported | `artifacts/neutral_operator_no_fit_output_v1.json` | Indirect input only | Collider-level neutral-sector Lagrangian |
| PMNS operator output | Exported | `artifacts/PMNS_no_fit_operator_output_v1.json` | Indirect input only | Neutrino-sector event-generation convention |
| CKM operator output | Exported | `artifacts/CKM_no_fit_operator_output_v1.json` | Indirect input only | Quark-sector interaction vertices |
| CP holonomy output | Exported | `artifacts/CP_no_fit_holonomy_output_v1.json` | Indirect input only | CP phase convention in Feynman rules |
| Boundary-scale transport identity | Exported | `artifacts/common_scale_boundary_transport_v1.json` | Indirect input only | External scale/scheme transport for collider comparison |
| External empirical comparison layer | Open/separate | `artifacts/BHSM_external_empirical_comparison_package_v1.json` | Validation only | Pinned empirical target tables |
| Full 4D physical Lagrangian | Not exported | None | Yes | Complete collider-ready QFT Lagrangian |
| Gauge-fixed interaction vertices | Not exported | None | Yes | Gauge choice, fields, couplings, vertices |
| Feynman rules | Not exported | None | Yes | Formal rule export and convention audit |
| UFO/FeynRules model | Not exported | None | Yes | UFO/FeynRules package |
| Mass/width parameter card | Not exported | None | Yes | Parameter-card mapping from BHSM artifacts |
| Event generator card | Not exported | None | Yes | MadGraph/Pythia/Herwig-compatible cards |
| Detector simulation card | Not exported | None | Yes | Athena/CMSSW or standalone detector-simulation configuration |

## Claim Boundary

The current package is suitable for internal boundary-artifact inspection and
comparison-layer planning. It is not suitable for collider event generation,
detector simulation, or official experiment software integration.
