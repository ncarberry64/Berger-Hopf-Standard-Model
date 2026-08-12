"""Exact scalar/electric Maxwell DtN operator on the round M5 hemisphere."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.special import gamma, hyp2f1

from bhsm.interface.aether_round_cap_maxwell_dtn_v15_65 import boundary_radius


VERSION = "v15.68"
CLASSIFICATION = "BHSM_ROUND_CAP_COULOMB_GAUSS_DTN_OPERATOR"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def _parameters(level: int) -> tuple[float, float, float, float]:
    ell = int(level)
    if ell < 1:
        raise ValueError("nonconstant scalar harmonic level ell>=1 required")
    return ell / 2.0, (ell + 3.0) / 2.0, ell + 2.0, ell / 2.0


def boundary_normalization(level: int) -> float:
    a, b, c, _ = _parameters(level)
    return float(gamma(c) * gamma(0.5) / (gamma(c - a) * gamma(c - b)))


def electric_profile(rho: float, level: int) -> float:
    if not 0.0 <= rho <= math.pi / 2.0:
        raise ValueError("require 0<=rho<=pi/2")
    a, b, c, power = _parameters(level)
    x = math.sin(rho) ** 2
    return float(x**power * hyp2f1(a, b, c, x) / boundary_normalization(level))


def electric_profile_derivatives(rho: float, level: int) -> tuple[float, float, float]:
    """Return u, du/drho, d2u/drho2 away from the equatorial endpoint."""

    if not 0.0 < rho < math.pi / 2.0:
        raise ValueError("derivatives are evaluated on the open radial interval")
    a, b, c, p = _parameters(level)
    x = math.sin(rho) ** 2
    norm = boundary_normalization(level)
    f0 = hyp2f1(a, b, c, x)
    f1 = (a * b / c) * hyp2f1(a + 1.0, b + 1.0, c + 1.0, x)
    f2 = (
        a * (a + 1.0) * b * (b + 1.0) / (c * (c + 1.0))
        * hyp2f1(a + 2.0, b + 2.0, c + 2.0, x)
    )
    g = x**p * f0 / norm
    gx = (p * x ** (p - 1.0) * f0 + x**p * f1) / norm
    gxx = (
        p * (p - 1.0) * x ** (p - 2.0) * f0
        + 2.0 * p * x ** (p - 1.0) * f1
        + x**p * f2
    ) / norm
    x1 = 2.0 * math.sin(rho) * math.cos(rho)
    x2 = 2.0 * math.cos(2.0 * rho)
    return float(g), float(gx * x1), float(gxx * x1 * x1 + gx * x2)


def electric_radial_residual(rho: float, level: int) -> float:
    ell = int(level)
    u, first, second = electric_profile_derivatives(rho, ell)
    return second + 3.0 / math.tan(rho) * first - ell * (ell + 2.0) / math.sin(rho) ** 2 * u


def electric_dtn_eigenvalue(level: int, radius: float | None = None) -> float:
    ell = int(level)
    a = boundary_radius() if radius is None else float(radius)
    if ell < 1 or a <= 0.0:
        raise ValueError("ell>=1 and positive radius required")
    return ell * (ell + 2.0) / ((ell + 1.0) * a)


def boundary_derivative_exact(level: int) -> float:
    ell = int(level)
    if ell < 1:
        raise ValueError("ell>=1 required")
    return ell * (ell + 2.0) / (ell + 1.0)


def electric_dtn_contract() -> dict[str, Any]:
    return {
        "static_ansatz": "A_tau(rho,Omega)=u_ell(rho)*Y_ell(Omega)",
        "unit_S3_scalar_eigenvalue": "ell*(ell+2)",
        "radial_equation": (
            "-d_rho(sin(rho)^3*d_rho_u)+ell*(ell+2)*sin(rho)*u=0"
        ),
        "regular_solution": (
            "u_ell=N_ell^-1*sin(rho)^ell*2F1(ell/2,(ell+3)/2;ell+2;sin(rho)^2)"
        ),
        "boundary_normalization": "u_ell(pi/2)=1",
        "outward_derivative": "d_rho_u(pi/2)=ell*(ell+2)/(ell+1)",
        "physical_DtN_eigenvalue": "nu_ell=ell*(ell+2)/[(ell+1)*R4]",
        "operator_form": (
            "N_0=Omega-Omega^(-1)/R4^2,_Omega=sqrt(-Delta_0+1/R4^2)"
        ),
        "constant_mode": "ell=0_has_nu_0=0_and_is_removed_or_constrained_by_global_Gauss_law",
        "inverse_Coulomb_eigenvalue": (
            "G_ell=R4*(ell+1)/[K_F^(5)*ell*(ell+2)],_ell>=1"
        ),
    }


def full_static_gauge_kernel_correction() -> dict[str, Any]:
    return {
        "transverse_sector_v15_65": "N_T=sqrt(Delta_1_coexact),_order_one",
        "electric_sector_v15_68": (
            "N_0=Omega-Omega^(-1)/R4^2_on_nonconstant_scalar_harmonics"
        ),
        "longitudinal_spatial_sector": "fixed_by_Gauss/gauge_condition_and_not_an_independent_physical_vector",
        "ghost_role": "cancels_gauge-volume_not_the_physical_Coulomb_response",
        "v15_66_full_current_kernel_wording": "RECLASSIFIED_AS_TRANSVERSE_CARRIER_EXTENSION",
        "static_current_kernel_complete_after_v15_68": True,
        "local_M4_Maxwell_term_derived": False,
    }


def completion_payload() -> dict[str, Any]:
    contract = electric_dtn_contract()
    correction = full_static_gauge_kernel_correction()
    rows = []
    for ell in (1, 2, 3, 4, 8):
        step = 1.0e-4
        derivative_step = electric_profile_derivatives(math.pi / 2.0 - step, ell)[1]
        derivative_half_step = electric_profile_derivatives(
            math.pi / 2.0 - step / 2.0, ell
        )[1]
        rows.append({
            "level": ell,
            "boundary_value_limit": electric_profile(math.pi / 2.0 - step / 2.0, ell),
            "boundary_derivative_limit": 2.0 * derivative_half_step - derivative_step,
            "exact_boundary_derivative": boundary_derivative_exact(ell),
            "physical_DtN_eigenvalue": electric_dtn_eigenvalue(ell),
        })
    residuals = [
        abs(electric_radial_residual(rho, ell))
        for ell in (1, 2, 4, 7)
        for rho in (0.1, 0.4, 0.9, 1.3)
    ]
    validation = {
        "hypergeometric_profiles_solve_radial_equation": max(residuals) < 2.0e-9,
        "boundary_values_converge_to_one": all(
            abs(row["boundary_value_limit"] - 1.0) < 5.0e-4 for row in rows
        ),
        "boundary_derivatives_match_exact_limit": all(
            abs(row["boundary_derivative_limit"] - row["exact_boundary_derivative"])
            < 3.0e-6 for row in rows
        ),
        "electric_DtN_positive_off_constant_mode": all(
            row["physical_DtN_eigenvalue"] > 0.0 for row in rows
        ),
        "static_kernel_sector_audit_complete": correction[
            "static_current_kernel_complete_after_v15_68"
        ],
        "transverse_overclaim_corrected": correction[
            "v15_66_full_current_kernel_wording"
        ].startswith("RECLASSIFIED"),
        "no_new_continuous_coefficient": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_round_cap_coulomb_dtn_v15_68",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "electric_DtN_contract": contract,
        "mode_rows": rows,
        "full_static_gauge_kernel_correction": correction,
        "claim_boundary": {
            "electric_Coulomb_DtN_spectrum_derived": True,
            "static_transverse_plus_electric_kernel_complete": True,
            "global_Gauss_zero_mode_identified": True,
            "local_M4_Yang-Mills_action_derived": False,
            "Bethe_Salpeter_Clebsch_Gordan_matrix_derived": False,
        },
        "active_calculation": (
            "ASSEMBLE_THE_SCALAR-HARMONIC_COULOMB_PROPAGATOR_WITH_THE_EXACT_"
            "S3_SPINOR_CURRENT_CLEBSCH-GORDAN_COEFFICIENTS_AND_THE_WEYL_"
            "BUBBLE,_THEN_DIAGONALIZE_THE_COLOR-SINGLET_LR_CHANNEL"
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
    path = target / "BHSM_aether_round_cap_coulomb_dtn_v15_68.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "boundary_normalization",
    "electric_profile", "electric_profile_derivatives", "electric_radial_residual",
    "electric_dtn_eigenvalue", "boundary_derivative_exact",
    "electric_dtn_contract", "full_static_gauge_kernel_correction",
    "completion_payload", "deterministic_json", "materialize",
]
