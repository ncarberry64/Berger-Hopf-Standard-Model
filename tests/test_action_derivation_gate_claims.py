from bhsm.interface.action_derivation_gates import build_action_derivation_report


def test_action_report_uses_no_empirical_theorem_inputs():
    report = build_action_derivation_report()
    assert report["no_empirical_theorem_inputs"] is True
    assert report["frozen_predictions_modified"] is False
    assert report["status"] == "ACTION_DERIVATION_GATES_OPEN"

