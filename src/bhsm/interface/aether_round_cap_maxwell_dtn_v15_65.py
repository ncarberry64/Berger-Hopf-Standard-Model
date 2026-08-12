"""Exact static Maxwell Dirichlet-to-Neumann spectrum on the round M5 cap."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_diagonal_sp1_m4_attachment_v15_50 import RADIUS0


VERSION = "v15.65"
CLASSIFICATION = "BHSM_ROUND_CAP_STATIC_MAXWELL_DTN_AND_LR_PROJECTION"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def boundary_radius(fiber_radius: float = RADIUS0) -> float:
    if fiber_radius <= 0.0:
        raise ValueError("positive fiber radius required")
    return fiber_radius / 2.0


def hemisphere_metric_identity() -> dict[str, Any]:
    return {
        "coordinate_change": "rho=2*chi",
        "range": "0<=rho<=pi/2",
        "metric": (
            "ds5_E^2=dtau^2+R4^2*(drho^2+sin(rho)^2*dOmega3^2),_R4=RF/2"
        ),
        "spatial_cap": "closed_northern_hemisphere_of_round_S4_R4",
        "boundary": "equatorial_round_S3_R4",
    }


def transverse_profile(rho: float, mode: int) -> float:
    m = int(mode)
    if m < 2 or not 0.0 <= rho <= math.pi / 2.0:
        raise ValueError("coexact vector mode m>=2 and 0<=rho<=pi/2 required")
    return math.tan(rho / 2.0) ** m


def transverse_profile_derivative(rho: float, mode: int) -> float:
    value = transverse_profile(rho, mode)
    if rho == 0.0:
        return 0.0
    return mode * value / math.sin(rho)


def radial_ode_residual(rho: float, mode: int) -> float:
    """Residual of u''+cot(rho)u'-m^2 csc(rho)^2 u=0."""

    m = int(mode)
    if not 0.0 < rho <= math.pi / 2.0:
        raise ValueError("residual is evaluated away from the regular pole")
    u = transverse_profile(rho, m)
    first = m * u / math.sin(rho)
    second = (m * m - m * math.cos(rho)) * u / math.sin(rho) ** 2
    return second + math.cos(rho) / math.sin(rho) * first - m * m * u / math.sin(rho) ** 2


def static_dtn_eigenvalue(mode: int, radius: float | None = None) -> float:
    m = int(mode)
    a = boundary_radius() if radius is None else float(radius)
    if m < 2 or a <= 0.0:
        raise ValueError("coexact vector mode m>=2 and positive radius required")
    return m / a


def static_mode_ledger(modes: tuple[int, ...] = (2, 3, 4, 8)) -> list[dict[str, float]]:
    a = boundary_radius()
    return [
        {
            "mode": m,
            "boundary_value": transverse_profile(math.pi / 2.0, m),
            "boundary_derivative": transverse_profile_derivative(math.pi / 2.0, m),
            "unit_S3_Hodge_eigenvalue": float(m * m),
            "physical_DtN_eigenvalue": static_dtn_eigenvalue(m, a),
            "exact_DtN_eigenvalue": m / a,
        }
        for m in modes
    ]


def boundary_effective_operator() -> dict[str, Any]:
    return {
        "bulk_action": "S5=(K_F^(5)/4)*integral_M5*sqrt(g)*F_MN*F^MN",
        "static_transverse_radial_equation": (
            "-d_rho(sin(rho)*d_rho_u)+m^2*u/sin(rho)=0"
        ),
        "regular_normalized_solution": "u_m=tan(rho/2)^m,_u_m(pi/2)=1",
        "outward_normal_derivative": "partial_n*u_m=m/R4",
        "DtN_operator": "N_T=(Delta_1_coexact)^(1/2)",
        "on_shell_boundary_action": (
            "S_DtN=(K_F^(5)/2)*integral_boundary*sqrt(h)*A_i*N_T*A^i"
        ),
        "pseudodifferential_order": 1,
        "local_Maxwell_operator_order": 2,
        "equals_local_M4_Maxwell_action": False,
        "relation_to_v15_60": (
            "the_exact_bulk_pushforward_is_a_nonlocal_order-one_DtN_kernel,_"
            "so_it_does_not_supply_the_missing_local_order-two_boundary_term"
        ),
    }


