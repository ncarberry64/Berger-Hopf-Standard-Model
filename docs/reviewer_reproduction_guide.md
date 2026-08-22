# Reviewer Reproduction Guide

## Current N12 continuum-majorant effectiveness checkpoint

Run the focused deterministic checkpoint first:

```bash
python -m pytest -q tests/test_bhsm_n12_effective_inverse_localization.py tests/test_bhsm_n12_continuum_majorant_checkpoint.py
python tools/audit_forbidden_claims.py
python tools/audit_bhsm_status.py
python tools/audit_frozen_prediction_integrity.py
git diff --check
```

Inspect the [continuum-majorant checkpoint manifest](../artifacts/n12_continuum_majorant_effectiveness/BHSM_N12_CONTINUUM_MAJORANT_CHECKPOINT_MANIFEST.json).
It hash-locks the constant-ownership audit, effective-inverse localization,
and positive-duration N12 symbol history. Reproducing the three JSON files
twice must give byte-identical output. The history is a sampled diagnostic,
not a whole-interval proof; the checkpoint does not certify a continuum child.

The deterministic PowerShell replay is:

```powershell
$env:PYTHONPATH='src'; $env:BHSM_N12_CONTINUUM_MAJORANT_OWNERSHIP_RESULT='artifacts/n12_continuum_majorant_effectiveness/BHSM_N12_CONTINUUM_MAJORANT_OWNERSHIP_AUDIT.json'; python scripts/audit_n12_continuum_majorant_ownership.py
python scripts/materialize_n12_effective_inverse_localization.py
$env:BHSM_N12_HISTORY_CALDERON_RESULT='artifacts/n12_continuum_majorant_effectiveness/BHSM_N12_POSITIVE_DURATION_CALDERON_HISTORY.json'; python scripts/audit_n12_positive_duration_calderon_history.py
python scripts/materialize_n12_continuum_majorant_checkpoint.py
```

## Prior N16 coupled momentum-response diagnostic

Run the hash-locked finite diagnostic first:

```bash
python -m pytest -q tests/test_bhsm_n16_coupled_momentum_response.py
python tools/audit_forbidden_claims.py
python tools/audit_bhsm_status.py
python tools/audit_frozen_prediction_integrity.py
git diff --check
```

Inspect the [N16 checkpoint manifest](../artifacts/n16_coupled_momentum_response/BHSM_N16_COUPLED_MOMENTUM_RESPONSE_CHECKPOINT_MANIFEST.json).
It records the exact paired hard-response reduction and the unchanged
category-2 soft classification. The stored N16 candidates are diagnostic
proposals, not roots or continuum backgrounds.

The deterministic PowerShell replay is:

```powershell
$env:PYTHONPATH='src'; $env:BHSM_N12_FULL_QVM_ORDERS='16,16'; $env:BHSM_N12_FULL_QVM_RESULT='artifacts/n16_coupled_momentum_response/BHSM_N16_FULL_QVM_SOURCE_TAIL_AUDIT.json'; $env:BHSM_N12_FULL_QVM_CORRECTION_CHECKPOINT='artifacts/n16_coupled_momentum_response/BHSM_N16_FULL_QVM_LINEAR_SOURCE_CANDIDATE.npz'; python scripts/audit_n12_full_qvm_constraint_tail.py
$env:BHSM_N16_COMPLETE_CHILD_AUDIT='artifacts/n16_coupled_momentum_response/BHSM_N16_COUPLED_MOMENTUM_RESPONSE_AUDIT.json'; $env:BHSM_N16_COUPLED_CANDIDATE='artifacts/n16_coupled_momentum_response/BHSM_N16_HARD_RESPONSE_CANDIDATE.npz'; python scripts/audit_n16_complete_child_candidate.py
```

## Prior dynamic-Calderon checkpoint

Run the hash-locked focused replay first:

```bash
python -m pytest -q tests/test_bhsm_n12_dynamic_calderon_checkpoint.py tests/test_bhsm_n12_direct_checkpoint.py
python tools/audit_forbidden_claims.py
python tools/audit_bhsm_status.py
python tools/audit_frozen_prediction_integrity.py
git diff --check
```

