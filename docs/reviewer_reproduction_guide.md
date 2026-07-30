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
python -m bhsm.interface original-generation-projector-status --format json
python -m bhsm.interface original-generation-projector-status --format markdown
python -m bhsm.interface.master_action.original_generation_projector --materialize
```

Verify the stored one-base-plus-two-excitation triples and rank-three input
projector. Check the complete roots
`(4r-3,r)`, `(4r+6,r)`, and `(12-2r,r)` in their declared ranges. Confirm
that `n_modes=2` is not promoted to an action theorem, the displayed higher
modes remain allowed, no mode-stress matrix or flavor observable is
fabricated, and the domain-wall fallback remains non-authoritative.
