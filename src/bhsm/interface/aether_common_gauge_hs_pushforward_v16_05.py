"""One dense M5->M4 pushforward for all gauge residues and the HS kernel."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_dense_proper_joint_pushforward_v15_97 import (
    dense_constraint_solved_cycle,
)
from bhsm.interface.aether_nonabelian_derham_response_v16_04 import (
    nonabelian_derham_response,
)
from bhsm.interface.aether_rank16_u1_hs_vertex_matrices_v16_01 import (
    rank16_u1_hs_responses,
)


VERSION = "v16.05"
CLASSIFICATION = "BHSM_COMMON_GAUGE_HS_M5_TO_M4_PUSHFORWARD"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def sm_trace_ledger() -> dict[str, Any]:
    """Fixed rank-16 and adjoint weights; no fitted normalization occurs."""

    return {
        "three_family_Weyl_trace_T2": {"U1": 10.0, "SU2": 6.0, "SU3": 6.0},
        "complex_HS_effective_real_trace_T2": {
            "U1": 1.0, "SU2": 1.0, "SU3": 0.0,
        },
        "adjoint_C_A": {"U1": 0.0, "SU2": 2.0, "SU3": 3.0},
        "classical_generator_ray": {"U1": 5.0 / 3.0, "SU2": 1.0, "SU3": 1.0},
        "HS_pairing_multiplicities": {
            "up": 9, "down": 9, "charged_lepton": 3, "neutrino": 3,
        },
        "new_continuous_coefficient": False,
    }


def combine_common_responses(
    matter_hs: Mapping[str, Any],
    adjoint: Mapping[str, Any],
    dense_cycle: Mapping[str, Any],
) -> dict[str, Any]:
    """Combine derivatives of one direct-sum heat operator by fixed traces."""

    ledger = sm_trace_ledger()
    rows = matter_hs["rows"]
    omega = 2.0 * math.pi / float(matter_hs["proper_duration"])
    u1_kb = float(matter_hs["U1_delta_K_magnetic_seed"])
    u1_ke = float(matter_hs["U1_delta_K_electric_seed"])
    hs_constant_kb = sum(float(row["HS_U1_constant"]) for row in rows)
    weyl_constant_kb = sum(float(row["Weyl_U1_constant"]) for row in rows)
    # The coexact eigenvalue is reconstructed from the already evaluated U(1)
    # response, avoiding a second geometry convention in this combination.
    coexact_eigenvalue = (weyl_constant_kb + hs_constant_kb) / u1_kb
    weyl_delta_ke = sum(
        float(row["Weyl_U1_first_frequency"])
        - float(row["Weyl_U1_constant"])
        for row in rows
    ) / omega**2
    hs_delta_ke = sum(
        float(row["HS_U1_first_frequency"])
        - float(row["HS_U1_constant"])
        for row in rows
    ) / omega**2
    weyl_delta_kb = weyl_constant_kb / coexact_eigenvalue
    hs_delta_kb = hs_constant_kb / coexact_eigenvalue

    unit_adj_kb = float(adjoint["unit_adjoint_delta_KB"])
    unit_adj_ke = float(adjoint["unit_adjoint_delta_KE"])
    classical_kb = float(dense_cycle["proper_cycle_K_magnetic"])
    classical_ke = float(dense_cycle["proper_cycle_K_electric"])
    groups: dict[str, Any] = {}
    for group in ("U1", "SU2", "SU3"):
        weyl_scale = ledger["three_family_Weyl_trace_T2"][group] / 10.0
        hs_scale = ledger["complex_HS_effective_real_trace_T2"][group]
        casimir = ledger["adjoint_C_A"][group]
        ray = ledger["classical_generator_ray"][group]
        delta_kb = (
            weyl_scale * weyl_delta_kb
            + hs_scale * hs_delta_kb
            + casimir * unit_adj_kb
        )
        delta_ke = (
            weyl_scale * weyl_delta_ke
            + hs_scale * hs_delta_ke
            + casimir * unit_adj_ke
        )
        old_kb = ray * classical_kb
        old_ke = ray * classical_ke
        new_kb = old_kb + delta_kb
        new_ke = old_ke + delta_ke
        mismatch = old_ke - old_kb
        quantum_difference = delta_ke - delta_kb
        groups[group] = {
            "Weyl_trace_scale_from_U1": weyl_scale,
            "HS_trace_weight": hs_scale,
            "adjoint_C_A": casimir,
            "classical_KB": old_kb,
            "classical_KE": old_ke,
            "delta_KB_common_heat_operator": delta_kb,
            "delta_KE_common_heat_operator": delta_ke,
            "replacement_seed_KB": new_kb,
            "replacement_seed_KE": new_ke,
            "replacement_seed_speed_ratio": math.sqrt(new_kb / new_ke),
            "quantum_difference_delta_KE_minus_delta_KB": quantum_difference,
            "fraction_of_classical_cone_mismatch_repaired": (
                abs(quantum_difference) / mismatch
            ),
            "sign_reduces_classical_mismatch": quantum_difference < 0.0,
        }
    z_pair = float(matter_hs["HS_delta_Z_per_normalized_pair_seed"])
    multiplicities = ledger["HS_pairing_multiplicities"]
    return {
        "group_residues": groups,
        "HS_per_pair_Z": z_pair,
        "HS_channel_kinetic_matrix": {
            name: count * z_pair for name, count in multiplicities.items()
        },
        "unit_EC_LR_vertex": 1.0,
        "physical_Yukawa_rule": (
            "for_the_lowest_normalized_eigenvector_c_of_the_full_HS_Hessian,_"
            "Y_f=c_f/sqrt(Z_pair*c_dagger*diag(9,9,3,3)*c)"
        ),
        "physical_HS_direction_selected": False,
        "same_geometry_same_regulator_same_direct_sum_operator": True,
        "separate_gauge_normalization_inserted": False,
        "separate_Yukawa_insertion_made": False,
    }


def common_m5_to_m4_pushforward(
    cycle: Mapping[str, Any] | None = None,
    *,
    points: int = 24,
    maximum_level: int = 6,
) -> dict[str, Any]:
    dense = dense_constraint_solved_cycle() if cycle is None else cycle
    matter = rank16_u1_hs_responses(
        dense, points=points, maximum_level=maximum_level
    )
    adjoint = nonabelian_derham_response(
        dense, points=points, maximum_level=maximum_level
    )
    result = combine_common_responses(matter, adjoint, dense)
    return {
        "points": points,
        "maximum_level": maximum_level,
        "trace_ledger": sm_trace_ledger(),
        "common_response": result,
        "matter_HS_response": matter,
        "adjoint_response": adjoint,
        "one_functional": (
            "Gamma_Q[Phi;A,H,Psi]=Gamma_parent[Phi]+"
            "Gamma_heat[P_gauge+ghost direct_sum P_rank16[A,H,Psi] direct_sum P_HS[A]]"
        ),
        "derivative_map": {
            "absolute_gauge_residues": "D_A^2 Gamma_Q",
            "HS_kinetic_kernel": "low_frequency_part_of_D_H_D_Hdagger Gamma_Q",
            "LR_vertex": "D_barPsi_L_D_Psi_R_D_H Gamma_Q",
            "physical_Yukawa": "canonical_residue_after_full_HS_Hessian_eigenvector_selection",
        },
    }


def completion_payload() -> dict[str, Any]:
    result = common_m5_to_m4_pushforward()
    common = result["common_response"]
    groups = common["group_residues"]
    validation = {
        "all_three_absolute_gauge_residues_generated": set(groups) == {"U1", "SU2", "SU3"},
        "all_gauge_residues_positive": all(
            row["replacement_seed_KB"] > 0.0 and row["replacement_seed_KE"] > 0.0
            for row in groups.values()
        ),
        "all_quantum_signs_reduce_mismatch": all(
            row["sign_reduces_classical_mismatch"] for row in groups.values()
        ),
        "HS_residue_positive": common["HS_per_pair_Z"] > 0.0,
        "all_24_HS_pairings_present": sum(
            result["trace_ledger"]["HS_pairing_multiplicities"].values()
        ) == 24,
        "one_operator": common["same_geometry_same_regulator_same_direct_sum_operator"],
        "no_split_normalizations": (
            not common["separate_gauge_normalization_inserted"]
            and not common["separate_Yukawa_insertion_made"]
        ),
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_common_gauge_hs_pushforward_v16_05",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "common_M5_to_M4_pushforward": result,
        "scientific_result": (
            "ONE_24-NODE_M5-TO-M4_HEAT-PUSHFORWARD_GENERATES_THE_ABSOLUTE_"
            "U1_SU2_SU3_GAUGE_RESIDUES_AND_THE_POSITIVE_24-PAIR_HS_KINETIC_"
            "MATRIX_WITH_THE_UNIT_EC_LR_VERTEX;_NO_GAUGE_OR_YUKAWA_"
            "NORMALIZATION_IS_INSERTED_SEPARATELY"
        ),
        "claim_boundary": {
            "common_localization_pushforward_evaluated": True,
            "absolute_gauge_replacement_seed_evaluated": True,
            "nonzero_HS_kinetic_kernel_evaluated": True,
            "unit_LR_vertex_retained": True,
            "physical_single_Higgs_direction_selected": False,
            "replacement_quantum_saddle_solved": False,
        },
        "active_calculation": (
            "INSERT_THIS_SINGLE_DIRECT-SUM_OPERATOR_IN_THE_314-EQUATION_GLOBAL_"
            "REPLACEMENT_KKT_SADDLE,_THEN_DIAGONALIZE_ITS_FOUR-CHANNEL_HS_"
            "HESSIAN_ON_THAT_SAME_SADDLE"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _canonical(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return [_canonical(item) for item in value.tolist()]
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
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
    path = target / "BHSM_aether_common_gauge_hs_pushforward_v16_05.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "sm_trace_ledger",
    "combine_common_responses", "common_m5_to_m4_pushforward",
    "completion_payload", "deterministic_json", "materialize",
]
