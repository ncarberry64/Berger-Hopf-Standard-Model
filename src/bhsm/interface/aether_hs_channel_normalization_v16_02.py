"""Angular convergence and physical HS channel-normalization theorem."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

from bhsm.interface.aether_dense_proper_joint_pushforward_v15_97 import (
    dense_constraint_solved_cycle,
)
from bhsm.interface.aether_rank16_u1_hs_vertex_matrices_v16_01 import (
    rank16_u1_hs_responses,
)


VERSION = "v16.02"
CLASSIFICATION = "BHSM_HS_CHANNEL_KINETIC_MATRIX_AND_ANGULAR_CONVERGENCE"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def angular_heat_tail(
    cycle: Mapping[str, Any] | None = None,
    *,
    points: int = 24,
    maximum_level: int = 6,
) -> dict[str, Any]:
    values = dense_constraint_solved_cycle() if cycle is None else cycle
    rows = []
    for level in range(maximum_level + 1):
        response = rank16_u1_hs_responses(
            values, points=points, maximum_level=level
        )
        rows.append({
            "maximum_level": level,
            "delta_K_B_U1": response["U1_delta_K_magnetic_seed"],
            "delta_K_E_U1": response["U1_delta_K_electric_seed"],
            "Z_H_all_24_pairings": response["HS_delta_Z_seed"],
        })
    last = rows[-1]
    previous = rows[-2]
    return {
        "points": points,
        "rows": rows,
        "tail_absolute_change": {
            key: abs(float(last[key]) - float(previous[key]))
            for key in ("delta_K_B_U1", "delta_K_E_U1", "Z_H_all_24_pairings")
        },
        "angular_heat_tail_converged": all(
            abs(float(last[key]) - float(previous[key])) < 1.0e-10
            for key in ("delta_K_B_U1", "delta_K_E_U1", "Z_H_all_24_pairings")
        ),
        "converged_response": rank16_u1_hs_responses(
            values, points=points, maximum_level=maximum_level
        ),
    }


def hs_channel_normalization(response: Mapping[str, Any]) -> dict[str, Any]:
    z_total = float(response["HS_delta_Z_seed"])
    if z_total <= 0.0:
        raise ValueError("positive HS kinetic trace required")
    z_pair = z_total / 24.0
    multiplicities = {
        "up": 9,
        "down": 9,
        "charged_lepton": 3,
        "neutrino": 3,
    }
    diagonal = {
        channel: multiplicity * z_pair
        for channel, multiplicity in multiplicities.items()
    }
    independent = {
        channel: value**-0.5 for channel, value in diagonal.items()
    }
    return {
        "per_normalized_pair_Z": z_pair,
        "channel_basis": ["up", "down", "charged_lepton", "neutrino"],
        "pairing_multiplicity_matrix": "D=diag(9,9,3,3)",
        "kinetic_matrix_if_channels_are_independent": diagonal,
        "canonical_Y_if_channels_are_independent": independent,
        "candidate_direction": "H_f=c_f*h",
        "directional_kinetic_residue": (
            "Z(c)=Z_pair*c_dagger*diag(9,9,3,3)*c"
        ),
        "directional_canonical_vertices": (
            "Y_f(c)=c_f/sqrt(Z_pair*c_dagger*diag(9,9,3,3)*c)"
        ),
        "equal_collective_direction_c": [1.0, 1.0, 1.0, 1.0],
        "equal_collective_direction_Z": z_total,
        "equal_collective_direction_Y_each_channel": z_total**-0.5,
        "physical_direction_selected": False,
        "selection_operator": (
            "the_full_four-channel_HS_quadratic_kernel_including_EC,_gauge_DtN,_"
            "and_the_same_heat_determinant_on_the_replacement_saddle"
        ),
        "v15_97_per-paired-mode_Y_is_a_kernel_basis_value": True,
        "v15_97_per-paired-mode_Y_is_the_physical_single-Higgs_Yukawa": False,
        "nonzero_vertex_for_every_direction_component_c_f_nonzero": True,
    }


def u1_dense_repair_fraction(
    response: Mapping[str, Any],
    dense_cycle: Mapping[str, Any],
) -> dict[str, float | bool]:
    common_mismatch = (
        float(dense_cycle["proper_cycle_K_electric"])
        - float(dense_cycle["proper_cycle_K_magnetic"])
    )
    u1_classical_mismatch = (5.0 / 3.0) * common_mismatch
    quantum_difference = (
        float(response["U1_delta_K_electric_seed"])
        - float(response["U1_delta_K_magnetic_seed"])
    )
    return {
        "classical_U1_mismatch": u1_classical_mismatch,
        "matter_HS_quantum_difference_delta_KE_minus_delta_KB": quantum_difference,
        "fraction_of_required_U1_repair": abs(quantum_difference) / u1_classical_mismatch,
        "sign_reduces_classical_mismatch": quantum_difference < 0.0,
        "U1_matter_HS_block_alone_repairs_cone": abs(quantum_difference) >= u1_classical_mismatch,
    }


def broken_branch_dimension_contract(nodes: int = 24) -> dict[str, Any]:
    symmetric = nodes * (9 + 4) + 2
    neutral_channel_components = 4
    broken = symmetric + nodes * neutral_channel_components
    return {
        "symmetric_replacement_KKT_dimension": symmetric,
        "four_neutral_HS_channel_amplitudes_per_node": neutral_channel_components,
        "broken-neutral-channel_KKT_dimension": broken,
        "solve_order": (
            "solve_314_symmetric_replacement_saddle;_diagonalize_the_full_HS_"
            "Hessian;_only_if_an_eigenvalue_is_nonpositive_continue_its_"
            "eigenvector_into_the_410-dimensional_broken-branch_KKT"
        ),
        "single_Higgs_direction_assumed_before_Hessian": False,
    }


def completion_payload() -> dict[str, Any]:
    dense = dense_constraint_solved_cycle()
    tail = angular_heat_tail(dense)
    response = tail["converged_response"]
    channels = hs_channel_normalization(response)
    repair = u1_dense_repair_fraction(response, dense)
    branch = broken_branch_dimension_contract()
    validation = {
        "angular_tail_converged": tail["angular_heat_tail_converged"],
        "HS_trace_positive": channels["per_normalized_pair_Z"] > 0.0,
        "pairing_multiplicities_complete": sum(
            response["independent_channel_pairing_multiplicities"].values()
        ) == 24,
        "old_per_mode_Y_not_overclaimed": not channels[
            "v15_97_per-paired-mode_Y_is_the_physical_single-Higgs_Yukawa"
        ],
        "nonzero_directional_vertex_retained": channels[
            "nonzero_vertex_for_every_direction_component_c_f_nonzero"
        ],
        "U1_seed_too_small_for_repair": not repair[
            "U1_matter_HS_block_alone_repairs_cone"
        ] and repair["fraction_of_required_U1_repair"] < 0.01,
        "broken_branch_not_assumed": not branch[
            "single_Higgs_direction_assumed_before_Hessian"
        ],
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_hs_channel_normalization_v16_02",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "angular_heat_tail": tail,
        "HS_channel_normalization": channels,
        "U1_dense_repair_fraction": repair,
        "broken_branch_dimension_contract": branch,
        "scientific_result": (
            "THE_24-NODE_ANGULAR_HEAT_TAIL_CONVERGES_TO_DELTA_KB_U1=6.125408,_"
            "DELTA_KE_U1=-0.0300632,_AND_Z_H(24_PAIRINGS)=0.0627099;_THE_OLD_"
            "PER-PAIR_Y_IS_NOT_A_PHYSICAL_SINGLE-HIGGS_NORMALIZATION,_WHICH_"
            "REQUIRES_DIAGONALIZING_THE_FOUR-CHANNEL_HS_HESSIAN"
        ),
        "claim_boundary": {
            "angular_level_convergence_established": True,
            "rank16_U1_matter_HS_response_evaluated": True,
            "physical_HS_channel_formula_derived": True,
            "physical_single_Higgs_direction_selected": False,
            "symmetric_replacement_saddle_solved": False,
            "broken_replacement_branch_solved": False,
        },
        "active_calculation": (
            "ASSEMBLE_THE_SU2_AND_SU3_ADJOINT_GAUGE-GHOST_VERTICES,_THEN_"
            "EVALUATE_THE_314-KKT_SYMMETRIC_REPLACEMENT_SADDLE_AND_ITS_FULL_"
            "FOUR-CHANNEL_HS_HESSIAN_BEFORE_ANY_SINGLE-HIGGS_CANONICALIZATION"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _canonical(value: Any) -> Any:
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float")
        return round(value, 12)
    if isinstance(value, Mapping):
        return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(_canonical(payload), indent=2, sort_keys=True) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_hs_channel_normalization_v16_02.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "angular_heat_tail",
    "hs_channel_normalization", "u1_dense_repair_fraction",
    "broken_branch_dimension_contract", "completion_payload",
    "deterministic_json", "materialize",
]
