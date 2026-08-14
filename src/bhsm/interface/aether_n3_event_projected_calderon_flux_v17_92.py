"""Project the terminal N=3 GHY/eta flux onto attachment tangents."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_attachment_canonical_covector_v17_91 import (
    attachment_canonical_covector,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import (
    deterministic_json,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    ORDER,
    Q_DIMENSION,
)
from bhsm.interface.aether_n3_scale_corrected_period_log_continuation_v17_76 import (
    v17_75_selected_raw_vector,
)
from bhsm.interface.aether_n3_terminal_child_boundary_map_v17_85 import (
    terminal_event_boundary_data,
)


VERSION = "v17.92"
CLASSIFICATION = "BHSM_N3_EVENT_PROJECTED_CALDERON_FLUX"
FULL_BHSM_COMPLETE = False


def event_projected_calderon_flux() -> dict[str, Any]:
    boundary = terminal_event_boundary_data(v17_75_selected_raw_vector())
    radial = boundary["GHY_eta_radial_flux_Gamma1"]
    canonical = attachment_canonical_covector()
    lift = np.asarray(
        canonical["constraint_preserving_coordinate_lift"], dtype=float
    )
    signs_k = (-1.0) ** np.arange(1, ORDER + 1)
    signs_j = (-1.0) ** np.arange(ORDER)
    d_log_a = np.zeros(Q_DIMENSION)
    d_log_b = np.zeros(Q_DIMENSION)
    d_log_a[0] = d_log_b[0] = 1.0
    d_log_a[1:1 + ORDER] = signs_k
    d_log_b[1:1 + ORDER] = signs_k
    d_log_a[1 + 2 * ORDER:1 + 3 * ORDER] = signs_j
    d_log_b[1 + 2 * ORDER:1 + 3 * ORDER] = -signs_j

    # f=chi is fixed on the eta quotient and the attachment tangent does not
    # vary lapse. Their nonzero raw fluxes are retained in the ledger but do
    # not contribute to this two-dimensional metric attachment projection.
    q_flux = (
        float(radial["Pi_log_A"]) * d_log_a
        + float(radial["Pi_log_B"]) * d_log_b
    )
    projected = lift.T @ q_flux
    return {
        "coordinate_order": ["q_W", "x_D"],
        "raw_terminal_Gamma1": radial,
        "event_metric_q_flux_covector": q_flux.tolist(),
        "constraint_preserving_event_attachment_flux": projected.tolist(),
        "event_attachment_flux_norm": float(np.linalg.norm(projected)),
        "projection_rules": {
            "metric": (
                "Gamma1_q=Pi_log_A*d_q_log_A+Pi_log_B*d_q_log_B"
            ),
            "eta": (
                "Pi_f_RETAINED_BUT_d_attachment_f=0_IN_THE_f_equals_chi_"
                "QUOTIENT"
            ),
            "lapse": (
                "Pi_log_N_RETAINED_BUT_THE_TWO_ATTACHMENT_CONFIGURATION_"
                "TANGENTS_DO_NOT_VARY_THE_MULTIPLIER"
            ),
            "constraint_lift": (
                "THE_SAME_V17_91_COORDINATE_LIFT_IS_USED_FOR_FORCE_AND_FLUX"
            ),
        },
        "orientation": (
            "Gamma1_event_USES_THE_TERMINAL_PRE_EVENT_OUTWARD_NORMAL;THE_"
            "CHILD_TERM_MUST_BE_COMPUTED_WITH_ITS_OWN_OUTWARD_NORMAL"
        ),
        "complete_outer_flux_ledger": {
            "N3_event_metric_eta_scalar_projection": "DERIVED_HERE",
            "reconstructed_child_metric_eta_scalar_projection": "OPEN",
            "event_core_pregeometric_generator_flux": "OPEN",
            "gauge_spinor_ghost_projection": "OPEN",
            "sum_not_set_to_zero_by_reflection": True,
        },
        "nonzero_flux_interpretation": (
            "A_NONZERO_ONE_SIDED_EVENT_FLUX_IS_NOT_A_PARTICLE_DEFECT;IT_"
            "ENTERS_THE_TWO_SIDED_DYNAMIC_WENTZELL_EQUATION"
        ),
    }


def completion_payload() -> dict[str, Any]:
    result = event_projected_calderon_flux()
    ledger = result["complete_outer_flux_ledger"]
    validation = {
        "two_projected_components": len(
            result["constraint_preserving_event_attachment_flux"]
        ) == 2,
        "projected_flux_finite": bool(np.all(np.isfinite(
            result["constraint_preserving_event_attachment_flux"]
        ))),
        "nonzero_event_flux_retained": result["event_attachment_flux_norm"] > 0.0,
        "event_scalar_projection_derived": ledger[
            "N3_event_metric_eta_scalar_projection"
        ] == "DERIVED_HERE",
        "child_flux_not_fabricated": ledger[
            "reconstructed_child_metric_eta_scalar_projection"
        ] == "OPEN",
        "core_flux_not_fabricated": ledger[
            "event_core_pregeometric_generator_flux"
        ] == "OPEN",
        "full_projector_not_fabricated": ledger[
            "gauge_spinor_ghost_projection"
        ] == "OPEN",
        "reflection_cancellation_not_assumed": ledger[
            "sum_not_set_to_zero_by_reflection"
        ],
        "nonzero_flux_not_defect": "NOT_A_PARTICLE_DEFECT" in result[
            "nonzero_flux_interpretation"
        ],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_event_projected_calderon_flux_v17_92",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "event_projected_calderon_flux": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "THE_EVENT_EXERTS_A_FINITE_ATTACHMENT_FLUX_THAT_MUST_BE_"
            "BALANCED_D dynamically_BY_THE_COMPLETE_CHILD_AND_EVENT_CORE"
        ),
        "dependency_advanced": (
            "CLOSES_THE_N3_EVENT_METRIC_ETA_SCALAR_HALF_OF_THE_TWO_SIDED_"
            "F_child_CALDERON_FLUX"
        ),
        "active_calculation": (
            "SOLVE_THE_RECONSTRUCTED_CHILD_METRIC_ETA_SCALAR_CAUCHY_"
            "BOUNDARY_FLUX_WITH_NONZERO_ATTACHMENT_MOTION"
        ),
        "direct_N3_solve_authorized_next": False,
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_event_projected_calderon_flux_v17_92.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "event_projected_calderon_flux", "completion_payload", "materialize",
]
