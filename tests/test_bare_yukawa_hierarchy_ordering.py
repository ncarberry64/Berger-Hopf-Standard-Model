from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_bare_yukawa_gate import (  # noqa: E402
    build_gate_payload,
    scan_universal_parameters,
)


def _row_map(payload: dict) -> dict[tuple[str, str], dict]:
    return {
        (sector, row["label"]): row
        for sector, sector_payload in payload["sector_results"].items()
        for row in sector_payload["rows"]
    }


def test_main_scan_passes_charged_sector_ordering() -> None:
    payload = build_gate_payload()
    rows = _row_map(payload)
    assert rows[("charged_lepton", "middle")]["predicted"] > rows[("charged_lepton", "light")]["predicted"]
    assert rows[("up", "middle")]["predicted"] > rows[("up", "light")]["predicted"]
    assert rows[("down", "middle")]["predicted"] > rows[("down", "light")]["predicted"]
    assert payload["main_scan"]["ordering_pass"] is True
    assert payload["main_scan"]["all_charged_ordering_pass"] is True


def test_bare_only_and_current_candidate_response_scenarios_are_reported() -> None:
    payload = build_gate_payload()
    assert set(payload["scenario_comparison"]) == {"bare_only", "current_candidate_responses"}
    for scenario, result in payload["scenario_comparison"].items():
        assert result["ordering_pass"] is True
        assert result["verdict"].startswith("BARE_YUKAWA_NUMERICAL_GATE_")


def test_universal_scan_is_candidate_ordering_only_for_current_grid() -> None:
    payload = build_gate_payload()
    assert payload["verdict"] == "BARE_YUKAWA_NUMERICAL_GATE_TIER_C_ORDERING_ONLY"
    assert payload["main_scan"]["rms_log_error"] > 1.25
    assert payload["main_scan"]["max_abs_log_error"] > 2.5


def test_scan_function_returns_same_score_shape_for_each_scenario() -> None:
    bare = scan_universal_parameters("bare_only")
    current = scan_universal_parameters("current_candidate_responses")
    for result in (bare, current):
        assert result["ordering_pass"] is True
        assert result["rms_log_error"] > 0.0
        assert result["max_abs_log_error"] > 0.0
        assert len(result["rows"]) == 6
