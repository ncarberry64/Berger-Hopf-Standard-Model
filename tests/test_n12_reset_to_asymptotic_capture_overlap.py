from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_n12_reset_to_asymptotic_capture_overlap.py"
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_RESET_TO_ASYMPTOTIC_CAPTURE_OVERLAP_AUDIT.json"
)


def _payload() -> dict:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_reset_epsilon_is_recomputed_but_no_capture_overlap_is_claimed() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    reset = payload["reset_data"]
    assert abs(reset["R4"] - 1.0023342201094778) < 1.0e-15
    assert 0.995 < reset["epsilon=R4^-2"] < 0.996
    assert payload["claim_boundary"]["reset_to_capture_overlap"] == "NOT_CERTIFIED"


def test_local_reset_ball_is_not_compared_to_asymptotic_radius() -> None:
    payload = _payload()
    assert payload["available_local_certificates"][
        "Calderon_action_coordinate_radius"
    ] == 7.62939453125e-17
    theorem = payload["noncomparison_theorem"]
    assert theorem[
        "Calderon_ball_radius_may_be_compared_directly_to_epsilon_star"
    ] is False
    assert theorem["one_stored_reset_representative_is_sufficient"] is False


def test_exact_join_requires_common_chart_set_containment() -> None:
    payload = _payload()
    missing = payload["missing_overlap_data"]
    assert missing["numeric_epsilon_star_lower"] is None
    assert missing["numeric_delta_star_lower"] is None
    assert missing["validated_reset_component_cover_to_capture_surface"] is None
    assert "ONE_COMMON_NORM_AND_CHART" in payload["exact_next_dependency"][
        "required_join"
    ]
    assert payload["claim_boundary"]["chord_03_authorized"] is False
