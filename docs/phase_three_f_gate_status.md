# Phase Three-F Gate Status

Machine-readable artifact:

```text
artifacts/BHSM_phase_three_f_gate_status_v0_8.json
```

## Recommended Status Language

BHSM Phase Three-F defines the canonical production basis for FeynRules/UFO
interfaces and separates no-fit derivation mode from collider runtime
comparison mode. The interface normalization gate is cleared by defining
`Z_A,prod = Z_psi,prod = 1` as canonical production-basis conventions, not BHSM
dynamical predictions. Complete 4D Lagrangian export, mass-width closure,
renormalization closure, and production vertex tables remain open.

## Remaining Blockers

- Complete 4D Lagrangian.
- Production vertex table.
- Mass-width closure for `BHSM_PURE_NOFIT`.
- Renormalization closure.
- FeynRules export.
- Loadable UFO model.
- MadGraph validation.
- LHE/HepMC generation.
- Athena/CMSSW integration.

