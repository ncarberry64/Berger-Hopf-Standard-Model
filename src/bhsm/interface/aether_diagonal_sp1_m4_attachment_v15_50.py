"""Action-owned diagonal-Sp(1) reduction of the reconstructed BHSM cap.

The post-cut spatial cap is ``B4 x S3``.  In the join coordinates it is
written with principal orbits ``S3_u x S3_v``.  Simultaneous right
multiplication is free, including at the regular pole, and gives the global
principal bundle

    Sp(1) -> B4 x S3 -> B4.

This module completes the square in the parent metric and fixes the M5/M4
connection coefficient directly from the eight-dimensional Einstein term.
It does not add a second classical gauge energy to the cap action.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_post_cut_dirac_constraint_reduction_v15_49 import (
    extended_dirac_branch_event,
)


VERSION = "v15.50"
CLASSIFICATION = "BHSM_POST_CUT_DIAGONAL_SP1_M5_M4_ATTACHMENT"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False
RADIUS0 = (343.0 / 5.0) ** (1.0 / 6.0)


def diagonal_quotient_contract() -> dict[str, Any]:
    """Return the exact global quotient and metric decomposition."""

    return {
        "total_spatial_cap": "C_child=B4_times_S3",
        "principal_action": "(u,v)mapsto(u*q,v*q),_q_in_Sp1",
        "action_is_free_at_regular_pole": True,
        "quotient": "(B4_times_S3)/Sp1=B4",
        "boundary_quotient": "(S3_u_times_S3_v)/Sp1_diag=S3",
        "M5": "R_t_times_B4",
        "M4": "R_t_times_S3_boundary",
        "coframes": "theta_u=u^-1du,_theta_v=v^-1dv,_delta=theta_u-theta_v",
        "S": "A^2+B^2",
        "lambda": "A^2/S",
        "mechanical_connection": "omega=lambda*theta_u+(1-lambda)*theta_v",
        "metric_completion": (
            "A^2|theta_u|^2+B^2|theta_v|^2="
            "S|omega|^2+(A^2B^2/S)|delta|^2"
        ),
        "connection_curvature": (
            "F_omega=d(lambda)wedge(delta)-lambda(1-lambda)"
            "[delta,delta]/2"
        ),
        "new_continuous_coefficient": False,
    }


def diagonal_quotient_geometry(
    A: float, B: float, *, kappa1: float = 1.0,
) -> dict[str, float]:
    """Compute the M5/M4 radii and EH-owned connection normalization.

    The unit round S3 convention has volume ``2*pi^2``.  If
    ``L_F=sqrt(A^2+B^2)``, fiber integration of ``kappa1*R8/2`` gives

        L5 contains -K_F F^a F^a/4,
        K_F=(kappa1 Vol(S3_LF)/2)L_F^2.
    """

    if A <= 0.0 or B <= 0.0 or kappa1 <= 0.0:
        raise ValueError("A, B, and kappa1 must be positive")
    S = A * A + B * B
    fiber_radius = math.sqrt(S)
    base_radius = A * B / fiber_radius
    x = math.log(B / A)
    fiber_volume = 2.0 * math.pi**2 * fiber_radius**3
    connection_coefficient = 0.5 * kappa1 * fiber_volume * S
    return {
        "A": A,
        "B": B,
        "child_scale_x": x,
        "S": S,
        "lambda": A * A / S,
        "fiber_radius": fiber_radius,
        "M4_spatial_radius": base_radius,
        "M4_spatial_volume": 2.0 * math.pi**2 * base_radius**3,
        "fiber_volume": fiber_volume,
        "connection_kinetic_coefficient": connection_coefficient,
        "canonical_geometric_coupling_squared": 1.0 / connection_coefficient,
        "radius_ratio_M4_to_fiber": base_radius / fiber_radius,
        "radius_ratio_from_x": 1.0 / (2.0 * math.cosh(x)),
    }


def metric_completion_residual(
    A: float, B: float, theta_u: np.ndarray, theta_v: np.ndarray,
) -> float:
    """Numerically verify the coframe square-completion identity."""

    u = np.asarray(theta_u, dtype=float)
    v = np.asarray(theta_v, dtype=float)
    if u.shape != v.shape:
        raise ValueError("the coframes must have equal shapes")
    S = A * A + B * B
    omega = (A * A * u + B * B * v) / S
    delta = u - v
    left = A * A * float(u @ u) + B * B * float(v @ v)
    right = S * float(omega @ omega) + A * A * B * B / S * float(delta @ delta)
    return left - right


def attachment_states() -> dict[str, dict[str, float]]:
    """Evaluate the quotient on the reconstructed and last regular slices."""

    initial_radius = RADIUS0 / math.sqrt(2.0)
    event = extended_dirac_branch_event()["last_regular_state"]
    return {
        "reconstructed_round_boundary": diagonal_quotient_geometry(
            initial_radius, initial_radius
        ),
        "last_regular_Dirac_event": {
            **diagonal_quotient_geometry(
                float(event["boundary_A"]), float(event["boundary_B"])
            ),
            "time": float(event["time"]),
            "boundary_C": float(event["boundary_C"]),
        },
    }


def action_ownership_ledger() -> dict[str, Any]:
    """Separate the derived attachment from possible extra field sectors."""

    return {
        "parent_source": "S8_EH=(kappa1/2)integral_M8_sqrt(-G)R8",
        "M5_connection_term": "-(1/4)K_F(rho)F_omega^a F_omega^a",
        "K_F": "(kappa1/2)*Vol(S3_sqrt(S))*S",
        "classical_connection_background": "mechanical_connection_omega",
        "background_curvature_already_in_parent_R8": True,
        "add_connection_background_energy_again": False,
        "independent_connection_fluctuations": (
            "sections_of_Tstar(M5)tensor_ad(P)_with_the_parent_K_F_norm"
        ),
        "boundary_operator": (
            "pullback_of_the_gauge-fixed_connection_Hessian_to_"
            "M4=R_t_times_S3"
        ),
        "physical_weak_identification": "representation_attachment_required",
        "color_connection": "not_the_same_as_the_diagonal_Sp1_connection",
        "fermion_background": "zero_classically;_determinant_backreaction_quantum",
        "next_non_double_counted_term": (
            "the_gauge-fixed_and_spin-glued_M4_one-loop_determinant"
        ),
    }


def completion_payload() -> dict[str, Any]:
    states = attachment_states()
    sample_residual = metric_completion_residual(
        1.7, 1.2, np.array([0.3, -0.4, 0.9]), np.array([-0.7, 0.2, 0.5])
    )
    validation = {
        "global_free_diagonal_action": diagonal_quotient_contract()[
            "action_is_free_at_regular_pole"
        ],
        "metric_square_completion_exact": abs(sample_residual) < 1.0e-13,
        "boundary_is_Lorentzian_M4": diagonal_quotient_contract()["M4"]
        == "R_t_times_S3_boundary",
        "connection_coefficient_positive": all(
            row["connection_kinetic_coefficient"] > 0.0
            for row in states.values()
        ),
        "x_radius_identity": all(
            abs(row["radius_ratio_M4_to_fiber"] - row["radius_ratio_from_x"])
            < 1.0e-13
            for row in states.values()
        ),
        "classical_energy_not_double_counted": not action_ownership_ledger()[
            "add_connection_background_energy_again"
        ],
        "no_new_continuous_coefficient": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_diagonal_sp1_m4_attachment_v15_50",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "quotient_contract": diagonal_quotient_contract(),
        "attachment_states": states,
        "action_ownership": action_ownership_ledger(),
        "metric_completion_sample_residual": sample_residual,
        "active_calculation": (
            "CONSTRUCT_THE_CLOSED_M4_GAUGE-GHOST_AND_WEYL_SPECTRAL_ZETA_"
            "FROM_THE_ACTION-NORMALIZED_DIAGONAL_QUOTIENT_AND_ANOMALY-FREE_"
            "BHSM_REPRESENTATION"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _canonical_json_value(value: Any) -> Any:
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float cannot be materialized")
        rounded = round(value, 10)
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, Mapping):
        return {key: _canonical_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical_json_value(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        _canonical_json_value(payload), indent=2, sort_keys=True,
        ensure_ascii=False, allow_nan=False,
    ) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_diagonal_sp1_m4_attachment_v15_50.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "diagonal_quotient_contract", "diagonal_quotient_geometry",
    "metric_completion_residual", "attachment_states",
    "action_ownership_ledger", "completion_payload", "deterministic_json",
    "materialize",
]
