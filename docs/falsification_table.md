# Brutal Falsification Table

Primitive-incidence candidates fail if the complete action does not select the
gcd normalization, maximal primitive overlap, or reciprocal log-transport
averaging rule. Arithmetic agreement alone is not protection from falsification.

| claim_id | track | claim | current_status | what_would_falsify_it |
| --- | --- | --- | --- | --- |
| ENG-01 | ENGINE | CERN open-data four-vector accuracy | ARTIFACT_BACKED | scale-aware error exceeds declared bound |
| ENG-02 | ENGINE | SIMD/control speedup | ENVIRONMENT_SPECIFIC | independent matched implementation is not faster |
| ENG-03 | ENGINE | ROOT implicit multithreading scaling | NEGATIVE_HOSTED_RESULT | no scaling or regression; current 2-thread run is 0.940x |
| ENG-04 | ENGINE | Native PMU explanation | RUNTIME_GATED | PMU counters contradict proposed mechanism |
| ENG-05 | ENGINE | Lorentz invariant preservation | ARTIFACT_BACKED | declared backward-error gate fails |
| ENG-06 | ENGINE | Round-trip coordinate transformation | ARTIFACT_BACKED | inverse fails scale-aware tolerance |
| PHY-01 | PHYSICS | Frozen prediction integrity | ESTABLISHED | frozen artifact hash changes unexpectedly |
| PHY-02 | PHYSICS | Charged projectors | ARTIFACT_BACKED | projector identities or ledger mapping fail |
| PHY-03 | PHYSICS | Common-16 generator | CONDITIONAL | no shared action generator exists |
| PHY-04 | PHYSICS | CKM exponent | OPEN | action-derived transport yields a different exponent |
| PHY-05 | PHYSICS | PMNS structure | CONDITIONAL | derived basis map conflicts with frozen structure |
| PHY-06 | PHYSICS | Neutral propagation | CONDITIONAL | complete action lacks propagation response |
| PHY-07 | PHYSICS | Neutral positivity | CONDITIONAL | admissible cone contains a negative direction |
| PHY-08 | PHYSICS | Physical neutrino mass | OPEN | no unit-safe physical map or external bounds conflict after one is derived |
| PHY-09 | PHYSICS | Omega_f action derivation | CONDITIONAL | complete action does not generate sector functional |
| PHY-10 | PHYSICS | rho_ch action derivation | OPEN | action selects a value other than 3 |
| PHY-11 | PHYSICS | Boundary-measure normalization | OPEN | normalized measure cannot be constructed |
| PHY-12 | PHYSICS | Gauge/scalar normalization | OPEN | complete action gives incompatible normalization |
| PHY-13 | PHYSICS | External HEP runtime readiness | RUNTIME_GATED | live toolchain validation fails |
