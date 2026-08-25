from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / (
    "scripts/derive_n12_parametric_reset_fiber_exterior_oracle_theorem.py"
)
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_PARAMETRIC_RESET_FIBER_EXTERIOR_ORACLE_THEOREM.json"
)


def _payload() -> dict:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_finite_stratum_regularity_is_derived_without_global_switch_claim() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    assert payload["adjudication"]["regularity_theorem"] == (
        "DERIVED_CONDITIONAL_ON_FIXED_REGULAR_FINITE_ENDPOINT_STRATUM"
    )
    assert payload["adjudication"][
        "global_smoothness_across_endpoint_switches_claimed"
    ] is False
    assert payload["adjudication"]["infinite_tail_analysis_reopened"] is False


def test_single_reset_representative_is_not_promoted() -> None:
    payload = _payload()
    assert payload["theorem_domain"]["raw_fixed_event_reset_tangent_dimension"] == 67
    assert payload["theorem_domain"][
        "retained_post_time_quotient_dimension_count"
    ] == 66
    assert payload["single_representative_necessity"]["selector_forbidden"] is True
    assert payload["adjudication"][
        "single_hand_selected_reset_history_sufficient"
    ] is False


def test_schur_response_derivatives_are_crosschecked_exactly() -> None:
    payload = _payload()
    witness = payload["exact_algebraic_crosscheck"]
    assert witness["value_identity_exact"] is True
    assert witness["first_identity_exact"] is True
    assert witness["second_identity_exact"] is True
    assert witness["first_directional_derivative"]["exact"] == (
        witness["independent_dual_number_first"]["exact"]
    )
    assert witness["second_directional_derivative"]["exact"] == (
        witness["independent_dual_number_second"]["exact"]
    )


def test_actual_oracle_force_and_hessian_remain_open() -> None:
    payload = _payload()
    boundary = payload["claim_boundary"]
    assert boundary["actual_parametric_exterior_oracle"] == "OPEN_CURRENT_OWNER"
    assert boundary["actual_projected_force"] == "OPEN"
    assert boundary["geometry_reset_KKT_Hessian"] == "OPEN"
    assert boundary["Gate8"] == "LOCKED"
    assert payload["FULL_BHSM_COMPLETE"] is False