Inspect the [dynamic-Calderon manifest](../artifacts/n12_dynamic_calderon_checkpoint/BHSM_N12_DYNAMIC_CALDERON_CHECKPOINT_MANIFEST.json).
It locks the exact ordered-event Feshbach audit, source-restricted N48/N64
Calderon probes, N64 full q-v-m tail diagnostic, and the retained N64 linear
candidate. The principal submatrix is not the unchanged ordered-event
definition; the positive finite dynamic gaps are not a uniform theorem. N48
and N64 probes must not be reported as complete-child roots.

The expensive numerical replay uses the existing scripts and no altered map:

```bash
PYTHONPATH=src python scripts/audit_n12_n48_ordered_event_feshbach_equivalence.py
BHSM_N12_FULL_QVM_ORDERS=48,64 BHSM_N12_FULL_QVM_POINTS=96 PYTHONPATH=src python scripts/audit_n12_full_qvm_constraint_tail.py
BHSM_N48_LINEAR_CANDIDATE_CHECKPOINT=artifacts/n12_dynamic_calderon_checkpoint/BHSM_N64_FULL_QVM_LINEAR_CORRECTION_CANDIDATES.npz BHSM_N48_CORRECTED_CALDERON_POINTS=96 PYTHONPATH=src python scripts/audit_n48_source_corrected_calderon_symbol.py
```

## Current direct N12 checkpoint

```bash
PYTHONPATH=src python scripts/audit_n12_corrected_action_execution_provenance.py --verify artifacts/n12_direct_checkpoint/BHSM_N12_CORRECTED_ACTION_EXECUTION_PROVENANCE.json
BHSM_N12_CHECKPOINT=artifacts/n12_direct_checkpoint/BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz BHSM_N12_RESULT=n12_residual_replay.json BHSM_N12_RESIDUAL_ONLY_DIAGNOSTIC=1 BHSM_CHORD_PROPOSAL_STEPS=0 PYTHONPATH=src python scripts/measure_n6_n12_joint_schur_chord_cover.py
python -m pytest -q tests/test_bhsm_n12_direct_checkpoint.py tests/test_engine_invariant_preservation.py tests/test_engine_physics_status_separation.py
python tools/audit_forbidden_claims.py
python tools/audit_bhsm_status.py
python tools/audit_frozen_prediction_integrity.py
git diff --check
```

Inspect the [N12 checkpoint manifest](../artifacts/n12_direct_checkpoint/BHSM_N12_SCIENTIFIC_CHECKPOINT_MANIFEST.json).
It verifies hashes for the exact state, residual, radii proof, physical
neighborhoods, exact normals, persistence witness, tail diagnostics, and the
retained-action source modules loaded by the corrected high-precision run.
The direct N12 child is finite-resolution evidence; the higher-order zero-padded
or source-corrected Calderon states through N64 are probes and must not be
reported as roots or a continuum certificate.

For the retained N3--N6 provenance, the focused replay is:

```bash
python -m pytest -q tests/test_bhsm_aether_cross_resolution_reconnaissance_v21_35.py -k "persisted_n6_repaired or replayable_returns or inverse_square_tail or local_energy"
```

This verifies the repaired existing N6 ordered-event gate, rebuilt child and
persistence record, the action-derived shell law and fail-closed finite bridge,
and also enforces that the reduced local N6 energy is not reported as mass.
The full historical pytest corpus remains available locally but is not a
mandatory pull-request check; run `python -m pytest -q` only when a full
historical regression is scientifically warranted.

## Current corrected-Rayleigh N=3 audit

The canonical snapshot is the validated rolling checkpoint at exact
`||F376|| = 0.777030406838571`. It is not a closed root. Run:

```bash
python -m pytest -q tests/test_bhsm_aether_n3_response_resolution_v20_78_to_v20_79.py tests/test_bhsm_public_readiness_v6_21_0.py
python tools/audit_public_readiness.py --format human
python tools/audit_frozen_prediction_integrity.py
git diff --check
```

