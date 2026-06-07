# BHSM v1.2B Parent Internal-Action Boundary Derivation Scaffold

Parent-action reduction status: `REDUCED_FROM_PARENT_ACTION`
Theorem complete: `False`

```text
S_int = int_I bar(Psi)(i slash D_Berger + A_Hopf + A_base + A_Higgs-U(1) + P_L + P_cof)Psi + S_boundary
```

## Parent Action Terms

| ID | Term | Contribution | Status |
| --- | --- | --- | --- |
| `I_D` | Berger twisted Dirac kinetic term | `parent kinetic operator and mode domain` | `ACTION_SCAFFOLD` |
| `I_HOPF` | Hopf-fiber connection | `hopf_fiber_orientation` | `REDUCED_FROM_PARENT_ACTION` |
| `I_U1` | Higgs-selected U(1) boundary connection | `hypercharge_higgs_boundary` | `REDUCED_FROM_PARENT_ACTION` |
| `I_BASE` | base S^2 angular connection | `base_node_phase` | `REDUCED_FROM_PARENT_ACTION` |
| `I_WEAK` | weak/chirality projector term | `chirality_sign and weak_component_sign` | `REDUCED_FROM_PARENT_ACTION` |
| `I_COF` | coframe triplet projector term | `coframe_participation` | `REDUCED_FROM_PARENT_ACTION` |
| `I_BDY` | sector boundary winding/index term | `family_index and sector_winding_multiplier` | `REDUCED_FROM_PARENT_ACTION` |

## Coefficient Reduction Table

| Sector | Coefficient | Value | Parent status | Dependencies |
| --- | --- | ---: | --- | --- |
| `lepton` | `fiber_q` | `-1` | `REDUCED_FROM_PARENT_ACTION` | `I_HOPF, I_U1` |
| `lepton` | `base_j` | `2` | `REDUCED_FROM_PARENT_ACTION` | `I_BASE, I_WEAK, I_COF` |
| `lepton` | `target` | `3` | `REDUCED_FROM_PARENT_ACTION` | `I_BDY` |
| `up` | `fiber_q` | `1` | `REDUCED_FROM_PARENT_ACTION` | `I_HOPF, I_U1` |
| `up` | `base_j` | `-2` | `REDUCED_FROM_PARENT_ACTION` | `I_BASE, I_WEAK, I_COF` |
| `up` | `target` | `6` | `REDUCED_FROM_PARENT_ACTION` | `I_BDY` |
| `down` | `fiber_q` | `1` | `REDUCED_FROM_PARENT_ACTION` | `I_HOPF, I_U1` |
| `down` | `base_j` | `4` | `REDUCED_FROM_PARENT_ACTION` | `I_BASE, I_WEAK, I_COF` |
| `down` | `target` | `12` | `REDUCED_FROM_PARENT_ACTION` | `I_BDY` |

## Necessary Terms

- Fiber coefficient requires: `I_HOPF, I_U1`.
- Base coefficient requires: `I_BASE, I_WEAK, I_COF`.
- Target requires: `I_BDY`.

## What v1.2B Shows and Does Not Show

- Shows: the sector boundary functional is reduced from the symbolic parent internal-action scaffold.
- Does not show: the complete Berger-Hopf twisted Dirac/bundle action uniquely generates the parent scaffold or the boundary functional.

## Limitations

- The sector boundary functional is reduced from a symbolic parent internal-action scaffold.
- This is not a full unique derivation from the complete Berger-Hopf twisted Dirac/bundle action.
- No empirical mass, CKM, PMNS, or residual inputs are used.
