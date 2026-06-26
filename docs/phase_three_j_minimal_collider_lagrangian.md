# Phase Three-J Minimal Collider-Interface Lagrangian

BHSM Phase Three-J exports a minimal bounded collider-interface Lagrangian
subset in the canonical production basis.

This subset includes only already-supported pieces:

- canonical production-basis kinetic structure;
- standard target gauge/current conventions;
- BHSM CKM charged-current source;
- BHSM PMNS charged-current source;
- BHSM CP phase only through CKM/PMNS mixing sources;
- `BHSM_COLLIDER_INTERFACE` runtime mode.

The subset explicitly excludes unresolved standalone pieces:

- `charged_boundary_response_matrix`, pending the `X_ch` theorem;
- `neutral_operator_kernel_BH`, pending neutrino basis/scale and
  Dirac-Majorana theorem;
- standalone `cp_holonomy_phase_attachment`, pending `O_int`;
- `BHSM_PURE_NOFIT` mass-width closure;
- full renormalization closure.

This is FeynRules-prep only. It is not the complete BHSM 4D Lagrangian, not a
production FeynRules file, not a UFO model, and not event-generation readiness.

## Phase Three-K Follow-On

Phase Three-K exports a disabled bounded FeynRules syntax draft for this
minimal subset. The draft remains disabled until real Mathematica/FeynRules
syntax validation is performed.
