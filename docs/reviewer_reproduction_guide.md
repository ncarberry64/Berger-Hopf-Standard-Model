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
