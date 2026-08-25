from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / (
    "scripts/certify_n12_parametric_exterior_oracle_executable_interface.py"
)
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_PARAMETRIC_EXTERIOR_ORACLE_EXECUTABLE_INTERFACE.json"
)


def _payload() -> dict:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_executable_interface_is_stable_covariant_and_inverse_free() -> None:
    payload = _payload()
    witness = payload["executable_crosscheck"]
    assert payload["validation_passed"] is True
    assert witness["first_centered_difference_residual"] < 1.0e-9
    assert witness["second_centered_difference_residual"] < 2.0e-7
    assert all(
        value < 1.0e-12
        for value in witness["block_unitary_covariance_residuals"].values()
    )
    assert witness["explicit_matrix_inverse_formed"] is False


def test_two_chord_cutoff_is_not_promoted_to_force_domain() -> None:
    payload = _payload()
    chord = payload["tracked_two_chord_adjudication"]
    assert chord["first_chord_exact_shadowing"] == "CERTIFIED"
    assert chord["second_chord_exact_shadowing"] == "CERTIFIED"
    assert chord["certified_core_end"] == 2.0e-8
    assert chord["terminal_event_or_canonical_stop_at_core_end"] is False
    assert chord["may_be_used_as_complete_force_domain"] is False
    assert chord["terminal_recurrence_reopened"] is False
    assert chord["chord_03_authorized"] is False


def test_actual_parametric_data_remain_the_current_owner() -> None:
    payload = _payload()
    boundary = payload["claim_boundary"]
    assert boundary["stable_Weyl_value_first_second_jet_solver"] == "DERIVED"
    assert boundary["actual_parametric_exterior_oracle"] == "OPEN_CURRENT_OWNER"
    assert boundary["actual_projected_force"] == "OPEN"
    assert boundary["Gate8"] == "LOCKED"
    assert payload["FULL_BHSM_COMPLETE"] is False
