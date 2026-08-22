import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_FINITE_FLOW_CONTINUATION_DICHOTOMY.json"
)


def test_finite_flow_continuation_dichotomy_is_scoped() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["theorem"]["unique_maximal_N12_solution_exists"] is True
    assert payload["theorem"][
        "return_exit_blowup_or_gap_outcome_selected"
    ] is False
    assert payload["continuum_transfer"][
        "continuum_maximal_flow_dichotomy_closed"
    ] is False
    assert payload["prediction_frozen"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