Then inspect the
[N=3 continuation ledger](BHSM_N3_CONTINUATION_LEDGER.md),
[rolling checkpoint artifact](../artifacts/BHSM_N3_FRESH_EIGENPAIR_CURVATURE_CONTINUATION_CHECKPOINT.json),
[claim boundaries](../CLAIMS.md), and [gate ledger](../theory/gate_ledger.md).
The checkpoint must show exact v21.32 -> v21.33 replay equivalence, fresh
curvature validation at every rolling step, strict exact-merit descent, and a
fresh rank-14 complete child passing eta, trace, constraints, momentum, flux,
persistence, and nonzero-motion gates at every promotion.

Do not compare legacy `~0.758...` residual values directly to the corrected
ordered-Rayleigh `~0.787...` series unless the legacy state is reevaluated with
the corrected definition.

## Historical v15.7 audit

Recommended current reviewer command:

```bash
python -m pytest -q tests/test_bhsm_aether_nonlinear_norman_cycle_bvp_v15_7.py tests/test_bhsm_public_status_sync_v15_7.py
```

Then inspect the
[controlling report](BHSM_NONLINEAR_NORMAN_CYCLE_BVP_AND_MAIN_SYNC_V15_7.md)
and run `python -m bhsm.interface physics-status --format json`.

## Historical v11.3 audit

```bash
python scripts/materialize_reciprocal_attachment_v11_3.py
python -m bhsm.interface reciprocal-attachment-status --format json
python -m bhsm.interface attachment-current-status --format markdown
python -m bhsm.interface three-mode-action-status-v11-3 --format markdown
python -m bhsm.interface mark-ii-status --format markdown
python -m pytest -q tests/test_bhsm_reciprocal_attachment_v11_3.py tests/test_current_program_status_v11_2.py
```

Expected verdict: `BHSM_RECIPROCAL_ATTACHMENT_ACTION_AND_CURRENT_DERIVED_WITH_THREE_MODE_DOMAIN_CONDITIONAL`.
Expected next object: `ACTION_NORMALIZED_CORE_WALL_RESPONSE_GRAM_HESSIAN_ON_COMMON_ATTACHMENT_DOMAIN`.

## Historical v11.2 audit

```bash
python scripts/materialize_complete_local_supported_action_v11_2.py
python -m bhsm.interface physical-completion-status-v11-2 --format markdown
python -m pytest -q tests/test_bhsm_complete_local_supported_action_v11_2.py
```

## Historical v11.1 audit

```bash
python scripts/materialize_support_representation_completion_v11_1.py
python -m bhsm.interface support-functor-status-v11-1 --format json
python -m bhsm.interface physical-completion-status-v11-1 --format markdown
python -m pytest -q tests/test_bhsm_support_representation_v11_1.py tests/test_current_program_status_v11_1.py
```

Expected verdict: `BHSM_SUPPORT_FUNCTOR_PHYSICAL_EQUIVALENCE_QUOTIENT_BLOCKED_BY_ABSENT_COMPLETE_LOCAL_BOUNDARY_AND_CORE_ACTION_DATA`.
Expected next object: `COMPLETE_LOCAL_SUPPORTED_ACTION_WITH_SUPPORT_DERIVATIVE_COUPLINGS_AND_BOUNDARY_CORE_CANONICAL_DOMAIN`.

- `reviewer-smoke`: `python -m pytest -q tests/test_engine_invariant_preservation.py tests/test_engine_physics_status_separation.py`
- `reviewer-full`: `python -m pytest -q`
- `reviewer-cern-open-data`: `python -m bhsm.interface.benchmarks.cern_open_data_benchmark --download --summary`
- `reviewer-invariants`: `python -m bhsm.interface engine-invariants --format json`
- `reviewer-claims-audit`: `python tools/audit_forbidden_claims.py`
- `reviewer-engine-report`: `python -m bhsm.interface engine-status --format markdown`
- `reviewer-physics-status`: `python -m bhsm.interface physics-status --format markdown`

