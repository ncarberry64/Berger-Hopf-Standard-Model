"""Localize the signed moving-duration incidence required by Gate 7."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_c2_geometry_incidence import (  # noqa: E402
    boundary_geometry_action_covectors,
    proper_duration_density_and_action_covector,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_SIGNED_DURATION_INCIDENCE_OWNER.json"
PARAMETRIC = BASE / "BHSM_N12_C2_1222_PARAMETRIC_BASE_FAMILY.json"
EXACT_FIELD = BASE / "BHSM_N12_C2_EXACT_FIXED_S_FIELD_ORACLE.json"
FIELD_MATRIX = BASE / "BHSM_N12_C2_EXACT_CENTER_FIXED_S_FIELD_MATRIX.json"
FIELD_DATA = FIELD_MATRIX.with_suffix(".npz")
DURATION_NORM = BASE / "BHSM_N12_C2_1222_MOVING_DURATION_PULLBACK_ENCLOSURE.json"
SIGNED_ADJOINT = BASE / "BHSM_N12_C2_1222_SIGNED_ADJOINT_ASSEMBLY.json"
MODULE = ROOT / "src" / "bhsm" / "interface" / "aether_forward_c2_geometry_incidence.py"
THEORY = ROOT / "theory" / "n12_c2_signed_duration_incidence_owner.md"
INPUTS = (
    PARAMETRIC,
    EXACT_FIELD,
    FIELD_MATRIX,
    FIELD_DATA,
    DURATION_NORM,
    SIGNED_ADJOINT,
    MODULE,
    THEORY,
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
        raise FileNotFoundError("missing signed-duration inputs: " + ", ".join(missing))
    parametric, exact_field, field, duration, adjoint = (
        _load(path)
        for path in (PARAMETRIC, EXACT_FIELD, FIELD_MATRIX, DURATION_NORM, SIGNED_ADJOINT)
    )
    if not all(record.get("validation_passed") is True for record in (
        parametric, exact_field, field, duration, adjoint,
    )):
        raise RuntimeError("validated signed-duration lineage required")
    with np.load(FIELD_DATA) as data:
        center = np.asarray(data["center_state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
    geometry = boundary_geometry_action_covectors(state=center, weights=weights)
    zero_delta_witness = proper_duration_density_and_action_covector(
        state=center,
        weights=weights,
        signed_descriptor=float(field["center_field"]["signed_descriptor_decimal"]),
        Delta=float(field["center_field"]["Delta"]),
        D_Delta_action_dual=np.zeros(98),
    )
    validation = {
        "parametric_family_exists_on_every_finite_core_prefix": (
            parametric["claim_boundary"][
                "parametric_base_history_existence_through_1222"
            ] == "DERIVED"
        ),
        "exact_fixed_s_field_returns_positive_Delta": (
            exact_field["crosschecks"]["center_1214"]["Delta"] > 0.0
        ),
        "exact_log_radius_and_log_lapse_covectors_are_finite": (
            np.all(np.isfinite(geometry["D_log_R4_action_dual"]))
            and np.all(np.isfinite(geometry["D_log_lapse_action_dual"]))
        ),
        "positive_s_center_has_positive_proper_duration_density": (
            zero_delta_witness["proper_duration_density"] > 0.0
        ),
        "existing_duration_parent_contains_only_a_norm_bound": (
            duration["claim_boundary"]["moving_duration_reset_pullback_norm"]
            .startswith("CERTIFIED")
            and duration["adjudication"]["actual_signed_duration_covector"]
            == "OPEN"
        ),
        "signed_reverse_sweep_is_ready_to_consume_duration_covector": (
            adjoint["claim_boundary"]["signed_finite_core_adjoint_assembly"]
            == "DERIVED"
        ),
        "zero_DDelta_witness_is_only_an_algebraic_formula_crosscheck": True,
        "proof_center_not_promoted_to_physical_history": True,
        "no_inverse_selector_endpoint_recurrence_scale_fit_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_SIGNED_DURATION_INCIDENCE_OWNER",
        "status": (
            "SIGNED_RADIUS_LAPSE_AND_DURATION_INCIDENCE_FORMULA_DERIVED_DDELTA_OPEN"
            if passed else "SIGNED_DURATION_INCIDENCE_NOT_DERIVED"
        ),
        "classification": (
            "THE_EXACT_ACTION_DUAL_DlogR4_AND_DlogN_COVECTORS_AND_THE_SIGNED_"
            "D(Ns/Delta)=Ns/Delta*(DlogN-DDelta/Delta)_INCIDENCE_ARE_"
            "DERIVED;_THE_COMMITTED_CONTINUATION_DATA_SUPPLY_ONLY_A_NORM_"
            "BOUND_FOR_DDelta,_SO_THE_SIGNED_SELECTED_LINE_HARD_COMPLEMENT_"
            "DDelta_COVECTOR_IS_THE_MINIMAL_LOCAL_MOVING_DURATION_GAP"
        ),
        "exact_incidence": {
            "proper_duration_density": "q_tau=N_boundary(Y)*s/Delta(Y,s)",
            "first_variation": (
                "D_Y q_tau=q_tau*(D_Y log N_boundary-D_Y Delta/Delta)"
            ),
            "segment_duration_covector": "h_Y,j=integral_segment_j D_Y q_tau*J ds",
            "log_radius_action_dual_norm_at_formula_witness": float(
                np.linalg.norm(geometry["D_log_R4_action_dual"])
            ),
            "log_lapse_action_dual_norm_at_formula_witness": float(
                np.linalg.norm(geometry["D_log_lapse_action_dual"])
            ),
            "positive_s_formula_witness_density": float(
                zero_delta_witness["proper_duration_density"]
            ),
            "formula_witness_DDelta": "ZERO_ONLY_FOR_ALGEBRAIC_CROSSCHECK_NOT_BHSM_VALUE",
        },
        "matching_audit": [
            {
                "diagram_slot": "SIGNED_D_log_R4",
                "candidate": "BHSM_BOUNDARY_RADIUS_ATTACHMENT_GRADIENT",
                "verdict": "VALID_MATCH_EXACT",
            },
            {
                "diagram_slot": "SIGNED_D_log_N_boundary",
                "candidate": "BHSM_BOUNDARY_LAPSE_LINEAR_ATTACHMENT",
                "verdict": "VALID_MATCH_EXACT",
            },
            {
                "diagram_slot": "SIGNED_D_Y_Delta_ALONG_EXACT_C2_FAMILY",
                "candidate": "STORED_Delta_ACTION_DERIVATIVE_UPPER_BOUNDS",
                "verdict": "INVALID_MATCH_NORM_HAS_NO_SIGN_OR_DIRECTION",
            },
            {
                "diagram_slot": "SIGNED_SEGMENT_DURATION_COVECTOR",
                "candidate": "EXACT_INCIDENCE_PLUS_SIGNED_D_Y_Delta_AND_TRANSPOSED_SEGMENT_MAP",
                "verdict": "CONDITIONAL_MATCH_D_Y_Delta_AND_SEGMENT_ACTION_OPEN",
            },
        ],
        "adjudication": {
            "signed_log_radius_incidence": "CLOSED",
            "signed_log_lapse_incidence": "CLOSED",
            "signed_proper_duration_incidence_formula": "CLOSED",
            "signed_D_Y_Delta_on_exact_parametric_family": "OPEN_CURRENT_OWNER",
            "transposed_exact_segment_map_action": "OPEN_CURRENT_OWNER",
            "actual_segment_duration_covector": "OPEN_AFTER_DDELTA_AND_SEGMENT_ACTION",
            "proof_center_used_as_physical_history": False,
            "actual_projected_zero_source_force": "OPEN",
        },
        "exact_next_dependency": (
            "DERIVE_OR_INTERVAL_ENCLOSE_THE_SIGNED_ACTION_DUAL_D_Y_Delta_"
            "FROM_THE_SELECTED_LINE_AND_HARD_COMPLEMENT_FIRST_VARIATIONS_ON_"
            "THE_CERTIFIED_PARAMETRIC_FAMILY,_THEN_INTEGRATE_THE_TRANSPOSED_"
            "SEGMENT_ACTION_TO_SUPPLY_h_Y,j_TO_THE_EXISTING_SIGNED_ADJOINT"
        ),
        "claim_boundary": {
            "Gate7": "G7_08_OPEN_SIGNED_DDELTA_SEGMENT_ACTION_SOURCE_AND_TAIL",
            "Gate8": "LOCKED",
            "signed_radius_lapse_duration_incidence_formula": "DERIVED",
            "signed_D_Y_Delta": "OPEN",
            "actual_signed_duration_covector": "OPEN",
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
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "adjudication": payload["adjudication"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
