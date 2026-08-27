from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_n12_gate7_global_connection_obstruction.py"


def _payload():
    spec = importlib.util.spec_from_file_location(
        "gate7_global_connection_obstruction", SCRIPT
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_payload()


def test_globalization_audit_localizes_exact_connector() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    assert payload["status"] == "EXACT_GLOBAL_CONNECTION_OBSTRUCTION_LOCALIZED"
    assert payload["trend_audit"]["cover_segment_count"] == 16
    assert payload["trend_audit"]["theta_step_last_over_first"] < 0.03
    assert (
        payload["trend_audit"]["terminal_projection"]["remaining_log_epsilon_gap"]
        > 4900.0
    )
    assert (
        payload["globalization_audit"]["DEGREE_COVERING"]["degree_value"]
        == "UNDEFINED_NOT_ZERO"
    )
    assert payload["adjudication"]["another_local_block_authorized_as_default_next_step"] is False


def test_obstruction_does_not_overclaim_nonconnection_or_completion() -> None:
    payload = _payload()
    assert payload["adjudication"]["RESET_TO_CAPTURE_GLOBAL_CONNECTION_DERIVED"] is False
    assert payload["adjudication"]["RESET_TO_FIRST_RETAINED_STOP_DERIVED"] is False
    assert payload["adjudication"]["connection_mathematically_impossible"] is False
    assert payload["claim_boundary"]["actual_projected_zero_source_force"] == (
        "OPEN_AFTER_CONNECTION_OR_STOP"
    )
    assert payload["claim_boundary"]["frozen_predictions_changed"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
