"""Cross-sector benchmark manifest evaluation for frozen BHSM predictions.

A benchmark suite is declared before comparison and contains no measured
values.  Each row names an action-selected mode, observable, allowed derived
classification, required engine capabilities, and whether the universal scale
map is required.  The evaluator accepts only physically promoted frozen
predictions from one action/background provenance.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from bhsm.interface.universal_prediction_freeze import (
    DERIVED_CLASSIFICATIONS,
    FrozenPrediction,
)


@dataclass(frozen=True)
class BenchmarkRequirement:
    benchmark_id: str
    mode_id: str
    observable_id: str
    allowed_classifications: tuple[str, ...]
    required_engine_ids: tuple[str, ...]
    dimensionful: bool
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.benchmark_id or not self.mode_id or not self.observable_id:
            raise ValueError("benchmark, mode, and observable ids are required")
        if (
            not self.allowed_classifications
            or not set(self.allowed_classifications) <= DERIVED_CLASSIFICATIONS
        ):
            raise ValueError("benchmark classifications must be derived outputs")
        if not self.required_engine_ids or not self.provenance:
            raise ValueError("benchmark engines and provenance are required")


@dataclass(frozen=True)
class BenchmarkSuite:
    suite_id: str
    requirements: tuple[BenchmarkRequirement, ...]
    action_version: str
    background_id: str
    scale_map_id: str
    definition_commit: str
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.suite_id or not self.requirements:
            raise ValueError("benchmark suite id and requirements are required")
        benchmark_ids = [row.benchmark_id for row in self.requirements]
        pairs = [(row.mode_id, row.observable_id) for row in self.requirements]
        if len(benchmark_ids) != len(set(benchmark_ids)):
            raise ValueError("benchmark ids must be unique")
        if len(pairs) != len(set(pairs)):
            raise ValueError("benchmark mode/observable pairs must be unique")
        if not all((
            self.action_version,
            self.background_id,
            self.scale_map_id,
            self.definition_commit,
            self.provenance,
        )):
            raise ValueError("benchmark action/background/scale provenance is required")


@dataclass(frozen=True)
class BenchmarkSuiteReport:
    suite_id: str
    rows: tuple[dict, ...]
    blockers: tuple[str, ...]

    @property
    def complete(self) -> bool:
        return not self.blockers and all(row["status"] == "PROMOTED" for row in self.rows)

    def require_complete(self) -> None:
        if not self.complete:
            raise RuntimeError(
                "BHSM benchmark suite blocked by: " + ", ".join(self.blockers)
            )

    def metadata(self) -> dict:
        return {
            "suite_id": self.suite_id,
            "rows": list(self.rows),
            "required_benchmark_count": len(self.rows),
            "promoted_benchmark_count": sum(
                row["status"] == "PROMOTED" for row in self.rows
            ),
            "blockers": list(self.blockers),
            "complete": self.complete,
            "experimental_values_in_manifest": False,
            "comparison_used_to_select_prediction": False,
        }


def evaluate_benchmark_suite(
    suite: BenchmarkSuite,
    predictions: Iterable[FrozenPrediction],
    *,
    available_engine_ids: Iterable[str],
) -> BenchmarkSuiteReport:
    entries = tuple(predictions)
    keys = [(entry.mode_id, entry.observable_id) for entry in entries]
    if len(keys) != len(set(keys)):
        raise ValueError("benchmark inputs contain duplicate frozen prediction pairs")
    lookup = dict(zip(keys, entries))
    engines = set(available_engine_ids)
    rows: list[dict] = []
    blockers: list[str] = []
    for requirement in suite.requirements:
        key = (requirement.mode_id, requirement.observable_id)
        prediction = lookup.get(key)
        missing_engines = sorted(set(requirement.required_engine_ids) - engines)
        row_blockers: list[str] = []
        if prediction is None:
            row_blockers.append("missing_frozen_prediction")
        else:
            if not prediction.physically_promoted:
                row_blockers.append("prediction_not_physically_promoted")
            if prediction.classification not in requirement.allowed_classifications:
                row_blockers.append("prediction_classification_mismatch")
            if prediction.action_version != suite.action_version:
                row_blockers.append("action_version_mismatch")
            if prediction.background_id != suite.background_id:
                row_blockers.append("background_mismatch")
            if requirement.dimensionful and prediction.scale_map_id != suite.scale_map_id:
                row_blockers.append("universal_scale_map_mismatch")
            if (
                not requirement.dimensionful
                and prediction.scale_map_id not in (None, suite.scale_map_id)
            ):
                row_blockers.append("foreign_scale_map")
        if missing_engines:
            row_blockers.append("missing_required_engines")
        status = "PROMOTED" if not row_blockers else "OPEN_INTERNAL_BLOCKER"
        rows.append({
            "benchmark_id": requirement.benchmark_id,
            "mode_id": requirement.mode_id,
            "observable_id": requirement.observable_id,
            "prediction_id": None if prediction is None else prediction.prediction_id,
            "classification": (
                "OPEN_INTERNAL_BLOCKER"
                if prediction is None else prediction.classification
            ),
            "status": status,
            "missing_engine_ids": missing_engines,
            "blockers": row_blockers,
        })
        blockers.extend(
            f"{requirement.benchmark_id}:{blocker}" for blocker in row_blockers
        )
    return BenchmarkSuiteReport(
        suite_id=suite.suite_id,
        rows=tuple(rows),
        blockers=tuple(blockers),
    )


__all__ = [
    "BenchmarkRequirement",
    "BenchmarkSuite",
    "BenchmarkSuiteReport",
    "evaluate_benchmark_suite",
]
