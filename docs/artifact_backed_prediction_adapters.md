# Artifact-backed prediction adapters

The v0.3 adapter layer reads existing local BHSM JSON artifacts and frozen
prediction exports. It does not recalculate or alter the underlying model. Each
returned matrix, phase, constant bundle, or mass-ratio bundle includes its local
path, artifact key, source field, load status, and explicit use-policy booleans.

Available local adapters cover CKM and PMNS matrix magnitudes, the CP holonomy
phase seed, boundary profile constants, and frozen charged-sector mass ratios.
The neutral boundary kernel is discoverable as a seed, but the physical
neutrino basis and dimensional scale remain an open theorem object.

Missing paths or fields return `ARTIFACT_NOT_FOUND`; the interface does not
substitute a number from prose, a plot, a reference table, or an internet
service.

Artifact-backed outputs are local BHSM outputs with provenance, not empirical validation claims.

Interface default formulas remain interface defaults unless a theorem-backed artifact or callable replaces them.

Reference values, including PDG values, are comparison inputs only and are never BHSM derivation inputs.

Missing artifacts are reported as missing, not inferred.

Theorem blockers remain blockers unless explicit artifact-backed theorem support is present.

Artifact discovery feeds the Sprint A proof gates, but artifact presence alone
does not satisfy the missing action, physical-map, or interaction-attachment
gates.
