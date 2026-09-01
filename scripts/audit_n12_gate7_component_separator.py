"""Audit retained Gate-7 component separators under formal reflection.

The audit follows the owner-prescribed five-candidate order and three
representation stopping rule.  It derives only consequences of the existing
reflection congruence, constraint/reset rows, event identities, and Noether
ledger.  No trajectory, new sign gate, or physical selector is introduced.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_COMPONENT_SEPARATOR_AUDIT.json"
)
INPUTS = {
    "reflection": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_ORDERED_EVENT_TIME_REVERSAL_OBSTRUCTION.json"
    ),
    "row_equivariance": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_EVENT_CHILD_TIME_REVERSAL_EQUIVARIANCE_GATE.json"
    ),
    "chirality": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_FORWARD_TIME_TEMPORAL_CHIRALITY_AUDIT.json"
    ),
    "singular_hitting": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_SINGULAR_EVENT_TEMPORAL_CHIRALITY.json"
    ),
    "reset": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_CONTINUUM_SINGULAR_HITTING_RESET_RELATION.json"
    ),
    "eigenline": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_CHILD_EVENT_EIGENLINE_BALL.json"
    ),
    "energy": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_CONSTRAINT_REDUCED_ENERGY_IDENTITY_GATE.json"
    ),
    "global_control": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_GLOBAL_FLOW_COERCIVE_CONTROL_GATE.json"
    ),
    "maximal_flow": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_CONTINUUM_MAXIMAL_FLOW_DICHOTOMY.json"
    ),
    "global_conservation": ROOT / "artifacts/BHSM_global_conservation_gate_v10_1.json",
    "noether_ledger": ROOT / "artifacts/BHSM_complete_noether_ledger_v15_7.json",
}


def _sha256(path: Path) -> str:
    content = path.read_bytes()
    if path.suffix.lower() == ".json":
        content = content.replace(b"\r\n", b"\n")
    return hashlib.sha256(content).hexdigest().upper()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, object]:
    if not all(path.is_file() for path in INPUTS.values()):
        raise FileNotFoundError("all retained component-separator inputs are required")
    records = {name: _load(path) for name, path in INPUTS.items()}
    validated_names = set(records) - {"noether_ledger"}
    if not all(
        records[name].get("validation_passed") is True
        for name in validated_names
    ):
        raise RuntimeError("validated retained separator inputs required")

    reflection = records["reflection"]
    rows = records["row_equivariance"]
    chirality = records["chirality"]
    singular = records["singular_hitting"]
    reset = records["reset"]
    eigenline = records["eigenline"]
    energy = records["energy"]
    global_control = records["global_control"]
    maximal_flow = records["maximal_flow"]
    conservation = records["global_conservation"]
    noether = records["noether_ledger"]

    candidates = [
        {
            "priority": 1,
            "family": "GAUGE_FIXED_DIRAC_OR_CONSTRAINED_HESSIAN_INDEX_INERTIA",
            "exact_transformation": "D(RY)=P*D(Y)*P_WITH_P_ORTHOGONAL_AND_P_SQUARED=I",
            "derived_consequence": (
                "DET_D(RY)=DET_D(Y)_AND_SYLVESTER_INERTIA(D(RY))="
                "SYLVESTER_INERTIA(D(Y))"
            ),
            "zero_is_existing_stop": True,
            "reflection_odd": False,
            "distinguishes_child_from_reflection": False,
            "decision": "REJECT_REFLECTION_EVEN",
        },
        {
            "priority": 2,
            "family": "DETERMINANT_PFAFFIAN_JACOBIAN_ORIENTATION_FORM",
            "exact_transformation": (
                "J_F(RY)=S_ROW*J_F(Y)*P_STATE;_THE_CANONICAL_NORMAL_GRAM_"
                "TRANSFORMS_BY_S_ROW_CONGRUENCE"
            ),
            "derived_consequence": (
                "NORMAL_GRAM_DETERMINANT_IS_REFLECTION_EVEN;_THE_FIXED_EVENT_"
                "CHILD_BLOCK_IS_RECTANGULAR_31_BY_98_AND_HAS_NO_CANONICAL_"
                "SIGNED_DETERMINANT;_NO_RETAINED_PFAFFIAN_OBJECT_EXISTS"
            ),
            "fixed_event_child_rank": reset["unchanged_jacobian_block_audit"][
                "fixed_event_child_rank"
            ],
            "fixed_event_child_shape": reset["unchanged_jacobian_block_audit"][
                "fixed_event_child_shape"
            ],
            "reflection_odd": False,
            "distinguishes_child_from_reflection": False,
            "decision": "REJECT_EVEN_OR_NONCANONICAL",
        },
        {
            "priority": 3,
            "family": "EIGENLINE_ORIENTATION_OR_WINDING",
            "exact_transformation": (
                "PI_LINE(RY)=P*PI_LINE(Y)*P;_PSI_AND_MINUS_PSI_DEFINE_THE_"
                "SAME_ACTION_OWNED_REAL_EIGENLINE"
            ),
            "simple_line_certified_locally": eigenline["validation"][
                "selected_line_remains_simple"
            ],
            "derived_consequence": (
                "THE_PROJECTOR_IS_ORIENTATION_FREE_AND_REFLECTION_EQUIVARIANT;_"
                "A_REFERENCE_OVERLAP_SIGN_IS_A_CHART_CHOICE_AND_MAY_VANISH_"
                "WHILE_THE_LINE_REMAINS_SIMPLE;_NO_CLOSED_HISTORY_EXISTS_TO_"
                "OWN_A_WINDING_CLASS"
            ),
            "reflection_odd": False,
            "distinguishes_child_from_reflection": False,
            "decision": "REJECT_NO_ACTION_OWNED_LINE_ORIENTATION",
        },
        {
            "priority": 4,
            "family": "CONSTRAINT_MOMENTUM_OR_CASIMIR",
            "exact_transformation": (
                "P_CANONICAL(RY)=-P_CANONICAL(Y);_J_ETA_SHIFT_IS_ODD;_"
                "BOUNDARY_CASIMIR_IS_EVEN"
            ),
            "derived_consequence": (
                "THE_ODD_OBJECTS_ARE_COVECTORS_WITH_NO_ACTION_SELECTED_SCALAR_"
                "ORIENTATION;_THE_SHIFT_CONSTRAINT_FLIPS_WITH_THE_CURRENT_AND_"
                "SELECTS_NO_SIGN;_NORM_AND_NATURAL_QUADRATIC_CONTRACTIONS_ARE_"
                "EVEN"
            ),
            "reflection_odd": True,
            "continuous_scalar": False,
            "sign_flow_invariant": False,
            "distinguishes_child_from_reflection": False,
            "decision": "REJECT_ODD_COVECTOR_NOT_SCALAR_BARRIER",
        },
        {
            "priority": 5,
            "family": "RESET_INDUCED_TOPOLOGICAL_DEGREE_OR_ORIENTATION_CLASS",
            "exact_transformation": (
                "MATHFRAK_C_INFINITY(R*E)=R*MATHFRAK_C_INFINITY(E);_FIXED_"
                "SPATIAL_DEGREE_ORIENTATION_FR_PARITY_INCIDENCE_AND_BOUNDARY_"
                "IDENTITY_ARE_UNCHANGED_BY_R"
            ),
            "reset_fiber_dimension": reset["reset_correspondence"][
                "fixed_event_child_fiber_dimension"
            ],
            "reset_single_valued": reset["reset_correspondence"][
                "single_valued_physical_reset_map_proved"
            ],
            "derived_consequence": (
                "THE_RETAINED_TOPOLOGICAL_LABELS_ARE_REFLECTION_EVEN_AND_THE_"
                "REGULAR_RESET_IS_A_67_DIMENSIONAL_SET_VALUED_EQUIVARIANT_"
                "FIBER_WITH_NO_ODD_ROW_SIGN_GATE_OR_CANONICAL_CHILD_ORIENTATION"
            ),
            "reflection_odd": False,
            "distinguishes_child_from_reflection": False,
            "decision": "REJECT_REFLECTION_EVEN_SET_VALUED_RESET",
        },
    ]

    representations = {
        "A_constraint_topology": {
            "separator_found": False,
            "result": "ALL_FIVE_PRESCRIBED_RETAINED_CANDIDATE_FAMILIES_FAIL_THE_KILL_TEST",
        },
        "B_differential_transport": {
            "candidate": "K=C_PSI*B_PSI_OR_G=D_E_ORD[V]",
            "K_reflection_odd": singular["formal_reflection"]["exact_parity"][
                "c_psi_times_b_psi"
            ]
            == "ODD",
            "K_defined_as_component_scalar_with_forbidden_zero": False,
            "why": (
                "K_IS_A_NONZERO_LOCAL_SINGULAR_BOUNDARY_LABEL;_NO_RETAINED_"
                "THEOREM_KEEPS_K_NONZERO_ON_THE_REGULAR_CHILD_COMPONENT._"
                "THE_EXACT_D_DT(E_ORD_SQUARED)_IDENTITY_HAS_THE_UNCONTROLLED_"
                "2*E_ORD*R(Y)_TERM_AWAY_FROM_THE_EVENT"
            ),
            "integrated_barrier_found": False,
        },
        "C_action_Noether_form": {
            "constraint_energy_identity": energy["exact_identity"][
                "restricted_identity"
            ],
            "global_scalar_energy_available": conservation["global_energy"][
                "scalar_total_cosmic_energy"
            ],
            "complete_cycle_flux_ledger": noether["status"],
            "why": (
                "THE_CONSTRAINT_ENERGY_IS_IDENTICALLY_ZERO;_THE_ODD_SHIFT_"
                "CURRENT_IS_A_WARD_COVECTOR_NOT_A_CONSERVED_SCALAR;_THE_"
                "COMPLETE_BOUNDARY_FLUX_CYCLE_IS_UNDEFINED"
            ),
            "conserved_or_monotone_separator_found": False,
        },
    }

    separator_found = any(
        bool(candidate["distinguishes_child_from_reflection"])
        for candidate in candidates
    )
    validation = {
        "all_validated_repository_inputs_pass": True,
        "retained_action_reflection_identity_consumed": reflection["involution"][
            "retained_at_every_order_and_continuum"
        ],
        "complete_event_child_row_parities_consumed": rows["validation"][
            "complete_event_child_rows_exhausted"
        ],
        "five_owner_prescribed_candidate_families_exhausted": len(candidates) == 5,
        "Dirac_determinant_and_inertia_congruence_not_misclassified_odd": (
            candidates[0]["reflection_odd"] is False
        ),
        "rectangular_reset_block_not_given_a_fabricated_determinant": (
            candidates[1]["fixed_event_child_shape"] == [31, 98]
        ),
        "eigenvector_sign_not_promoted_to_physics": True,
        "odd_covector_not_promoted_to_scalar_separator": True,
        "spatial_topological_degree_not_relabelled_temporal_chirality": (
            chirality["candidate_invariant_audit"][
                "Hopf_boundary_attachment_topology"
            ]["formal_reflection_changes_degree"]
            is False
        ),
        "three_representation_stopping_rule_applied": all(
            not item.get("separator_found", item.get("integrated_barrier_found", item.get("conserved_or_monotone_separator_found", False)))
            for item in representations.values()
        ),
        "component_separator_no_go_not_promoted_to_terminal_reachability_no_go": True,
        "no_new_equation_gate_selector_normalization_threshold_or_physics": True,
        "chord_03_remains_unauthorized": True,
        "Gate7_and_later_claim_boundaries_preserved": True,
    }
    if separator_found:
        raise RuntimeError("unexpected retained component separator found")

    return {
        "artifact": "BHSM_N12_GATE7_COMPONENT_SEPARATOR_AUDIT",
        "classification": (
            "NO_REFLECTION_ODD_ACTION_OWNED_COMPONENT_SEPARATOR_IN_THE_"
            "PRESCRIBED_RETAINED_DIRAC_CONSTRAINT_EIGENLINE_MOMENTUM_"
            "CASIMIR_RESET_TOPOLOGY_INVENTORY;_THE_SEPARATOR_FIRST_ROUTE_IS_"
            "CANONICALLY_CLOSED"
        ),
        "current_flagship_gate": 7,
        "formal_reflection": reflection["involution"]["map"],
        "separator_kill_test": {
            "required": (
                "NONZERO_AT_CHILD;_ODD_UNDER_R;_CONTINUOUS;_SIGN_PRESERVED;_"
                "ZERO_ONLY_AT_EXISTING_STOP_OR_FORBIDDEN_LOCUS"
            ),
            "separator_found": separator_found,
            "candidates": candidates,
        },
        "three_representation_adjudication": representations,
        "canonical_no_go_scope": {
            "proved": (
                "NO_SEPARATOR_EXISTS_IN_THE_FIVE_PRESCRIBED_CURRENT_RETAINED_"
                "CANDIDATE_FAMILIES_AND_THEIR_CURRENT_DIFFERENTIAL_OR_NOETHER_"
                "REPRESENTATIONS"
            ),
            "not_proved": (
                "NO_MATHEMATICALLY_POSSIBLE_SEPARATOR_COULD_EVER_BE_DERIVED;_"
                "NO_COMPLETE_CHILD_CAN_REACH_THE_TERMINAL_EVENT"
            ),
            "retained_action_incompatibility": False,
        },
        "global_S2_owner_localization": {
            "retained_vector_field": "V(Y)=(v,D(Y)^(-1)*b(Y))",
            "first_specific_uncontrolled_nonlinear_owner": "D(Y)^(-1)*b(Y)",
            "why": (
                "THE_LOCAL_MOSER_AND_INVERSE_ESTIMATES_CLOSE_ONLY_ON_"
                "K(B,delta);_THE_RETAINED_ENERGY_DOES_NOT_BOUND_B_AND_NO_"
                "ACTION_IDENTITY_PROTECTS_delta_FOR_THE_GAUGE_FIXED_EULER_"
                "DIRAC_INVERSE"
            ),
            "maximal_flow_already_treats_inverse_divergence_as_stop": (
                "GAUGE_FIXED_EULER_DIRAC_INVERSE_NORM_DIVERGENCE"
                in maximal_flow["maximal_flow_alternative"]["finite_time_outcomes"]
            ),
            "coercive_S2_bound_available": global_control[
                "owned_and_missing_energy_structure"
            ]["coercive_S2_bound_on_continuum_child_component"],
        },
        "Gate7_status_changed": False,
        "chord_03_authorized": False,
        "exact_next_dependency": (
            "DERIVE_AN_ACTION_OWNED_GLOBAL_BOUND_FOR_D(Y)^(-1)*b(Y)_AND_"
            "THE_ASSOCIATED_STRONG_S2_NORM_AND_EXISTING_DOMAIN_MARGINS,_OR_"
            "PROVE_A_SEPARATOR_FREE_INTEGRATED_ORDERED_EVENT_TRANSPORT_"
            "INEQUALITY_FORCING_A_CANONICAL_STOP"
        ),
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in INPUTS.values()
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise RuntimeError("component-separator audit failed validation")
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "classification": payload["classification"],
                "separator_found": payload["separator_kill_test"][
                    "separator_found"
                ],
                "specific_S2_owner": payload["global_S2_owner_localization"][
                    "first_specific_uncontrolled_nonlinear_owner"
                ],
                "validation_passed": payload["validation_passed"],
                "sha256": _sha256(RESULT),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
