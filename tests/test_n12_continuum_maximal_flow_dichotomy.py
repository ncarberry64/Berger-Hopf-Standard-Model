import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_continuum_maximal_flow_dichotomy_is_fail_closed() -> None:
    artifact = json.loads(
        (ROOT / "artifacts" / "intrinsic_state_selection"
         / "BHSM_N12_CONTINUUM_MAXIMAL_FLOW_DICHOTOMY.json").read_text(
            encoding="utf-8"
        )
    )

    assert artifact["validation_passed"] is True
    assert artifact["domain"]["new_gate"] is False
    assert artifact["uniform_local_estimate"][
        "trajectory_sampling_used"
    ] is False
    assert artifact["maximal_flow_alternative"][
        "global_if_norm_and_all_existing_margins_remain_controlled"
    ] is True
    assert artifact["ordered_event"]["outcome_selected"] is False
    assert "GLOBAL_SIGN_OR_INTEGRATED_BOUND" in artifact[
        "flagship_chain"
    ]["active_lemma"]
