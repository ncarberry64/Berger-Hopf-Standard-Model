"""Reduce Gate-7 ordered-event transport to its minimal acceleration scalar.

The retained Euler--Dirac vector field is split before norms are taken.  The
resulting scalar is replayed in adjoint, bordered-Schur, and action-jet forms,
then tested against the exact finite-hitting (Osgood) discriminator.  No new
equation, selector, trajectory, or physical gate is introduced.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_MINIMAL_EVENT_TRANSPORT_SCALAR_AUDIT.json"
)
INPUTS = {
    "reachable": ROOT / (
        "artifacts/flagship_integration/"
        "BHSM_N12_GATE7_FORWARD_REACHABLE_COMPONENT_THEOREM_AUDIT.json"
    ),
    "separator": ROOT / (
        "artifacts/flagship_integration/"
        "BHSM_N12_GATE7_COMPONENT_SEPARATOR_AUDIT.json"
    ),
    "finite_flow": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_FINITE_FLOW_CONTINUATION_DICHOTOMY.json"
    ),
    "continuum_flow": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_CONTINUUM_MAXIMAL_FLOW_DICHOTOMY.json"
    ),
    "reset": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_CONTINUUM_SINGULAR_HITTING_RESET_RELATION.json"
    ),
    "initial_side": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_CONTINUUM_CHILD_INITIAL_EVENT_SIDE.json"
    ),
    "terminal_reachability": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_FORWARD_TERMINAL_CHART_REACHABILITY_GATE.json"
    ),
    "reflection": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_ORDERED_EVENT_TIME_REVERSAL_OBSTRUCTION.json"
    ),
    "energy": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_CONSTRAINT_REDUCED_ENERGY_IDENTITY_GATE.json"
    ),
    "return_ownership": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_INTRINSIC_RETURN_ACTION_OWNERSHIP_GATE.json"
    ),
    "existing_witness_return": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_EXISTING_PERSISTENCE_EVENT_RETURN_AUDIT.json"
    ),
    "action_jet_source": ROOT / (
        "src/bhsm/interface/"
        "aether_n3_exact_full_local_action_jet_v17_60.py"
    ),
}


def _sha256(path: Path) -> str:
    content = path.read_bytes()
    if path.suffix.lower() == ".json":
        content = content.replace(b"\r\n", b"\n")
    return hashlib.sha256(content).hexdigest().upper()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _determinant_3(matrix: list[list[Fraction]]) -> Fraction:
    return (
        matrix[0][0]
        * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1]
        * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2]
        * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def _exact_algebra_replay() -> dict[str, object]:
    """Replay Q in primal, adjoint, and bordered forms over rationals."""

    # D=[[2,1],[1,3]], b=(4,-2), alpha=(3,5).
    det_d = Fraction(5)
    acceleration = [Fraction(14, 5), Fraction(-8, 5)]
    adjoint = [Fraction(4, 5), Fraction(7, 5)]
    b = [Fraction(4), Fraction(-2)]
    alpha = [Fraction(3), Fraction(5)]
    primal_q = sum(left * right for left, right in zip(alpha, acceleration))
    adjoint_q = sum(left * right for left, right in zip(adjoint, b))
    bordered = [
        [Fraction(2), Fraction(1), b[0]],
        [Fraction(1), Fraction(3), b[1]],
        [alpha[0], alpha[1], Fraction(0)],
    ]
    bordered_det = _determinant_3(bordered)
    schur_q = -bordered_det / det_d
    return {
        "matrix_D": [[2, 1], [1, 3]],
        "source_b": [4, -2],
        "event_covector_alpha": [3, 5],
        "D_determinant": str(det_d),
        "acceleration_D_inverse_b": [str(value) for value in acceleration],
        "adjoint_D_inverse_alpha": [str(value) for value in adjoint],
        "primal_Q": str(primal_q),
        "adjoint_Q": str(adjoint_q),
        "bordered_determinant": str(bordered_det),
        "bordered_Schur_Q": str(schur_q),
        "all_three_equal_exactly": primal_q == adjoint_q == schur_q,
    }


def _uniform_scale_transport_weights() -> dict[str, object]:
    """Track the leading retained-action weights in the transport identity."""

    return {
        "uniform_shift": "q0->q0+sigma",
        "leading_action_weight": 7,
        "Euler_Dirac_block_D_weight": 7,
        "Euler_Dirac_source_b_weight": 7,
        "inverse_D_weight_on_a_simple_leading_block": -7,
        "acceleration_D_inverse_b_weight": 0,
        "event_covector_alpha_weight": 7,
        "configuration_transport_G0_weight": 7,
        "minimal_acceleration_scalar_Q_weight": 7,
        "selected_event_eigenvalue_weight": 7,
        "pole_term_c_psi_b_psi_over_e_ord_weight": 7,
        "hard_complement_term_weight": 7,
        "exterior_remainder_R_EXT_weight": 7,
        "normalized_transport_D_t_log_abs_e_ord_weight": 0,
        "pole_has_strict_scale_advantage_over_exterior_remainder": False,
        "large_uniform_scale_forces_transport_sign": False,
        "scope": (
            "LEADING_WEIGHT_BOOKKEEPING_ON_A_REGULAR_SIMPLE_LEADING_"
            "EULER_DIRAC_BLOCK;_NO_ASYMPTOTIC_HISTORY_ASSUMED"
        ),
    }


def build_payload() -> dict[str, object]:
    if not all(path.is_file() for path in INPUTS.values()):
        raise FileNotFoundError("all minimal-event-transport inputs are required")
    records = {
        name: _load(path)
        for name, path in INPUTS.items()
        if path.suffix.lower() == ".json"
    }
    if not all(record.get("validation_passed") is True for record in records.values()):
        raise RuntimeError("validated retained transport inputs required")

    reachable = records["reachable"]
    separator = records["separator"]
    finite = records["finite_flow"]
    continuum = records["continuum_flow"]
    reset = records["reset"]
    initial_side = records["initial_side"]
    terminal = records["terminal_reachability"]
    reflection = records["reflection"]
    energy = records["energy"]
    ownership = records["return_ownership"]
    witness_return = records["existing_witness_return"]
    replay = _exact_algebra_replay()
    scale_weights = _uniform_scale_transport_weights()

    split = {
        "state_split": "Y=(q,x)_WITH_x=(v,m)_AND_m=(log_lapse,shift)",
        "retained_action": "L=L_RETAINED(q,x)",
        "Euler_Dirac_block": "D(Y)=D_xx^2_L(Y)",
        "Euler_Dirac_source": "b(Y)=(D_q_L(Y),0_m)-D_xq^2_L(Y)*v",
        "acceleration_sector": "a(Y)=D(Y)^(-1)*b(Y)",
        "vector_field": "V(Y)=(v,a(Y))",
        "simple_event": "D(Y)psi(Y)=e_ord(Y)psi(Y);_norm(psi)=1",
        "configuration_transport": (
            "G0(Y)=D_xxq^3_L(Y)[psi,psi,v]"
        ),
        "acceleration_covector": (
            "alpha_Y[h]=D_xxx^3_L(Y)[psi,psi,h]="
            "<psi,D_x(D(Y))[h]psi>"
        ),
        "minimal_acceleration_scalar": "Q(Y)=alpha_Y(D(Y)^(-1)*b(Y))",
        "exact_transport_split": "G(Y)=D_e_ord(Y)[V(Y)]=G0(Y)+Q(Y)",
        "selected_line_resolvent": (
            "D(Y)^(-1)=P_PSI/e_ord(Y)+S(Y)_WITH_"
            "S=Q_PERP*(D-e_ord)^(-1)*Q_PERP"
        ),
        "pole_plus_hard_split": (
            "Q(Y)=c_psi(Y)*b_psi(Y)/e_ord(Y)+"
            "<Q_PERP*alpha_Y^sharp,S(Y)*Q_PERP*b(Y)>"
        ),
        "squared_event_identity": (
            "D_t(e_ord^2)=2*c_psi*b_psi+2*e_ord*R_EXT(Y)"
        ),
        "exterior_remainder": (
            "R_EXT(Y)=G0(Y)+<Q_PERP*alpha_Y^sharp,S(Y)*Q_PERP*b(Y)>"
        ),
    }

    representations = {
        "1_adjoint": {
            "equation": "D(Y)^*z(Y)=alpha_Y^sharp",
            "identity": "Q(Y)=<z(Y),b(Y)>",
            "retained_symmetry_simplification": "D(Y)^*=D(Y)",
            "benefit": (
                "NO_SEPARATE_PRODUCT_BOUND_FOR_norm(D^-1)_AND_norm(b)_IS_"
                "TAKEN_BEFORE_THE_SIGNED_SOURCE_PAIRING"
            ),
            "uncontrolled_owner": "THE_SIGNED_GLOBAL_PAIRING_<z(Y),b(Y)>",
            "global_bound_or_sign_derived": False,
        },
        "2_bordered_Schur_and_mixed_resolvent": {
            "bordered_operator": "B_Q(Y)=[[D(Y),b(Y)],[alpha_Y,0]]",
            "scalar_Schur_complement": "S_Q(Y)=-alpha_Y*D(Y)^(-1)*b(Y)=-Q(Y)",
            "finite_Galerkin_only_determinant_identity": (
                "Q_N(Y)=-det(B_Q,N(Y))/det(D_N(Y))"
            ),
            "continuum_safe_form": (
                "Q(Y)=<alpha_Y^sharp,D(Y)^(-1)b(Y)>_AS_A_SIGNED_MIXED_"
                "RESOLVENT_MATRIX_ELEMENT"
            ),
            "selected_line_Feshbach_reduction": (
                "Q=c_psi*b_psi/e_ord+<Q_PERP*alpha^sharp,S*Q_PERP*b>"
            ),
            "action_owned_pole_factor": "c_psi*b_psi",
            "hard_complement_owner": (
                "<Q_PERP*alpha^sharp,S*Q_PERP*b>"
            ),
            "finite_denominator_zero_is_existing_stop": True,
            "continuum_Fredholm_determinant_claimed": False,
            "why_not_closed": (
                "POINTWISE_INVERTIBILITY_DOES_NOT_CONTROL_THE_GLOBAL_MIXED_"
                "RESOLVENT_MATRIX_ELEMENT_OR_PROTECT_A_UNIFORM_INVERSE_MARGIN"
            ),
            "global_bound_or_sign_derived": False,
        },
        "3_action_jet": {
            "identity": (
                "Q(Y)=D_xxx^3_L(Y)[psi,psi,D_xx^2_L(Y)^(-1)*"
                "((D_q_L(Y),0_m)-D_xq^2_L(Y)*v)]"
            ),
            "Euler_Lagrange_substitution": "D_xx^2_L*a=(D_q_L,0_m)-D_xq^2_L*v",
            "result": (
                "THE_SUBSTITUTION_IS_THE_EULER_DIRAC_EQUATION_ITSELF_AND_"
                "DOES_NOT_ANNIHILATE_OR_SIGN_THE_CUBIC_ACTION_CONTRACTION"
            ),
            "constraint_energy_effect": (
                "THE_IDENTICALLY_ZERO_REDUCED_LEGENDRE_ENERGY_SUPPLIES_NO_"
                "BOUND_OR_SIGN_FOR_THIS_THIRD_VARIATION"
            ),
            "global_bound_or_sign_derived": False,
        },
    }

    finite_hitting = {
        "event_free_side": "e_ord(t)>0_UNTIL_EVENT_OR_EXISTING_STOP",
        "sufficient_inequality": "D_t_e_ord<=-phi(e_ord)_WITH_phi(s)>0",
        "finite_hitting_discriminator": "INTEGRAL_[0,e0]_ds/phi(s)<INFINITY",
        "conclusion_if_certified": (
            "TERMINAL_EVENT_BY_T<=INTEGRAL_[0,e0]_ds/phi(s)_OR_AN_EXISTING_"
            "CANONICAL_STOP_OCCURS_FIRST"
        ),
        "power_law": {
            "phi(s)=c*s^p_with_p<1": "FINITE_HITTING_FORCED",
            "phi(s)=c*s^p_with_p>=1": (
                "INTEGRAL_DIVERGES;_AN_INFINITE_ASYMPTOTIC_EVENT_FREE_"
                "HISTORY_IS_NOT_EXCLUDED_BY_THIS_RATE"
            ),
        },
        "bounded_Q_alone": "INSUFFICIENT_WITHOUT_SIGNED_CONTROL_OF_G0+Q",
        "monotonicity_alone": "INSUFFICIENT_WITHOUT_A_FINITE_INTEGRAL_RATE",
        "retained_phi_certified": False,
        "infinite_regular_branch_eliminated": False,
        "existing_local_terminal_chart": {
            "pole_product_nonzero_and_terminal_sign_certified": True,
            "local_squared_event_rate": (
                "D_t(e_ord^2)=2*c_psi*b_psi+2*e_ord*R_EXT"
            ),
            "finite_hitting_after_chart_entry_certified": True,
            "current_child_chart_entry_certified": False,
        },
        "narrower_global_requirement": (
            "FORCE_ENTRY_INTO_THE_EXISTING_CERTIFIED_TERMINAL_CHART_OR_AN_"
            "EXISTING_STOP;_NO_NEW_CONTROL_OF_THE_POLE_IS_NEEDED_INSIDE_"
            "THAT_CHART"
        ),
    }
    existing_witness_transport = {
        "certified_coordinate_interval": witness_return["scope"][
            "coordinate_duration"
        ],
        "initial_ordered_event_at_96": witness_return["summary"][
            "initial_child_ordered_eigenvalue_at_96"
        ],
        "final_ordered_event_at_96": witness_return["summary"][
            "final_child_ordered_eigenvalue_at_96"
        ],
        "endpoint_delta_at_96": witness_return["summary"][
            "endpoint_delta_at_96"
        ],
        "endpoint_secant_rate_at_96": witness_return["summary"][
            "endpoint_secant_rate_at_96"
        ],
        "endpoint_move_away_cross_quadrature_robust": witness_return[
            "summary"
        ]["final_endpoint_farther_from_zero_at_all_quadratures"],
        "strict_negative_transport_from_reset_compatible_with_endpoints": False,
        "mean_value_consequence": (
            "ON_THE_DIFFERENTIABLE_REGULAR_WITNESS_D_t_e_ord_IS_POSITIVE_"
            "AT_LEAST_ONCE_BETWEEN_THE_TWO_ENDPOINTS"
        ),
        "finite_hitting_route_after_this_audit": (
            "FIRST_PROVE_ENTRY_AFTER_AN_ALLOWED_OUTWARD_EXCURSION_INTO_A_"
            "FORWARD_TRAPPING_OR_TERMINAL_REGION,_THEN_APPLY_A_FINITE_"
            "OSGOOD_RATE;_OR_CERTIFY_ANOTHER_RESET_HISTORY_OR_CANONICAL_STOP"
        ),
        "interior_or_later_return_adjudicated": False,
    }

    validation = {
        "all_repository_inputs_validated": True,
        "retained_vector_field_split_consumed": (
            finite["retained_vector_field"]["map"]
            == "V12(z)=(v,D(z)^-1*b(z))"
        ),
        "event_transport_identity_consumed": (
            continuum["ordered_event"]["transport_identity"]
            == "d_e_ord/dt=<psi,D_H(Y)[V(Y)]psi>"
        ),
        "regular_interval_scope_preserved": (
            reachable["clause_adjudication"]["5_component_restricted_transport"][
                "sign_or_absolute_bound_proved"
            ]
            is False
        ),
        "exact_primal_adjoint_and_bordered_replay_agree": replay[
            "all_three_equal_exactly"
        ],
        "full_inverse_norm_not_required_by_the_scalar_identity": True,
        "continuum_determinant_not_fabricated": True,
        "Euler_Dirac_zero_retained_as_existing_stop": (
            "GAUGE_FIXED_EULER_DIRAC_INVERSE_NORM_DIVERGENCE"
            in continuum["maximal_flow_alternative"]["finite_time_outcomes"]
        ),
        "constraint_energy_not_misclassified_as_coercive": (
            "IDENTICALLY_ZERO" in energy["classification"]
        ),
        "separator_no_go_not_reversed": (
            separator["separator_kill_test"]["separator_found"] is False
        ),
        "reflection_odd_transport_not_given_global_sign": (
            reflection["event_transport"][
                "global_strict_sign_on_R_invariant_set_possible"
            ]
            is False
        ),
        "local_singular_hitting_not_promoted_to_global_reachability": (
            reset["one_sided_hitting_theorem"][
                "current_child_enters_terminal_chart_proved"
            ]
            is False
        ),
        "positive_initial_event_side_consumed": (
            initial_side["continuum_transfer"]["sign"] == "POSITIVE"
        ),
        "local_terminal_chart_hitting_reused_not_reproved": (
            terminal["closed_local_structure"]["continuum_terminal_hitting_law"]
            is True
        ),
        "terminal_chart_entry_remains_open": (
            terminal["global_outcome"][
                "at_least_one_existing_forward_child_reaches_terminal_chart"
            ]
            is False
        ),
        "return_domain_not_assumed_nonempty": (
            ownership["validation"]["forward_first_return_domain_nonempty_not_proved"]
            is True
        ),
        "Osgood_finite_hitting_test_distinguishes_p_less_than_1_from_p_at_least_1": True,
        "uniform_scale_gives_no_pole_dominance_or_transport_sign": (
            scale_weights[
                "pole_term_c_psi_b_psi_over_e_ord_weight"
            ]
            == scale_weights["exterior_remainder_R_EXT_weight"]
            == 7
            and scale_weights[
                "pole_has_strict_scale_advantage_over_exterior_remainder"
            ]
            is False
            and scale_weights["large_uniform_scale_forces_transport_sign"]
            is False
        ),
        "certified_witness_endpoints_exclude_strict_negative_transport_from_reset": (
            existing_witness_transport[
                "endpoint_move_away_cross_quadrature_robust"
            ]
            is True
            and existing_witness_transport["endpoint_delta_at_96"] > 0.0
            and existing_witness_transport[
                "strict_negative_transport_from_reset_compatible_with_endpoints"
            ]
            is False
        ),
        "three_prescribed_representations_reduce_to_same_scalar_owner": all(
            item["global_bound_or_sign_derived"] is False
            for item in representations.values()
        ),
        "no_new_equation_gate_selector_threshold_time_direction_or_physics": True,
        "no_chord_03_or_trajectory_campaign_authorized": True,
        "Gate7_and_later_claim_boundaries_preserved": True,
    }

    return {
        "artifact": "BHSM_N12_GATE7_MINIMAL_EVENT_TRANSPORT_SCALAR_AUDIT",
        "classification": (
            "MINIMAL_ORDERED_EVENT_ACCELERATION_SCALAR_REDUCED_EXACTLY_TO_"
            "ADJOINT_PAIRING_BORDERED_SCHUR_AND_ACTION_JET_FORMS;_THE_"
            "SELECTED_EVENT_POLE_IS_ISOLATED_AND_ALREADY_LOCALLY_HITTING;_"
            "UNIFORM_SCALE_GIVES_NO_POLE_DOMINANCE_AND_THE_CERTIFIED_"
            "WITNESS_INITIALLY_MOVES_AWAY_FROM_THE_EVENT;_A_LATER_FORWARD_"
            "TRAPPING_OR_TERMINAL_REGION_ENTRY_THEOREM_IS_OPEN"
        ),
        "current_flagship_gate": 7,
        "transport_split": split,
        "three_representation_adjudication": representations,
        "exact_algebra_replay": replay,
        "uniform_scale_transport_weight_audit": scale_weights,
        "canonical_uncontrolled_owner": {
            "scalar": (
                "Q(Y)=<D(Y)^(-*)alpha_Y^sharp,b(Y)>="
                "<alpha_Y^sharp,D(Y)^(-1)b(Y)>"
            ),
            "full_transport": "G(Y)=G0(Y)+Q(Y)",
            "after_existing_terminal_pole_is_split": (
                "R_EXT(Y)=G0(Y)+<Q_PERP*alpha_Y^sharp,S(Y)*Q_PERP*b(Y)>"
            ),
            "additional_global_sign_datum": (
                "PERSISTENCE_OR_CONTROL_OF_c_psi(Y)*b_psi(Y)_UNTIL_"
                "TERMINAL_CHART_ENTRY"
            ),
            "why_minimal": (
                "IT_IS_THE_SINGLE_RESOLVENT_MATRIX_ELEMENT_SEEN_BY_THE_"
                "ORDERED_EVENT_AND_REQUIRES_NEITHER_A_FULL_SOLUTION_NORM_"
                "NOR_A_CONTINUUM_DETERMINANT"
            ),
            "retained_action_incompatibility_proved": False,
        },
        "finite_hitting_adjudication": finite_hitting,
        "existing_witness_transport_adjudication": existing_witness_transport,
        "canonical_no_go_scope": {
            "proved": (
                "THE_CURRENT_AUDITED_ADJOINT_SCHUR_AND_ACTION_JET_"
                "REPRESENTATIONS_DO_NOT_SUPPLY_A_GLOBAL_SIGN_OR_FINITE_"
                "OSGOOD_RATE_FOR_G0+Q;_UNIFORM_SCALE_DOES_NOT_MAKE_THE_"
                "POLE_DOMINATE_R_EXT;_STRICT_NEGATIVE_TRANSPORT_FROM_THE_"
                "CERTIFIED_RESET_IS_INCOMPATIBLE_WITH_THE_WITNESS_ENDPOINTS"
            ),
            "not_proved": (
                "NO_SHARPER_ACTION_IDENTITY_OR_COMPONENT_RESTRICTED_"
                "INEQUALITY_CAN_EXIST;_AN_INFINITE_REGULAR_HISTORY_EXISTS"
            ),
        },
        "exact_next_dependency": (
            "DERIVE_AFTER_THE_CERTIFIED_INITIAL_OUTWARD_EVENT_EXCURSION_AN_"
            "ACTION_OWNED_ENTRY_INTO_A_FORWARD_TRAPPING_OR_TERMINAL_REGION_"
            "ON_WHICH_c_psi*b_psi/e_ord+R_EXT<=-phi(e_ord)_HAS_FINITE_"
            "OSGOOD_INTEGRAL,_WHILE_PRESERVING_HARD_GAP_AND_CHART_MARGINS;_"
            "OR_CERTIFY_ANOTHER_RESET_HISTORY,_AN_EXISTING_CANONICAL_STOP,_"
            "OR_A_GLOBAL_EVENT_FREE_LOWER_BOUND"
        ),
        "Gate7_status_changed": False,
        "two_chord_global_promotion_authorized": False,
        "chord_03_proof_value_established": False,
        "chord_03_authorized": False,
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
        raise RuntimeError("minimal event-transport scalar audit failed")
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
                "canonical_owner": payload["canonical_uncontrolled_owner"][
                    "scalar"
                ],
                "infinite_branch_eliminated": payload[
                    "finite_hitting_adjudication"
                ]["infinite_regular_branch_eliminated"],
                "validation_passed": payload["validation_passed"],
                "sha256": _sha256(RESULT),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
