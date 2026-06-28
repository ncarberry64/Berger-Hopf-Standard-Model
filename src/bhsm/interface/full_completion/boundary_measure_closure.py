"""Conditional closure of collar-measure shape and identity transport."""

from __future__ import annotations

import json
from fractions import Fraction
from functools import reduce
from operator import mul
from pathlib import Path
from typing import Iterable

from .common import BoundaryMeasureClosureResult, repository_root
from .priority import select_highest_leverage_target


SOURCE_ARTIFACTS = (
    "artifacts/BHSM_neutral_boundary_measure_v1_0.json",
    "artifacts/common_scale_boundary_transport_v1.json",
    "theory/theorem_discharge_collar_measure_extrinsic_geometry.md",
    "theory/theorem_discharge_complete_scalar_topographic_collar_action.md",
)


def collar_jacobian_from_principal_curvatures(
    rho: Fraction,
    principal_curvatures: Iterable[Fraction],
    *,
    orientation: int = 1,
) -> Fraction:
    """Evaluate det(I + orientation*rho*S) in a principal-curvature basis."""

    if orientation not in (-1, 1):
        raise ValueError("orientation must be -1 or 1")
    factors = (Fraction(1) + orientation * rho * Fraction(kappa) for kappa in principal_curvatures)
    return reduce(mul, factors, Fraction(1))


def boundary_jacobian_normalization(principal_curvatures: Iterable[Fraction]) -> Fraction:
    """The relative collar Jacobian is exactly one at rho=0."""

    return collar_jacobian_from_principal_curvatures(Fraction(0), principal_curvatures)


def same_scale_boundary_transport(mu_from: str, mu_to: str) -> Fraction | None:
    """Return the exact identity only when both scales are the same named scale."""

    return Fraction(1) if mu_from == mu_to else None


def build_boundary_measure_closure(
    repository: str | Path | None = None,
) -> BoundaryMeasureClosureResult:
    root = repository_root(repository)
    missing = tuple(path for path in SOURCE_ARTIFACTS if not (root / path).is_file())
    if missing:
        raise FileNotFoundError(f"missing boundary-measure sources: {', '.join(missing)}")

    measure = json.loads((root / SOURCE_ARTIFACTS[0]).read_text(encoding="utf-8"))
    transport = json.loads((root / SOURCE_ARTIFACTS[1]).read_text(encoding="utf-8"))
    geometry = (root / SOURCE_ARTIFACTS[2]).read_text(encoding="utf-8")
    source_search_complete = all(
        (
            measure["status"] == "OPEN_MISSING_BOUNDARY_MEASURE",
            transport["T_total(mu_BH_boundary -> mu_BH_boundary)"] == 1.0,
            "J(Y,rho) = det(I + rho S(Y))" in geometry,
            "J(Y,0) = 1" in geometry,
        )
    )
    selected = select_highest_leverage_target()
    return BoundaryMeasureClosureResult(
        target_id="boundary_measure_collar_transport",
        status_before="OPEN_MISSING_BOUNDARY_MEASURE",
        status_after="CONDITIONAL_BOUNDARY_MEASURE_SHAPE_DERIVED_PHYSICAL_NORMALIZATION_OPEN",
        closure_result="PARTIAL_CLOSURE_BOUNDARY_MEASURE_SHAPE_AND_IDENTITY_TRANSPORT",
        selected_by_predeclared_score=selected.target_id == "boundary_measure_collar_transport",
        source_search_complete=source_search_complete,
        source_artifacts=SOURCE_ARTIFACTS,
        collar_jacobian_formula="J(Y,rho)=det(I +/- rho S(Y))=sqrt(det h(Y,rho)/det h(Y,0))",
        boundary_normalization_formula="J(Y,0)=1",
        same_scale_transport_formula="T(mu_BH_boundary -> mu_BH_boundary)=1",
        collar_shape_derived_conditionally=source_search_complete,
        boundary_value_exact=boundary_jacobian_normalization((Fraction(1), Fraction(2))) == 1,
        same_scale_transport_exact=same_scale_boundary_transport("mu_BH_boundary", "mu_BH_boundary") == 1,
        physical_measure_normalization_available=bool(measure["physical_normalization_available"]),
        cross_scale_transport_available=False,
        physical_units_available=measure["unit"] is not None,
        closed_subblockers=(
            "relative collar Jacobian shape formula",
            "boundary-relative normalization J(Y,0)=1",
            "same-scale boundary transport identity",
        ),
        remaining_subblockers=(
            "BHSM-specific shape operator S(Y) and orientation",
            "physical dimension and absolute normalization of dmu_boundary dt",
            "neutral background energy density",
            "nontrivial cross-scale transport law",
            "complete collar edge and variation data",
        ),
        empirical_inputs_used=False,
        official_prediction_logic_changed=False,
        frozen_predictions_changed=False,
        claim_boundary=(
            "The relative collar-measure shape and same-scale identity transport are conditionally/exactly "
            "closed from existing artifacts. Physical measure units, absolute normalization, BHSM-specific "
            "shape data, and cross-scale transport remain open."
        ),
    )
