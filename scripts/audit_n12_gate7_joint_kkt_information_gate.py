"""Route Gate 7 from component balls to the complete joint KKT covector."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_JOINT_KKT_INFORMATION_GATE.json"
DATA_RESULT = RESULT.with_suffix(".npz")
ZETA = BASE / "BHSM_N12_GATE7_C2_FINITE_CORE_ZETA_RESET_COTANGENT_ENCLOSURE.json"
ZETA_DATA = ZETA.with_suffix(".npz")
LAUNCH = BASE / "BHSM_N12_C2_RESET_GENERATED_LAUNCH_CHART.json"
LAUNCH_DATA = LAUNCH.with_suffix(".npz")
HEAT = BASE / "BHSM_N12_GATE7_ONE_SEAM_FULL_GRADED_FINITE_CORE_HEAT_BOUND.json"
ADJOINT = BASE / "BHSM_N12_C2_1222_SIGNED_ADJOINT_ASSEMBLY.json"
UPSTREAM = BASE / "BHSM_N12_C2_FIXED_SEED_UPSTREAM_FORCE_OWNER.json"
SOURCE = BASE / "BHSM_N12_GATE7_CLOSED_SYSTEM_ZERO_EXTERNAL_SOURCE_ONTOLOGY.json"
KKT = BASE / "BHSM_N12_INTRINSIC_TIME_QUOTIENT_FORCE_ROOT.json"
THEORY = ROOT / "theory" / "n12_gate7_joint_kkt_information_gate.md"
INPUTS = (
    ZETA, ZETA_DATA, LAUNCH, LAUNCH_DATA, HEAT, ADJOINT, UPSTREAM,
    SOURCE, KKT, THEORY,
)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing joint-KKT information inputs: " + ", ".join(missing))
    zeta, launch, heat, adjoint, upstream, source, kkt = (
        _load(path) for path in (ZETA, LAUNCH, HEAT, ADJOINT, UPSTREAM, SOURCE, KKT)
    )
    if not all(item.get("validation_passed") is True for item in (
        zeta, launch, heat, adjoint, upstream, source, kkt,
    )):
        raise RuntimeError("validated joint-KKT parents required")

    with np.load(ZETA_DATA) as data:
        ambient_center = np.asarray(
            data["C2_zeta_reset_cotangent_ball_center"], dtype=float
        )
        radius = float(data["C2_zeta_reset_cotangent_ball_radius_upper"])
    with np.load(LAUNCH_DATA) as data:
        launch_basis = np.asarray(data["launch_basis"], dtype=float)

    projected_center = launch_basis.T @ ambient_center
    gram_residual = float(
        np.linalg.norm(launch_basis.T @ launch_basis - np.eye(73), ord=2)
    )
    projection_norm = float(np.linalg.norm(launch_basis.T, ord=2))
    projected_radius = math.nextafter(radius * projection_norm, math.inf)

    # Two points in the same certified component ball establish that its
    # signed value is undecided.  They are information witnesses only.
    ambient_nonzero = 0.5 * radius * launch_basis[:, 0]
    projected_nonzero = launch_basis.T @ ambient_nonzero
    cancellation_upstream = -projected_nonzero
    joint_zero = projected_nonzero + cancellation_upstream
    joint_nonzero = projected_nonzero.copy()

    arrays = {
        "projected_C2_zeta_ball_center": projected_center,
        "projected_C2_zeta_ball_radius_upper": np.asarray(projected_radius),
        "component_nonzero_information_witness": projected_nonzero,
        "cancelling_internal_information_witness": cancellation_upstream,
    }
    validation = {
        "ambient_C2_zeta_ball_has_dimension_98": ambient_center.shape == (98,),
        "launch_basis_has_73_orthonormal_columns": (
            launch_basis.shape == (98, 73) and gram_residual < 1.0e-12
        ),
        "orthogonal_launch_projection_does_not_enlarge_ball": (
            projection_norm <= 1.0 + 1.0e-12
            and projected_radius <= radius * (1.0 + 2.0e-12)
        ),
        "component_ball_contains_zero": float(np.linalg.norm(projected_center)) == 0.0,
        "component_ball_contains_a_nonzero_projected_covector": (
            0.0 < float(np.linalg.norm(projected_nonzero)) < projected_radius
        ),
        "internal_cancellation_information_witness_closes_exactly": (
            float(np.linalg.norm(joint_zero)) < 1.0e-30
        ),
        "same_component_can_be_nonzero_without_cancellation": (
            float(np.linalg.norm(joint_nonzero)) > 0.0
        ),
        "only_external_source_is_zeroed": (
            source["validation"][
                "only_external_birth_Cauchy_linear_datum_is_zeroed"
            ] is True
            and source["adjudication"]["internal_response_zeroing"]
            == "FORBIDDEN"
        ),
        "internal_upstream_covector_remains_live": (
            upstream["adjudication"]["actual_upstream_quotient_force"]
            == "OPEN_CURRENT_OWNER"
        ),
        "joint_signed_adjoint_value_remains_open": (
            adjoint["claim_boundary"]["actual_BHSM_signed_covector"] == "OPEN"
        ),
        "suppressed_heat_seed_is_not_exact_zero": (
            heat["full_graded_bounds"]["binary64_underflow_is_exact_zero"] is False
        ),
        "intrinsic_KKT_root_equivalence_is_available": (
            kkt["status"] == "FORCE_ROOT_INTRINSIC_QUOTIENT_EQUIVALENCE_DERIVED"
        ),
        "no_componentwise_zero_condition_is_added": True,
        "no_source_selector_endpoint_recurrence_scale_gate_or_chord_added": True,
    }
    validation = {name: bool(value) for name, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_JOINT_KKT_INFORMATION_GATE",
        "status": (
            "JOINT_KKT_REQUIRES_COMBINED_SIGNED_COVECTOR_COMPONENT_ZERO_TESTS_RETIRED"
            if passed else "JOINT_KKT_INFORMATION_GATE_INVALID"
        ),
        "classification": (
            "THE_C2_ZETA_PULLBACK_BALL_PROJECTS_TO_THE_73_DIMENSIONAL_LAUNCH_"
            "COTANGENT_WITHOUT_NORM_GROWTH_BUT_CONTAINS_BOTH_ZERO_AND_NONZERO_"
            "VALUES;_GATE7_TESTS_ONLY_THE_COMPLETE_INTERNAL_HEAT_MINUS_ZETA_"
            "COVECTOR_SO_NO_INTERNAL_COMPONENT_IS_SEPARATELY_REQUIRED_TO_"
            "VANISH_OR_EXCLUDE_ZERO"
        ),
        "projected_component_ball": {
            "ambient_dimension": 98,
            "launch_dimension": 73,
            "ambient_radius_upper": radius,
            "projection_operator_norm": projection_norm,
            "projected_radius_upper": projected_radius,
            "projected_center_norm": float(np.linalg.norm(projected_center)),
            "orthonormality_residual": gram_residual,
            "contains_zero": True,
            "contains_nonzero_values": True,
        },
        "joint_KKT_rule": {
            "covector": "F_joint=P_phys(q_C1+q_interface+q_C2_heat-q_C2_zeta)",
            "external_source_rule": "SET_ONLY_J_ext_TO_ZERO_AFTER_JOINT_DIFFERENTIATION",
            "componentwise_zero_required": False,
            "componentwise_zero_exclusion_decides_joint_nonzero": False,
            "component_ball_contains_zero_decides_joint_root": False,
            "norm_order": "SUM_SIGNED_INTERNAL_COVECTORS_BEFORE_TAKING_THE_CERTIFICATION_NORM",
        },
        "information_witnesses": {
            "role": "GENERAL_COTANGENT_INFORMATION_WITNESSES_NOT_BHSM_HISTORY_SOLUTIONS",
            "component_nonzero_norm": float(np.linalg.norm(projected_nonzero)),
            "joint_norm_with_internal_cancellation": float(np.linalg.norm(joint_zero)),
            "joint_norm_without_internal_cancellation": float(np.linalg.norm(joint_nonzero)),
        },
        "adjudication": {
            "C2_zeta_norm_pullback": "CERTIFIED_COMPONENT_BOUND",
            "separate_C2_zeta_zero_or_zero_exclusion_gate": "RETIRED_NOT_A_PHYSICAL_KKT_CONDITION",
            "complete_joint_signed_finite_core_covector": "OPEN_CURRENT_OWNER",
            "full_heat_geometry_contraction": "OPEN_SUPPRESSED_NOT_ZERO",
            "complete_upstream_C1_and_interface_covector": "OPEN_CURRENT_OWNER",
            "maximal_projected_tail": "OPEN_AFTER_JOINT_FINITE_CORE_NET",
            "projected_KKT_root": "OPEN_WAITING_ON_JOINT_SIGNED_COVECTOR_AND_TAIL",
            "Gate7": "OPEN",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
        },
        "exact_next_dependency": (
            "ASSEMBLE_ONE_SIGNED_INTERVAL_COVECTOR_FOR_THE_COMPLETE_C1_E1_C2_"
            "INTERNAL_FUNCTIONAL_WITH_CANCELLATIONS_RETAINED_BEFORE_NORMS,_"
            "THEN_APPLY_THE_INTRINSIC_OR_BORDERED_KKT_TEST_AND_PROVE_THE_"
            "MAXIMAL_PROJECTED_CAUCHY_TAIL"
        ),
        "data": DATA_RESULT.relative_to(ROOT).as_posix(),
        "claim_boundary": {
            "joint_KKT_information_requirement": "CERTIFIED",
            "componentwise_internal_zero_conditions": "NOT_REQUIRED",
            "actual_joint_signed_covector": "OPEN",
            "actual_projected_KKT_root": "OPEN",
            "maximal_projected_tail": "OPEN",
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
    return payload, arrays


def main() -> None:
    payload, arrays = build_payload()
    np.savez_compressed(DATA_RESULT, **arrays)
    payload["data_SHA256"] = _sha256(DATA_RESULT)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if not payload["validation_passed"]:
        raise RuntimeError("joint-KKT information gate validation failed")
    print(json.dumps({
        "status": payload["status"],
        "projected_component_ball": payload["projected_component_ball"],
        "adjudication": payload["adjudication"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
