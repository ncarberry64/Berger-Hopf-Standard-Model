# Phase Three-O Runtime Assets And HEP Handoff

BHSM Phase Three-O packages a CERN-like institutional HEP handoff package for
the bounded minimal collider-interface subset.

It adds:

- runtime asset manifest;
- legal-source download policy artifact;
- Wolfram runtime mapping status;
- FeynRules mapping/install status;
- MadGraph mapping/install status;
- institutional validation protocol;
- collider-interface model card;
- setup scripts, Makefile targets, and optional devcontainer metadata.

The current environment detects Python but does not detect WolframScript,
WolframKernel/Mathematica, FeynRules, or MadGraph. No external runtime
readiness is claimed.

This is a reproducible handoff package for HEP-style review. It is not an
experiment-approved software integration, not a complete BHSM 4D Lagrangian,
and not UFO/MadGraph/event readiness.

## v1.1.0 Release-Facing Consolidation

Phase Three-O is consolidated into the BHSM v1.1.0 HEP handoff package through:

- `docs/hep_review_quickstart.md`
- `docs/institutional_hep_handoff_index.md`
- `docs/bhsm_v1_1_0_release_scope.md`
- `docs/bhsm_v1_1_0_claim_status.md`
- `artifacts/BHSM_v1_1_0_phase_three_consolidated_gate_status.json`

