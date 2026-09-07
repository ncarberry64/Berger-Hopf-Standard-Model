"""Canonical-stop coexact gauge/BRST Calderon response on current C2."""

from __future__ import annotations

from typing import Any

import numpy as np

from bhsm.interface.ae4_stratified_dirac_zeta_induced_owner import ACTION_VERSION
from bhsm.interface.aether_forward_c2_weyl_riccati import (
    finite_core_weyl_and_coefficient_cotangent,
)
from bhsm.interface.aether_nonabelian_coexact_vertex_v16_03 import (
    coexact_curl_basis,
)


CLASSIFICATION = "AE4_CURRENT_C2_STOP_GAUGE_BRST_CALDERON"
LOWEST_COEXACT_CURL = 2.0
LOWEST_NONZERO_SCALAR_LAPLACIAN = 3.0


def stop_gauge_brst_calderon(
    *,
    log_radii: np.ndarray,
    proper_durations: np.ndarray,
    spectral_parameter: float = -1.0,
    friedrichs_terminal_selected: bool,
    decimal_precision: int = 60,
) -> dict[str, Any]:
    """Evaluate the lowest coexact and BRST boundary blocks at a stop.

    The canonical stop supplies the far Friedrichs form-core graph.  The
    transverse block uses the exact level-zero curl potential ``2^2=4``.
    The lowest nonconstant scalar harmonic has Laplacian three; the two real
    gauge/constraint coordinates and one complex ghost use that same scalar
    operator and the same terminal graph, so their graded boundary tractions
    cancel mode by mode.

    ``spectral_parameter`` is a negative-axis resolvent probe.  It is not
    interpreted as a fitted Lorentzian frequency or a photon residue.
    """

    if not bool(friedrichs_terminal_selected):
        raise ValueError("the canonical-stop Friedrichs terminal graph is required")
    decomposition = coexact_curl_basis(0)
    curl = np.asarray(decomposition["coexact_eigenvalues"], dtype=float)
    if curl.shape != (3,) or not np.array_equal(
        curl, np.full(3, LOWEST_COEXACT_CURL)
    ):
        raise ValueError("unexpected lowest coexact curl sector")

    common = {
        "log_radii": np.asarray(log_radii, dtype=float),
        "proper_durations": np.asarray(proper_durations, dtype=float),
        "channel": "scalar",
        "spectral_parameter": float(spectral_parameter),
        "terminal_load": None,
        "decimal_precision": int(decimal_precision),
    }
    transverse = finite_core_weyl_and_coefficient_cotangent(
        **common,
        unit_channel_value=LOWEST_COEXACT_CURL**2,
    )
    brst_scalar = finite_core_weyl_and_coefficient_cotangent(
        **common,
        unit_channel_value=LOWEST_NONZERO_SCALAR_LAPLACIAN,
    )
    transverse_weyl = float(transverse["Weyl_birth_value"])
    brst_weyl = float(brst_scalar["Weyl_birth_value"])
    coexact_block = transverse_weyl * np.eye(3)
    constraint_block = brst_weyl * np.eye(2)
    ghost_graded_block = -brst_weyl * np.eye(2)
    cancellation = constraint_block + ghost_graded_block
    return {
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "spectral_parameter": float(spectral_parameter),
        "spectral_domain": "REAL_NEGATIVE_AXIS_RESOLVENT_PROBE",
        "terminal_domain": "CANONICAL_STOP_FRIEDRICHS_FORM_CLOSURE",
        "coexact_curl_eigenvalues": curl,
        "coexact_potential_coefficient": LOWEST_COEXACT_CURL**2,
        "coexact_multiplicity": 3,
        "coexact_Weyl_birth_value": transverse_weyl,
        "coexact_D_spectral_parameter_Weyl": float(
            transverse["D_spectral_parameter_Weyl"]
        ),
        "coexact_D_uniform_log_R4_Weyl_decimal": transverse[
            "D_log_R4_uniform_shift_decimal"
        ],
        "coexact_boundary_block": coexact_block,
        "lowest_nonzero_scalar_laplacian": LOWEST_NONZERO_SCALAR_LAPLACIAN,
        "global_scalar_gauge_zero_mode_quotiented": True,
        "BRST_scalar_Weyl_birth_value": brst_weyl,
        "BRST_scalar_D_spectral_parameter_Weyl": float(
            brst_scalar["D_spectral_parameter_Weyl"]
        ),
        "constraint_two_real_boundary_block": constraint_block,
        "complex_ghost_graded_two_real_boundary_block": ghost_graded_block,
        "BRST_graded_boundary_block": cancellation,
        "BRST_graded_boundary_trace": float(np.trace(cancellation)),
        "BRST_cancellation_residual_norm": float(np.linalg.norm(cancellation)),
        "gauge_constraint_real_weight": 2,
        "complex_ghost_real_weight": -2,
        "same_scalar_operator_and_terminal_domain_for_BRST_pair": True,
        "coexact_supertrace_boundary_value": float(np.trace(coexact_block)),
        "total_gauge_BRST_supertrace_boundary_value": float(
            np.trace(coexact_block) + np.trace(cancellation)
        ),
        "all_boundary_blocks_finite": bool(
            np.all(np.isfinite(coexact_block))
            and np.all(np.isfinite(constraint_block))
            and np.all(np.isfinite(ghost_graded_block))
        ),
        "coexact_block_positive": bool(transverse_weyl > 0.0),
        "independent_gauge_or_ghost_normalization_inserted": False,
        "Lorentzian_frequency_or_residue_inferred_from_resolvent_probe": False,
        "particle_spectrum_rebuilt": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "AE4_CURRENT_C2_CANONICAL_STOP_COEXACT_CALDERON_CENTER_EVALUATED": True,
        "AE4_CURRENT_C2_CANONICAL_STOP_BRST_QUOTIENT_CENTER_EVALUATED": True,
        "AE4_CURRENT_C2_STOP_MATCHED_NONLINEAR_INTERVAL_GAUGE_BRST_BLOCK_DERIVED": False,
        "AE4_CURRENT_C2_PHYSICAL_EVENT_GAUGE_BRST_BLOCK_DERIVED": False,
        "CURRENT_C2_LORENTZIAN_MAXWELL_RESIDUE_DERIVED": False,
        "CURRENT_C2_NORMALIZED_PHOTON_PROPAGATOR_DERIVED": False,
        "PHYSICAL_ENCAPSULATION_IDENTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "LOWEST_COEXACT_CURL",
    "LOWEST_NONZERO_SCALAR_LAPLACIAN",
    "claim_boundary",
    "stop_gauge_brst_calderon",
]
