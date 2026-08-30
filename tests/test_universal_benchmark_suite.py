import pytest

from bhsm.interface.universal_benchmark_suite import (
    BenchmarkRequirement,
    BenchmarkSuite,
    evaluate_benchmark_suite,
)
from bhsm.interface.universal_prediction_freeze import FrozenPrediction
from bhsm.interface.universal_spectral_forecast import CertifiedInterval


def requirement(
    benchmark_id: str,
    mode_id: str,
    observable_id: str,
    *engines: str,
    dimensionful: bool = True,
) -> BenchmarkRequirement:
    return BenchmarkRequirement(
        benchmark_id=benchmark_id,
        mode_id=mode_id,
        observable_id=observable_id,
        allowed_classifications=("DERIVED_INTERVAL_PREDICTION",),
        required_engine_ids=engines,
        dimensionful=dimensionful,
        provenance=("pre-comparison benchmark definition",),
    )


def prediction(mode_id: str, observable_id: str, *, promoted: bool = True):
    return FrozenPrediction(
        prediction_id=f"prediction:{mode_id}:{observable_id}",
        mode_id=mode_id,
        observable_id=observable_id,
        classification="DERIVED_INTERVAL_PREDICTION",
        interval=CertifiedInterval(1.0, 2.0),
        categorical_value=None,
        action_version="TEST-ACTION",
        background_id="TEST-BACKGROUND",
        scale_map_id="TEST-SCALE",
        frozen_git_commit="freeze-commit",
        provenance=("same-action test prediction",),
        gate7_closed=promoted,
        engine_promotion_passed=promoted,
    )


def suite() -> BenchmarkSuite:
    return BenchmarkSuite(
        suite_id="BHSM-TEST-SUITE",
        requirements=(
            requirement("muon-g2", "muon-mode", "magnetic-moment", "form-factor", "loop"),
            requirement("new-mode-width", "mode-X", "total-width", "spectrum", "decay"),
        ),
        action_version="TEST-ACTION",
        background_id="TEST-BACKGROUND",
        scale_map_id="TEST-SCALE",
        definition_commit="benchmark-definition-commit",
        provenance=("benchmark suite frozen before comparison",),
    )


def test_complete_cross_sector_benchmark_suite() -> None:
    report = evaluate_benchmark_suite(
        suite(),
        (
            prediction("muon-mode", "magnetic-moment"),
            prediction("mode-X", "total-width"),
        ),
        available_engine_ids=("form-factor", "loop", "spectrum", "decay"),
    )
    assert report.complete is True
    assert all(row["status"] == "PROMOTED" for row in report.rows)
    assert report.metadata()["experimental_values_in_manifest"] is False
    report.require_complete()


def test_missing_prediction_engine_and_promotion_fail_closed() -> None:
    report = evaluate_benchmark_suite(
        suite(),
        (prediction("muon-mode", "magnetic-moment", promoted=False),),
        available_engine_ids=("form-factor",),
    )
    assert report.complete is False
    assert "muon-g2:prediction_not_physically_promoted" in report.blockers
    assert "muon-g2:missing_required_engines" in report.blockers
    assert "new-mode-width:missing_frozen_prediction" in report.blockers
    with pytest.raises(RuntimeError, match="prediction_not_physically_promoted"):
        report.require_complete()


def test_duplicate_requirement_or_prediction_pair_is_rejected() -> None:
    row = requirement("duplicate", "mode", "mass", "spectrum")
    with pytest.raises(ValueError, match="benchmark ids"):
        BenchmarkSuite(
            "bad-suite", (row, row), "A", "B", "S", "C", ("p",)
        )
    duplicate_prediction = prediction("mode", "mass")
    with pytest.raises(ValueError, match="duplicate frozen prediction"):
        evaluate_benchmark_suite(
            BenchmarkSuite(
                "single", (row,), "TEST-ACTION", "TEST-BACKGROUND",
                "TEST-SCALE", "commit", ("p",),
            ),
            (duplicate_prediction, duplicate_prediction),
            available_engine_ids=("spectrum",),
        )
