# BHSM v1.1.0 Release Scope

## Included

- Internal boundary no-fit package.
- Frozen prediction integrity.
- Claim-status ledger.
- Minimal bounded collider-interface subset.
- CKM charged-current bounded target.
- PMNS charged-current bounded target.
- BHSM CKM/PMNS source matrices.
- FeynRules-prep JSON/docs.
- Disabled minimal FeynRules draft.
- Runtime validation runner package.
- Institutional HEP handoff package.

## Excluded

- Complete BHSM 4D Lagrangian.
- `charged_boundary_response_matrix` as production vertex.
- `neutral_operator_kernel_BH` as physical neutrino mass matrix.
- Standalone `cp_holonomy_phase_attachment` as production vertex.
- Pure no-fit mass-width closure.
- Renormalization closure.
- Enabled validated FeynRules file.
- UFO export/loadability.
- MadGraph validation.
- LHE/HepMC event generation.
- Athena integration.
- CMSSW integration.
- Official CERN software integration.
- Empirical validation.

## Status Language

BHSM v1.1.0 packages the status-reconciled internal boundary no-fit release and the Phase Three bounded collider-interface HEP handoff chain. It is ready for external HEP-style review and runtime validation attempts, but it is not an officially integrated CERN software package, not complete BHSM 4D Lagrangian export, not FeynRules/UFO/MadGraph validated, and not empirically validated.
