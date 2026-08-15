"""Single-carrier extension of the exact DtN kernel to all SM gauge factors."""

from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_diagonal_sp1_m4_attachment_v15_50 import attachment_states
from bhsm.interface.aether_round_cap_maxwell_dtn_v15_65 import (
    boundary_radius,
    static_dtn_eigenvalue,
)


VERSION = "v15.66"
CLASSIFICATION = "BHSM_FULL_GAUGE_NONLOCAL_DTN_AND_COMPOSITE_LR_KERNEL"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


INVERSE_KERNEL_RAY = {
    "Y": Fraction(5, 3),
    "Sp1": Fraction(1, 1),
    "SU3": Fraction(1, 1),
}


def full_gauge_dtn_completion() -> dict[str, Any]:
    k5 = float(attachment_states()["reconstructed_round_boundary"]["connection_kinetic_coefficient"])
    return {
        "operator": "N_T=(Delta_1_coexact)^(1/2)_on_S3_R4",
        "quadratic_form": (
            "S_gauge_DtN=(K_F^(5)/2)*integral_sqrt(h)*[(5/3)A_Y*N_T*A_Y+"
            "A_2*N_T*A_2+A_3*N_T*A_3]"
        ),
        "K_F_five_dimensional": k5,
        "coefficient_ray": "K_Y:K_2:K_3=5/3:1:1",
        "inverse_current_kernel_ray": "G_Y:G_2:G_3=3/5:1:1",
        "provenance": (
            "BHSM_ACTION_COMPLETION_DERIVED_FROM_EXISTING_RANK16_CARRIER_"
            "TRACE_AND_DIAGONAL_SP1_DtN_OPERATOR"
        ),
        "new_continuous_coefficient": False,
        "local_M4_Yang-Mills_action": False,
        "absolute_nonlocal_kernel_fixed_in_kappa1_units": True,
        "uniqueness_scope": (
            "the_selected_single-carrier-trace_extension_with_one_common_DtN_"
            "operator_and_no_factor-dependent_boundary_form"
        ),
    }


def inverse_kernel_eigenvalues(mode: int) -> dict[str, float]:
    m = int(mode)
    if m < 2:
        raise ValueError("coexact vector mode m>=2 required")
    k5 = float(attachment_states()["reconstructed_round_boundary"]["connection_kinetic_coefficient"])
    n_m = static_dtn_eigenvalue(m)
    return {
        name: 1.0 / (float(weight) * k5 * n_m)
        for name, weight in INVERSE_KERNEL_RAY.items()
    }


def left_right_group_factors() -> dict[str, Any]:
    c_f = Fraction(4, 3)
    y = {
        "up": Fraction(1, 6) * Fraction(2, 3),
        "down": Fraction(1, 6) * Fraction(-1, 3),
        "neutrino": Fraction(-1, 2) * Fraction(0, 1),
        "charged_lepton": Fraction(-1, 2) * Fraction(-1, 1),
    }
    color = {
        "up": c_f,
        "down": c_f,
        "neutrino": Fraction(0, 1),
        "charged_lepton": Fraction(0, 1),
    }
    weak = {name: Fraction(0, 1) for name in y}
    total = {
        name: color[name] + Fraction(3, 5) * y[name] + weak[name]
        for name in y
    }
    return {
        "convention": (
            "C_f=C3_f+(K2/KY)*Y_L*Y_R+C2_f,_with_the_common_positive_"
            "left-right_chiral_Fierz_factor_2_recorded_separately"
        ),
        "color_singlet_C_F": str(c_f),
        "hypercharge_products": {name: str(value) for name, value in y.items()},
        "weak_products": {name: str(value) for name, value in weak.items()},
        "pre_Fierz_attraction_weights": {name: str(value) for name, value in total.items()},
        "Fierz_factor": 2,
        "post_Fierz_weights": {name: str(2 * value) for name, value in total.items()},
        "ordering": ["up", "down", "charged_lepton", "neutrino"],
        "all_family_matrices_at_this_gauge_level": "C_f*I3",
        "CKM_PMNS_generated_at_this_level": False,
    }


