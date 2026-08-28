import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_RETAINED_CORRECTION_EIGENLINE_FIRST_JETS.json"
)


def test_retained_correction_eigenline_first_jets_are_scoped():
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert len(payload["rows"]) == 48
    assert payload["validation"]["same_selected_branch_24_on_all_seams"] is True
    assert payload["validation"][
        "branchwise_denominators_used_without_smallest_gap_collapse"
    ] is True
    assert payload["validation"][
        "retained_and_JAX_directional_D3_agree_below_1e_minus_10_relative"
    ] is True
    assert payload["claim_boundary"]["retained_center_eigenline_first_jet"] == (
        "DERIVED"
    )
    assert payload["claim_boundary"]["outward_eigenline_first_jet_tube"] == "OPEN"
    assert payload["claim_boundary"]["Gate7"] == "ACTIVE"
    assert payload["FULL_BHSM_COMPLETE"] is False
