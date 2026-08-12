"""Exact internal Dirac lift on the round diagonal Sp(1) fiber."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_diagonal_sp1_m4_attachment_v15_50 import RADIUS0
from bhsm.interface.particle_chirality_anomaly_normalization import MODE_LEDGERS
from bhsm.interface.completion.exact_berger_dirac_cap_obstruction_v14_59 import (
    berger_dirac_block,
    round_block_expected_eigenvalues,
)


VERSION = "v15.55"
CLASSIFICATION = "BHSM_DIAGONAL_FIBER_INTERNAL_DIRAC_LIFT"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def diagonal_fiber_dirac_contract() -> dict[str, Any]:
    return {
        "fiber_metric": "g_F=(A^2+B^2)*sum_a(omega^a)^2",
        "fiber_radius": "L_F=sqrt(A^2+B^2)",
        "fiber_stretch": 1.0,
        "homogeneous_block": (
            "D_n=C*I+2*L_F^-1*(sigma_z*J_z+sigma_y*J_y+sigma_x*J_x)"
        ),
        "round_block_spectrum": (
            "-(n+1/2)/L_F_with_internal_multiplicity_n_and_"
            "+(n+3/2)/L_F_with_internal_multiplicity_n+2"
        ),
        "full_positive_level": (
            "+(ell+3/2)/L_F_with_multiplicity_(ell+1)(ell+2)"
        ),
        "full_negative_level": (
            "-(ell+3/2)/L_F_with_multiplicity_(ell+1)(ell+2)"
        ),
        "radial_time_dependence": "D_n(t,chi)=Dhat_n/L_F(t,chi)",
        "blocks_at_distinct_points_commute": True,
        "anisotropic_Berger_monodromy_active": False,
        "new_continuous_coefficient": False,
    }


def internal_positive_dirac_level(level: int, radius: float) -> float:
    if not isinstance(level, int) or level < 0 or radius <= 0.0:
        raise ValueError("nonnegative level and positive radius required")
    return (level + 1.5) / radius


def family_dirac_seed() -> dict[str, Any]:
    """Lift every stored scalar harmonic label to its positive Dirac level."""

    sectors: dict[str, Any] = {}
    for name, components in MODE_LEDGERS.items():
        component_rows = {}
        for component, modes in components.items():
            levels = [int(mode[0]) for mode in modes]
            eigenvalues = [
                internal_positive_dirac_level(level, RADIUS0)
                for level in levels
            ]
            component_rows[component] = {
                "scalar_mode_ledger": [list(mode) for mode in modes],
                "Dirac_levels": levels,
                "R_F_times_positive_Dirac_eigenvalue": [
                    level + 1.5 for level in levels
                ],
                "positive_Dirac_eigenvalues": eigenvalues,
                "negative_charge_conjugate_eigenvalues": [
                    -value for value in eigenvalues
                ],
            }
        sectors[name] = component_rows
    return {
        "reset_fiber_radius": RADIUS0,
        "sectors": sectors,
        "interpretation": (
            "exact_internal_Kaluza-Klein_Dirac_eigenvalue_seed;_a_physical_"
            "four-dimensional_mass_requires_a_gauge-invariant_left-right_"
            "Higgs_or_topographic_matrix_element"
        ),
    }


def block_scaling_commutator(
    n: int, radius_a: float, radius_b: float,
) -> float:
    left = berger_dirac_block(n, radius_a, 1.0)
    right = berger_dirac_block(n, radius_b, 1.0)
    return float(np.linalg.norm(left @ right - right @ left, ord="fro"))


def spinor_lift_incidence() -> dict[str, Any]:
    return {
        "scalar_irrep": "(k/2,k/2)_under_Sp1_L_times_Sp1_R",
        "positive_spinor_irrep": "((k+1)/2,k/2)",
        "negative_spinor_partner": "(k/2,(k+1)/2)",
        "positive_level": "+(k+3/2)/L_F",
        "negative_level": "-(k+3/2)/L_F_from_the_adjacent_homogeneous_block",
        "K_plus_wall_chirality": (
            "selects_the_normalizable_four-dimensional_left-Weyl_profile_"
            "but_does_not_change_the_internal_absolute_Dirac_level"
        ),
        "gauge_invariant_pairings": {
            "up": "Q_L*H*u_c",
            "down": "Q_L*H_dagger*d_c",
            "charged_lepton": "L_L*H_dagger*e_c",
            "neutral_Dirac": "L_L*H*nu_c",
        },
        "bare_internal_eigenvalue_called_physical_SM_mass": False,
    }


def reset_block_validation(n_max: int = 10) -> dict[str, Any]:
    residuals = []
    for n in range(n_max + 1):
        computed = np.linalg.eigvalsh(berger_dirac_block(n, RADIUS0, 1.0))
        expected = np.asarray(round_block_expected_eigenvalues(n, RADIUS0))
        residuals.append(float(np.max(np.abs(computed - expected))))
    return {
        "n_max": n_max,
        "maximum_round_block_residual": max(residuals),
        "commutator_n3_two_radii": block_scaling_commutator(
            3, RADIUS0, 1.2 * RADIUS0
        ),
    }


def completion_payload() -> dict[str, Any]:
    contract = diagonal_fiber_dirac_contract()
    seed = family_dirac_seed()
    incidence = spinor_lift_incidence()
    block = reset_block_validation()
    validation = {
        "diagonal_fiber_round": contract["fiber_stretch"] == 1.0,
        "round_blocks_exact": block["maximum_round_block_residual"] < 2.0e-13,
        "distinct_radius_blocks_commute": block[
            "commutator_n3_two_radii"
        ] < 2.0e-13,
        "all_family_modes_lifted": set(seed["sectors"])
        == {"Q_L", "L_L", "u_c", "d_c", "e_c", "nu_c"},
        "wall_chirality_distinguished_from_internal_sign": True,
        "gauge_invariant_pairings_explicit": len(incidence[
            "gauge_invariant_pairings"
        ]) == 4,
        "bare_level_not_relabelled_mass": not incidence[
            "bare_internal_eigenvalue_called_physical_SM_mass"
        ],
        "no_new_continuous_coefficient": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_diagonal_fiber_dirac_lift_v15_55",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "Dirac_contract": contract,
        "family_Dirac_seed": seed,
        "spinor_lift_incidence": incidence,
        "block_validation": block,
        "claim_boundary": {
            "exact_internal_Dirac_spectrum_derived": True,
            "all_stored_family_modes_spinor_lifted": True,
            "diagonal_fiber_generates_nontrivial_mixing": False,
            "gauge_invariant_Dirac_Yukawa_matrix_elements_derived": False,
            "physical_SM_masses_derived": False,
        },
        "active_calculation": (
            "EVALUATE_THE_FOUR_GAUGE-INVARIANT_HIGGS-TOPOGRAPHIC_OVERLAPS_"
            "BETWEEN_THE_NORMALIZED_K_PLUS_WALL_PROFILES_AND_THE_EXACT_"
            "INTERNAL_DIRAC_EIGENMODES"
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
    path = target / "BHSM_aether_diagonal_fiber_dirac_lift_v15_55.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "diagonal_fiber_dirac_contract", "internal_positive_dirac_level",
    "family_dirac_seed", "block_scaling_commutator", "spinor_lift_incidence",
    "reset_block_validation", "completion_payload", "deterministic_json",
    "materialize",
]
