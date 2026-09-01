from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_C2_EXTENDED_DESCRIPTOR_RESOLUTION_AUDIT.json"
)


def test_n12_c2_extended_descriptor_resolution_audit() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["cover"]["certified_additional_box_count"] == 434
    assert payload["cover"]["certified_total_segment_count"] == 436
    assert payload["cover"]["exhaustion_classification"] == (
        "CURRENT_BINARY64_SIGNED_DESCRIPTOR_INCREMENT_NOT_RESOLVED"
    )
    witness = payload["cover"]["resolution_witness"]
    assert witness["attempted_cover_index_after_two_segment_prefix"] == 435
    assert witness["step_to_ulp_ratio"] < 1.0
    assert witness["binary64_signed_lambda_end"] == witness["signed_lambda_start"]
    assert witness["binary64_physical_u_increment"] == 0.0
    assert payload["arithmetic_adjudication"]["physical_event_reached"] is False
    assert payload["arithmetic_adjudication"]["canonical_stop_reached"] is False
    assert payload["claim_boundary"]["chord_03_authorized"] is False