The CERN command is `requires_network_or_cached_data`; all other listed status and invariant commands are offline.

The README animation itself is fully offline. To regenerate its compact sample
and assets, cache the checksum-pinned source and run:

```bash
python docs/assets/pr98_cms_open_data_animation/generate_pr98_cms_animation.py
```

The generator verifies the PR #98 SHA-256 before reading 64 deterministic
event rows. It never commits or embeds the complete source dataset.
<!-- BHSM_FIXED_H_VARIATIONAL_FAMILY_SOLVABILITY_V6_30_4 -->
## Reviewer checkpoint: v6.30.4

The v6.30.4 package is a same-domain Fredholm-solvability result, not a
potential or mass prediction. Reviewers should verify that D0 fixes
`r(q)=r0`, that D2 coefficients are absent from the selected source, that
the weighted KKT projection is exactly zero, and that both independent
numerical routes reproduce the constructed `Phi2`. The permission artifact
opens only v6.30.5; it explicitly leaves v6.31 closed.

<!-- BHSM_FIXED_H_LYAPUNOV_SCHMIDT_POTENTIAL_V6_30_5 -->
## Reviewer checkpoint: v6.30.5

Verify the sign and two-cap factor in `Gamma4=-2 Z5 g3`, the separation
between the blocked exact branch and valid reduced family, and the
field-dependent Noether completion. Confirm that the D0 kinetic norm
excludes historical D2 threading/Weyl pieces and that the scale artifact
explicitly denies v6.31 because `G5` is unselected.

## Reviewer checkpoint: v8.1

```bash
python -m bhsm.interface mode-resolved-curvature-status --format json
python -m bhsm.interface mode-resolved-curvature-status --format markdown
python -m bhsm.interface.master_action.mode_resolved_curvature_incidence --materialize
```

Verify the four-dimensional one-quarter trace split, the first-order
cap-identified Brown--York response, the second-order signed-even intrinsic
operator response, and the firewall between internal Hopf representations
and physical S3 momentum harmonics. The artifact must define no family
dimension, response matrix, mass ratio, or CKM result.

## Reviewer checkpoint: v8.2

```bash
python -m bhsm.interface generation-projector-action-status --format json
python -m bhsm.interface generation-projector-action-status --format markdown
python -m bhsm.interface.master_action.generation_projector_action_attachment --materialize
```

Verify the imported primitive spectrum `[1,2,3]`, the exact frozen
one-base-plus-two-excitation triples, source hashes, rank-three projectors,
and localized field/domain attachment. Confirm that higher tower modes are
not typed as extra generations, the `(6,0)` middle-up factor remains `1/2`,
no mode-stress matrix or flavor observable is fabricated, and the
domain-wall route remains a non-authoritative fallback.

## Reviewer checkpoint: v8.3

```bash
python -m bhsm.interface classical-mode-stress-status --format json
python -m bhsm.interface classical-mode-stress-status --format markdown
python -m bhsm.interface.master_action.classical_mode_stress_incidence --materialize
```

Verify that the frozen ledgers are unchanged and the basis-free projected
spectral route is exhausted. Confirm the exact associated-scalar operator,
the conditional proxy derivatives `(0,-2,-18)`, `(0,-72,-128)`, and
`(0,0,-32)`, and the missing action intertwiner from frozen `(k,j,q)` slots
to normalized `(J,m)` eigenspaces. Confirm that proxy matrices are not
promoted, the formal M4 stress is rejected as family central, background
quadratic response is separated from quartic self-backreaction, response
matrices remain `None`, the virtual-door factor is applied zero times, and
no alpha factor is inserted.

## Reviewer checkpoint: v8.4--v9.0

```bash
python -m bhsm.interface composite-carrier-current-status --format json
python -m bhsm.interface topographic-profile-status --format json
python -m bhsm.interface complex-profile-status --format json
python -m bhsm.interface channel-normalization-status --format json
python -m bhsm.interface common-parent-current-status --format json
python -m bhsm.interface geometric-lens-status --format json
python -m bhsm.interface 8d-vacuum-flavor-status --format json
python scripts/materialize_action_selected_8d_vacuum_flavor_v9_0.py
```

