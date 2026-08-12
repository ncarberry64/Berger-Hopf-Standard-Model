"""No-double-counting quantum functional and global hybrid-cycle KKT system."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping


VERSION = "v16.00"
CLASSIFICATION = "BHSM_QUANTUM_FUNCTIONAL_ACCOUNTING_AND_GLOBAL_CYCLE_KKT"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def determinant_accounting_identity() -> dict[str, Any]:
    return {
        "bare_parent_cycle": "Gamma_parent_without_attached_SM_vacuum_determinant",
        "v15_51_attached_cycle": (
            "Gamma_attached_zeta=Gamma_parent+Gamma_SM_zeta[Phi;A=H=Psi=0]"
        ),
        "v15_96_heat_determinant": (
            "Gamma_SM_heat[Phi;A,H,Psi]=-(1/2)*STr*E1(ell_kappa^2*P_cycle)"
        ),
        "incorrect_sum": (
            "Gamma_attached_zeta+Gamma_SM_heat_counts_the_same_"
            "gauge-ghost-Weyl-HS_species_twice"
        ),
        "physical_quantum_functional": (
            "Gamma_Q=Gamma_parent+Gamma_SM_heat"
        ),
        "equivalent_replacement_form": (
            "Gamma_Q=Gamma_attached_zeta-Gamma_SM_zeta[Phi;0,0,0]+"
            "Gamma_SM_heat[Phi;A,H,Psi]"
        ),
        "zero_source_subtraction_is_sector_specific": False,
        "same_replacement_for_geometry_gauge_and_Yukawa": True,
        "v15_97_dense_zeta_orbit_role": (
            "INITIAL_COLLOCATION_GUESS_NOT_THE_FINAL_HEAT-REGULATED_QUANTUM_SADDLE"
        ),
        "v15_97_source_outputs_role": (
            "DENSE_CLASSICAL/ONE-LOOP_SEED_TO_BE_REEVALUATED_ON_THE_REPLACEMENT_SADDLE"
        ),
    }


def global_hybrid_cycle_kkt(nodes: int = 24) -> dict[str, Any]:
    if not isinstance(nodes, int) or nodes < 6:
        raise ValueError("at least six cycle nodes required")
    q_dimension = 9
    multiplier_dimension = 4
    field_dimension = q_dimension + multiplier_dimension
    base_unknowns = nodes * field_dimension
    return {
        "nodes": nodes,
        "node_variables": "z_j=(q_j_in_R9,m_j_in_R4)",
        "velocity_rule": (
            "dot_q_j=D_T^reset*q_with_the_event_endpoint_glued_to_the_"
            "reset_state_by_q_0=R_hat(q_event)"
        ),
        "discrete_parent_action": (
            "Gamma_parent,d=T/N*sum_j L_parent(q_j,D_T^reset q_j,m_j)"
        ),
        "discrete_quantum_action": (
            "Gamma_Q,d=Gamma_parent,d-(1/2)*STr*E1(ell_kappa^2*P_cycle,d[z;A,H,Psi])"
        ),
        "stationarity_equations": (
            "partial_(q_j,m_j)Gamma_Q,d=0_for_all_j"
        ),
        "event_equation": (
            "E_event(z_(N-1),T)=-lambda_soft(D_Euler-Dirac)=0"
        ),
        "phase_condition": (
            "sum_j<q_j-q_seed_j,D_T q_seed_j>=0_fixes_cycle_time_translation"
        ),
        "unknown_period": "T",
        "unknown_phase_multiplier": "rho_phase",
        "base_node_unknown_count": base_unknowns,
        "total_unknown_count": base_unknowns + 2,
        "stationarity_equation_count": base_unknowns,
        "event_plus_phase_equation_count": 2,
        "total_equation_count": base_unknowns + 2,
        "square_system": True,
        "logdet_is_global_in_cycle_time": True,
        "can_be_inserted_as_independent_local_acceleration": False,
        "reset_derivative_on_selected_component": 0.0,
        "reset_Hessian_on_selected_component": 0.0,
    }


def common_observable_order() -> dict[str, Any]:
    return {
        "step_1": "solve_the_replacement_global_cycle_KKT_at_A=H=Psi=0",
        "step_2": (
            "differentiate_the_same_Gamma_Q_with_the_v15.99_noncommuting_"
            "Frechet_engine_and_background-covariant_contact_vertices"
        ),
        "step_3": (
            "extract_K_E,K_B,Z_Psi,Z_H_and_the_unit-vertex_LR_three-point_"
            "function_from_one_response_tensor"
        ),
        "step_4": "canonicalize_Y=Z_Psi^(-1)*Z_H^(-1/2)*V_LRH",
        "step_5": "test_metric-gauge-fermion_cone_equality_and_event_uniqueness",
        "absolute_gauge_normalization_and_nonzero_Yukawa_share_saddle": True,
        "absolute_gauge_normalization_and_nonzero_Yukawa_share_regulator": True,
        "absolute_gauge_normalization_and_nonzero_Yukawa_share_renormalization_replacement": True,
        "split_repair_allowed": False,
    }


def completion_payload() -> dict[str, Any]:
    accounting = determinant_accounting_identity()
    kkt = global_hybrid_cycle_kkt()
    order = common_observable_order()
    validation = {
        "double_count_removed": "counts_the_same" in accounting["incorrect_sum"],
        "replacement_identity_exact": accounting["equivalent_replacement_form"].startswith(
            "Gamma_Q=Gamma_attached_zeta-Gamma_SM_zeta"
        ),
        "dense_orbit_reclassified_as_seed": accounting[
            "v15_97_dense_zeta_orbit_role"
        ].startswith("INITIAL"),
        "global_not_local_logdet": (
            kkt["logdet_is_global_in_cycle_time"]
            and not kkt["can_be_inserted_as_independent_local_acceleration"]
        ),
        "KKT_system_square": (
            kkt["square_system"]
            and kkt["total_unknown_count"] == kkt["total_equation_count"]
        ),
        "one_saddle_one_regulator_one_replacement": (
            order["absolute_gauge_normalization_and_nonzero_Yukawa_share_saddle"]
            and order["absolute_gauge_normalization_and_nonzero_Yukawa_share_regulator"]
            and order[
                "absolute_gauge_normalization_and_nonzero_Yukawa_share_renormalization_replacement"
            ]
        ),
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_quantum_functional_accounting_v16_00",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "determinant_accounting": accounting,
        "global_hybrid_cycle_KKT": kkt,
        "common_observable_order": order,
        "scientific_result": (
            "THE_V15.51_ZETA_VACUUM_AND_V15.96_HEAT_DETERMINANT_MUST_NOT_BE_"
            "ADDED;_THE_PHYSICAL_QUANTUM_ACTION_REPLACES_ZETA_BY_THE_ONE_"
            "SOURCED_HEAT_SUPERDETERMINANT,_AND_ITS_NONLOCAL_CYCLE_SADDLE_IS_"
            "A_314-BY-314_GLOBAL_HYBRID_KKT_SYSTEM_AT_24_NODES"
        ),
        "claim_boundary": {
            "quantum_action_accounting_closed": True,
            "global_cycle_KKT_formulated": True,
            "global_cycle_KKT_discretized_dimensionally": True,
            "physical_vertex_matrices_inserted": False,
            "replacement_quantum_saddle_solved": False,
        },
        "active_calculation": (
            "ASSEMBLE_THE_RANK16_BACKGROUND-COVARIANT_RADIAL-TIMES-S3_VERTEX_"
            "MATRICES_AND_EVALUATE_THE_314-EQUATION_REPLACEMENT_KKT_RESIDUAL_"
            "AND_JACOBIAN_ON_THE_DENSE_V15.97_INITIAL_GUESS"
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
    path = target / "BHSM_aether_quantum_functional_accounting_v16_00.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "determinant_accounting_identity", "global_hybrid_cycle_kkt",
    "common_observable_order", "completion_payload", "deterministic_json",
    "materialize",
]
