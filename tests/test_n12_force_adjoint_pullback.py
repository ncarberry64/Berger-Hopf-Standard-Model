from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_force_adjoint_pullback.py"
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/BHSM_N12_FORCE_ADJOINT_PULLBACK.json"
)


def _payload() -> dict:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_adjoint_matches_forward_pullback_and_removes_time_shift() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    witness = payload["witness"]
    assert witness["forward_vs_adjoint_pullback_residual"] < 1.0e-12
    assert witness["moving_endpoint_time_shift_residual"] < 1.0e-12


def test_force_covector_does_not_require_forward_column_family() -> None:
    payload = _payload()
    consequence = payload["computational_consequence"]
    assert consequence["forward_Jacobi_columns_required"] == 0
    assert consequence["required_base_history"] is True
    assert consequence["second_state_or_operator_jet_required_before_first_force"] is False
    assert payload["inverse_free_Euler_Dirac_adjoint"][
        "highest_action_derivative_before_first_force"
    ] == "D3_L"


def test_physical_quotient_and_later_saddle_remain_open() -> None:
    payload = _payload()
    theorem = payload["continuous_adjoint_theorem"]
    assert theorem["physical_quotient_force"] == "F_phys=N_phys^dagger*q_xi"
    assert payload["computational_consequence"]["reset_representative_selected"] is False
    assert payload["claim_boundary"]["G7_08_actual_projected_force"] == "OPEN_CURRENT_OWNER"
    assert payload["claim_boundary"]["same_action_saddle"] == "PENDING_ON_FORCE_RESULT"
    assert payload["FULL_BHSM_COMPLETE"] is False