Run the materializer twice and compare bytes. All matrices in the v8.5--v8.9
diagnostics must remain `PROXY_STRESS_TEST_ONLY`; the v9.0 physical matrix must
remain null unless the complete action-owned dependency chain is supplied.

## Reviewer checkpoint: v9.1

```bash
python -m bhsm.interface geometry-only-geon-fr-status --format json
python -m bhsm.interface geometry-only-geon-fr-status --format markdown
python scripts/materialize_geometry_only_geon_fr_carrier_v9_1.py
python -m pytest -q tests/test_bhsm_geometry_only_geon_fr_carrier_v9_1.py
```

Run the materializer twice and compare bytes. Verify that the declared
small-diffeomorphism quotient has `pi1=0`, that the optional `Theta_8=Z2`
large mapping class is not promoted to rotation/exchange or a local spinor,
and that the v6.6 mapping-space FR line remains adopted rather than
parent-derived. The closed-FLRW numerical branch is an ansatz validation only.
All physical Gram/Hessian/current/matrix and mass/lepton outputs must remain
null, and no minimal extension may be marked adopted.

## Reviewer checkpoint: v10.0

```bash
python -m bhsm.interface unified-envelopment-status --format json
python -m bhsm.interface dynamic-envelope-status --format json
python -m bhsm.interface completion-marks-status --format markdown
python -m bhsm.interface global-scale-status --format json
python -m bhsm.interface particle-orbit-status --format json
python scripts/materialize_unified_envelopment_foundation_v10_0.py
python -m pytest -q tests/test_bhsm_envelopment_foundation_v10_0.py tests/test_bhsm_dynamic_action_v10_0.py tests/test_bhsm_collective_reduction_v10_0.py tests/test_bhsm_floquet_v10_0.py tests/test_bhsm_completion_gate_v10_0.py
```

Run the materializer twice and compare bytes. Verify the independent profile
quadratures, symbolic equilibrium identities, four completion marks, unchanged
frozen-file hashes, null physical mass/matrices, and exact global-scale
degeneracy. The representative collective-radius calculation is `PROXY_ONLY`,
not a particle boundary-value solution.

## Reviewer checkpoint: v10.1

```bash
python -m bhsm.interface relational-envelopment-status --format json
python -m bhsm.interface topological-buoyancy-status --format json
python -m bhsm.interface global-conservation-status --format json
python -m bhsm.interface boundary-complementarity-status --format json
python -m bhsm.interface neutrino-identity-status --format json
python -m bhsm.interface relational-constraint-status --format json
python scripts/materialize_relational_envelopment_holism_v10_1.py
python -m pytest -q tests/test_bhsm_relational_axioms_v10_1.py tests/test_bhsm_geometry_reconciliation_v10_1.py tests/test_bhsm_topological_buoyancy_v10_1.py tests/test_bhsm_global_conservation_v10_1.py tests/test_bhsm_boundary_complementarity_v10_1.py tests/test_bhsm_neutrino_identity_v10_1.py tests/test_bhsm_relational_completion_gate_v10_1.py
```

Run the materializer twice. Verify doctrine SHA
`f981a6501526a3ff324cbf5cb4f1e26b1f7d3ecd0c7b2759c200f6aa1ee184b0`,
typed statuses, no `S3 x M4=M8` identification, no inserted buoyancy force,
the scalar-energy caveat, eta-sector-only complementarity, null neutrino
observables, and unchanged frozen hashes.

## Reviewer checkpoint: v10.4

