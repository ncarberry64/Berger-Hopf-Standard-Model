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
