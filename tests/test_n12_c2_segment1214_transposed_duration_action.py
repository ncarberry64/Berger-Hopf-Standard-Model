import json
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_C2_SEGMENT1214_TRANSPOSED_DURATION_ACTION.json"
)


def test_segment1214_transposed_duration_action() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["status"] == (
        "C2_SEGMENT1214_TRANSPOSED_DURATION_ACTION_CERTIFIED"
    )
    assert payload["segment"]["global_segment_index"] == 1214
    assert payload["segment"]["signed_descriptor_step_interval"][0] > 0.0
    assert payload["transposed_action"]["full_transition_matrix_inverted"] is False
    assert payload["transposed_action"]["zero_exclusion_margin_lower"] > 0.0
    assert payload["adjudication"]["segment1214_transposed_exact_map_action"] == (
        "CERTIFIED"
    )
    assert payload["adjudication"]["remaining_1221_segment_duration_actions"] == (
        "OPEN"
    )
    assert payload["adjudication"]["Gate7"] == "OPEN"
    assert payload["FULL_BHSM_COMPLETE"] is False
    for relative, digest in payload["inputs"].items():
        path = ROOT / relative
        content = path.read_bytes()
        if path.suffix.lower() in {".json", ".md", ".py"}:
            content = content.replace(b"\r\n", b"\n")
        assert hashlib.sha256(content).hexdigest().upper() == digest
