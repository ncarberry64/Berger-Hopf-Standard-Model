from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_CURRENT_GREEN_MIXED_TRANSVERSE_COMPUTE_BENCHMARK.json"


def test_compute_benchmark_selects_minimum_precision_and_worker_knee() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["selected_precision_bits"] == 192
    assert payload["selected_worker_count"] == 8
    assert payload["precision_benchmarks"]["128"][
        "maximum_scaled_component_radius"
    ] > 0.1
    assert payload["precision_benchmarks"]["192"][
        "maximum_scaled_component_radius"
    ] < 2.0e-16
    assert set(payload["parallel_worker_benchmarks"]) == {"1", "2", "4", "8", "16"}


def test_named_benchmark_files_match_hashes() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    for relative, expected in payload["named_benchmark_inputs"].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest().upper() == expected
