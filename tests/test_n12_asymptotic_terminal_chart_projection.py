from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "derive_n12_asymptotic_terminal_chart_projection.py"


def _payload():
    spec = importlib.util.spec_from_file_location("terminal_chart_projection", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_payload()


def test_terminal_projection_closes_map_but_not_connection() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    assert payload["map"]["descriptor_dimension"] == 74
    assert payload["supersession"]["terminal_transition_block"] == "CLOSED_BY_THIS_ARTIFACT"
    assert payload["supersession"]["remaining_connection_blocks"] == 1
    assert payload["claim_boundary"]["reset_to_capture_or_stop_certificate"] == "OPEN_CURRENT_OWNER"
    assert payload["claim_boundary"]["FULL_BHSM_COMPLETE"] is False


def test_capture_origin_replay_avoids_binary64_epsilon() -> None:
    payload = _payload()
    witness = payload["capture_origin_witness"]
    assert witness["binary64_epsilon_underflows"] is True
    assert witness["descriptor_norm"] < 1.0e-12
    assert payload["finite_core_diagnostic"]["inside_capture_tube"] is False
