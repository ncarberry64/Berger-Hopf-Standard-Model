# BHSM v1.3F State Ontology

Theorem complete: `False`

BHSM v1.3F clarifies that internal modes and virtual dressing contributions are not automatically new observable particles. Extra observable light states remain forbidden unless identified experimentally or lifted/screened by the H_T/scalar-sector mechanisms.

## Categories

| Category | Count |
| --- | --- |
| `ON_SHELL_SM_PARTICLE` | `3` |
| `COMPOSITE_QCD_STATE` | `3` |
| `INTERNAL_BERGER_HOPF_MODE` | `1` |
| `VIRTUAL_EXCITATION` | `1` |
| `DRESSING_CONTRIBUTION` | `1` |
| `HEAVY_LIFTED_STATE` | `1` |
| `SCREENED_TOPOGRAPHIC_STATE` | `1` |
| `FORBIDDEN_EXTRA_LIGHT_STATE` | `1` |
| `OPEN_UNCLASSIFIED` | `0` |

## Rules

| Rule | Category | Statement |
| --- | --- | --- |
| `R1` | `ON_SHELL_SM_PARTICLE` | Standard Model elementary particles are real/on-shell particle states only if they correspond to the accepted SM field ledger. |
| `R2` | `COMPOSITE_QCD_STATE` | Composite hadrons, mesons, baryons, resonances, and bound states are downstream QCD composite states, not elementary BHSM ledger entries. |
| `R3` | `INTERNAL_BERGER_HOPF_MODE` | Internal Berger-Hopf eigenmodes are not automatically observable particles. |
| `R4` | `VIRTUAL_EXCITATION` | Virtual charm, top, quark, lepton, gauge, or scalar contributions are virtual excitations or dressing contributions unless they correspond to on-shell states. |
| `R5` | `DRESSING_CONTRIBUTION` | Virtual-environment corrections such as Z_virt^{u,2}=1/2 are dressing contributions, not new particles. |
| `R6` | `FORBIDDEN_EXTRA_LIGHT_STATE` | Any additional internal mode below the H_T gap that couples as an observable on-shell state is a forbidden extra-light state unless experimentally identified. |
| `R7` | `HEAVY_LIFTED_STATE` | Heavy internal modes above the Hopf/H_T lift scale are heavy lifted states. |
| `R8` | `SCREENED_TOPOGRAPHIC_STATE` | Scalar/topographic modes are allowed only if Higgs-projected, heavy, derivative-filtered, curvature-filtered, or screened; otherwise they are forbidden extra-light states. |

## Example Classifications

| State | Category | Observable particle | Virtual/dressing | Forbidden extra-light |
| --- | --- | --- | --- | --- |
| `electron` | `ON_SHELL_SM_PARTICLE` | `True` | `False` | `False` |
| `charm_quark_field` | `ON_SHELL_SM_PARTICLE` | `True` | `False` | `False` |
| `photon` | `ON_SHELL_SM_PARTICLE` | `True` | `False` | `False` |
| `proton` | `COMPOSITE_QCD_STATE` | `True` | `False` | `False` |
| `neutron` | `COMPOSITE_QCD_STATE` | `True` | `False` | `False` |
| `pion` | `COMPOSITE_QCD_STATE` | `True` | `False` | `False` |
| `lepton_internal_mode_5_2` | `INTERNAL_BERGER_HOPF_MODE` | `False` | `False` | `False` |
| `non_sm_light_internal_mode` | `FORBIDDEN_EXTRA_LIGHT_STATE` | `False` | `False` | `True` |
| `heavy_complement_mode` | `HEAVY_LIFTED_STATE` | `False` | `False` | `False` |
| `screened_topographic_scalar` | `SCREENED_TOPOGRAPHIC_STATE` | `False` | `False` | `False` |
| `temporary_charm_sector_dressing` | `VIRTUAL_EXCITATION` | `False` | `True` | `False` |
| `z_virt_u2_half` | `DRESSING_CONTRIBUTION` | `False` | `True` | `False` |

## Limitations

- This is a semantic and structural ontology layer, not a model-output change.
- It does not compute the full H_T spectrum or prove the no-extra-light theorem.
