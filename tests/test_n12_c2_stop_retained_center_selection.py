import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_C2_STOP_RETAINED_CENTER_SELECTION.json"
)


def test_quarter_step_center_reduces_correlated_defect() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    comparison = payload["comparison"]
    assert payload["validation_passed"] is True
    assert comparison["correlated_correction_reduction_factor"] > 5.0
    assert comparison["terminal_correction_reduction_factor"] > 9.0
    assert (
        comparison["quarter_step"]["correlated_correction_max"]
        < comparison["half_step"]["correlated_correction_max"]
    )


def test_center_selection_is_not_gate_or_physical_selector() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["selection_rule"].startswith("MINIMIZE_MATCHED_CORRELATED")
    assert payload["validation"][
        "selection_is_proof_coordinate_only_not_physical_selector"
    ] is True
    assert payload["claim_boundary"]["finite_interval_history_certified"] is False
    assert payload["claim_boundary"]["Gate7"].startswith("ACTIVE_")
    assert payload["claim_boundary"]["FULL_BHSM_COMPLETE"] is False
