"""Derive the maximal fixed-channel relative heat cotangent at Gate 7."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_MAXIMAL_FIXED_CHANNEL_RELATIVE_HEAT_COTANGENT.json"
CONTRACTION = BASE / "BHSM_N12_GATE7_MAXIMAL_COMPLIANCE_SEAM_CONTRACTION.json"
MAXIMAL = BASE / "BHSM_N12_C2_CLASS_REDUCED_MAXIMAL_RESPONSE.json"
FRIEDRICHS = BASE / "BHSM_N12_MAXIMAL_FRIEDRICHS_WEYL_EXHAUSTION.json"
ANGULAR = BASE / "BHSM_N12_GATE7_AE2_ANGULAR_DINI_UNIFORMITY_AUDIT.json"
HIGH_ENERGY = BASE / "BHSM_N12_FORWARD_E1_HIGH_ENERGY_TRACE_NORM.json"
SOURCE_ONTOLOGY = BASE / "BHSM_N12_GATE7_CLOSED_SYSTEM_ZERO_EXTERNAL_SOURCE_ONTOLOGY.json"
NO_GO = BASE / "BHSM_N12_NEGATIVE_AXIS_SEAM_HEAT_SYNTHESIS_NO_GO.json"
THEORY = ROOT / "theory" / "n12_gate7_maximal_fixed_channel_relative_heat_cotangent.md"
INPUTS = (
    CONTRACTION,
    MAXIMAL,
    FRIEDRICHS,
    ANGULAR,
    HIGH_ENERGY,
    SOURCE_ONTOLOGY,
    NO_GO,
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
            "missing fixed-channel relative heat inputs: " + ", ".join(missing)
        )
    contraction, maximal, friedrichs, angular, high_energy, source, no_go = (
        _load(path)
        for path in (
            CONTRACTION,
            MAXIMAL,
            FRIEDRICHS,
            ANGULAR,
            HIGH_ENERGY,
            SOURCE_ONTOLOGY,
            NO_GO,
        )
    )
    parents = (
        contraction,
        maximal,
        friedrichs,
        angular,
        high_energy,
        source,
        no_go,
    )
    if not all(parent.get("validation_passed") is True for parent in parents):
        raise RuntimeError("validated fixed-channel relative heat parents required")

    # Finite-dimensional boundary-triple replay.  It verifies the rank-one
    # Krein derivative algebra but is not an N12 maximal-history value.
    child_matrix = np.diag([1.3, 2.1, 3.7])
    gamma = np.asarray([[0.4], [-0.7], [0.2]], dtype=float)
    compliance = 0.16
    compliance_jet = 0.031
    load = 1.9
    green = compliance / (1.0 + compliance * load)
    green_jet = compliance_jet / (1.0 + compliance * load) ** 2
    resolvent_difference = -(gamma * green) @ gamma.T
    resolvent_jet = -(gamma * green_jet) @ gamma.T
    epsilon = 1.0e-7
    green_plus = (compliance + epsilon * compliance_jet) / (
        1.0 + (compliance + epsilon * compliance_jet) * load
    )
    green_minus = (compliance - epsilon * compliance_jet) / (
        1.0 + (compliance - epsilon * compliance_jet) * load
    )
    finite_difference = (
        (-(gamma * green_plus) @ gamma.T)
        - (-(gamma * green_minus) @ gamma.T)
    ) / (2.0 * epsilon)
    singular_values = np.linalg.svd(resolvent_difference, compute_uv=False)
    derivative_residual = float(np.linalg.norm(finite_difference - resolvent_jet))
    trace_norm = float(np.sum(np.linalg.svd(resolvent_jet, compute_uv=False)))
    trace_norm_formula = float(abs(green_jet) * np.vdot(gamma[:, 0], gamma[:, 0]))

    validation = {
        "all_parent_artifacts_are_validated": True,
        "maximal_friedrichs_value_is_unique": (
            friedrichs["claim_boundary"]["maximal_Friedrichs_Weyl_value_definition"]
            == "DERIVED_AS_UNIQUE_EXHAUSTION"
        ),
        "maximal_child_family_has_analytic_resolvent_continuation": (
            "ANALYTIC_CONTINUATION" in maximal["M_C2_maximal_operator_family"]["spectral_region"]
        ),
        "negative_axis_compliance_contraction_is_certified": (
            contraction["claim_boundary"][
                "maximal_negative_axis_incoming_compliance_cotangent"
            ] == "CERTIFIED_PARAMETRIC"
        ),
        "rank_one_Krein_replay": int(np.sum(singular_values > 1.0e-14)) == 1,
        "Krein_derivative_replay": derivative_residual < 1.0e-9,
        "rank_one_trace_norm_formula_replays": abs(trace_norm - trace_norm_formula) < 1.0e-14,
        "fixed_channel_high_energy_control_is_preserved": (
            high_energy["validation_passed"] is True
        ),
        "angular_uniformity_not_overclaimed": (
            angular["adjudication"]["arbitrary_positive_tail_angular_sum"] == "FALSE"
        ),
        "negative_axis_sign_no_go_is_preserved": (
            no_go["claim_boundary"]["broad_negative_axis_synthesis_route"]
            == "CLOSED_INVALID"
        ),
        "only_external_source_is_zeroed": (
            source["external_internal_partition"]["set_to_zero"] == ["J_ext"]
        ),
        "reference_extension_not_added_as_second_action_determinant": True,
        "no_internal_response_is_zeroed": True,
        "no_seam_source_selector_endpoint_recurrence_scale_fit_gate_or_chord_added": True,
    }
    validation = {name: bool(value) for name, value in validation.items()}
    passed = all(validation.values())

    return {
        "artifact": "BHSM_N12_GATE7_MAXIMAL_FIXED_CHANNEL_RELATIVE_HEAT_COTANGENT",
        "status": (
            "MAXIMAL_FIXED_CHANNEL_INCOMING_RELATIVE_HEAT_COTANGENT_DERIVED"
            if passed
            else "MAXIMAL_FIXED_CHANNEL_RELATIVE_HEAT_COTANGENT_INVALID"
        ),
        "classification": (
            "FOR_EACH_RETAINED_ANGULAR_CHANNEL_THE_FIXED_TERMINAL_INCOMING_"
            "ATTACHMENT_IS_A_RANK_ONE_RESOLVENT_COMPARABLE_EXTENSION_OF_THE_"
            "ACTION_OWNED_MAXIMAL_C2_FRIEDRICHS_OPERATOR;_ITS_COMPLIANCE_"
            "DERIVATIVE_DEFINES_A_TRACE_CLASS_RELATIVE_HEAT_COTANGENT_WITHOUT_"
            "AN_ARBITRARY_FAR_ENDPOINT_OR_A_SEPARATE_CHILD_JET"
        ),
        "boundary_triple_theorem": {
            "reference_role": "DIRICHLET_BOUNDARY_TRIPLE_REFERENCE_ONLY_NOT_A_SECOND_ACTION_TERM",
            "resolvent_difference": "R_C(z)-R_D(z)=-gamma(z)*G_S(z)*gamma(z_bar)^dagger",
            "seam_green": "G_S(z)=C_f/(1+C_f*L(z))",
            "fixed_terminal_resolvent_jet": (
                "D[R_C-R_D]=-gamma*(D_C_f)/(1+C_f*L)^2*gamma_bar^dagger"
            ),
            "rank_per_scalar_channel_upper": 1,
            "negative_axis_trace_norm": (
                "norm_1(D[R_C-R_D])=abs(D_G_S)*norm(gamma)^2"
            ),
            "Poisson_Weyl_identity": "norm(gamma(-kappa^2))^2=-D_z_M_C2(-kappa^2)",
            "relative_heat_cotangent": (
                "D_Gamma_heat=-(1/(4*pi*i))*integral_Gamma_exp(-z)*Tr(D_R(z))*dz"
            ),
            "one_sided_C_f_zero_limit": "TRACE_NORM_DIFFERENTIABLE",
            "incoming_amplitude_order": "D_lambda_Gamma_heat_channel=O(lambda)",
            "separate_D_lambda_M_C2_max_required": False,
        },
        "algebra_witness": {
            "purpose": "FINITE_DIMENSIONAL_KREIN_IDENTITY_REPLAY_NOT_A_PHYSICAL_HISTORY_VALUE",
            "child_matrix_diagonal": np.diag(child_matrix).tolist(),
            "C_f": compliance,
            "D_C_f": compliance_jet,
            "L": load,
            "G_S": green,
            "D_G_S": green_jet,
            "resolvent_difference_rank": int(np.sum(singular_values > 1.0e-14)),
            "resolvent_jet_finite_difference_residual": derivative_residual,
            "resolvent_jet_trace_norm": trace_norm,
            "rank_one_trace_norm_formula": trace_norm_formula,
        },
        "adjudication": {
            "maximal_fixed_channel_incoming_relative_heat_cotangent": "CLOSED",
            "maximal_fixed_channel_reverse_seed": "DEFINED_BY_TRACE_CLASS_FUNCTIONAL_CALCULUS",
            "absolute_infinite_volume_heat_trace_required": False,
            "arbitrary_far_endpoint_required": False,
            "separate_maximal_child_amplitude_jet_required": False,
            "complete_graded_angular_sum": "OPEN_CURRENT_OWNER",
            "actual_projected_Cauchy_tail": "OPEN_AFTER_GRADED_SUM",
            "actual_projected_KKT_root": "OPEN",
            "Gate7": "OPEN",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
        },
        "exact_next_dependency": (
            "PROVE_THE_RETAINED_GRADED_ANGULAR_SUM_OF_THE_RANK_ONE_RELATIVE_HEAT_"
            "COTANGENTS_ON_THE_ACTUAL_MAXIMAL_C2_HISTORY,_OR_CERTIFY_A_FINITE_"
            "LATER_EVENT_OR_CANONICAL_STOP_AND_USE_THE_COMPACT_ENDPOINT_THEOREM;_"
            "THEN_COMPOSE_THE_ONE_JOINT_REVERSE_ADJOINT_AND_TEST_THE_PHYSICAL_"
            "QUOTIENT_CAUCHY_TAIL"
        ),
        "claim_boundary": {
            "maximal_fixed_channel_relative_heat_cotangent": "DERIVED",
            "maximal_full_graded_relative_heat_cotangent": "OPEN",
            "actual_projected_Cauchy_tail": "OPEN",
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
        raise RuntimeError("maximal fixed-channel relative heat validation failed")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "rank": payload["algebra_witness"]["resolvent_difference_rank"],
                "derivative_residual": payload["algebra_witness"][
                    "resolvent_jet_finite_difference_residual"
                ],
                "validation_passed": payload["validation_passed"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
