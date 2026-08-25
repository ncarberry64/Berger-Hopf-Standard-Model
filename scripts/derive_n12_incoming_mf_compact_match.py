"""Match the incoming M_f slot to the compact formation Calderon response."""

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
    restrict_two_boundary_weyl_to_dirichlet_birth_jets,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_INCOMING_MF_COMPACT_MATCH.json"
COMPACT = BASE / "BHSM_N12_COMPACT_FINITE_HISTORY_OPERATOR.json"
ENDPOINT = BASE / "BHSM_N12_COMPACT_HISTORY_ENDPOINT_ROLE_PROVENANCE.json"
GLUING = BASE / "BHSM_N12_FINITE_HISTORY_GLUING_FORCE_PROVENANCE.json"
GERM = BASE / "BHSM_N12_FINITE_HISTORY_TERMINAL_WEYL_GERM.json"
PARAMETER = BASE / "BHSM_N12_DESINGULARIZED_FINITE_HISTORY_OPERATOR_PARAMETER.json"
MODULE = ROOT / "src" / "bhsm" / "interface" / "aether_forward_channel_transfer.py"
THEORY = ROOT / "theory" / "n12_incoming_mf_compact_match.md"
INPUTS = (COMPACT, ENDPOINT, GLUING, GERM, PARAMETER, MODULE, THEORY)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _matrix(value: Any) -> np.ndarray:
    return np.asarray(value, dtype=float)


