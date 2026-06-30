from __future__ import annotations

import numpy as np

from bhsm.interface.benchmarks.coordinate_methods import (
    BHSM_KERNEL_STATUS,
    benchmark_kernel,
    generate_kinematic_dataset,
    validate_kernel_equivalence,
)


def test_dataset_is_deterministic_and_boundary_heavy() -> None:
    first, labels, summary = generate_kinematic_dataset(10_000, 0.30, 1729)
    second, _, second_summary = generate_kinematic_dataset(10_000, 0.30, 1729)
    assert np.array_equal(first, second)
    assert summary.sha256 == second_summary.sha256
    assert summary.boundary_event_count == 3_000
    assert np.count_nonzero(labels) == 3_000


def test_kernels_are_numerically_equivalent() -> None:
    states, _, _ = generate_kinematic_dataset(5_000, 0.40, 7)
    result = validate_kernel_equivalence(states)
    assert all(row["allclose_rtol_1e_12_atol_1e_12"] for row in result.values())
    assert max(row["max_absolute_difference"] for row in result.values()) < 1.0e-11


def test_benchmark_reports_timing_memory_and_counter_status() -> None:
    states, _, _ = generate_kinematic_dataset(2_000, 0.25, 11)
    result = benchmark_kernel("bhsm_boundary_vectorized", states, repeats=1)
    assert result.median_seconds > 0.0
    assert result.events_per_second > 0.0
    assert result.implementation_status == BHSM_KERNEL_STATUS
    assert result.hardware_branch_misses is None
    assert result.branch_counter_status


def test_benchmark_does_not_modify_frozen_model_files() -> None:
    import hashlib
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    expected = {
        "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
        "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
        "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
    }
    for relative, digest in expected.items():
        assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == digest
