# Brutal Falsification Table

Primitive-incidence candidates fail if the complete action does not select the
gcd normalization, maximal primitive overlap, or reciprocal log-transport
averaging rule. Arithmetic agreement alone is not protection from falsification.

The CKM application fails if the complete transport functional does not act on
sixteen equivalent bilinear channels, even though the abstract minimization
lemma is mathematically correct.

The v2.2 channel audit also falsifies maximal-self-response selection if the
complete transport action selects dimension 8, 21, 49, or another space.

The v2.3 bidirectional candidate fails if the complete action lacks an
off-diagonal up/down block, is not adjoint closed, or assigns unequal physical
transport roles to the two directions.

The v2.5 normalized-action selection fails if the normalized action selects
one-way up/down (8), maximal self-response (16), sector self-response (21),
total charged endomorphism (49), or any other CKM transport space. The
bidirectional adjoint-pair channel count is 16, but this is a conditional
channel assignment until selected by the normalized action.

The v2.6 charged-current action audit fails closed unless BHSM locates a
normalized charged-current action term with operator domain/codomain and uses
that term to select the transport space. The existence of a Hermitian-conjugate
term supports action reality but does not by itself derive CKM transport-space
selection.

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
| PHY-14 | PHYSICS | Bounded CKM interface promotion | OPEN | a complete normalized action source supplies the missing measure, coefficient, projector sandwich, and variational provenance |
| PHY-15 | PHYSICS | CKM transport-space selection | OPEN | all upstream gates close and select a different space, or no CKM identification theorem exists |
| PHY-16 | PHYSICS | CKM measure/coefficient normalization | OPEN | one normalized action source supplies both on the bounded term |
| PHY-17 | PHYSICS | CKM coefficient value | OPEN | normalized weak gauge action fixes `g2_BH` |
