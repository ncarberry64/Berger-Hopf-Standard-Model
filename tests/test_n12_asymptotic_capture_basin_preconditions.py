from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_n12_asymptotic_capture_basin_preconditions.py"
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_ASYMPTOTIC_CAPTURE_BASIN_PRECONDITIONS.json"
)


def _payload() -> dict:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_two_jet_and_single_branch_are_not_promoted_to_a_basin() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    assert payload["certified"]["one_complete_action_analytic_infinity_branch"] is True
    assert payload["not_certified"]["open_local_capture_basin"] is False
    assert payload["not_certified"]["AE2_reset_image_intersects_capture_basin"] is False
    assert payload["supersession"]["open_basin_promotion_authorized"] is False


def test_missing_nonlinear_leading_weight_identity_is_localized() -> None:
    payload = _payload()
    obstruction = payload["logical_obstruction"]
    assert obstruction["known_jet_conditions"] == "N7(0,0)=0_AND_D_N7(0,0)=0"
    assert "N7(a,0)=0" in obstruction["missing_identity"]
    assert "CUBIC_WEIGHT_SEVEN_ACTION_TERM" in obstruction["why_two_jet_is_insufficient"]


def test_gate_and_owner_boundaries_remain_frozen() -> None:
    payload = _payload()
    boundary = payload["claim_boundary"]
    assert boundary["Gate7"].startswith("ACTIVE_")
    assert boundary["Gate8"] == "LOCKED"
    assert boundary["chord_03_authorized"] is False
    assert boundary["frozen_predictions_changed"] is False
    assert boundary["FULL_BHSM_COMPLETE"] is False