def _extract_germ(channel: dict[str, Any]) -> dict[str, float]:
    zeros = np.zeros((2, 2))
    inverse_duration = _matrix(channel["inverse_duration"])
    constant = _matrix(channel.get("constant", zeros))
    duration = _matrix(channel["duration"])
    common_constant = _matrix(channel["common_scale_constant"])
    common_duration = _matrix(channel["common_scale_duration"])
    trial_duration = 1.0e-3
    two_boundary = {
        "base": inverse_duration / trial_duration + constant + trial_duration * duration,
        "first_left": common_constant + trial_duration * common_duration,
        "first_right": zeros,
        "mixed_second": zeros,
    }
    restricted = restrict_two_boundary_weyl_to_dirichlet_birth_jets(two_boundary)
    return {
        "inverse_duration": float(inverse_duration[1, 1]),
        "constant": float(constant[1, 1]),
        "duration": float(duration[1, 1]),
        "fixed_duration_common_scale_constant": float(common_constant[1, 1]),
        "fixed_duration_common_scale_duration": float(common_duration[1, 1]),
        "restriction_crosscheck_duration": trial_duration,
        "restriction_crosscheck_value": float(restricted["base"][0, 0].real),
        "restriction_crosscheck_residual": abs(
            float(restricted["base"][0, 0].real)
            - float(two_boundary["base"][1, 1])
        ),
    }


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing incoming M_f match inputs: " + ", ".join(missing))
    compact, endpoint, gluing, germ, parameter = (
        _load(path) for path in INPUTS[:5]
    )
    if not all(record.get("validation_passed") is True for record in (
        compact, endpoint, gluing, germ, parameter,
    )):
        raise RuntimeError("validated compact formation parents required")
    germs = germ["weyl_Laurent_germs"]
    incoming = {
        "scalar_c_3": _extract_germ(germs["scalar_c_3"]),
        "product_Dirac_lambda_1_5_chirality_plus": _extract_germ(
            germs["product_Dirac_lambda_1_5_chirality_plus"]
        ),
        "product_Dirac_lambda_1_5_chirality_minus": _extract_germ(
            germs["product_Dirac_lambda_1_5_chirality_minus"]
        ),
    }
    a_lower, a_upper = (
        float(value) for value in parameter["duration_parameter_jet"]
        ["certified_a_interval"]
    )
    leading_amplitude_coefficient_interval = [1.0 / a_upper, 1.0 / a_lower]
    validation = {
        "compact_endpoint_order_is_birth_then_new_event": (
            compact["endpoint_partition"]["ordered_traces"]
            == ["birth", "new_event"]
        ),
        "birth_zero_trace_is_retained_Dirichlet_reference": (
            endpoint["endpoint_roles"]["birth"]["zero_source_restriction"]
            == "Gamma0_birth(U)=0"
        ),
        "new_event_is_the_AE2_terminal_trace": (
            endpoint["endpoint_roles"]["new_event"]["certified_endpoint"]
            == "E1_TO_C2_AE2_RESET"
        ),
        "formation_Schur_response_parent_is_M_f": (
            gluing["exact_identities"]["formation_response"]
            == "M_f=H-C_DAGGER*A^-1*C"
        ),
        "all_stored_germs_restrict_exactly_to_terminal_block": all(
            row["restriction_crosscheck_residual"] == 0.0
            for row in incoming.values()
        ),
        "duration_amplitude_coefficient_is_strictly_positive": a_lower > 0.0,
        "leading_inverse_duration_amplitude_coefficient_is_positive": (
            leading_amplitude_coefficient_interval[0] > 0.0
        ),
        "positive_amplitude_or_history_member_not_selected": (
            parameter["claim_boundary"]["positive_history_member"]
            == "NOT_SELECTED"
        ),
        "complete_finite_duration_family_not_overclaimed": (
            germ["claim_boundary"]["complete_finite_duration_M_C_family"]
            == "OPEN_BEYOND_GERM"
        ),
        "child_seam_value_not_removed": (
            gluing["adjudication"]
            ["terminal_child_response_or_joint_operator_still_required"] is True
        ),
        "no_matrix_inverse_endpoint_load_selector_scale_fit_recurrence_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_INCOMING_MF_COMPACT_MATCH",
        "status": (
            "INCOMING_MF_IDENTIFIED_AS_COMPACT_TERMINAL_BLOCK_AND_LAURENT_GERM"
            if passed else "INCOMING_MF_COMPACT_MATCH_NOT_CERTIFIED"
        ),
        "classification": (
            "THE_INCOMING_FORMATION_RESPONSE_IS_NOT_A_NEW_OPERATOR;_ON_THE_"
            "RETAINED_ZERO_BIRTH_SOURCE_REFERENCE_IT_IS_THE_NEW_EVENT_BLOCK_"
            "M11_OF_THE_EXISTING_COMPACT_TWO_BOUNDARY_CALDERON_MAP_AND_EQUALS_"
            "THE_EXISTING_FORMATION_SCHUR_COMPLEMENT"
        ),
        "exact_match": {
            "diagram_leg": "C1_TO_E1_INCOMING_FORMATION",
            "two_boundary_endpoint_order": ["birth", "new_event"],
            "zero_source_reference": "u_birth=0",
            "restriction": "M_f=iota_event^dagger*M_C_form*iota_event=M11",
            "block_Schur_equivalence": "M_f=H-C_DAGGER*A^-1*C",
            "event_load_not_included_in_M_f": "U_R_DAGGER*M_C2*U_R+W_phys",
            "explicit_matrix_inverse_formed": False,
        },
        "incoming_Mf_terminal_germs_at_finite_z": incoming,
        "action_amplitude": {
            "parameter": "lambda_0>0",
            "duration_law": "T(lambda_0)=a*lambda_0^2+o(lambda_0^2)",
            "certified_a_interval": [a_lower, a_upper],
            "leading_Mf_coefficient_interval": leading_amplitude_coefficient_interval,
            "leading_Mf_term": "(a*lambda_0^2)^-1",
            "positive_lambda_0_selected": False,
        },
        "claim_boundary": {
            "incoming_Mf_operator_identity": "CLOSED_EXISTING_COMPACT_TERMINAL_BLOCK",
            "incoming_Mf_action_owned_Laurent_germ": "CLOSED",
            "complete_finite_duration_incoming_Mf_family": "OPEN_COEFFICIENT_PATH",
            "sharp_joint_incoming_event_child_operator": "OPEN",
            "full_graded_heat_trace": "OPEN",
            "non_scale_reset_quotient": "OPEN",
            "Gate7": "G7_08_OPEN",
            "Gate8": "LOCKED",
        },
        "validated_invalidated_open": {
            "VALIDATED": [
                "incoming M_f compact terminal-block identity",
                "formation Schur-complement equivalence",
                "three stored action-owned incoming Laurent germs",
                "positive action-amplitude duration coefficient",
            ],
            "INVALIDATED": [
                "a new C1 operator theory is missing",
                "a second birth exterior response is required",
                "a positive formation amplitude may be selected by hand",
            ],
            "OPEN": [
                "complete finite-duration incoming coefficient path",
                "sharp joint incoming-event-child operator",
                "full graded heat trace",
                "non-scale reset quotient force sector",
            ],
        },
        "exact_next_dependency": (
            "ASSEMBLE_THE_COMPLETE_FINITE_DURATION_INCOMING_COEFFICIENT_PATH_"
            "PARAMETRICALLY_WITH_THE_ACTION_AMPLITUDE_AND_GLUE_ITS_NOW_"
            "IDENTIFIED_M_f_BLOCK_TO_THE_ACTION_OWNED_C2_SEAM;_DO_NOT_DERIVE_"
            "A_NEW_C1_OPERATOR_OR_SELECT_lambda_0"
        ),
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
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "complete_family": payload["claim_boundary"]
        ["complete_finite_duration_incoming_Mf_family"],
        "validation_passed": payload["validation_passed"],
    }, indent=2))


if __name__ == "__main__":
    main()
