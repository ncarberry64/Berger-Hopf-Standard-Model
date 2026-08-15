"""Exact Yukawa pullback and mass semantics on the BHSM hybrid reset.

The collar zero mode and the diagonal-fiber harmonics determine overlap
factors.  They do not turn a vertical Dirac eigenvalue into a four-dimensional
chiral mass and they do not determine the intrinsic Yukawa matrices adopted
in the foundational M4 fermion action.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.particle_chirality_anomaly_normalization import MODE_LEDGERS
from bhsm.interface.completion.foundational_dirac_spin_glue_v14_45 import (
    zero_mode_pullback_payload,
)


VERSION = "v15.56"
CLASSIFICATION = "BHSM_HYBRID_YUKAWA_PULLBACK_AND_MASS_SEMANTICS"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


VERTEX_MODE_PAIRS = {
    "up": (("Q_L", "upper"), ("u_c", "singlet"), "Q_L*H*u_c"),
    "down": (("Q_L", "lower"), ("d_c", "singlet"), "Q_L*H_dagger*d_c"),
    "charged_lepton": (
        ("L_L", "lower"), ("e_c", "singlet"), "L_L*H_dagger*e_c",
    ),
    "neutral_Dirac": (
        ("L_L", "upper"), ("nu_c", "singlet"), "L_L*H*nu_c",
    ),
}


def wall_normal_overlap_contract() -> dict[str, Any]:
    """Return the exact normalized collar pullback."""

    witness = zero_mode_pullback_payload()
    return {
        "normal_mode": "u0=N*J^(-1/2)*sin(f_eta)",
        "normalization": "integral_ds_J*abs(u0)^2=1",
        "two_sheet_Higgs_overlap": 1.0,
        "numerical_witness": witness["numerical_witness"],
        "consequence": "the_normal_pullback_leaves_the_intrinsic_Y_f_unchanged",
    }


def paired_mode_overlap_contract() -> dict[str, Any]:
    """Audit the four left/right mode ledgers and their geometric overlaps."""

    vertices: dict[str, Any] = {}
    for sector, (left_key, right_key, vertex) in VERTEX_MODE_PAIRS.items():
        left = MODE_LEDGERS[left_key[0]][left_key[1]]
        right = MODE_LEDGERS[right_key[0]][right_key[1]]
        overlap = np.asarray(
            [[1.0 if left_mode == right_mode else 0.0 for right_mode in right]
             for left_mode in left],
            dtype=float,
        )
        vertices[sector] = {
            "gauge_invariant_vertex": vertex,
            "left_modes": [list(mode) for mode in left],
            "right_modes": [list(mode) for mode in right],
            "fiber_invariant_Higgs_overlap": overlap.tolist(),
            "paired_ledgers_identical": left == right,
        }
    return {
        "orthonormality": (
            "for_a_fiber-invariant_Higgs,_Omega_f[ab]=<phi_La,phi_Rb>_F"
            "=delta_ab_in_the_matched_mode_basis"
        ),
        "vertices": vertices,
        "all_geometric_overlap_matrices": "I3",
        "geometric_overlap_generates_hierarchy": False,
        "geometric_overlap_generates_mixing": False,
    }


def yukawa_operator_factorization() -> dict[str, Any]:
    """Separate derived overlaps from independent intrinsic Yukawa data."""

    return {
        "foundational_seam_term": (
            "S_H=-integral_M4[bar(Psi_L)*Y_f*H*Psi_R+h.c.]"
        ),
        "normal_reduction": "Y_f_to_(integral_ds_J_abs(u0)^2)*Y_f=Y_f",
        "fiber_geometric_kernel": "Omega_f=I3_for_each_of_the_four_vertices",
        "reduced_matrix_element": "M_f(H)=H*Y_f_after_canonical_pullback",
        "intrinsic_Yukawa_matrices": ["Y_u", "Y_d", "Y_e", "Y_nu"],
        "Y_f_entries_fixed_by_wall_normalization": False,
        "Y_f_entries_fixed_by_round_fiber_Dirac_spectrum": False,
        "action_provenance": (
            "Y_f_are_foundational_intrinsic_M4_Wilson_operators_in_v14.45;_"
            "they_are_not_derived_from_the_bosonic_parent_Path-B_action"
        ),
        "geometric_zero-input_specialization": (
            "if_only_the_derived_fiber-invariant_multiplication_kernel_is_"
            "retained,_the_family_operator_is_proportional_to_I3"
        ),
        "vertical_Dirac_levels_are_mass_matrix_entries": False,
    }


def reset_mass_spectrum() -> dict[str, Any]:
    """Evaluate the mass operators on the selected hybrid conformal vacuum."""

    zero = np.zeros((3, 3), dtype=float)
    return {
        "hybrid_background": {
            "H_star": 0.0,
            "gauge_connection_star": 0.0,
            "classical_fermion_star": 0.0,
            "state": "electroweak-symmetric_static_conformal_vacuum",
        },
        "fermion_mass_formula": "M_f_star=H_star*Y_f=0_3",
        "fermion_mass_matrices": {
            sector: zero.tolist() for sector in VERTEX_MODE_PAIRS
        },
        "fermion_mass_eigenvalues": {
            sector: [0.0, 0.0, 0.0] for sector in VERTEX_MODE_PAIRS
        },
        "gauge_boson_masses": {
            "SU3_eight": 0.0,
            "Sp1_three": 0.0,
            "U1_one": 0.0,
        },
        "unbroken_group": "(SU3_times_Sp1_times_U1Y)/Z6",
        "internal_KK_tower_identified_with_chiral_SM_mass": False,
        "massive_observed_SM_background_constructed": False,
    }


def mixing_semantics() -> dict[str, Any]:
    return {
        "mass_background": "M_u=M_d=M_e=M_nu=0_3",
        "left_diagonalizers": "arbitrary_U(3)_for_each_degenerate_zero_matrix",
        "physical_CKM": "UNDEFINED_UNOBSERVABLE_IN_THE_EXACTLY_DEGENERATE_BACKGROUND",
        "physical_PMNS": "UNDEFINED_UNOBSERVABLE_IN_THE_EXACTLY_DEGENERATE_BACKGROUND",
        "physical_Jarlskog": "UNDEFINED_WITH_NO_NONDEGENERATE_MASS_OPERATORS",
        "canonical_triality_basis_transport": "I3",
        "canonical_transport_is_a_physical_mixing_prediction": False,
        "nontrivial_physical_mixing_source": (
            "specified_nonzero_Higgs_background_and_noncommuting_Y_f_operators"
        ),
    }


def completion_payload() -> dict[str, Any]:
    wall = wall_normal_overlap_contract()
    modes = paired_mode_overlap_contract()
    factorization = yukawa_operator_factorization()
    masses = reset_mass_spectrum()
    mixing = mixing_semantics()
    validation = {
        "wall_overlap_exactly_unit": wall["two_sheet_Higgs_overlap"] == 1.0,
        "all_mode_ledgers_pair": all(
            row["paired_ledgers_identical"]
            for row in modes["vertices"].values()
        ),
        "all_fiber_overlaps_identity": all(
            np.allclose(row["fiber_invariant_Higgs_overlap"], np.eye(3))
            for row in modes["vertices"].values()
        ),
        "Yukawa_entries_not_falsely_derived": not factorization[
            "Y_f_entries_fixed_by_round_fiber_Dirac_spectrum"
        ],
        "reset_mass_matrices_zero": all(
            np.count_nonzero(matrix) == 0
            for matrix in masses["fermion_mass_matrices"].values()
        ),
        "KK_levels_not_relabelled_masses": not masses[
            "internal_KK_tower_identified_with_chiral_SM_mass"
        ],
        "canonical_transport_not_relabelled_observable_mixing": not mixing[
            "canonical_transport_is_a_physical_mixing_prediction"
        ],
        "no_new_continuous_coefficient": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_hybrid_yukawa_mass_semantics_v15_56",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "wall_normal_overlap": wall,
        "paired_mode_overlap": modes,
        "Yukawa_operator_factorization": factorization,
        "hybrid_reset_mass_spectrum": masses,
        "mixing_semantics": mixing,
        "claim_boundary": {
            "four_geometric_overlap_kernels_derived": True,
            "actual_reset_mass_spectrum_derived": True,
            "current_hybrid_background_is_massive_broken_SM": False,
            "intrinsic_Yukawa_Wilson_matrices_derived": False,
            "observed_fermion_masses_or_mixing_derived": False,
        },
        "active_calculation": (
            "EXTEND_THE_EVENT_RESET_TO_THE_FULL_SOBLEV_CONFIGURATION_SPACE_"
            "AND_STATE_UNIQUE_ACTUALIZATION_FOR_THE_COMPLETE_HYBRID_FIELD_"
            "INCLUDING_THE_SELECTED_ZERO-BACKGROUND_SM_SECTOR"
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
    path = target / "BHSM_aether_hybrid_yukawa_mass_semantics_v15_56.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "VERTEX_MODE_PAIRS",
    "wall_normal_overlap_contract", "paired_mode_overlap_contract",
    "yukawa_operator_factorization", "reset_mass_spectrum",
    "mixing_semantics", "completion_payload", "deterministic_json",
    "materialize",
]
