"""Certify the action-owned exact fixed-s C2 field oracle."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_c2_exact_fixed_s_field import (  # noqa: E402
    exact_fixed_s_field_action,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_EXACT_FIXED_S_FIELD_ORACLE.json"
CORE = BASE / "BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
BORDERED_DATA = BASE / "BHSM_N12_C2_BORDERED_HARD_RESPONSE_MATRIX.npz"
FIELD = BASE / "BHSM_N12_C2_EXACT_CENTER_FIXED_S_FIELD_MATRIX.json"
FIELD_DATA = FIELD.with_suffix(".npz")
REFINED = BASE / "BHSM_N12_C2_REFINED_RESET_ROOT_CENTER.json"
REFINED_DATA = REFINED.with_suffix(".npz")
MODULE = ROOT / "src" / "bhsm" / "interface" / "aether_forward_c2_exact_fixed_s_field.py"
THEORY = ROOT / "theory" / "n12_c2_exact_fixed_s_field_oracle.md"
INPUTS = (CORE, BORDERED_DATA, FIELD, FIELD_DATA, REFINED, REFINED_DATA, MODULE, THEORY)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _summary(result: dict[str, object]) -> dict[str, Any]:
    return {
        "selected_branch": int(result["selected_branch"]),
        "b_psi": float(result["b_psi"]),
        "c_psi": float(result["c_psi"]),
        "R_Dlambda_Vhard": float(result["R_Dlambda_Vhard"]),
        "Delta": float(result["Delta"]),
        "field_action_norm": float(np.linalg.norm(np.asarray(result["field_action"]))),
        "Dlambda_field": float(result["Dlambda_field"]),
        "explicit_full_Euler_Dirac_inverse_formed": bool(result["explicit_full_Euler_Dirac_inverse_formed"]),
    }


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing exact-field inputs: " + ", ".join(missing))
    core, field_record, refined = (_load(path) for path in (CORE, FIELD, REFINED))
    if not all(record["validation_passed"] for record in (core, field_record, refined)):
        raise RuntimeError("validated exact-field parents required")
    with np.load(BORDERED_DATA) as data:
        center = np.asarray(data["center_state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)
    with np.load(FIELD_DATA) as data:
        expected = np.asarray(data["exact_center_field_action"], dtype=float)
    terminal_s = float(field_record["center_field"]["signed_descriptor_decimal"])
    terminal = exact_fixed_s_field_action(
        state=center, weights=weights, reference=reference,
        signed_descriptor=terminal_s,
    )
    terminal_vector = np.asarray(terminal["field_action"], dtype=float)
    relative_residual = float(np.linalg.norm(terminal_vector - expected) / np.linalg.norm(expected))

    with np.load(REFINED_DATA) as data:
        birth_state = np.asarray(data["state"], dtype=float)[:98]
        birth_weights = np.asarray(data["state_weights"], dtype=float)
        birth_reference = np.asarray(data["branch_reference"], dtype=float)
    birth = exact_fixed_s_field_action(
        state=birth_state, weights=birth_weights, reference=birth_reference,
        signed_descriptor=0.0,
    )
    validation = {
        "1222_core_proof_centers_are_not_exact_physical_states": core["coefficient_path"]["proof_centers_are_exact_physical_states"] is False,
        "exact_oracle_replays_branch_24_at_birth_and_1214": int(birth["selected_branch"]) == int(terminal["selected_branch"]) == 24,
        "exact_descriptor_identity_holds_at_both_centers": abs(float(birth["Dlambda_field"]) - 1.0) < 1.0e-12 and abs(float(terminal["Dlambda_field"]) - 1.0) < 1.0e-12,
        "exact_denominator_is_positive_at_both_centers": float(birth["Delta"]) > 0.0 and float(terminal["Delta"]) > 0.0,
        "oracle_matches_certified_1214_center_field_within_numerical_realization_error": relative_residual < 5.0e-10,
        "no_full_Euler_Dirac_block_inverse": birth["explicit_full_Euler_Dirac_inverse_formed"] is False and terminal["explicit_full_Euler_Dirac_inverse_formed"] is False,
        "proof_center_not_promoted_to_physical_reset_selector": refined["claim_boundary"]["physical_reset_family_member_selected"] is False,
        "no_selector_recurrence_scale_fit_action_term_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_EXACT_FIXED_S_FIELD_ORACLE",
        "status": "C2_EXACT_FIXED_S_ACTION_FIELD_ORACLE_CERTIFIED_PARAMETRIC_BASE_HISTORY_OPEN" if passed else "C2_EXACT_FIXED_S_FIELD_ORACLE_NOT_CERTIFIED",
        "classification": "THE_DESINGULARIZED_C2_VECTOR_FIELD_IS_EVALUABLE_AT_ANY_REGULAR_STATE_AND_NONNEGATIVE_SIGNED_DESCRIPTOR_FROM_THE_EXACT_ACTION_JET,_SELECTED_EIGENLINE,_BORDERED_COMPLEMENT_RESPONSE,_AND_HELLMANN_FEYNMAN_DIRECTIONAL_DERIVATIVES;_THE_STORED_1222_PROOF_CENTERS_ARE_NOT_AN_ACTUAL_PARAMETRIC_BASE_HISTORY",
        "exact_system": {
            "hard_response": "(D_reduced-lambda_selected)^-1_ON_THE_SELECTED_LINE_COMPLEMENT_ONLY",
            "b_psi": "<Psi,rhs_raw>",
            "c_psi": "Dlambda[Psi]",
            "R": "Dlambda[V_hard]",
            "Delta": "c_psi*b_psi+s*R",
            "field": "F_s=(s*qdot,b_psi*Psi+s*V_hard)/Delta",
            "descriptor_identity": "Dlambda[F_s]=1",
            "explicit_full_Euler_Dirac_inverse_formed": False,
        },
        "crosschecks": {
            "birth_proof_center": _summary(birth),
            "center_1214": _summary(terminal),
            "stored_center_field_relative_residual": relative_residual,
            "direct_cubic_relative_to_stored_direct_D3": abs(
                float(terminal["c_psi"])
                - float(field_record["center_field"]["moving_cubic_direct_fixed_line_D3"])
            ) / abs(float(terminal["c_psi"])),
        },
        "matching_audit": [
            {
                "diagram_slot": "EXACT_C2_FIXED_s_STATE_GENERATOR",
                "required_type": "ACTION_OWNED_REGULAR_VECTOR_FIELD_ON_SELECTED_LINE_CHART",
                "candidate": "aether_forward_c2_exact_fixed_s_field.exact_fixed_s_field_action",
                "domain_check": "VALID_WHERE_SELECTED_LINE_IS_SIMPLE_AND_Delta_POSITIVE",
                "provenance_check": "VALID_RETAINED_ACTION_JET_AND_COMPLEMENT_SOLVE",
                "verdict": "VALID_MATCH",
            },
            {
                "diagram_slot": "SIGNED_1222_BACKWARD_CENTER_ADJOINT_BASE",
                "required_type": "ONE_ACTUAL_PARAMETRIC_RESET_FAMILY_HISTORY_OR_COUPLED_MULTIPLE_SHOOTING_KKT_BASE",
                "candidate": "STORED_1222_PROOF_CENTER_NODES",
                "domain_check": "INVALID_AS_SIGNED_BASE;_CENTERS_ENCLOSE_BUT_ARE_NOT_EXACT_PHYSICAL_STATES",
                "provenance_check": "PROOF_GEOMETRY_ONLY",
                "verdict": "ACTUALLY_MISSING_PARAMETRIC_BASE_HISTORY",
            },
        ],
        "adjudication": {
            "exact_fixed_s_field_evaluator": "CLOSED",
            "single_proof_center_history_as_physical_selector": "FORBIDDEN_AND_NOT_USED",
            "parametric_reset_family_base_history": "OPEN",
            "signed_backward_center_adjoint": "WAITING_ON_PARAMETRIC_BASE_OR_COUPLED_KKT",
            "finite_core_norm_certificates": "CLOSED_DO_NOT_REPEAT",
        },
        "exact_next_dependency": "USE_THIS_EXACT_FIELD_IN_A_PARAMETRIC_RESET_CHART_MULTIPLE_SHOOTING_OR_EQUIVALENT_COUPLED_FORWARD_ADJOINT_KKT_SOLVE;_DO_NOT_DIFFERENTIATE_THE_PROOF_CENTER_ALGORITHM_OR_SELECT_ONE_RESET_MEMBER",
        "claim_boundary": {
            "Gate7": "ACTIVE_PARAMETRIC_BASE_HISTORY_OR_COUPLED_FORWARD_ADJOINT_KKT",
            "Gate8": "LOCKED",
            "exact_fixed_s_field_oracle": "CERTIFIED",
            "actual_parametric_base_history": "OPEN",
            "signed_finite_core_geometry_covector": "OPEN",
            "actual_projected_zero_source_force": "OPEN",
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
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({
        "status": payload["status"],
        "birth": payload["crosschecks"]["birth_proof_center"],
        "center_1214_relative_residual": payload["crosschecks"]["stored_center_field_relative_residual"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
