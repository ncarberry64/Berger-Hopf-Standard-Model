# Workspace preservation — 24 September 2026

The user requested a clean, fully updated Git checkpoint. This commit preserves
29 pre-existing source, historical handoff, mission-ledger and backup files,
plus existing provenance-hash updates. Python sources parse and JSON payloads
parse. Their inclusion is not a new scientific validation or an authority
change. The current Gate 7 result remains the quadratic checkpoint in
`docs/GATE7_QUADRATIC_RESUME_20260924.md`.

Hidden numerical work caches remain on disk under explicit ignore rules; no
research data was deleted. The five formerly unregistered large inherited
inputs were verified byte-for-byte against `cef38b6b` and pinned in the exact
hash registry. Two historical mission ledgers are registered as preservation
artifacts, not new certificates.

Preserved paths:

- `BHSM_MANUAL_HANDOFF.md`
- `CONTINUE_BHSM_MANUALLY.ps1`
- `artifacts/BHSM_GLOBAL_ACTION_X2_SELECTION_V1.json`
- `artifacts/mission_state/BHSM_COSMOLOGY_MISSION_STATE_V1.json`
- `artifacts/mission_state/BHSM_COSMOLOGY_MISSION_STATE_V1.md`
- `artifacts/mission_state/BHSM_GATE7_AUTHORITATIVE_N12_LEDGER_V15.json`
- `artifacts/mission_state/BHSM_GATE7_ENDPOINT071_CONTINUATION_20260923.md`
- `artifacts/mission_state/BHSM_GATE7_ENDPOINT071_MIXED_REMAINDER_STATUS_20260923.json`
- `artifacts/mission_state/BHSM_GATE7_FULL_HISTORY_BOUNDARY_TRACE_V16.json`
- `artifacts/mission_state/BHSM_GATE7_FULL_HISTORY_PIPELINE_STATE_V17.json`
- `artifacts/mission_state/BHSM_GATE7_INTERVAL14_RECOVERY_PROBE_V1.json`
- `artifacts/mission_state/BHSM_GATE7_INTERVAL14_RECOVERY_PROBE_V1.md`
- `artifacts/mission_state/BHSM_GATE7_MIDPOINT14_REPRO_DIFF_V5.json`
- `artifacts/mission_state/BHSM_GATE7_POST_INTERVAL14_LEDGER_AUDIT_V14.json`
- `artifacts/mission_state/BHSM_SYSTEMS_INTEGRATION_V27_BACKUP/derive_n12_action_signed_interval_majorants.py.active_before`
- `artifacts/mission_state/BHSM_SYSTEMS_INTEGRATION_V27_BACKUP/derive_n12_gate7_exact_signed_mixed_field_curvature.py.active_before`
- `docs/BHSM_GLOBAL_ACTION_X2_SELECTION_V1.md`
- `scripts/audit_global_action_x2_selection_v1.py`
- `scripts/certify_n12_gate7_directional_tube_rows.py`
- `scripts/certify_n12_gate7_rebalanced_tube_operator.py`
- `scripts/certify_n12_gate7_signed_tube_operator.py`
- `scripts/certify_n12_gate7_signed_tube_rows.py`
- `scripts/diagnose_n12_gate7_eigenvalue_refined_mixed_only.py`
- `scripts/diagnose_n12_gate7_endpoint_mixed_remainder_transport.py`
- `scripts/diagnose_n12_gate7_primal_refined_saved_anchor_hessian.py`
- `scripts/diagnose_n12_gate7_saved_mixed_width_sources.py`
- `scripts/extract_gate7_local_cosmology_response_v1.py`
- `scripts/inspect_gate7_green_image_amplitude.py`
- `scripts/refine_n12_gate7_saved_mixed_normalization.py`
