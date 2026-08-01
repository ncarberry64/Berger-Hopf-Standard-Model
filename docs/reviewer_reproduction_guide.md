# Reviewer Reproduction Guide

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
python scripts/materialize_physical_deformation_domain_v10_3.py
python -m pytest -q tests/test_bhsm_full_configuration_space_v10_3.py tests/test_bhsm_embedding_constraint_v10_3.py tests/test_bhsm_local_radion_v10_3.py tests/test_bhsm_gauge_invariant_deformation_v10_3.py tests/test_bhsm_stress_pullback_v10_3.py tests/test_bhsm_global_zero_mode_v10_3.py tests/test_bhsm_common_envelopment_mode_v10_3.py tests/test_bhsm_deformation_intertwiner_v10_3.py tests/test_bhsm_effective_mode_reductions_v10_3.py tests/test_bhsm_coupled_physical_rank_v10_3.py tests/test_bhsm_deformation_selection_gate_v10_3.py
```

Run the materializer twice and compare bytes. Verify the historical-name
equivalences; codimensions four, one, and one for the three embedding problems;
Einstein-frame radion coefficient `6`; the gauge-invariant combination; formal
tangential delta stress and its shape-force divergence; the exact v6.27
seam--fold projection; `UNDEFINED_CROSS_DOMAIN` fold--Hopf mixed blocks; rank
bounds `{1,2}`; `EQUIVALENCE_UNRESOLVED` rather than inequivalence; null
physical outputs; and unchanged frozen predictions.

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
