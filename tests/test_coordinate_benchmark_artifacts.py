from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/coordinate_benchmark/coordinate_benchmark_results.json"
PNG = ROOT / "artifacts/coordinate_benchmark/coordinate_benchmark_latency.png"
PDF = ROOT / "output/pdf/BHSM_coordinate_method_benchmark.pdf"


def test_measured_benchmark_artifact_is_large_boundary_heavy_and_claim_bounded() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["dataset"]["event_count"] == 10_000_000
    assert payload["dataset"]["boundary_event_count"] == 3_500_000
    assert payload["correctness"]["all_kernels_equivalent"] is True
    assert payload["benchmark_status"] == "SYNTHETIC_MICROBENCHMARK_NOT_PRODUCTION_HEP_VALIDATION"
    assert payload["bhsm_kernel_status"] == "BHSM_INSPIRED_BOUNDARY_MAP_NOT_OFFICIAL_TRACKING_ENGINE"
    assert payload["hardware_counters"]["branch_mispredictions_collected"] is False


def test_benchmark_reports_both_scalar_and_vectorized_deltas() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    comparisons = payload["comparisons"]
    assert comparisons["scalar_baseline_speedup"] > 1.0
    assert comparisons["vectorized_control_speedup"] > 1.0
    assert comparisons["memory_reduction_vs_scalar_percent"] < 0.0
    assert comparisons["memory_reduction_vs_vectorized_control_percent"] > 0.0


def test_benchmark_graph_outputs_exist_and_have_expected_signatures() -> None:
    assert PNG.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    assert PDF.read_bytes().startswith(b"%PDF-")