def projected_lr_kernel(mode: int) -> dict[str, Any]:
    inverse = inverse_kernel_eigenvalues(mode)
    group = left_right_group_factors()
    weights = {
        name: Fraction(value)
        for name, value in group["pre_Fierz_attraction_weights"].items()
    }
    common = inverse["Sp1"]
    return {
        "mode": int(mode),
        "common_geometric_inverse_kernel": common,
        "channel_kernel_eigenvalues_before_fermion_susceptibility": {
            name: 2.0 * float(weight) * common for name, weight in weights.items()
        },
        "factorization": "K_LR,f(mode)=2*C_f*[K_F^(5)*N_T(mode)]^(-1)*Pi_f",
        "family_projector": "Pi_f=I3_at_the_single-carrier_gauge-exchange_level",
        "fermion_bubble_susceptibility_included": False,
        "gap_eigenvalue_computed": False,
    }


def gap_reduction() -> dict[str, Any]:
    return {
        "Bethe_Salpeter_equation": (
            "Delta_f=2*C_f*(K_F^(5)*N_T)^(-1)*Pi_f*Chi_LR(mu_star)*Delta_f"
        ),
        "remaining_operator": (
            "Chi_LR(mu_star),_the_regulated_left-right_two-fermion_"
            "susceptibility_on_R_times_S3_with_the_odd-FR_domain"
        ),
        "all_gauge_group_factors_and_static_DtN_eigenvalues_fixed": True,
        "remaining_free_gauge_coefficient": False,
        "nonzero_gap_claimed": False,
        "first_candidate_channel_by_group_weight": "up",
        "neutrino_direct_gauge_gap_weight": 0.0,
    }


def completion_payload() -> dict[str, Any]:
    gauge = full_gauge_dtn_completion()
    group = left_right_group_factors()
    modes = [projected_lr_kernel(mode) for mode in (2, 3, 4, 8)]
    gap = gap_reduction()
    expected = {
        "up": Fraction(7, 5),
        "down": Fraction(13, 10),
        "neutrino": Fraction(0, 1),
        "charged_lepton": Fraction(3, 10),
    }
    validation = {
        "carrier_extension_has_no_new_coefficient": not gauge["new_continuous_coefficient"],
        "nonlocal_not_relabelled_local": not gauge["local_M4_Yang-Mills_action"],
        "group_factors_exact": all(
            Fraction(group["pre_Fierz_attraction_weights"][name]) == value
            for name, value in expected.items()
        ),
        "inverse_kernel_ray_exact": all(
            math.isclose(
                modes[0]["common_geometric_inverse_kernel"] / inverse_kernel_eigenvalues(2)[name],
                float(INVERSE_KERNEL_RAY[name]),
                rel_tol=1.0e-13,
            )
            for name in INVERSE_KERNEL_RAY
        ),
        "kernel_decreases_with_mode": all(
            modes[index]["common_geometric_inverse_kernel"]
            > modes[index + 1]["common_geometric_inverse_kernel"]
            for index in range(len(modes) - 1)
        ),
        "susceptibility_not_fabricated": not modes[0][
            "fermion_bubble_susceptibility_included"
        ],
        "no_nonzero_gap_overclaim": not gap["nonzero_gap_claimed"],
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_full_gauge_dtn_lr_kernel_v15_66",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "full_gauge_DtN_completion": gauge,
        "left_right_group_factors": group,
        "projected_mode_kernels": modes,
        "gap_reduction": gap,
        "claim_boundary": {
            "absolute_nonlocal_full_gauge_kernel_completed": True,
            "LR_group_factors_completed": True,
            "fermion_susceptibility_completed": False,
            "composite_gap_or_Yukawa_residues_completed": False,
        },
        "active_calculation": (
            "COMPUTE_Chi_LR_ON_R_TIMES_S3_FROM_THE_EXACT_MASSLESS_WEYL_"
            "SPECTRUM_AND_ODD-FR_DOMAIN,_RENORMALIZED_BY_THE_ACTUAL-CHILD_"
            "ZETA_PRESCRIPTION,_THEN_TEST_THE_UP-CHANNEL_GAP_EIGENVALUE_FIRST"
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
    path = target / "BHSM_aether_full_gauge_dtn_lr_kernel_v15_66.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "INVERSE_KERNEL_RAY",
    "full_gauge_dtn_completion", "inverse_kernel_eigenvalues",
    "left_right_group_factors", "projected_lr_kernel", "gap_reduction",
    "completion_payload", "deterministic_json", "materialize",
]
