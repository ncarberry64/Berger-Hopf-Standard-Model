# Falsification Ledger

The v1.0 package includes explicit falsification and weakening criteria. These
criteria protect the no-retuning status of the frozen branches.

| ID | Criterion | Status |
| --- | --- | --- |
| `F1` | If alpha-anchored `a` cannot be derived from the internal action, BHSM geometry weakens. | `OPEN_PROOF_OBLIGATION` |
| `F2` | If `Omega_f` cannot be derived from the twisted Dirac/bundle action, mass hierarchy predictions remain unsupported. | `OPEN_PROOF_OBLIGATION` |
| `F3` | If scheme-consistent quark ratios disagree beyond fixed tolerance bands, BHSM flavor mapping fails or must be revised. | `FALSIFIABLE_NUMERICAL_BRANCH` |
| `F4` | If canonical BHSM `V_us`, `V_cb`, `V_ub`, `delta`, and `J` fail outside fixed tolerances, BHSM flavor mapping is falsified or constrained. | `FALSIFIABLE_NUMERICAL_BRANCH` |
| `F5` | If neutrino ordering, octant, or phase decisively contradict BHSM effective-extension outputs, the neutrino branch fails. | `EFFECTIVE_EXTENSION_BRANCH` |
| `F6` | If the full twisted Dirac/`H_T` spectrum produces extra light states below `4*pi^2*v`, the SM-equivalent BHSM mapping fails. | `OPEN_SPECTRAL_THEOREM` |
| `F7` | If unscreened light scalar/topographic modes remain, BHSM fails as a Standard-Model-equivalent low-energy theory. | `OPEN_ACTION_LEVEL_PROOF` |
| `F8` | If higher-loop/threshold RG matching moves coupling agreement away from the electroweak scale beyond tolerance, the coupling branch weakens. | `OPEN_RG_MATCHING` |
| `F9` | Any post-freeze adjustment of `a`, `S`, modes, or `Z_virt` based on residuals invalidates the v1.0 prediction set. | `FREEZE_CONSTRAINT` |

## Fixed Tolerance Bands

| Class | Tolerance |
| --- | --- |
| `exact_status` | `pass_fail` |
| `gauge_couplings` | `0.01` |
| `higgs_electroweak_v` | `0.01` |
| `higgs_mass_zeroth_order` | `0.02` |
| `charged_lepton_ratios` | `0.25` |
| `quark_ratios_scheme_aware` | `0.25` |
| `quark_ratios_otherwise` | `SCHEME_SENSITIVE` |
| `ckm_angles` | `0.1` |
| `ckm_cp_jarlskog` | `0.1` |
| `pmns_effective` | `0.05` |
| `ht_gap` | `binary_pass_fail` |
| `scalar_decoupling` | `binary_scaffold_pass_fail` |

The frozen score summaries are:

- Bare: `{'PASS': 22}`
- Dressed candidate: `{'PASS': 21, 'SCHEME_SENSITIVE': 1}`
