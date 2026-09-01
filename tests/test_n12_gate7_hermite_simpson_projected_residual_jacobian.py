from __future__ import annotations
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_HERMITE_SIMPSON_PROJECTED_RESIDUAL_JACOBIAN_ADJUDICATION.json"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_projected_residual_jacobian_route_is_rejected() -> None:
    p = json.loads(RESULT.read_text(encoding="utf-8"))
    assert p["validation_passed"] is True
    assert p["adjudication"]["hybrid_graph_Jacobian_as_complete_block_derivative"] == "REJECTED"
    assert p["adjudication"]["further_scalar_damping_of_same_direction"].startswith("REJECTED")
    assert p["summary"]["actual_to_stored_model_scale_ratio"] > 100.0
    assert p["summary"]["next_secant_optimal_alpha"] < 1.0e-3
    assert p["claim_boundary"]["continuous_action_constrained_center"].startswith("OPEN")
    assert p["FULL_BHSM_COMPLETE"] is False


def test_projected_residual_jacobian_provenance_matches_disk() -> None:
    p = json.loads(RESULT.read_text(encoding="utf-8"))
    for relative, expected in p["inputs"].items():
        assert _sha256(ROOT / relative) == expected
