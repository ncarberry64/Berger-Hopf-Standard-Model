from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.run_root_imt_scaling import add_scaling_metrics, parse_threads


ROOT = Path(__file__).resolve().parents[1]


def test_thread_parser_requires_unique_positive_counts() -> None:
    assert parse_threads("1,2,4,8") == [1, 2, 4, 8]
    with pytest.raises(ValueError):
        parse_threads("1,2,2")
    with pytest.raises(ValueError):
        parse_threads("0,1")


def test_scaling_metrics_use_one_thread_baseline() -> None:
    rows = add_scaling_metrics(
        [
            {"threads": 1, "entries_per_second": 100.0, "checksum_ok": True},
            {"threads": 2, "entries_per_second": 180.0, "checksum_ok": True},
            {"threads": 4, "entries_per_second": 320.0, "checksum_ok": True},
        ]
    )
    assert rows[1]["speedup_vs_one_thread"] == 1.8
    assert rows[1]["parallel_efficiency"] == 0.9
    assert rows[2]["parallel_efficiency"] == 0.8


def test_status_reports_unfavorable_ci_scaling_without_preclaim() -> None:
    payload = json.loads(
        (ROOT / "artifacts/root_imt_scaling/scaling_status.json").read_text(encoding="utf-8")
    )
    assert payload["status"] == "ROOT_IMT_SCALING_MEASURED_ENVIRONMENT_SPECIFIC"
    assert payload["linear_scaling_claimed"] is False
    assert payload["two_thread_improvement_observed"] is False
    assert payload["rows"][1]["speedup_vs_one_thread"] < 1.0
    assert payload["all_checksums_pass"] is True
    assert payload["frozen_predictions_changed"] is False


def test_cmake_builds_and_smoke_tests_root_imt_target() -> None:
    cmake = (ROOT / "CMakeLists.txt").read_text(encoding="utf-8")
    source = (ROOT / "integrations/cern-root/tests/root_imt_scaling.cxx").read_text(
        encoding="utf-8"
    )
    assert "bhsm_root_imt_scaling" in cmake
    assert "bhsm_root_imt_scaling_smoke" in cmake
    assert "ROOT::EnableImplicitMT(threads)" in source
    assert "checksum_ok" in source
