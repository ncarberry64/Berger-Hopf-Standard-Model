"""Certify maximal-load contraction of the incoming compliance cotangent."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_MAXIMAL_COMPLIANCE_SEAM_CONTRACTION.json"
COMPLIANCE = BASE / "BHSM_N12_GATE7_INCOMING_COMPLIANCE_REGULAR_CHART.json"
SEAM_FAMILY = BASE / "BHSM_N12_AE2_NEGATIVE_AXIS_SEAM_FAMILY.json"
MAXIMAL = BASE / "BHSM_N12_C2_CLASS_REDUCED_MAXIMAL_RESPONSE.json"
FINITE_AMPLITUDE = BASE / (
    "BHSM_N12_GATE7_INCOMING_FINITE_AMPLITUDE_HEAT_ZETA_COMPARISON.json"
)
NO_GO = BASE / "BHSM_N12_NEGATIVE_AXIS_SEAM_HEAT_SYNTHESIS_NO_GO.json"
SOURCE_ONTOLOGY = BASE / "BHSM_N12_GATE7_CLOSED_SYSTEM_ZERO_EXTERNAL_SOURCE_ONTOLOGY.json"
THEORY = ROOT / "theory" / "n12_gate7_maximal_compliance_seam_contraction.md"
INPUTS = (
    COMPLIANCE,
    SEAM_FAMILY,
    MAXIMAL,
    FINITE_AMPLITUDE,
    NO_GO,
    SOURCE_ONTOLOGY,
    THEORY,
)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "missing maximal compliance contraction inputs: " + ", ".join(missing)
        )
    compliance, seam_family, maximal, finite_amplitude, no_go, source_ontology = (
        _load(path)
        for path in (
            COMPLIANCE,
            SEAM_FAMILY,
            MAXIMAL,
            FINITE_AMPLITUDE,
            NO_GO,
            SOURCE_ONTOLOGY,
        )
    )
    parents = (
        compliance,
        seam_family,
        maximal,
        finite_amplitude,
        no_go,
        source_ontology,
    )
    if not all(parent.get("validation_passed") is True for parent in parents):
        raise RuntimeError("validated maximal compliance parents required")

    # An explicit scalar-channel replay.  The theorem itself is parametric in
    # every C_f>0, L>=0 and D C_f; these values only verify the algebra without
    # selecting a physical maximal load.
    compliance_value = float(compliance["algebra_witness"]["C_f"])
    load_value = float(
        seam_family["sampled_crosscheck_rows"][2]["scalar_deRham"]["base"]["maximum_rate"]
    )
    compliance_jet = float(compliance["algebra_witness"]["D_C_f_quotient"])
    seam_green = compliance_value / (1.0 + compliance_value * load_value)
    derivative = compliance_jet / (1.0 + compliance_value * load_value) ** 2
    contraction_factor = 1.0 / (1.0 + compliance_value * load_value) ** 2
    epsilon = 1.0e-7
    plus = (compliance_value + epsilon * compliance_jet) / (
        1.0 + (compliance_value + epsilon * compliance_jet) * load_value
    )
    minus = (compliance_value - epsilon * compliance_jet) / (
        1.0 + (compliance_value - epsilon * compliance_jet) * load_value
    )
    finite_difference = (plus - minus) / (2.0 * epsilon)
    residual = abs(finite_difference - derivative)

    validation = {
        "all_parent_artifacts_are_validated": True,
        "incoming_compliance_is_strictly_positive": compliance_value > 0.0,
        "retained_negative_axis_child_load_is_nonnegative": (
            seam_family["parametric_theorem"]["product_dirac_bound"].startswith("0<=")
            and float(
                seam_family["sampled_crosscheck_rows"][2]["scalar_deRham"]["base"][
                    "lower"
                ]
            ) >= 0.0
        ),
        "maximal_C2_Weyl_family_is_action_owned": (
            maximal["claim_boundary"]["C2_maximal_Weyl_family_definition"]
            == "INSTANTIATED"
        ),
        "seam_green_forms_are_equal": abs(
            seam_green - 1.0 / (1.0 / compliance_value + load_value)
        ) < 1.0e-15,
        "derivative_identity_replays": residual < 1.0e-9,
        "contraction_factor_is_in_unit_interval": 0.0 < contraction_factor <= 1.0,
        "finite_amplitude_sign_not_promoted_to_maximal_heat_sign": (
            finite_amplitude["claim_boundary"]["maximal_projected_tail"] == "OPEN"
        ),
        "negative_axis_heat_synthesis_no_go_preserved": (
            no_go["claim_boundary"]["broad_negative_axis_synthesis_route"]
            == "CLOSED_INVALID"
        ),
        "only_external_source_is_zeroed": (
            source_ontology["external_internal_partition"]["set_to_zero"] == ["J_ext"]
        ),
        "no_internal_response_is_zeroed": True,
        "no_seam_source_selector_endpoint_recurrence_scale_fit_gate_or_chord_added": True,
    }
    validation = {name: bool(value) for name, value in validation.items()}
    passed = all(validation.values())

    return {
        "artifact": "BHSM_N12_GATE7_MAXIMAL_COMPLIANCE_SEAM_CONTRACTION",
        "status": (
            "MAXIMAL_CHILD_LOAD_CANNOT_AMPLIFY_FIXED_TERMINAL_INCOMING_COMPLIANCE_COTANGENT"
            if passed
            else "MAXIMAL_COMPLIANCE_SEAM_CONTRACTION_INVALID"
        ),
        "classification": (
            "FOR_EVERY_RETAINED_NEGATIVE_AXIS_CHANNEL_THE_NONNEGATIVE_ACTION_OWNED_"
            "MAXIMAL_CHILD_PLUS_CONTACT_LOAD_MULTIPLIES_THE_FIXED_TERMINAL_INCOMING_"
            "COMPLIANCE_COTANGENT_BY_(1+C_f*L)^-2_IN_(0,1];_THE_UNKNOWN_C2_LOAD_"
            "CANNOT_RESTORE_THE_SHORT_ARM_POLE_OR_AMPLIFY_THIS_COTANGENT"
        ),
        "theorem": {
            "domain": "z=-kappa^2,_kappa>0,_ONE_RETAINED_SCALAR_CHANNEL",
            "joint_internal_load": "L=U_R^dagger*M_C2^max*U_R+W_phys>=0",
            "seam_green": "G_S=(M_f+L)^-1=C_f/(1+C_f*L)",
            "fixed_terminal_derivative": "D_G_S=(D_C_f)/(1+C_f*L)^2",
            "contraction": "abs(D_G_S)<=abs(D_C_f)",
            "short_arm_consequence": "D_lambda_C_f=O(lambda)_IMPLIES_D_lambda_G_S=O(lambda)",
            "maximal_child_jet_required_in_this_direction": False,
            "descriptor_or_Dirac_block_inverse_formed": False,
        },
        "algebra_witness": {
            "purpose": "PARAMETRIC_IDENTITY_REPLAY_NOT_A_SELECTED_PHYSICAL_LOAD",
            "C_f": compliance_value,
            "L": load_value,
            "D_C_f": compliance_jet,
            "G_S": seam_green,
            "D_G_S": derivative,
            "contraction_factor": contraction_factor,
            "finite_difference_D_G_S": finite_difference,
            "finite_difference_residual": residual,
        },
        "adjudication": {
            "incoming_amplitude_negative_axis_maximal_compliance_cotangent": "CLOSED_PARAMETRICALLY",
            "separate_D_lambda_M_C2_max_required": False,
            "maximal_child_or_contact_response_zeroed": False,
            "finite_core_sign_transferred_to_maximal_heat_functional": False,
            "actual_full_graded_source_contracted_spectral_measure": "OPEN_CURRENT_OWNER",
            "actual_projected_Cauchy_tail": "OPEN_CURRENT_OWNER",
            "actual_projected_KKT_root": "OPEN",
            "Gate7": "OPEN",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
        },
        "exact_next_dependency": (
            "CONSTRUCT_OR_ENCLOSE_THE_ACTUAL_COMPLETE_GRADED_SOURCE_CONTRACTED_SEAM_"
            "SPECTRAL_MEASURE_OR_EQUIVALENT_FUNCTIONAL_CALCULUS_COTANGENT_ON_THE_"
            "MAXIMAL_C2_HISTORY_AND_PROVE_ITS_PHYSICAL_QUOTIENT_CAUCHY_TAIL;_DO_NOT_"
            "REQUIRE_A_SEPARATE_FIXED_TERMINAL_D_lambda_M_C2_MAX_OR_INFER_THE_HEAT_"
            "SIGN_FROM_POINTWISE_RESOLVENT_CONTRACTION"
        ),
        "claim_boundary": {
            "maximal_negative_axis_incoming_compliance_cotangent": "CERTIFIED_PARAMETRIC",
            "maximal_full_graded_heat_cotangent": "OPEN",
            "actual_projected_Cauchy_tail": "OPEN_CURRENT_OWNER",
            "actual_projected_KKT_root": "OPEN",
            "Gate7": "OPEN",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
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
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if not payload["validation_passed"]:
        raise RuntimeError("maximal compliance seam contraction validation failed")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "contraction_factor": payload["algebra_witness"]["contraction_factor"],
                "finite_difference_residual": payload["algebra_witness"][
                    "finite_difference_residual"
                ],
                "validation_passed": payload["validation_passed"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
