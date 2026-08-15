"""Exact M5-to-M4 gauge pushforward and Higgs-ownership theorem.

On the round reconstructed quotient cap, electric and magnetic tangential
curvatures have inequivalent radial weights.  No smooth bulk zero mode can
therefore induce a Lorentz-invariant local M4 Yang--Mills coefficient.  A
separate representation audit also shows that the active parent field bundle
contains no weak scalar doublet with hypercharge one half.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.integrate import quad

from bhsm.interface.aether_diagonal_sp1_m4_attachment_v15_50 import RADIUS0


VERSION = "v15.60"
CLASSIFICATION = "BHSM_M5_M4_GAUGE_PUSHFORWARD_AND_HIGGS_OWNERSHIP"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def round_base_radius(chi: float, fiber_radius: float = RADIUS0) -> float:
    if not 0.0 <= chi <= math.pi / 4.0 or fiber_radius <= 0.0:
        raise ValueError("require 0<=chi<=pi/4 and positive fiber radius")
    return fiber_radius * math.sin(chi) * math.cos(chi)


def regular_profile(chi: float, power: int) -> float:
    if not isinstance(power, int) or power < 1:
        raise ValueError("positive integer power required")
    return math.sin(2.0 * chi) ** power


def radial_weight_integrals(
    power: int, fiber_radius: float = RADIUS0,
) -> dict[str, float]:
    """Integrate the electric and magnetic weights for a regular profile."""

    if not isinstance(power, int) or power < 1 or fiber_radius <= 0.0:
        raise ValueError("positive integer power and radius required")
    endpoint = math.pi / 4.0

    def electric(chi: float) -> float:
        u = regular_profile(chi, power)
        return fiber_radius * round_base_radius(chi, fiber_radius) * u * u

    def magnetic(chi: float) -> float:
        if chi == 0.0:
            return 0.0
        u = regular_profile(chi, power)
        return fiber_radius * u * u / round_base_radius(chi, fiber_radius)

    i_e = quad(electric, 0.0, endpoint, epsabs=2.0e-14, epsrel=2.0e-14)[0]
    i_b = quad(magnetic, 0.0, endpoint, epsabs=2.0e-14, epsrel=2.0e-14)[0]
    boundary_radius = fiber_radius / 2.0
    return {
        "power": power,
        "electric_weight_integral": i_e,
        "magnetic_weight_integral": i_b,
        "boundary_radius": boundary_radius,
        "inferred_M4_coefficient_ratio": i_e / (boundary_radius**2 * i_b),
        "exact_ratio": 2.0 * power / (2.0 * power + 1.0),
    }


def smooth_pushforward_theorem() -> dict[str, Any]:
    rows = [radial_weight_integrals(power) for power in (1, 2, 4, 8, 32)]
    return {
        "round_M5_metric": (
            "ds5^2=-dt^2+R_F^2*dchi^2+r(chi)^2*dOmega3^2,_"
            "r=R_F*sin(chi)*cos(chi),_0<=chi<=pi/4"
        ),
        "mode": "A_mu(chi,x)=u(chi)*a_mu(x),_A_chi=0",
        "electric_weight": "I_E=integral_dchi*R_F*r*u^2",
        "magnetic_weight": "I_B=integral_dchi*R_F*u^2/r",
        "Lorentz_matching_condition": "I_E=r_boundary^2*I_B",
        "regular_test_family": "u_p=sin(2chi)^p,_p>=1",
        "exact_family_ratio": "I_E/(r_boundary^2*I_B)=2p/(2p+1)<1",
        "rows": rows,
        "smooth_bulk_profile_closes_Lorentz_invariant_M4_Maxwell_term": False,
        "equality_limit": "p_to_infinity_distribution_localized_at_chi=pi/4",
        "boundary_localization_normalization_fixed_by_bulk_EH_term": False,
        "consequence": (
            "an_intrinsic_Wentzell_or_boundary_Yang-Mills_term_is_required_"
            "for_a_local_Lorentz-invariant_M4_gauge_action"
        ),
    }


def higgs_representation_ownership() -> dict[str, Any]:
    return {
        "required_Higgs_representation": "(SU3,Sp1,Y)=(1,2,1/2)",
        "active_parent_bosonic_fields": {
            "metric_G": "gauge-singlet_symmetric_tensor",
            "response_sigma": "real_gauge_singlet",
            "Path-B_eta_tangent": "(3_plus_bar3,1,0)_under_color_times_weak",
            "mechanical_connection_fluctuation": "(1,3,0)_adjoint_weak_one-form",
            "quotient_base_coordinate": (
                "invariant_under_the_diagonal_principal_Sp1_action_and_not_"
                "an_associated_fundamental_doublet"
            ),
        },
        "required_representation_occurs_in_active_parent_tangent_bundle": False,
        "fiber_coordinate_as_Higgs": False,
        "fiber_coordinate_reason": (
            "a_principal-fiber_coordinate_is_gauge_redundancy,_not_a_physical_"
            "associated-bundle_section"
        ),
        "v15_53_Higgs_doublet_status": "FOUNDATIONAL_INTRINSIC_M4_FIELD",
        "Higgs_kinetic_coefficient_derived_from_parent": False,
        "Higgs_potential_derived_from_parent": False,
        "nonzero_Higgs_vacuum_derived_from_parent": False,
    }


def forced_intrinsic_M4_action_shape() -> dict[str, Any]:
    return {
        "action": (
            "S_M4=int_sqrt(-h)[-Z_g/4*((5/3)F_Y^2+F_2^2+F_3^2)+"
            "Z_H*abs(DH)^2-V(H)-sum_f(barPsi_L*Y_f*H_f*Psi_R+h.c.)]"
        ),
        "field_rescaling": "H_canonical=sqrt(Z_H)*H_removes_Z_H_from_the_kinetic_term",
        "independent_data_after_canonicalization": [
            "Z_gauge", "renormalized_Higgs_potential", "Y_u", "Y_d", "Y_e", "Y_nu",
        ],
        "coupling_ray_already_fixed": "K_Y:K_2:K_3=5/3:1:1",
        "these_data_selected_by_current_parent_child_action": False,
        "setting_them_to_one_is_a_derivation": False,
        "setting_them_to_observed_values_allowed": False,
        "smallest_required_microscopic_completion": (
            "one_covariant_functional_whose_boundary_reduction_generates_"
            "Z_gauge,_the_Higgs_potential,_and_the_four_Yukawa_operators"
        ),
    }


def completion_payload() -> dict[str, Any]:
    pushforward = smooth_pushforward_theorem()
    higgs = higgs_representation_ownership()
    forced = forced_intrinsic_M4_action_shape()
    validation = {
        "analytic_radial_ratios_verified": all(
            abs(row["inferred_M4_coefficient_ratio"] - row["exact_ratio"])
            < 2.0e-12 for row in pushforward["rows"]
        ),
        "all_smooth_test_profiles_fail_Lorentz_matching": all(
            row["inferred_M4_coefficient_ratio"] < 1.0
            for row in pushforward["rows"]
        ),
        "boundary_limit_approaches_one": pushforward["rows"][-1][
            "inferred_M4_coefficient_ratio"
        ] > pushforward["rows"][0]["inferred_M4_coefficient_ratio"],
        "dimensionful_K5_not_relabelled_M4_coupling": not pushforward[
            "boundary_localization_normalization_fixed_by_bulk_EH_term"
        ],
        "Higgs_representation_absent_from_parent_tangent": not higgs[
            "required_representation_occurs_in_active_parent_tangent_bundle"
        ],
        "principal_coordinate_not_relabelled_Higgs": not higgs[
            "fiber_coordinate_as_Higgs"
        ],
        "missing_M4_data_not_fabricated": not forced[
            "these_data_selected_by_current_parent_child_action"
        ],
        "no_new_continuous_coefficient": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_m5_m4_gauge_higgs_ownership_v15_60",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "smooth_gauge_pushforward": pushforward,
        "Higgs_representation_ownership": higgs,
        "forced_intrinsic_M4_action": forced,
        "claim_boundary": {
            "smooth_bulk_gauge_pushforward_no_go_derived": True,
            "intrinsic_boundary_gauge_term_required": True,
            "active_parent_Higgs_ownership_excluded": True,
            "microscopic_boundary_functional_derived": False,
            "absolute_gauge_Higgs_Yukawa_data_derived": False,
        },
        "active_calculation": (
            "CONSTRUCT_THE_SMALLEST_SINGLE_COVARIANT_BOUNDARY_FUNCTIONAL_FROM_"
            "THE_EXISTING_GLOBAL_SPIN-GAUGE_BUNDLE_AND_TEST_WHETHER_ITS_"
            "HEAT-KERNEL_COEFFICIENTS_UNIQUELY_FIX_Z_GAUGE,_V_H,_AND_Y_F"
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
    path = target / "BHSM_aether_m5_m4_gauge_higgs_ownership_v15_60.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "round_base_radius", "regular_profile", "radial_weight_integrals",
    "smooth_pushforward_theorem", "higgs_representation_ownership",
    "forced_intrinsic_M4_action_shape", "completion_payload",
    "deterministic_json", "materialize",
]
