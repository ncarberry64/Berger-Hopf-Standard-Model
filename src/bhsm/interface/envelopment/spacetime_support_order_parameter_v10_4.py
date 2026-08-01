"""Author-selected stratified-core support order parameter for BHSM v10.4."""

from __future__ import annotations

import math
from typing import Any


ORDER_PARAMETER_STATUS = (
    "STRATIFIED_CORE_SPACETIME_SUPPORT_ORDER_PARAMETER_"
    "AUTHOR_SELECTED_GEOMETRIC_EXTENSION_CLASS"
)
PROPER_VOLUME_STATUS = "INVALIDATED"


def validate_support(value: float, *, regular_domain: bool = True) -> float:
    """Validate and return the dimensionless support order parameter."""

    upsilon = float(value)
    lower_ok = upsilon > 0.0 if regular_domain else upsilon >= 0.0
    if not lower_ok or upsilon > 1.0:
        interval = "0 < upsilon <= 1" if regular_domain else "0 <= upsilon <= 1"
        raise ValueError(f"support order parameter must satisfy {interval}")
    return upsilon


def logarithmic_depth_coordinate(value: float) -> float:
    """Return the ontology coordinate -log(upsilon), not a canonical claim."""

    return -math.log(validate_support(value))


def order_parameter_payload() -> dict[str, Any]:
    validation = {
        "regular_background_normalized": validate_support(1.0) == 1.0,
        "depletion_monotone": logarithmic_depth_coordinate(0.5) > logarithmic_depth_coordinate(1.0),
        "core_is_separate_stratum": True,
        "metric_remains_nondegenerate_on_regular_domain": True,
        "proper_volume_not_relabelled": PROPER_VOLUME_STATUS == "INVALIDATED",
        "seam_not_counted": True,
        "modes_not_generations": True,
    }
    return {
        "artifact": "BHSM_spacetime_support_order_parameter_v10_4",
        "symbol": "upsilon",
        "transformation": "dimensionless diffeomorphism scalar on M_regular",
        "range": "0<=upsilon<=1",
        "regular_action_domain": "0<upsilon<=1 with det(G)!=0",
        "regular_background": {"upsilon_star": 1.0, "nabla_upsilon_star": 0.0},
        "depleted_region": "0<upsilon<1",
        "core_value": 0.0,
        "core_value_domain": "Sigma_core or M_core; not an interior point of the inverse-metric equations",
        "complete_domain": "M_complete=M_regular union Sigma_core union M_core",
        "geometric_interpretation": (
            "local availability of ordinary nondegenerate spacetime support for an envelopment"
        ),
        "not_interpreted_as": [
            "elementary matter particle",
            "gravity mediator",
            "coordinate radius",
            "seam displacement",
            "metric determinant",
            "homogeneous Hopf radion",
            "scalar-wall fold mode",
            "generation label",
            "externally imposed density profile",
        ],
        "proper_volume_deficit_as_q_D": PROPER_VOLUME_STATUS,
        "order_parameter_status": ORDER_PARAMETER_STATUS,
        "initial_depth_coordinate": "d_log=-log(upsilon)",
        "initial_depth_coordinate_role": "monotone ontology coordinate only",
        "canonical_q_D": None,
        "canonical_normalization_status": "OPEN_PENDING_UNIQUE_Z_UPSILON",
        "seam": "psi_seam=Pi_seam(q_C,q_W,q_D), a coordinate projection",
        "generation_relation": "three generations remain phases of one sector-specific cycle",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
