import json
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RADIUS = 5.5212888273161885e-11


def load(name: str) -> dict:
    return json.loads((BASE / name).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_segment1214_joint_domain_extension() -> None:
    cb = load("BHSM_N12_C2_SEGMENT1214_JOINT_NON_SCALE_CB_OPERATOR.json")
    suppressed = load(
        "BHSM_N12_C2_SEGMENT1214_JOINT_COMPLETE_SUPPRESSED_R_OPERATOR.json"
    )
    ddelta = load(
        "BHSM_N12_C2_SEGMENT1214_JOINT_NON_SCALE_DDELTA_OPERATOR.json"
    )
    duration = load(
        "BHSM_N12_C2_SEGMENT1214_JOINT_DURATION_DENSITY_COVECTOR.json"
    )
    assert all(item["validation_passed"] is True for item in (
        cb, suppressed, ddelta, duration,
    ))
    assert cb["domain"]["joint_action_radius"] == RADIUS
    assert cb["row_count"] == 97
    assert (
        suppressed["parent_ball_containment"]["node_1214_tube_radius"]
        == RADIUS
    )
    assert ddelta["transport"]["state_action_radius"] == RADIUS
    assert (
        ddelta["transport"]["transported_covector_zero_exclusion_margin_lower"]
        > 0.0
    )
    assert duration["tube"]["state_action_radius"] == RADIUS
    assert duration["covector"]["zero_exclusion_margin_lower"] > 0.0
    assert duration["adjudication"]["transposed_exact_segment_map_action"] == (
        "OPEN_CURRENT_OWNER"
    )
    assert duration["adjudication"]["Gate7"] == "OPEN"
    assert duration["adjudication"]["Gate8"] == "LOCKED"
    assert duration["FULL_BHSM_COMPLETE"] is False
    for payload in (cb, suppressed, ddelta, duration):
        for relative, digest in payload["inputs"].items():
            assert sha256(ROOT / relative) == digest
        if "data" in payload:
            assert sha256(ROOT / payload["data"]) == payload["data_SHA256"]
