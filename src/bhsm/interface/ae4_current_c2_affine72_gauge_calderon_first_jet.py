"""Proper-time gauge/BRST Calderon first jets on a supplied path family."""

from __future__ import annotations

from typing import Any

import numpy as np

from bhsm.interface.ae4_stratified_dirac_zeta_induced_owner import ACTION_VERSION
from bhsm.interface.aether_forward_c2_weyl_riccati import (
    finite_core_weyl_and_coefficient_cotangent,
)


CLASSIFICATION = "AE4_CURRENT_C2_AFFINE72_GAUGE_CALDERON_FIRST_JET"


def scalar_friedrichs_weyl_first_jet(
    *,
    log_radii: np.ndarray,
    normalized_proper_times: np.ndarray,
    proper_duration: float,
    log_radius_first_jet: np.ndarray,
    proper_duration_first_jet: np.ndarray,
    unit_potential_coefficient: float,
    spectral_parameter: float = -1.0,
    decimal_precision: int = 60,
) -> dict[str, Any]:
    """Contract the inverse-free Weyl cotangent with coefficient-path jets.

    The input coefficient derivative is taken at fixed normalized proper time
    ``u=tau/T``.  Hence ``h_i=T*(u_(i+1)-u_i)`` and
    ``D h_i=(u_(i+1)-u_i) D T``.  The far graph is the canonical-stop
    Friedrichs limit; no terminal load or derivative is inserted.
    """

    x = np.asarray(log_radii, dtype=float)
    u = np.asarray(normalized_proper_times, dtype=float)
    x_first = np.asarray(log_radius_first_jet, dtype=float)
    duration_first = np.asarray(proper_duration_first_jet, dtype=float)
    duration = float(proper_duration)
    if (
        x.ndim != 1
        or u.shape != x.shape
        or x_first.ndim != 2
        or x_first.shape[0] != x.size
        or duration_first.shape != (x_first.shape[1],)
        or x.size < 2
        or not np.all(np.isfinite(x))
        or not np.all(np.isfinite(u))
        or not np.all(np.isfinite(x_first))
        or not np.all(np.isfinite(duration_first))
        or not np.isfinite(duration)
        or duration <= 0.0
        or u[0] != 0.0
        or u[-1] != 1.0
        or np.any(np.diff(u) <= 0.0)
    ):
        raise ValueError("finite normalized proper-time path and first jets required")
    normalized_width = np.diff(u)
    proper_durations = duration * normalized_width
    duration_segment_first = normalized_width[:, None] * duration_first[None, :]
    weyl = finite_core_weyl_and_coefficient_cotangent(
        log_radii=x,
        proper_durations=proper_durations,
        channel="scalar",
        unit_channel_value=float(unit_potential_coefficient),
        spectral_parameter=float(spectral_parameter),
        terminal_load=None,
        decimal_precision=int(decimal_precision),
    )
    node_cotangent = np.asarray(weyl["D_log_R4_node_Weyl"], dtype=float)
    duration_cotangent = np.asarray(weyl["D_proper_duration_Weyl"], dtype=float)
    radius_part = node_cotangent @ x_first
    duration_part = duration_cotangent @ duration_segment_first
    total = radius_part + duration_part
    return {
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "unit_potential_coefficient": float(unit_potential_coefficient),
        "spectral_parameter": float(spectral_parameter),
        "terminal_domain": "CANONICAL_STOP_FRIEDRICHS_FORM_CLOSURE",
        "node_count": int(x.size),
        "segment_count": int(x.size - 1),
        "parameter_count": int(x_first.shape[1]),
        "proper_duration": duration,
        "Weyl_birth_value": float(weyl["Weyl_birth_value"]),
        "D_parameter_Weyl": total,
        "D_parameter_Weyl_radius_part": radius_part,
        "D_parameter_Weyl_duration_part": duration_part,
        "D_parameter_Weyl_2_norm": float(np.linalg.norm(total)),
        "D_parameter_Weyl_max_abs": float(np.max(np.abs(total))),
        "all_first_jet_values_finite": bool(np.all(np.isfinite(total))),
        "explicit_matrix_inverse_formed": False,
        "terminal_load_or_jet_inserted": False,
    }


def affine72_gauge_brst_first_jet(
    *,
    log_radii: np.ndarray,
    normalized_proper_times: np.ndarray,
    proper_duration: float,
    log_radius_first_jet: np.ndarray,
    proper_duration_first_jet: np.ndarray,
    spectral_parameter: float = -1.0,
) -> dict[str, Any]:
    """Return the coexact and cancelling scalar BRST first jets."""

    common = {
        "log_radii": log_radii,
        "normalized_proper_times": normalized_proper_times,
        "proper_duration": proper_duration,
        "log_radius_first_jet": log_radius_first_jet,
        "proper_duration_first_jet": proper_duration_first_jet,
        "spectral_parameter": spectral_parameter,
    }
    coexact = scalar_friedrichs_weyl_first_jet(
        **common,
        unit_potential_coefficient=4.0,
    )
    scalar = scalar_friedrichs_weyl_first_jet(
        **common,
        unit_potential_coefficient=3.0,
    )
    constraint = 2.0 * np.asarray(scalar["D_parameter_Weyl"], dtype=float)
    ghost = -2.0 * np.asarray(scalar["D_parameter_Weyl"], dtype=float)
    residual = constraint + ghost
    return {
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "coexact": coexact,
        "BRST_scalar": scalar,
        "constraint_two_real_first_jet": constraint,
        "complex_ghost_graded_two_real_first_jet": ghost,
        "BRST_graded_first_jet": residual,
        "BRST_first_jet_cancellation_residual_norm": float(
            np.linalg.norm(residual)
        ),
        "surviving_gauge_BRST_first_jet": np.asarray(
            coexact["D_parameter_Weyl"], dtype=float
        ),
        "independent_normalization_inserted": False,
        "particle_spectrum_rebuilt": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "AE4_CURRENT_C2_AFFINE72_PROPER_TIME_GAUGE_CALDERON_FIRST_JET_EVALUATED": True,
        "AE4_CURRENT_C2_NONLINEAR72_GAUGE_CALDERON_FIRST_JET_DERIVED": False,
        "AE4_CURRENT_C2_PHYSICAL_EVENT_GAUGE_BRST_BLOCK_DERIVED": False,
        "CURRENT_C2_LORENTZIAN_MAXWELL_RESIDUE_DERIVED": False,
        "PHYSICAL_ENCAPSULATION_IDENTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "affine72_gauge_brst_first_jet",
    "claim_boundary",
    "scalar_friedrichs_weyl_first_jet",
]