```bash
python -m bhsm.interface spacetime-removal-depth-status --format json
python -m bhsm.interface spacetime-support-status --format json
python -m bhsm.interface support-action-status --format json
python -m bhsm.interface support-constraint-status --format json
python -m bhsm.interface core-stratum-status --format json
python -m bhsm.interface support-three-mode-status --format json
python -m bhsm.interface three-mode-action-status --format json
python -m bhsm.interface global-equilibrium-status --format json
python -m bhsm.interface cosmic-unit-anchor-status --format json
python -m bhsm.interface particle-cycle-status --format json
python -m bhsm.interface physical-mass-mixing-status --format json
python -m bhsm.interface v10-4-final-completion-status --format json
python scripts/materialize_spacetime_removal_completion_v10_4.py
python -m pytest -q tests/test_bhsm_proper_volume_depth_v10_4.py tests/test_bhsm_depth_constraint_reduction_v10_4.py tests/test_bhsm_spacetime_support_order_parameter_v10_4.py tests/test_bhsm_support_action_v10_4.py tests/test_bhsm_support_constraint_analysis_v10_4.py tests/test_bhsm_core_stratum_matching_v10_4.py tests/test_bhsm_support_three_mode_coupling_v10_4.py tests/test_bhsm_three_mode_action_v10_4.py tests/test_bhsm_global_equilibrium_scale_v10_4.py tests/test_bhsm_particle_generation_mass_mixing_v10_4.py tests/test_bhsm_final_completion_gate_v10_4.py
```

Run the materializer twice and compare bytes. Verify
`q_V=-(7/8)delta rho`, DeWitt coefficient `-42`, positive shape eigenvalues
`4/7` and `2`, the zero reduced volume projection, no propagated conformal
ghost claim, author-selected `upsilon` without an adopted action coefficient,
null three-mode/orbit/scale/mass/mixing
outputs, no particle calibration, and unchanged frozen predictions.

## Reviewer checkpoint: v11.0

```bash
python -m bhsm.interface canonical-ontology-status-v11 --format json
python -m bhsm.interface support-action-status-v11 --format json
python -m bhsm.interface core-transfer-status-v11 --format json
python -m bhsm.interface three-mode-status-v11 --format json
python -m bhsm.interface topological-buoyancy-status-v11 --format json
python -m bhsm.interface higgs-buoyancy-status-v11 --format json
python -m bhsm.interface geometric-charge-status-v11 --format json
python -m bhsm.interface quantum-measurement-status-v11 --format json
python -m bhsm.interface physical-completion-status-v11 --format markdown
python scripts/materialize_unified_physical_completion_v11_0.py
python -m pytest -q tests/test_bhsm_support_composition_v11_0.py tests/test_bhsm_supported_parent_action_v11_0.py tests/test_bhsm_core_stratum_action_v11_0.py tests/test_bhsm_canonical_crystallization_v11_0.py tests/test_bhsm_final_physical_gate_v11_0.py
```

Run the materializer twice and compare bytes. Verify typed doctrine boundaries,
the D00-D13 acyclic graph, logarithmic depth and Haar metric, unfixed support
characters and `lambda_D`, the infinite-distance core endpoint, null core
transfer/buoyancy/Higgs/charge/measurement outputs, unchanged frozen ledgers,
and no particle or cosmic calibration.

## Reviewer checkpoint: v10.3

```bash
python -m bhsm.interface deformation-domain-status --format json
python -m bhsm.interface embedding-constraint-status --format json
python -m bhsm.interface local-radion-status --format json
python -m bhsm.interface common-stress-pullback-status --format json
python -m bhsm.interface global-zero-mode-status --format json
python -m bhsm.interface deformation-selection-status --format json
python -m bhsm.interface common-envelopment-mode-status --format json
python -m bhsm.interface deformation-intertwiner-status --format json
python -m bhsm.interface coupled-deformation-rank-status --format json
python -m bhsm.interface three-mode-envelopment-status --format json
python -m bhsm.interface spacetime-removal-depth-v10-3-status --format json
python -m bhsm.interface three-mode-interference-status --format json
python -m bhsm.interface seam-projection-status --format json
python -m bhsm.interface global-scale-anchor-status --format json
python -m bhsm.interface generation-phase-interface-status --format json
python scripts/materialize_physical_deformation_domain_v10_3.py
python -m pytest -q tests/test_bhsm_full_configuration_space_v10_3.py tests/test_bhsm_embedding_constraint_v10_3.py tests/test_bhsm_local_radion_v10_3.py tests/test_bhsm_gauge_invariant_deformation_v10_3.py tests/test_bhsm_stress_pullback_v10_3.py tests/test_bhsm_global_zero_mode_v10_3.py tests/test_bhsm_common_envelopment_mode_v10_3.py tests/test_bhsm_deformation_intertwiner_v10_3.py tests/test_bhsm_effective_mode_reductions_v10_3.py tests/test_bhsm_coupled_physical_rank_v10_3.py tests/test_bhsm_three_mode_architecture_v10_3.py tests/test_bhsm_spacetime_removal_depth_v10_3.py tests/test_bhsm_three_mode_interference_v10_3.py tests/test_bhsm_seam_projection_v10_3.py tests/test_bhsm_global_scale_anchor_v10_3.py tests/test_bhsm_generation_phase_interface_v10_3.py tests/test_bhsm_deformation_selection_gate_v10_3.py
```

