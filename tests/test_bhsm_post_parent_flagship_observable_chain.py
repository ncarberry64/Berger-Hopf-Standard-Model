import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/qxi_relative_energy_preparation/"
    "BHSM_POST_PARENT_FLAGSHIP_OBSERVABLE_GATE.json"
)


def test_post_parent_flagship_observable_gate_fails_closed() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["CONTINUUM_EVENT_CHILD_CERTIFIED"] is True
    assert payload["prediction_frozen"] is False
    assert payload["held_out_comparison_performed"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
    rows = {row["candidate"]: row for row in payload["candidate_chain_audit"]}
    assert rows["matched_parent_Q_xi_and_Delta_H"][
        "parent_substitution_or_manual_zero_allowed"
    ] is False
    assert rows["internal_absolute_unit_ratios"]["values"] == {
        "M_BH_over_M_star": 0.5,
        "R_BH_over_ell_star": 2.0,
        "sigma_scale": 0.5,
    }
    assert payload["shortest_nonfabricated_flagship_route"]["first_missing_object"] == (
        "ACTION_SELECTED_INTRINSIC_PHYSICAL_STATE_AND_OBSERVABLE_MAP_ON_"
        "THE_CERTIFIED_CONTINUUM_CHILD"
    )
