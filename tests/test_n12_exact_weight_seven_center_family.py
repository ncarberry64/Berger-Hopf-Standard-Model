from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_exact_weight_seven_center_family.py"
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_EXACT_WEIGHT_SEVEN_CENTER_FAMILY.json"
)


def _payload() -> dict:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_complete_weight_seven_center_family_variations_cancel() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    identities = payload["exact_variational_identities"]
    assert identities["consequence"] == "N7(a,0)=0_ON_THE_EXACT_CENTER_FAMILY"
    assert identities["response_beta_squared_first_variation"] == 0
    check = payload["numerical_crosscheck"]
    assert check["maximum_coordinate_EL_residual"] < 5.0e-12
    assert check["maximum_constraint_residual"] < 5.0e-12


def test_family_exhausts_linear_physical_centers() -> None:
    payload = _payload()
    parameters = payload["exact_family"]["physical_parameters"]
    assert parameters == {
        "common_scale_orbit_phase": 1,
        "total": 25,
        "w_and_b_shape_parameters": 24,
    }
    assert payload["supersession"]["precondition_N7_a_0_identity"].startswith("CLOSED")


def test_normal_attraction_and_gate_remain_open() -> None:
    payload = _payload()
    owner = payload["remaining_basin_owner"]
    assert owner["nonlinear_normal_attraction_or_trapping_bound"] == "OPEN_CURRENT_OWNER"
    assert payload["supersession"]["open_capture_basin"] == "NOT_YET_DERIVED"
    assert payload["claim_boundary"]["Gate8"] == "LOCKED"
    assert payload["claim_boundary"]["chord_03_authorized"] is False
