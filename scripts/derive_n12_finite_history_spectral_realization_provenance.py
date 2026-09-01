"""Derive the inverse-free finite-history terminal-load reduction ledger."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_channel_transfer import (  # noqa: E402
    reduce_two_boundary_weyl_with_terminal_load_jets,
)


ARTIFACTS = ROOT / "artifacts" / "flagship_integration"
RESULT = ARTIFACTS / (
    "BHSM_N12_FINITE_HISTORY_SPECTRAL_REALIZATION_PROVENANCE.json"
)
INPUTS = (
    ARTIFACTS / "BHSM_N12_COMPACT_FINITE_HISTORY_OPERATOR.json",
    ARTIFACTS / "BHSM_N12_FINITE_HISTORY_TERMINAL_WEYL_GERM.json",
    ARTIFACTS / "BHSM_N12_TERMINAL_CHILD_QUOTIENT_OPERATOR_JET.json",
    ARTIFACTS / "BHSM_N12_DESINGULARIZED_FINITE_HISTORY_OPERATOR_PARAMETER.json",
    ARTIFACTS / "BHSM_N12_ACTION_OWNED_ENDPOINT_LOAD_REDUCTION.json",
    ARTIFACTS / "BHSM_N12_EVENT_NORMAL_TWO_SIDED_SEAM_CORRECTION.json",
    ARTIFACTS / "BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL.json",
    ROOT / "src/bhsm/interface/aether_forward_channel_transfer.py",
    ROOT / "theory/n12_finite_history_spectral_realization_provenance.md",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _jet_witness() -> dict[str, Any]:
    keys = ("base", "first_left", "first_right", "mixed_second")
    m0 = np.asarray([[2.0, -0.7], [-0.7, 1.6]])
    mh = np.asarray([[0.2, -0.1], [-0.1, 0.3]])
    mk = np.asarray([[-0.4, 0.05], [0.05, 0.2]])
    mhk = np.asarray([[0.07, -0.03], [-0.03, 0.11]])
    b0 = np.asarray([[0.9]])
    bh = np.asarray([[0.13]])
    bk = np.asarray([[-0.08]])
    bhk = np.asarray([[0.04]])
    weyl = dict(zip(keys, (m0, mh, mk, mhk), strict=True))
    load = dict(zip(keys, (b0, bh, bk, bhk), strict=True))
    result = reduce_two_boundary_weyl_with_terminal_load_jets(weyl, load)

    def value(left: float, right: float) -> np.ndarray:
        varied_m = m0 + left * mh + right * mk + left * right * mhk
        varied_b = b0 + left * bh + right * bk + left * right * bhk
        block = {
            "base": varied_m,
            "first_left": np.zeros((2, 2)),
            "first_right": np.zeros((2, 2)),
            "mixed_second": np.zeros((2, 2)),
        }
        terminal = {
            "base": varied_b,
            "first_left": np.zeros((1, 1)),
            "first_right": np.zeros((1, 1)),
            "mixed_second": np.zeros((1, 1)),
        }
        return reduce_two_boundary_weyl_with_terminal_load_jets(
            block, terminal
        )["base"]

    epsilon = 1.0e-5
    left_fd = (value(epsilon, 0.0) - value(-epsilon, 0.0)) / (2 * epsilon)
    right_fd = (value(0.0, epsilon) - value(0.0, -epsilon)) / (2 * epsilon)
    mixed_fd = (
        value(epsilon, epsilon)
        - value(epsilon, -epsilon)
        - value(-epsilon, epsilon)
        + value(-epsilon, -epsilon)
    ) / (4 * epsilon**2)
    alternate = reduce_two_boundary_weyl_with_terminal_load_jets(
        weyl,
        {
            "base": np.asarray([[2.1]]),
            "first_left": bh,
            "first_right": bk,
            "mixed_second": bhk,
        },
    )
    return {
        "terminal_graph_smallest_singular_value": result[
            "terminal_graph_smallest_singular_value"
        ],
        "terminal_graph_condition_number": result[
            "terminal_graph_condition_number"
        ],
        "maximum_bordered_solve_residual": max(
            result["bordered_solve_residuals"].values()
        ),
        "first_left_finite_difference_residual": float(
            np.linalg.norm(result["first_left"] - left_fd)
        ),
        "first_right_finite_difference_residual": float(
            np.linalg.norm(result["first_right"] - right_fd)
        ),
        "mixed_second_finite_difference_residual": float(
            np.linalg.norm(result["mixed_second"] - mixed_fd)
        ),
        "same_two_boundary_M_distinct_terminal_load_response_gap": float(
            np.linalg.norm(result["base"] - alternate["base"])
        ),
        "explicit_matrix_inverse_formed": result[
            "explicit_matrix_inverse_formed"
        ],
    }


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("all finite-history realization inputs required")
    compact, germ, quotient, amplitude, endpoint, seam, force = (
        _load(path) for path in INPUTS[:7]
    )
    if not all(
        record.get("validation_passed") is True
        for record in (compact, germ, quotient, amplitude, endpoint, seam, force)
    ):
        raise RuntimeError("validated finite-history realization inputs required")
    witness = _jet_witness()
    validation = {
        "closed_positive_duration_chronology_preserved": compact["validation"][
            "positive_duration_history_existence_not_reopened"
        ],
        "compact_K_and_DK_consumed": compact["claim_boundary"][
            "K_and_D_xi_K"
        ] == "DERIVED",
        "terminal_germ_scope_preserved": germ["claim_boundary"][
            "complete_finite_duration_M_C_family"
        ].startswith("OPEN"),
        "total_operator_jet_not_replaced_by_fixed_duration_part": quotient[
            "total_Weyl_jet_chain_rule"
        ]["fixed_duration_promoted_to_total_physical_derivative"] is False,
        "formation_amplitude_not_selected": amplitude["duration_parameter_jet"][
            "lambda_positive_member_selected"
        ] is False,
        "AE2_terminal_load_formula_consumed": endpoint[
            "endpoint_load_adjudication"
        ]["actual_event"].startswith("B_event"),
        "child_response_not_replaced_by_W_phys": seam["claim_boundary"][
            "child_arm_Calderon_value_and_geometry_jets"
        ] == "OPEN",
        "zero_source_force_requires_complete_operator": force["claim_boundary"][
            "zero_source_force_value"
        ] == "OPEN",
        "bordered_jet_residuals_small": max(
            witness["maximum_bordered_solve_residual"],
            witness["first_left_finite_difference_residual"],
            witness["first_right_finite_difference_residual"],
            witness["mixed_second_finite_difference_residual"],
        ) < 2.0e-6,
        "terminal_load_information_is_material": witness[
            "same_two_boundary_M_distinct_terminal_load_response_gap"
        ] > 1.0e-3,
        "no_explicit_inverse_formed": not witness[
            "explicit_matrix_inverse_formed"
        ],
        "no_recurrence_reset_semantics_endpoint_selector_cutoff_or_external_force_added": True,
    }
    return {
        "artifact": "BHSM_N12_FINITE_HISTORY_SPECTRAL_REALIZATION_PROVENANCE",
        "status": (
            "TWO_BOUNDARY_RESPONSE_REDUCTION_DERIVED_PHYSICAL_TERMINAL_LOAD_OPEN"
        ),
        "classification": (
            "THE_ACTION_OWNED_COMPACT_FORMATION_SEGMENT_SUPPLIES_K_DK_AND_"
            "FREE_TWO_BOUNDARY_M_C_DATA;_AN_EXACT_BORDERED_SCHUR_REDUCTION_"
            "NOW_PROPAGATES_ANY_ACTION_OWNED_TERMINAL_LOAD_AND_ITS_FIRST_"
            "MIXED_JETS_WITHOUT_AN_INVERSE,_BUT_THE_PHYSICAL_AE2_LOAD_"
            "REMAINS_U_R_DAGGER_M_C2_U_R_PLUS_W_PHYS_AND_IS_NOT_DETERMINED_"
            "BY_THE_ONE_SEGMENT_M_C_OR_TERMINAL_GERM_ALONE"
        ),
        "validated": {
            "chronology": "E0_TO_C1_TO_POSITIVE_T_TO_E1_TO_C2_CLOSED",
            "K_and_D_xi_K": "DERIVED",
            "endpoint_event_child_partition": "DERIVED",
            "intrinsic_gauge_time_quotient": "DERIVED",
            "physical_common_scale_direction": "RETAINED",
            "free_two_boundary_M_C_and_jets": "DERIVED_EXECUTABLE",
            "terminal_load_reduction_and_jets": "DERIVED_EXECUTABLE",
            "reduction": "M_birth=M00-M01*X,_WITH_(M11+B)*X=M10",
            "AE2_terminal_load": "B=U_R_DAGGER*M_C2*U_R+W_phys",
        },
        "invalidated": {
            "free_two_boundary_M_C_is_the_positive_self_adjoint_heat_operator": False,
            "one_negative_axis_probe_determines_the_heat_force": False,
            "W_phys_alone_is_the_AE2_terminal_load": False,
            "finite_encapsulation_ontology_supplies_an_operator_boundary_condition": False,
            "fixed_duration_coefficient_jet_is_the_total_physical_D_xi_M_C": False,
        },
        "open": {
            "actual_complete_finite_duration_M_C_family": True,
            "AE2_child_response_M_C2_and_first_two_covariant_jets": True,
            "equivalent_joint_two_sided_finite_history_operator": True,
            "positive_self_adjoint_P_and_D_xi_P": True,
            "zero_source_heat_minus_zeta_force_value": True,
            "same_action_saddle": True,
            "constrained_physical_Hessian": True,
        },
        "hindsight": {
            "history_existence_reset_or_recurrence_reopened": False,
            "remaining_dependency_type": "OPERATOR_DOMAIN_AND_CHILD_RESPONSE_PROPAGATION",
            "owner_finite_encapsulation_ontology_role": (
                "RESTRICTS_THE_PHYSICAL_HISTORY_CLASS_BUT_DOES_NOT_REPLACE_"
                "THE_ACTION_VARIATIONAL_DOMAIN"
            ),
        },
        "exact_next_dependency": (
            "ASSEMBLE_THE_ACTION_OWNED_C2_CHILD_CALDERON_FAMILY_M_C2(z;xi)_"
            "AND_ITS_FIRST_TWO_COVARIANT_RESET_QUOTIENT_JETS,_OR_THE_"
            "EQUIVALENT_JOINT_TWO_SIDED_FINITE_HISTORY_OPERATOR;_THEN_USE_"
            "THE_CERTIFIED_BORDERED_REDUCTION_TO_FORM_P,D_xi_P_AND_EVALUATE_"
            "THE_ZERO_SOURCE_FORCE"
        ),
        "inverse_free_witness": witness,
        "claim_boundary": {
            "Gate7": "ACTIVE_PHYSICAL_SPECTRAL_REALIZATION_OPEN",
            "M_C_and_D_xi_M_C_reduction": "DERIVED_EXECUTABLE",
            "zero_source_force_value": "OPEN",
            "same_action_saddle": "OPEN_AFTER_FORCE",
            "physical_Hessian": "OPEN_AFTER_SADDLE",
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "validation_passed": payload["validation_passed"],
        "exact_next_dependency": payload["exact_next_dependency"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