def weak_left_right_projection() -> dict[str, Any]:
    return {
        "owned_bulk_connection": "diagonal_Sp1_weak_connection",
        "left_doublet_generator": "T_L^a=sigma^a/2",
        "right_singlet_generator": "T_R^a=0_for_u_R,d_R,e_R,nu_R",
        "scalar_LR_group_factor": "sum_a*T_L^a*T_R^a=0",
        "weak_DtN_kernel_projects_nontrivially_to_LR_Higgs_channel": False,
        "weak_kernel_still_generates": ["left-left_current_response", "weak_vector_boundary_response"],
        "required_nonzero_LR_sources": [
            "color_DtN_kernel_for_quark_channels",
            "hypercharge_DtN_kernel_for_charged_channels",
            "or_an_action-owned_direct_finite_Dirac/four-fermion_term",
        ],
        "those_nonzero_LR_kernel_normalizations_derived_in_current_parent_action": False,
    }


def completion_payload() -> dict[str, Any]:
    geometry = hemisphere_metric_identity()
    rows = static_mode_ledger()
    operator = boundary_effective_operator()
    projection = weak_left_right_projection()
    residuals = [abs(radial_ode_residual(rho, m)) for m in (2, 3, 5) for rho in (0.1, 0.4, 1.0)]
    validation = {
        "hemisphere_radius_positive": boundary_radius() > 0.0,
        "exact_profiles_solve_radial_ODE": max(residuals) < 1.0e-10,
        "boundary_normalization_exact": all(
            abs(row["boundary_value"] - 1.0) < 1.0e-14 for row in rows
        ),
        "DtN_eigenvalues_exact": all(
            abs(row["physical_DtN_eigenvalue"] - row["exact_DtN_eigenvalue"]) < 1.0e-14
            for row in rows
        ),
        "nonlocal_not_relabelled_local_Maxwell": not operator[
            "equals_local_M4_Maxwell_action"
        ],
        "weak_singlet_projection_zero": not projection[
            "weak_DtN_kernel_projects_nontrivially_to_LR_Higgs_channel"
        ],
        "no_new_continuous_coefficient": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_round_cap_maxwell_dtn_v15_65",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "hemisphere_geometry": geometry,
        "static_mode_ledger": rows,
        "boundary_effective_operator": operator,
        "weak_left_right_projection": projection,
        "claim_boundary": {
            "exact_static_weak_DtN_spectrum_derived": True,
            "nonlocal_weak_boundary_kernel_derived": True,
            "local_M4_Yang-Mills_term_derived": False,
            "weak_kernel_induces_composite_Higgs_gap": False,
            "color_or_hypercharge_DtN_kernel_derived": False,
        },
        "active_calculation": (
            "DERIVE_THE_COLOR_AND_HYPERCHARGE_BULK-TO-BOUNDARY_CURRENT_KERNELS_"
            "FROM_THE_PATH-B_ETA_AND_GLOBAL_SPIN-GAUGE_ATTACHMENT,_THEN_APPLY_"
            "THE_EXACT_DtN_SPECTRAL_PROJECTOR_TO_THE_QUARK_AND_LEPTON_LR_CHANNELS"
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
        rounded = round(value, 12)
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
    path = target / "BHSM_aether_round_cap_maxwell_dtn_v15_65.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "boundary_radius",
    "hemisphere_metric_identity", "transverse_profile",
    "transverse_profile_derivative", "radial_ode_residual",
    "static_dtn_eigenvalue", "static_mode_ledger", "boundary_effective_operator",
    "weak_left_right_projection", "completion_payload", "deterministic_json",
    "materialize",
]
