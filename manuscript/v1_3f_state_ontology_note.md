# BHSM v1.3F State Ontology Note

Branch: `bhsm-v1.3-ht-spectrum`

Status: development audit

Theorem complete: `False`

## Purpose

BHSM v1.3F adds a state ontology ledger that separates observable Standard
Model particles and QCD composites from internal Berger-Hopf modes, virtual
excitations, dressing contributions, heavy lifted states, screened
topographic states, and forbidden extra-light states.

No frozen BHSM v1.0/v1.1 predictions, canonical constants, tolerances, mode
ledger, public release tags, v1.2 action-origin outputs, or v1.3 `H_T`
spectral-bound logic are changed.

## Ontology Categories

The audit uses these categories:

| Category | Meaning |
| --- | --- |
| `ON_SHELL_SM_PARTICLE` | Accepted on-shell Standard Model field state. |
| `COMPOSITE_QCD_STATE` | QCD composite state such as a baryon or meson. |
| `INTERNAL_BERGER_HOPF_MODE` | Internal mode label not automatically promoted to an observable particle. |
| `VIRTUAL_EXCITATION` | Off-shell or temporary contribution. |
| `DRESSING_CONTRIBUTION` | Virtual-environment dressing factor, not a particle. |
| `HEAVY_LIFTED_STATE` | Internal complement mode lifted above the Hopf/`H_T` scale. |
| `SCREENED_TOPOGRAPHIC_STATE` | Scalar/topographic mode allowed only through Higgs projection, screening, or filtering. |
| `FORBIDDEN_EXTRA_LIGHT_STATE` | Non-SM light internal state that would couple as an observable on-shell state. |
| `OPEN_UNCLASSIFIED` | State not classified by the current rules. |

## Rules R1-R8

| Rule | Statement |
| --- | --- |
| `R1` | Standard Model elementary particles are real/on-shell particle states only if they correspond to the accepted SM field ledger. |
| `R2` | Composite hadrons, mesons, baryons, resonances, and bound states are downstream QCD composite states. |
| `R3` | Internal Berger-Hopf eigenmodes are not automatically observable particles. |
| `R4` | Virtual charm, top, quark, lepton, gauge, or scalar contributions are virtual excitations or dressing contributions unless on-shell. |
| `R5` | `Z_virt^{u,2}=1/2` is a dressing contribution, not a new particle. |
| `R6` | Any additional internal mode below the `H_T` gap that couples as an observable on-shell state is forbidden unless experimentally identified. |
| `R7` | Heavy internal modes above the Hopf/`H_T` lift scale are heavy lifted states. |
| `R8` | Scalar/topographic modes are allowed only if Higgs-projected, heavy, derivative-filtered, curvature-filtered, or screened. |

## Example Classifications

| Example | Classification |
| --- | --- |
| electron | `ON_SHELL_SM_PARTICLE` |
| charm quark field excitation | `ON_SHELL_SM_PARTICLE` when treated as a real SM field excitation |
| temporary charm loop or dressing effect | `VIRTUAL_EXCITATION` |
| `Z_virt^{u,2}=1/2` | `DRESSING_CONTRIBUTION` |
| proton, neutron, pion | `COMPOSITE_QCD_STATE` |
| internal charged-lepton mode `(5,2)` | `INTERNAL_BERGER_HOPF_MODE` |
| non-SM light observable internal mode below the gap | `FORBIDDEN_EXTRA_LIGHT_STATE` |
| heavy complement mode above `4 pi^2 v` | `HEAVY_LIFTED_STATE` |
| screened topographic scalar | `SCREENED_TOPOGRAPHIC_STATE` |

## Claim Boundary

BHSM v1.3F clarifies that internal modes and virtual dressing contributions
are not automatically new observable particles. Extra observable light states
remain forbidden unless identified experimentally or lifted/screened by the
`H_T`/scalar-sector mechanisms.

This note does not prove the full `H_T` no-extra-light theorem and does not
change any frozen prediction branch.

## Remaining Blockers

- Prove the full twisted Dirac / `H_T` spectrum and protected
  kernel/complement split.
- Prove scalar/topographic decoupling from the full action-level spectrum and
  couplings.
- Derive virtual dressing factors from a full loop/threshold calculation if
  they are to move beyond candidate status.
