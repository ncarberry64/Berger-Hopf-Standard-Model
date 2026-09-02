"""Attach preserved BHSM particle fibers to an affine AE4 Dirac carrier jet.

The frozen ``(k,j)`` labels live in the internal Berger family factor.  The
round-S3 product-Dirac level ``n`` lives in the spacetime carrier factor.
This module keeps those indices distinct, evaluates the carrier Calderon
first jet, and tensors that common response with the already-derived family
projectors.  It neither rebuilds the particle spectrum nor interprets a raw
operator level as a physical mass.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np

from bhsm.interface.ae4_stratified_dirac_zeta_induced_owner import ACTION_VERSION
from bhsm.interface.aether_forward_c2_weyl_riccati import (
    finite_core_weyl_and_coefficient_cotangent,
)


CLASSIFICATION = "AE4_CURRENT_C2_AFFINE72_PARTICLE_FIBER_CALDERON"


def product_dirac_friedrichs_weyl_first_jet(
    *,
    log_radii: np.ndarray,
    normalized_proper_times: np.ndarray,
    proper_duration: float,
    log_radius_first_jet: np.ndarray,
    proper_duration_first_jet: np.ndarray,
    spatial_dirac_level: int,
    chirality: int,
    spectral_parameter: float = -1.0,
    decimal_precision: int = 60,
) -> dict[str, Any]:
    """Contract the product-Dirac Weyl cotangent with a carrier first jet."""

    x = np.asarray(log_radii, dtype=float)
    u = np.asarray(normalized_proper_times, dtype=float)
    x_first = np.asarray(log_radius_first_jet, dtype=float)
    duration_first = np.asarray(proper_duration_first_jet, dtype=float)
    duration = float(proper_duration)
    level = int(spatial_dirac_level)
    sign = int(chirality)
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
        or level < 0
        or sign not in (-1, 1)
    ):
        raise ValueError("finite carrier data, n>=0, and chirality +/-1 required")
    normalized_width = np.diff(u)
    proper_durations = duration * normalized_width
    duration_segment_first = normalized_width[:, None] * duration_first[None, :]
    eigenvalue = level + 1.5
    weyl = finite_core_weyl_and_coefficient_cotangent(
        log_radii=x,
        proper_durations=proper_durations,
        channel="product_Dirac",
        unit_channel_value=eigenvalue,
        chirality=sign,
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
        "spatial_carrier_manifold": "ROUND_S3",
        "spatial_dirac_level_n": level,
        "unit_radius_dirac_eigenvalue_mu_n": eigenvalue,
        "chirality": sign,
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
        "internal_Berger_family_mode_used_as_spatial_level": False,
        "raw_Dirac_level_identified_as_physical_mass": False,
    }


def attach_preserved_particle_fibers(
    *,
    log_radii: np.ndarray,
    normalized_proper_times: np.ndarray,
    proper_duration: float,
    log_radius_first_jet: np.ndarray,
    proper_duration_first_jet: np.ndarray,
    frozen_fiber_rows: Sequence[dict[str, Any]],
    spatial_dirac_level: int = 0,
    spectral_parameter: float = -1.0,
) -> dict[str, Any]:
    """Tensor one common carrier response with preserved family projectors."""

    rows = [dict(row) for row in frozen_fiber_rows]
    if len(rows) != 9:
        raise ValueError(
            "the nine provenance-frozen charged-sector fibers are required"
        )
    required = {"sector", "slot", "mode_label", "projector_rank"}
    if any(not required.issubset(row) for row in rows):
        raise ValueError("each frozen fiber row must carry its existing identity")
    if len({(row["sector"], int(row["slot"])) for row in rows}) != 9:
        raise ValueError("frozen fiber rows must be distinct")

    common = {
        "log_radii": log_radii,
        "normalized_proper_times": normalized_proper_times,
        "proper_duration": proper_duration,
        "log_radius_first_jet": log_radius_first_jet,
        "proper_duration_first_jet": proper_duration_first_jet,
        "spatial_dirac_level": spatial_dirac_level,
        "spectral_parameter": spectral_parameter,
    }
    chiral = {
        "plus": product_dirac_friedrichs_weyl_first_jet(**common, chirality=1),
        "minus": product_dirac_friedrichs_weyl_first_jet(**common, chirality=-1),
    }
    attached = []
    for row in rows:
        attached.append(
            {
                "sector": row["sector"],
                "slot": int(row["slot"]),
                "internal_Berger_mode_label_k_j": list(row["mode_label"]),
                "existing_projector_rank": int(row["projector_rank"]),
                "existing_parent_stop_event_child_enclosure_transport": row.get(
                    "parent_stop_event_child_enclosure_child_transport"
                ),
                "spatial_carrier_level_n": int(spatial_dirac_level),
                "carrier_response_key": "COMMON_LOWEST_SPATIAL_PRODUCT_DIRAC_BLOCK",
                "family_projector_reused": True,
                "internal_mode_relabelled_as_spatial_mode": False,
            }
        )
    return {
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "tensor_factor_rule": (
            "CALDERON_(n,chirality)_ON_CARRIER_SPINOR_TENSOR_"
            "Pi_(sector,slot)_ON_PRESERVED_INTERNAL_FAMILY_FIBER"
        ),
        "index_separation": {
            "internal_family_mode": "(k,j)_ON_BERGER_INTERNAL_FACTOR",
            "spatial_carrier_mode": "n_ON_ROUND_S3_SPACETIME_FACTOR",
            "indices_identified_with_each_other": False,
        },
        "spatial_carrier_level_n": int(spatial_dirac_level),
        "chiral_carrier_responses": chiral,
        "attached_particle_fibers": attached,
        "attached_fiber_count": len(attached),
        "carrier_response_is_family_central_before_existing_internal_operators": True,
        "existing_family_noncentral_operators_erased": False,
        "new_particle_labels": [],
        "particle_spectrum_rebuilt": False,
        "physical_mass_operator_derived": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "AE4_CURRENT_C2_AFFINE72_PRODUCT_DIRAC_CARRIER_FIRST_JET_EVALUATED": True,
        "ALL_NINE_EXISTING_CHARGED_PARTICLE_FIBERS_ATTACHED_TO_CARRIER": True,
        "INTERNAL_BERGER_AND_SPATIAL_DIRAC_MODE_INDICES_KEPT_DISTINCT": True,
        "AE4_CURRENT_C2_NONLINEAR72_PARTICLE_FIBER_CALDERON_DERIVED": False,
        "AE4_CURRENT_C2_PHYSICAL_FERMION_POLES_DERIVED": False,
        "CURRENT_C2_PHYSICAL_MASS_OPERATOR_DERIVED": False,
        "PARTICLE_SPECTRUM_REBUILT": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "attach_preserved_particle_fibers",
    "claim_boundary",
    "product_dirac_friedrichs_weyl_first_jet",
]
