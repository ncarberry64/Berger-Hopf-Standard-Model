# BHSM v1.2 Omega Action-Origin Scaffold

This development report attacks the boundary-operator proof gap without changing the frozen v1.0/v1.1 prediction packages.

Theorem complete: `False`

## Action Terms

| ID | Term | Source factor | Status |
| --- | --- | --- | --- |
| `I_D` | internal Dirac kinetic term | `twisted_dirac_operator` | `ACTION_LINKED` |
| `I_HOPF` | Hopf-fiber covariant derivative | `hopf_fiber_phase` | `DERIVED_FROM_BOUNDARY_FUNCTIONAL` |
| `I_BASE` | base S^2 angular derivative | `base_node_phase` | `DERIVED_FROM_BOUNDARY_FUNCTIONAL` |
| `I_U1` | Higgs-selected U(1) boundary phase | `hypercharge_higgs_boundary` | `ACTION_LINKED` |
| `I_WEAK` | weak-doublet chirality projector | `chirality_weak_component` | `DERIVED_FROM_BOUNDARY_FUNCTIONAL` |
| `I_COF` | quark coframe triplet projector | `coframe_triplet_participation` | `ACTION_LINKED` |

## Coefficient Status Table

| Sector | Coefficient | Value | Status | Source |
| --- | --- | ---: | --- | --- |
| `lepton` | `fiber_q` | `-1` | `DERIVED_FROM_BOUNDARY_FUNCTIONAL` | hopf_fiber_orientation * hypercharge_higgs_boundary |
| `lepton` | `base_j` | `2` | `DERIVED_FROM_BOUNDARY_FUNCTIONAL` | base_node_phase * chirality_sign * weak_component_sign * coframe_participation |
| `lepton` | `target` | `3` | `DERIVED_FROM_BOUNDARY_FUNCTIONAL` | family_index * sector_winding_multiplier |
| `up` | `fiber_q` | `1` | `DERIVED_FROM_BOUNDARY_FUNCTIONAL` | hopf_fiber_orientation * hypercharge_higgs_boundary |
| `up` | `base_j` | `-2` | `DERIVED_FROM_BOUNDARY_FUNCTIONAL` | base_node_phase * chirality_sign * weak_component_sign * coframe_participation |
| `up` | `target` | `6` | `DERIVED_FROM_BOUNDARY_FUNCTIONAL` | family_index * sector_winding_multiplier |
| `down` | `fiber_q` | `1` | `DERIVED_FROM_BOUNDARY_FUNCTIONAL` | hopf_fiber_orientation * hypercharge_higgs_boundary |
| `down` | `base_j` | `4` | `DERIVED_FROM_BOUNDARY_FUNCTIONAL` | base_node_phase * chirality_sign * weak_component_sign * coframe_participation |
| `down` | `target` | `12` | `DERIVED_FROM_BOUNDARY_FUNCTIONAL` | family_index * sector_winding_multiplier |

## Recovered Boundary Equations

- `lepton`: `Omega_ell = -q+2j = 3`, selected `[(5, 2), (9, 3)]`, recovered `True`
- `up`: `Omega_u = q-2j = 6`, selected `[(6, 0), (10, 1)]`, recovered `True`
- `down`: `Omega_d = q+4j = 12`, selected `[(6, 3), (8, 2)]`, recovered `True`

## Dependency Graph Summary

### lepton
- `fiber_q` = `-1` from `hopf_fiber_orientation * hypercharge_higgs_boundary` using `I_HOPF, I_U1`; status `DERIVED_FROM_BOUNDARY_FUNCTIONAL`.
- `base_j` = `2` from `base_node_phase * chirality_sign * weak_component_sign * coframe_participation` using `I_BASE, I_WEAK, I_COF`; status `DERIVED_FROM_BOUNDARY_FUNCTIONAL`.
- `target` = `3` from `family_index * sector_winding_multiplier` using `I_BDY`; status `DERIVED_FROM_BOUNDARY_FUNCTIONAL`.
### up
- `fiber_q` = `1` from `hopf_fiber_orientation * hypercharge_higgs_boundary` using `I_HOPF, I_U1`; status `DERIVED_FROM_BOUNDARY_FUNCTIONAL`.
- `base_j` = `-2` from `base_node_phase * chirality_sign * weak_component_sign * coframe_participation` using `I_BASE, I_WEAK, I_COF`; status `DERIVED_FROM_BOUNDARY_FUNCTIONAL`.
- `target` = `6` from `family_index * sector_winding_multiplier` using `I_BDY`; status `DERIVED_FROM_BOUNDARY_FUNCTIONAL`.
### down
- `fiber_q` = `1` from `hopf_fiber_orientation * hypercharge_higgs_boundary` using `I_HOPF, I_U1`; status `DERIVED_FROM_BOUNDARY_FUNCTIONAL`.
- `base_j` = `4` from `base_node_phase * chirality_sign * weak_component_sign * coframe_participation` using `I_BASE, I_WEAK, I_COF`; status `DERIVED_FROM_BOUNDARY_FUNCTIONAL`.
- `target` = `12` from `family_index * sector_winding_multiplier` using `I_BDY`; status `DERIVED_FROM_BOUNDARY_FUNCTIONAL`.

Open parts:
- derive the sector boundary functional from variation of the full internal action
- derive coframe triplet participation from the complete bundle action
- derive the Higgs-selected U(1) boundary phase from the full topological sector
- compute the full twisted Dirac/bundle spectrum

## What v1.2 Proves and Does Not Prove

- Proves within the scaffold: the charged-sector omega coefficients follow from the explicit symbolic sector boundary functional.
- Does not prove: the full twisted Dirac/bundle action uniquely generates that functional.

## Assumptions

- The sector boundary functional is supplied as a symbolic action-origin scaffold.
- No empirical masses, residuals, or CKM values are used to select coefficients.
- Canonical a and S remain fixed by the v1.0/v1.1 frozen model package.

## Limitations

- DERIVED_FROM_BOUNDARY_FUNCTIONAL means derived inside the explicit symbolic boundary functional only.
- Omega_f is not yet derived from a completed variation/spectrum of the full Berger-Hopf internal action.
- The v1.0/v1.1 frozen prediction packages are not modified by this report.
