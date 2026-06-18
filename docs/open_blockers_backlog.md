# Open Blockers Backlog

Current public status: structural architecture integrated conditional; numerical closure open.

Each blocker must be handled without fitting observed data after comparison and without changing frozen predictions.

| Blocker | Current status | Why it matters | Next valid action | Forbidden invalid action |
| --- | --- | --- | --- | --- |
| `DELTA_Y_NU_NEUTRAL_SADDLE_DISPLACEMENT_OPEN` | open localizable `S_nu_topo` dependency | Needed for the Hessian/barrier candidate formula. | Derive `Delta y_nu` from the neutral finite-width saddle or boundary/topographic action before comparison. | Choose `Delta y_nu` to reproduce observed neutrino mass scale or PMNS residuals. |
| `H_TOPO_NU_HESSIAN_DERIVATION_OPEN` | open localizable `S_nu_topo` dependency | Needed to define `G_nu_topo = 1/2 E_nu^T H_topo^(nu) E_nu`. | Derive the neutral topographic Hessian from the full boundary/topographic action. | Insert a Hessian eigenvalue fitted to neutrino data. |
| `E_NU_LABEL_TO_DISTANCE_MAP_OPEN` | open localizable `S_nu_topo` dependency | Needed to map neutral labels into the topographic displacement metric. | Derive `E_nu` from neutral sector boundary tensors and finite-width geometry. | Pick an embedding that makes the suppression numerically work. |
| `S_BARRIER_NEUTRAL_TOPOGRAPHIC_OPEN` | open localizable `S_nu_topo` dependency | Needed to decide whether a positive barrier term contributes to suppression. | Derive or prove unnecessary `S_barrier` from the neutral boundary action. | Fit a barrier term to the neutrino scale. |
| `SCALAR_TOPOGRAPHIC_PROFILE_SOLUTION_OPEN` | open theorem/scaffold dependency | Needed for the full scalar/topographic profile and neutral finite-width saddle/path. | Solve or bound the profile from the scalar/topographic action. | Tune profile parameters to hide residuals or extra light modes. |
| `POSITIVITY_PROOF_S_NU_TOPO_OPEN` | open proof dependency | Needed to justify suppression as positive action rather than a fitted damping factor. | Prove positivity of the derived neutral suppression action. | Assume positivity from the desired exponential hierarchy. |
| `CKM_1_16_EXPONENT_NOT_DERIVED` | open localized numerical-closure object | Controls the candidate CKM 2-3 dressing exponent. | Derive or reject the exponent from BHSM structure before comparison. | Fit `1/16` to CKM residuals after comparison. |
| `S_NU_TOPO_DERIVATION_OPEN` | open localized numerical-closure object | Sets the neutral topographic suppression scale. | Derive or constrain `S_nu_topo` from topographic/boundary action structure before comparison. | Fit `S_nu_topo` to neutrino mass scale. |
| `SCALAR_TOPOGRAPHIC_DECOUPLING_OPEN` | open theorem blocker | Needed to exclude unwanted light scalar/topographic modes. | Prove or bound scalar/topographic decoupling in the action/scaffold. | Hide extra light states by tuning profile parameters. |
| `HIGHER_LOOP_THRESHOLDS_OPEN` | open comparison blocker | Required for precision RG/QCD comparison. | Implement validated higher-loop/threshold matching with labeled inputs. | Use mixed-scale masses as precision truth. |
| `NUMERICAL_MASS_RATIO_LOCK_OPEN` | open pre-comparison lock | Needed before claiming mass-ratio prediction. | Lock all symbolic mass inputs and tolerances before comparison. | Adjust metrics or prefactors after seeing residuals. |
| `CKM_NUMERICAL_LOCK_OPEN` | open pre-comparison lock | Needed before claiming numerical CKM prediction. | Lock sector displacement, phase, and finite-width inputs before comparison. | Tune CKM phases or mixing metrics to observed CKM. |
| `PMNS_NUMERICAL_LOCK_OPEN` | open pre-comparison lock | Needed before claiming numerical PMNS prediction. | Lock neutral operator parameters and phase loop before comparison. | Tune PMNS angles or CP phase to data. |
| `NEUTRINO_ORDERING_OPEN` | open physics-output blocker | Needed before any neutrino ordering claim. | Derive ordering from the neutral operator after pre-comparison lock. | Choose ordering from observed oscillation data. |
| `STABILITY_AND_COUPLING_BOUNDS_OPEN` | open theorem blocker | Needed for robust low-energy equivalence and decoupling claims. | Prove stability and coupling bounds in the relevant operator/domain scaffold. | Assert stability from finite tests alone. |
