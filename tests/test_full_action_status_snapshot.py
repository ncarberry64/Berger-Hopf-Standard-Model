from bhsm.interface.full_action_closure.common import build_status_snapshot


def test_snapshot_keeps_completion_open():
    payload = build_status_snapshot()
    assert payload["status"] == "FULL_BHSM_NOT_COMPLETE"
    assert payload["frozen_predictions_changed"] is False
    assert payload["official_prediction_logic_changed"] is False
