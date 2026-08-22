import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_FORWARD_TERMINAL_CHART_REACHABILITY_GATE.json"
)


def test_global_reachability_obstruction_is_localized_without_overclaim():
    data = json.loads(RESULT.read_text(encoding="utf-8"))
    assert data["validation_passed"] is True
    assert data["closed_local_structure"]["continuum_terminal_hitting_law"] is True
    assert data["closed_local_structure"]["regular_set_valued_reset_relation"] is True
    assert data["global_outcome"][
        "at_least_one_existing_forward_child_reaches_terminal_chart"
    ] is False
    assert data["global_outcome"][
        "no_existing_forward_child_reaches_terminal_chart"
    ] is False
    assert data["localized_obstruction"]["constraint_reduced_energy"] == (
        "IDENTICALLY_ZERO"
    )
    assert "OBSTRUCTION_TO_THE_CURRENT_GLOBAL_PROOF_ROUTE" in data[
        "localized_obstruction"
    ]["interpretation"]
    assert data["claim_boundaries"]["formal_reflection_quotiented"] is False
    assert data["claim_boundaries"][
        "matched_parent_Q_xi_or_Delta_H_unlocked"
    ] is False
    assert data["FULL_BHSM_COMPLETE"] is False
