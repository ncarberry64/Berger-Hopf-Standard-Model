"""Reference-set architecture for BHSM quark mass comparisons.

This module only organizes comparison schemes already represented in the
repository. It does not fetch external data, tune BHSM ratios, or implement
precision QCD.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from mass_scheme import MassReference, default_mass_references
from quark_running import (
    MZ,
    PLACEHOLDER_PRECISION_QCD,
    build_common_scale_references,
    build_threshold_common_scale_references,
)


MIXED_DEFAULT = "MIXED_DEFAULT"
COMMON_SCALE_APPROX = "COMMON_SCALE_APPROX"
THRESHOLD_AWARE_APPROX = "THRESHOLD_AWARE_APPROX"
PRECISION_QCD_PLACEHOLDER = "PRECISION_QCD_PLACEHOLDER"


@dataclass(frozen=True)
class QuarkMassReferenceSet:
    """One labeled quark-mass comparison reference set."""

    name: str
    status: str
    references: dict[str, MassReference]
    target_scale: float | None
    scheme_consistent: bool
    comparison_final: bool
    notes: tuple[str, ...]


def mixed_default_reference_set() -> QuarkMassReferenceSet:
    """Return the current mixed repository mass references."""

    refs = {
        key: value
        for key, value in default_mass_references()[MIXED_DEFAULT].items()
        if key in {"u", "c", "t", "d", "s", "b"}
    }
    return QuarkMassReferenceSet(
        name=MIXED_DEFAULT,
        status="SCHEME_SENSITIVE_BASELINE",
        references=refs,
        target_scale=None,
        scheme_consistent=False,
        comparison_final=False,
        notes=(
            "Current repository mass inputs are mixed across schemes/scales for quark ratios.",
            "Use for continuity with frozen residual ledgers, not final QCD comparison.",
        ),
    )


def common_scale_approx_reference_set(target_scale: float = MZ) -> QuarkMassReferenceSet:
    """Return fixed-nf one-loop-inspired common-scale approximate references."""

    refs = {
        key: value
        for key, value in build_common_scale_references(target_scale).items()
        if key in {"u", "c", "t", "d", "s", "b"}
    }
    return QuarkMassReferenceSet(
        name=COMMON_SCALE_APPROX,
        status="APPROXIMATE_RUNNING_SCAFFOLD",
        references=refs,
        target_scale=float(target_scale),
        scheme_consistent=True,
        comparison_final=False,
        notes=(
            "Fixed-nf one-loop-inspired common-scale scaffold.",
            "Not precision QCD; no final tolerance verdict should be based on this alone.",
        ),
    )


def threshold_aware_approx_reference_set(target_scale: float = MZ) -> QuarkMassReferenceSet:
    """Return piecewise-nf threshold-aware approximate references."""

    refs = {
        key: value
        for key, value in build_threshold_common_scale_references(target_scale).items()
        if key in {"u", "c", "t", "d", "s", "b"}
    }
    return QuarkMassReferenceSet(
        name=THRESHOLD_AWARE_APPROX,
        status="THRESHOLD_AWARE_APPROXIMATE_RUNNING_SCAFFOLD",
        references=refs,
        target_scale=float(target_scale),
        scheme_consistent=True,
        comparison_final=False,
        notes=(
            "Piecewise-nf approximate scaffold with threshold labels.",
            "Still not precision QCD and not a final scheme-consistent reference set.",
        ),
    )


def precision_qcd_placeholder_reference_set(target_scale: float = MZ) -> QuarkMassReferenceSet:
    """Return an explicit placeholder for future precision QCD references."""

    refs = {
        key: MassReference(
            particle=key,
            value=0.0,
            unit="GeV",
            scheme=PRECISION_QCD_PLACEHOLDER,
            scale=f"{float(target_scale):g} GeV",
            source_label=PLACEHOLDER_PRECISION_QCD,
            uncertainty=None,
            notes=(
                "Placeholder only; precision QCD matching values are not supplied.",
                "Do not compare BHSM predictions against this row.",
            ),
        )
        for key in ("u", "c", "t", "d", "s", "b")
    }
    return QuarkMassReferenceSet(
        name=PRECISION_QCD_PLACEHOLDER,
        status="PLACEHOLDER_NOT_COMPUTED",
        references=refs,
        target_scale=float(target_scale),
        scheme_consistent=False,
        comparison_final=False,
        notes=(
            "Future two-/three-loop threshold-matched reference set.",
            "Contains no precision numerical masses in this phase.",
        ),
    )


def available_reference_sets(target_scale: float = MZ) -> tuple[QuarkMassReferenceSet, ...]:
    """Return all Gate 2 reference-set definitions."""

    return (
        mixed_default_reference_set(),
        common_scale_approx_reference_set(target_scale),
        threshold_aware_approx_reference_set(target_scale),
        precision_qcd_placeholder_reference_set(target_scale),
    )


def reference_sets_asdict(target_scale: float = MZ) -> dict[str, Any]:
    """Return JSON-ready reference-set metadata."""

    return {item.name: asdict(item) for item in available_reference_sets(target_scale)}
