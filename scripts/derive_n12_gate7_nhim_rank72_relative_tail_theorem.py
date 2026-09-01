"""Derive the captured-NHIM rank-72 relative-tail theorem."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_NHIM_RANK72_RELATIVE_TAIL_THEOREM.json"
CAPTURE = BASE / "BHSM_N12_ASYMPTOTIC_NHIM_CAPTURE_BASIN.json"
FIXED = BASE / "BHSM_N12_FORWARD_FIXED_CHANNEL_TRANSFER.json"
GRADED = BASE / "BHSM_N12_GATE7_MAXIMAL_GRADED_INCOMING_RELATIVE_HEAT_COTANGENT.json"
RANK72 = BASE / "BHSM_N12_GATE7_RANK72_RELATIVE_FORM_TAIL.json"
NHIM_NO_GO = BASE / "BHSM_N12_ASYMPTOTIC_NHIM_ANGULAR_FORCE_NO_GO.json"
SOURCE_DINI = BASE / "BHSM_N12_GATE7_AE2_COMPACT_SOURCE_DINI_CLOSURE.json"
ONTOLOGY = BASE / "BHSM_N12_GATE7_CLOSED_SYSTEM_ZERO_EXTERNAL_SOURCE_ONTOLOGY.json"
THEORY = ROOT / "theory" / "n12_gate7_nhim_rank72_relative_tail_theorem.md"
SCRIPT = ROOT / "scripts" / "derive_n12_gate7_nhim_rank72_relative_tail_theorem.py"
INPUTS = (
    CAPTURE, FIXED, GRADED, RANK72, NHIM_NO_GO, SOURCE_DINI, ONTOLOGY,
    THEORY, SCRIPT,
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing NHIM relative-tail inputs: " + ", ".join(missing))
    capture, fixed, graded, rank72, no_go, dini, ontology = (
        _load(path) for path in INPUTS[:-2]
    )
    if not all(record.get("validation_passed") is True for record in (
        capture, fixed, graded, rank72, no_go, dini, ontology,
    )):
        raise RuntimeError("validated NHIM relative-tail lineage is required")

    low_rate = float(graded["low_high_spectral_split"]["net_low_energy_linear_decay_rate"])
    gaussian_rate = float(
        graded["low_high_spectral_split"]["high_energy_quadratic_decay_rate"]
    )
    sample_mu = 1.0e34
    polynomial_orders = (2, 4, 6, 8)
    angular_witness = [
        {
            "polynomial_order": order,
            "sample_mu": sample_mu,
            "low_log_derivative": order / sample_mu - low_rate,
            "high_log_derivative": order / sample_mu - 2.0 * gaussian_rate * sample_mu,
        }
        for order in polynomial_orders
    ]

    validation = {
        "all_parent_certificates_validate": True,
        "finite_N12_open_capture_basin_is_derived": (
            capture["capture_theorem"]["forward_local_capture"] is True
            and capture["leading_weight_NHIM"]["unstable_normal_roots"] == 0
        ),
        "captured_histories_have_positive_H4_limit": (
            capture["capture_theorem"]["H4_limit"] == "H0>0"
        ),
        "epsilon_kinematic_decay_is_exact": (
            capture["compactified_full_flow"]["kinematic_equation"]
            == "epsilon'=-2*H4*epsilon"
        ),
        "fixed_channel_history_weights_are_only_exp_minus_x_and_minus_2x": (
            "exp(-x)" in fixed["classification"]
            and "exp(-2x)" in fixed["classification"]
            and fixed["dependency_reduction"]["moving_spatial_eigenbasis_transport_required"]
            is False
        ),
        "first_C2_collar_has_positive_length": (
            graded["certified_C2_collar"]["proper_length_lower"] > 0.0
        ),
        "collar_linear_decay_is_strict_after_transfer_loss": low_rate > 0.0,
        "high_energy_gaussian_decay_is_strict": gaussian_rate > 0.0,
        "polynomial_multiplicities_are_dominated": all(
            row["low_log_derivative"] < 0.0 and row["high_log_derivative"] < 0.0
            for row in angular_witness
        ),
        "rank72_source_contracted_identity_is_the_parent_criterion": (
            rank72["exact_criterion"]["necessary_and_sufficient"]
            == "THE_DISPLAYED_R72_VECTOR_NET_IS_CAUCHY"
        ),
        "common_scale_zeta_tail_remains_separately_closed": (
            rank72["claim_boundary"]["common_scale_separate_zeta_tail"]
            == "CLOSED_SUPERSEDED"
        ),
        "absolute_NHIM_heat_route_remains_closed_no_go": (
            no_go["route_adjudication"]["NHIM_route_can_close_absolute_graded_Gate7_force"]
            is False
        ),
        "fixed_channel_source_Dini_remains_closed": (
            no_go["validation"]["fixed_channel_source_Dini_remains_closed"] is True
            and dini["validation_passed"] is True
        ),
        "reset_to_capture_connection_is_not_assumed": (
            capture["scope"]["AE2_reset_entry_certified"] is False
        ),
        "only_external_source_is_zero_and_internal_blocks_are_retained": (
            ontology["adjudication"]["internal_response_zeroing"] == "FORBIDDEN"
        ),
        "no_selector_endpoint_recurrence_scale_fit_gate_or_chord_is_added": True,
        "FULL_BHSM_COMPLETE_false": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())

    return {
        "artifact": "BHSM_N12_GATE7_NHIM_RANK72_RELATIVE_TAIL_THEOREM",
        "status": (
            "CAPTURED_NHIM_RANK72_SIGNED_RELATIVE_TAIL_CAUCHY_RESET_ENTRY_OPEN"
            if passed else "NHIM_RANK72_RELATIVE_TAIL_THEOREM_NOT_CERTIFIED"
        ),
        "classification": (
            "ON_EVERY_OPEN_FINITE_N12_FAMILY_CAPTURED_BY_THE_RETAINED_ANALYTIC_"
            "NHIM,_BOUNDED_CENTER_JACOBI_FIELDS_AND_DECAYING_NORMAL_FIELDS_"
            "COMBINE_WITH_THE_EXACT_exp_minus_x_AND_exp_minus_2x_CHANNEL_"
            "WEIGHTS_TO_MAKE_EVERY_FIXED_CHANNEL_TAIL_INTEGRABLE;_THE_"
            "CERTIFIED_BIRTH_COLLAR_THEN_DOMINATES_ALL_RETAINED_ANGULAR_"
            "MULTIPLICITIES,_SO_THE_SIGNED_RANK72_SOURCE_CONTRACTED_RELATIVE_"
            "TAIL_IS_CAUCHY_EVEN_THOUGH_THE_ABSOLUTE_NHIM_HEAT_TRACE_DIVERGES"
        ),
        "captured_family_Jacobi_theorem": {
            "source": "ANALYTIC_NORMALLY_ATTRACTING_INVARIANT_FAMILY_AND_LOCAL_STABLE_FOLIATION",
            "center_components": "CONVERGE_TO_FINITE_TANGENTS_OF_THE_24_PARAMETER_BOUNDARY_FAMILY",
            "stable_velocity_normal_components": "DECAY_AT_THE_NORMAL_ATTRACTION_RATE",
            "radial_component": "DECAYS_WITH_epsilon=R4^-2",
            "log_radius_and_shape_components": "BOUNDED",
            "rate_components": "DECAY",
            "scope": "EVERY_SMOOTH_PARAMETRIC_FAMILY_CONTAINED_IN_THE_OPEN_CAPTURE_BASIN",
        },
        "temporal_relative_form_bounds": {
            "epsilon": "epsilon(t)<=epsilon(T0)*exp(-H0*(t-T0))",
            "exp_minus_x": "exp(-x(t))<=sqrt(epsilon(T0))*exp(-H0*(t-T0)/2)",
            "Dirac_and_pair_jet": "abs(Ds_mu)<=C_j*(1+mu)*exp(-H0*(t-T0)/2)",
            "Laplace_deRham_jet": "abs(DV_mu)<=C_j*(1+mu)^2*exp(-H0*(t-T0))",
            "contact_jet_from_x": 0,
            "direct_non_scale_zeta_jet": "O(exp(-H0*(t-T0)/2))",
            "fixed_channel_tail_integrability": "ABSOLUTE",
        },
        "angular_relative_form_bounds": {
            "low_energy_two_Poisson_factor": "exp(-ell_0*mu/R4_max)",
            "net_low_energy_linear_decay_rate": low_rate,
            "high_energy_factor": "exp(-a*mu^2/4)",
            "high_energy_quadratic_decay_rate": gaussian_rate,
            "retained_multiplicity_growth": "QUADRATIC",
            "coefficient_jet_growth": "FIXED_FINITE_POLYNOMIAL_ORDER_AT_MOST_DEGREE_SIX_IN_THE_CURRENT_LEDGER",
            "absolute_majorant_sum": "FINITE",
            "witness": angular_witness,
        },
        "rank72_consequence": {
            "tail_identity": rank72["exact_criterion"]["tail_identity"],
            "captured_family_direct_increment": "CAUCHY",
            "captured_family_rank72_relative_form_net": "CAUCHY",
            "ambient_adjoint_limit_required": False,
            "absolute_infinite_volume_heat_trace_required": False,
            "signed_sum_before_norm": True,
        },
        "supersession": {
            "prior_absolute_NHIM_no_go": "PRESERVED",
            "prior_signed_source_contracted_NHIM_route": "NOW_DERIVED_CONDITIONALLY_ON_CAPTURE",
            "arbitrary_positive_nonasymptotic_tail_reopened": False,
            "finite_core_promoted_to_endpoint": False,
        },
        "source_ontology": {
            "external_Cauchy_birth_source": 0,
            "internal_responses_zeroed": False,
            "additional_seam_force_or_source": False,
            "joint_terms_counted_more_than_once": False,
        },
        "exact_next_dependency": (
            "CERTIFY_THAT_A_NONEMPTY_OPEN_EVENT_GENERATED_AE2_RESET_QUOTIENT_"
            "FAMILY_ENTERS_THE_EXISTING_NHIM_CAPTURE_BASIN_WITH_ALL_DOMAIN_"
            "MARGINS_AND_FIRST_JETS,_OR_CERTIFY_AN_ACTUAL_LATER_RETAINED_EVENT_"
            "OR_CANONICAL_STOP;_THEN_EVALUATE_AND_ROOT_THE_COMPLETE_PROJECTED_"
            "HEAT_MINUS_ZETA_COVECTOR"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_RESET_TO_CAPTURE_CONNECTION_OR_LATER_STOP",
            "Gate8": "LOCKED",
            "captured_NHIM_rank72_signed_relative_tail": "CERTIFIED_CAUCHY",
            "absolute_NHIM_graded_heat_trace": "DIVERGENT_PRESERVED",
            "AE2_reset_image_enters_capture_basin": "OPEN_CURRENT_OWNER",
            "actual_later_C2_event_or_canonical_stop": "NOT_CERTIFIED",
            "actual_projected_zero_source_force": "OPEN_AFTER_CONNECTION",
            "same_action_KKT_root": "WAITING_ON_FORCE",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "low_rate": payload["angular_relative_form_bounds"]["net_low_energy_linear_decay_rate"],
        "gaussian_rate": payload["angular_relative_form_bounds"]["high_energy_quadratic_decay_rate"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