Run the materializer twice and compare bytes. Verify the historical-name
equivalences; codimensions four, one, and one for the three embedding problems;
Einstein-frame radion coefficient `6`; the gauge-invariant combination; formal
tangential delta stress and its shape-force divergence; the exact v6.27
seam--fold projection; the seam excluded from the physical-mode count; exactly
three author-ontology slots `q_C,q_W,q_D`; no eligible action-owned `q_D`;
null common three-mode matrices, interference output, and global scale; the
historical one-mode audit marked `INVALIDATED_BY_AUTHOR_ONTOLOGY`; no particle
calibration; and unchanged frozen predictions.

## Reviewer checkpoint: v10.2

```bash
python -m bhsm.interface normal-radion-status --format json
python -m bhsm.interface global-constraint-status --format json
python -m bhsm.interface topological-buoyancy-status --format json
python -m bhsm.interface local-backreaction-status --format json
python -m bhsm.interface buoyancy-weak-field-status --format json
python scripts/materialize_topological_buoyancy_functional_v10_2.py
python -m pytest -q tests/test_bhsm_normal_geometry_v10_2.py tests/test_bhsm_radion_variation_v10_2.py tests/test_bhsm_global_constraint_v10_2.py tests/test_bhsm_backreaction_v10_2.py tests/test_bhsm_buoyancy_functional_v10_2.py tests/test_bhsm_buoyancy_gate_v10_2.py
```

Run the materializer twice and compare bytes. Verify the exact projector and
collar identities, fixed-embedding action domain, strictly negative static
Hopf-radion curvature derivative, exhaustive rejection of all six global
constraint candidates, zero inherited mixed action blocks, null physical
depth/weak-field outputs, no numerical scan, and unchanged frozen predictions.

## Reviewer checkpoint: v10.1

```bash
python -m bhsm.interface relational-envelopment-status --format json
python -m bhsm.interface topological-buoyancy-status --format json
python -m bhsm.interface global-conservation-status --format json
python -m bhsm.interface boundary-complementarity-status --format json
python -m bhsm.interface neutrino-identity-status --format json
python -m bhsm.interface relational-constraint-status --format json
python scripts/materialize_relational_envelopment_holism_v10_1.py
python -m pytest -q tests/test_bhsm_relational_axioms_v10_1.py tests/test_bhsm_geometry_reconciliation_v10_1.py tests/test_bhsm_topological_buoyancy_v10_1.py tests/test_bhsm_global_conservation_v10_1.py tests/test_bhsm_boundary_complementarity_v10_1.py tests/test_bhsm_neutrino_identity_v10_1.py tests/test_bhsm_relational_completion_gate_v10_1.py
```

Run the materializer twice. Verify doctrine SHA
`f981a6501526a3ff324cbf5cb4f1e26b1f7d3ecd0c7b2759c200f6aa1ee184b0`,
typed statuses, no `S3 x M4=M8` identification, no inserted buoyancy force,
the scalar-energy caveat, eta-sector-only complementarity, null neutrino
observables, and unchanged frozen hashes.
