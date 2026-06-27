# Artifact provenance policy

Every adapter result carries a `ValueWithProvenance` record. The record names
the local source and explicitly marks whether a value is a frozen prediction,
a calibration input, a reference-only comparison input, or an empirical
derivation input. These booleans are always present in JSON output.

BHSM internal and frozen artifacts set `frozen_prediction=true` and
`empirical_derivation_input=false`. Reference data, when used by a separate
comparison interface, set `reference_comparison_input=true` and remain outside
the derivation path. Calibration anchors are similarly distinct from
independent predictions.

Artifact-backed outputs are local BHSM outputs with provenance, not empirical validation claims.

Reference values, including PDG values, are comparison inputs only and are never BHSM derivation inputs.

Missing artifacts are reported as missing, not inferred.
