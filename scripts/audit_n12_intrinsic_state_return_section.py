"""Audit action selection on the certified continuum child manifold.

The N12 radii theorem is a square normal-section theorem for a 57-row map on
196 Cauchy variables.  This audit distinguishes that certified normal root
from selection of one physical point/orbit along the retained child tangents.
It then types the first-positive-return map that the existing action, flow and
ordered-event section would provide if a return exists.  No return, clock or
observable is assumed or numerically manufactured here.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz"
)
DIRECT = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_CERTIFICATE.json"
)
CONTINUUM = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_CONTINUUM_EVENT_CHILD_CERTIFICATE.json"
)
NORMAL = ROOT / (
    "artifacts/n12_direct_checkpoint/BHSM_N12_EXACT_NORMAL_1E24.json"
)
CROSS = ROOT / "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
COLLECTIVE = ROOT / "artifacts/BHSM_aether_collective_symplectic_manifold_v15_22.json"
CLOCK = ROOT / "artifacts/BHSM_aether_joint_hamiltonian_selection_v15_2.json"
NORMAN = ROOT / "artifacts/BHSM_norman_cycle_ontology_v15_6.json"
RELATIVE_PERIODIC = ROOT / "artifacts/BHSM_relative_periodic_persistence_v15_7.json"
POST_PARENT = ROOT / (
    "artifacts/qxi_relative_energy_preparation/"
    "BHSM_POST_PARENT_FLAGSHIP_OBSERVABLE_GATE.json"
)
RESULT = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_INTRINSIC_STATE_RETURN_SECTION_GATE.json"
)
THEOREM = ROOT / "theory/n12_intrinsic_first_return_section.md"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    inputs = (
        STATE, DIRECT, CONTINUUM, NORMAL, CROSS, COLLECTIVE, CLOCK,
        NORMAN, RELATIVE_PERIODIC, POST_PARENT, THEOREM,
    )
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing intrinsic-state inputs: " + ", ".join(missing))

    checkpoint = np.load(STATE)
    state = np.asarray(checkpoint["state"], dtype=float)
    full_jacobian = np.asarray(checkpoint["paired_jacobian"], dtype=float)
    singular_values = np.linalg.svd(full_jacobian, compute_uv=False)
    threshold = (
        max(full_jacobian.shape) * np.finfo(float).eps * singular_values[0]
    )
    full_rank = int(np.count_nonzero(singular_values > threshold))
    full_nullity = int(full_jacobian.shape[1] - full_rank)

    direct = json.loads(DIRECT.read_text(encoding="utf-8"))
    continuum = json.loads(CONTINUUM.read_text(encoding="utf-8"))
    normal = json.loads(NORMAL.read_text(encoding="utf-8"))
    cross = json.loads(CROSS.read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    collective = json.loads(COLLECTIVE.read_text(encoding="utf-8"))
    clock = json.loads(CLOCK.read_text(encoding="utf-8"))
    norman = json.loads(NORMAN.read_text(encoding="utf-8"))
    relative_periodic = json.loads(RELATIVE_PERIODIC.read_text(encoding="utf-8"))
    post_parent = json.loads(POST_PARENT.read_text(encoding="utf-8"))

    scope = cross["normal_section_S2_compactness_scope"]
    cycle = cross["N6_reduced_local_energy_readout_reconnaissance"]
    order = int(direct["order"])
    physical_child_tangent_dimension = 6 * order - 6
    collective_contract = collective["collective_state_manifold_contract"]

    validation = {
        "direct_and_continuum_children_certified": (
            direct["DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED"] is True
            and continuum["CONTINUUM_EVENT_CHILD_CERTIFIED"] is True
        ),
        "stored_joint_state_has_196_variables": state.shape == (196,),
        "unchanged_full_linearized_map_has_57_rows": full_jacobian.shape == (57, 196),
        "full_linearized_row_rank_is_57": full_rank == 57,
        "local_full_state_nullity_is_139": full_nullity == 139,
        "certified_square_normal_map_has_rank_57": normal["analytic_rank"] == 57,
        "normal_section_is_not_a_physical_selector": scope["validation"][
            "normal_section_is_a_chart_choice_not_a_physical_selector"
        ] is True,
        "N12_child_tangent_dimension_is_66": physical_child_tangent_dimension == 66,
        "physical_child_tangents_are_retained": scope["validation"][
            "tangent_motion_is_not_reclassified_as_a_defect"
        ] is True,
        "collective_reduced_state_solution_is_absent": (
            collective_contract["actual_Phi_star_solution"] is None
            and collective["retained_phase_space_provenance"]
            ["physical_collective_state_manifold_present"] is False
        ),
        "relative_periodic_cycle_is_absent": cycle["v14_54_conditional_contract"][
            "relative_periodic_cycle_and_monodromy_exist"
        ] is False,
        "stable_reference_cycle_is_not_action_selected": clock["clock"][
            "action_selected_stable_core_cycle"
        ] is False,
        "historical_persistence_theorem_class_is_reused_not_reinvented": (
            norman["morphisms"][1]["symbol"] == "P"
            and norman["morphisms"][1]["theorem_class_owned"] is True
            and norman["morphisms"][1]["action_derived_map"] is False
            and relative_periodic["action_selected_orbit"] is None
        ),
        "no_observable_or_prediction_promoted": (
            post_parent["prediction_frozen"] is False
            and post_parent["held_out_comparison_performed"] is False
        ),
    }

    first_missing = (
        "PROVE_EXISTENCE_TRANSVERSALITY_AND_CONTINUUM_WELL_POSEDNESS_OF_"
        "THE_FIRST_POSITIVE_COMPLETE_EVENT_RETURN_MAP_ON_THE_EXISTING_"
        "GAUGE_TIME_QUOTIENTED_CHILD_MANIFOLD_OR_PROVE_ITS_RETURN_DOMAIN_EMPTY"
    )
    payload = {
        "artifact": "BHSM_N12_INTRINSIC_STATE_RETURN_SECTION_GATE",
        "classification": (
            "CONTINUUM_CHILD_IS_AN_ACTION_DEFINED_LOCAL_SOLUTION_MANIFOLD;_"
            "AN_ACTION_SELECTED_INTRINSIC_PHYSICAL_POINT_OR_ORBIT_IS_OPEN"
        ),
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in inputs
        },
        "regular_level_set_audit": {
            "map": "F12:R^196_TO_R^57",
            "stored_full_linearized_shape": list(full_jacobian.shape),
            "rank_threshold": float(threshold),
            "largest_singular_value": float(singular_values[0]),
            "smallest_row_singular_value": float(singular_values[-1]),
            "row_rank": full_rank,
            "local_linearized_nullity": full_nullity,
            "certified_normal_section_dimension": 57,
            "normal_section_root_ball_radius": direct["certified_root_ball"]["radius"],
            "normal_section_contraction_bound": direct["certified_root_ball"]
            ["contraction_bound"],
            "interpretation": (
                "the radii theorem selects one root in the chosen square normal "
                "section; it does not collapse the full complete-child tangent set"
            ),
        },
        "physical_tangent_moduli": {
            "existing_general_N_law": "6N-6",
            "N12_child_tangent_dimension": physical_child_tangent_dimension,
            "tangent_kernel": scope["normal_tangent_decomposition"]["tangent_kernel"],
            "tangents_are_physical_and_retained": True,
            "normal_complement_is_a_physical_selector": False,
            "nonzero_motion_momentum_or_time_dependence_is_a_defect": False,
        },
        "action_selection_status": {
            "unchanged_action_equations_closed": True,
            "ordered_event_branch_action_owned_and_simple": direct[
                "existing_physical_gates"
            ]["corrected_action_owned_ordered_branch"],
            "one_complete_child_normal_representative_certified": True,
            "one_intrinsic_physical_point_or_orbit_selected": False,
            "reason": (
                "the retained physical tangent moduli are not fixed by the normal "
                "chart, and no reduced collective solution or returned orbit exists"
            ),
        },
        "existing_assets_and_absences": {
            "candidate_reduced_action": collective_contract["reduced_action"],
            "candidate_collective_state_equation": collective_contract["state_equation"],
            "actual_collective_solution": collective_contract["actual_Phi_star_solution"],
            "positive_duration_local_child_flow": True,
            "relative_periodic_cycle_and_monodromy_exist": False,
            "action_selected_stable_reference_cycle": False,
            "historical_v15_6_persistence_map_type": norman["morphisms"][1],
            "historical_v15_7_relative_periodic_theorem_class": (
                relative_periodic["theorem_class"]
            ),
            "historical_v15_7_action_selected_orbit": (
                relative_periodic["action_selected_orbit"]
            ),
            "reuse_conclusion": (
                "THE_CURRENT_FIRST_RETURN_SECTION_INSTANTIATES_THE_EXISTING_"
                "PERSISTENCE_THEOREM_CLASS_ON_THE_CERTIFIED_CONTINUUM_CHILD;_"
                "FORMATION_OR_DE_ENVELOPMENT_IS_NOT_REOPENED"
            ),
        },
        "derived_first_return_section": {
            "role": "ACTION_OWNED_STATE_SELECTION_OBJECT_NOT_A_NEW_PHYSICAL_EQUATION",
            "section": (
                "Sigma_complete_is_the_existing_ordered_complete_event_section_"
                "inside_the_certified_continuum_child_manifold"
            ),
            "existing_event_equation": (
                "E_ord(Y)=THE_ALREADY_SELECTED_SIMPLE_ORDERED_EULER_DIRAC_"
                "EIGENVALUE_EQUALS_ZERO"
            ),
            "existing_event_to_child_map": (
                "C_infinity:E_prime_TO_THE_CERTIFIED_COMPLETE_PERSISTENT_CHILD_"
                "RECONSTRUCTION_AT_E_prime"
            ),
            "map": (
                "P([E,C(E)])=[E_prime,C_infinity(E_prime)]_WHERE_"
                "E_prime=Flow_retained^tau(E,C)(C)_AND_tau_IS_THE_FIRST_"
                "STRICTLY_POSITIVE_TIME_WITH_E_ord(E_prime)=0"
            ),
            "quotient": "EXISTING_GAUGE_AND_WHOLE_SYSTEM_TIME_TRANSLATION_ONLY",
            "domain": (
                "states_for_which_the_existing_admissible_persistent_flow_has_a_"
                "finite_transverse_first_positive_complete_event_return"
            ),
            "fixed_or_periodic_orbits_would_be_action_selected_states": True,
            "required_existing_properties_to_close": [
                "RETAINED_CHILD_FLOW_EXISTS_AND_REMAINS_ETA_DIRAC_ADMISSIBLE_UNTIL_tau",
                "A_FINITE_STRICTLY_POSITIVE_FIRST_RETURN_tau_EXISTS",
                "THE_RETURNED_ORDERED_EVENT_IS_SIMPLE_AND_TRANSVERSE",
                "THE_CERTIFIED_CONTINUUM_EVENT_TO_CHILD_MAP_APPLIES_AT_E_prime",
                "THE_RESULT_DESCENDS_TO_THE_EXISTING_GAUGE_TIME_QUOTIENT",
            ],
            "return_existence_or_transversality_proved": False,
            "map_executable": False,
            "new_clock_period_event_equation_constraint_or_gate_added": False,
            "conditional_regular_map_theorem": (
                "PROVED_BY_THE_IMPLICIT_FUNCTION_THEOREM_AT_ANY_FINITE_"
                "SIMPLE_TRANSVERSE_ADMISSIBLE_FIRST_RETURN"
            ),
            "return_time_derivative": (
                "D_tau[h]=-D_E_ord(E_prime)D_Flow_tau[h]/"
                "(D_E_ord(E_prime)V(E_prime))"
            ),
            "proof": "theory/n12_intrinsic_first_return_section.md",
        },
        "first_missing_action_owned_object": first_missing,
        "after_it": (
            "CLASSIFY_FIXED_AND_PRIMITIVE_PERIODIC_RETURN_ORBITS_MODULO_TRUE_"
            "EQUIVALENCES;_THEN_EVALUATE_THE_SHORTEST_INTRINSIC_DIMENSIONLESS_"
            "ACTION_INVARIANT_AND_FREEZE_BEFORE_COMPARISON"
        ),
        "prediction_frozen": False,
        "held_out_comparison_performed": False,
        "CONTINUUM_EVENT_CHILD_CERTIFIED": True,
        "FULL_BHSM_COMPLETE": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "classification": payload["classification"],
        "first_missing_action_owned_object": first_missing,
        "full_nullity": full_nullity,
        "N12_child_tangent_dimension": physical_child_tangent_dimension,
        "result": str(RESULT.relative_to(ROOT)).replace("\\", "/"),
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
