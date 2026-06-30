from __future__ import annotations

import json
from pathlib import Path

from tools.run_linux_perf_profile import derived_metrics, parse_perf_stat


ROOT = Path(__file__).resolve().parents[1]


def test_perf_parser_and_derived_rates() -> None:
    text = "\n".join(
        (
            "200000000;;cycles;100.00;1.0;;",
            "400000000;;instructions;100.00;1.0;;",
            "1000000;;branches;100.00;1.0;;",
            "10000;;branch-misses;100.00;1.0;;",
            "500000;;cache-references;100.00;1.0;;",
            "25000;;cache-misses;100.00;1.0;;",
        )
    )
    counters = parse_perf_stat(text)
    metrics = derived_metrics(counters)
    assert metrics["instructions_per_cycle"] == 2.0
    assert metrics["branch_miss_rate"] == 0.01
    assert metrics["cache_miss_rate"] == 0.05


def test_profile_status_does_not_invent_hardware_results() -> None:
    payload = json.loads(
        (ROOT / "artifacts/native_microarchitecture_profile/profile_status.json").read_text(
            encoding="utf-8"
        )
    )
    assert payload["status"] == "PROFILING_HARNESS_READY_COUNTERS_NOT_COLLECTED"
    assert payload["measured_values"] is None
    assert payload["hardware_explanation_claimed"] is False
    assert payload["frozen_predictions_changed"] is False


def test_native_harness_is_target_scoped_and_self_testing() -> None:
    cmake = (ROOT / "CMakeLists.txt").read_text(encoding="utf-8")
    source = (
        ROOT / "integrations/native-benchmark/native_coordinate_benchmark.cxx"
    ).read_text(encoding="utf-8")
    assert "bhsm_native_coordinate_benchmark" in cmake
    assert "bhsm_native_coordinate_self_test" in cmake
    assert "--self-test" in source
    assert "NATIVE_COORDINATE_PROFILE_KERNEL" in source
