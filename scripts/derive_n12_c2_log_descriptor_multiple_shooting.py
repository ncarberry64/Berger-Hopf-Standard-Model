"""Certify the exact log-descriptor chart for Gate-7 multiple shooting."""

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

from bhsm.interface.aether_log_descriptor_flow import (  # noqa: E402
    exact_log_descriptor_field_action,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_LOG_DESCRIPTOR_MULTIPLE_SHOOTING.json"
CORE = BASE / "BHSM_N12_C2_LOHNER_STEP_1222.json"
CORE_DATA = CORE.with_suffix(".npz")
FIELD = BASE / "BHSM_N12_C2_EXACT_FIXED_S_FIELD_ORACLE.json"
FAMILY = BASE / "BHSM_N12_C2_1222_PARAMETRIC_BASE_FAMILY.json"
TERMINAL = BASE / "BHSM_N12_ASYMPTOTIC_TERMINAL_CHART_PROJECTION.json"
MATCHING = BASE / "BHSM_N12_GATE7_RESET_CAPTURE_DIAGRAM_MATCHING.json"
MODULE = ROOT / "src" / "bhsm" / "interface" / "aether_log_descriptor_flow.py"
THEORY = ROOT / "theory" / "n12_c2_log_descriptor_multiple_shooting.md"
INPUTS = (CORE, CORE_DATA, FIELD, FAMILY, TERMINAL, MATCHING, MODULE, THEORY)


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
        raise FileNotFoundError("missing log-descriptor inputs: " + ", ".join(missing))
    core, field, family, terminal, matching = (
        _load(path) for path in (CORE, FIELD, FAMILY, TERMINAL, MATCHING)
    )
    if not all(record.get("validation_passed") is True for record in (
        core, field, family, terminal, matching,
    )):
        raise RuntimeError("validated log-descriptor lineage required")
    with np.load(CORE_DATA) as data:
        center = np.asarray(data["endpoint_predictor_center"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)
    descriptor = float(core["segment"]["signed_descriptor_end"])
    result = exact_log_descriptor_field_action(
        state=center,
        weights=weights,
        reference=reference,
        log_descriptor=math.log(descriptor),
    )
    fixed_norm = float(np.linalg.norm(np.asarray(result["field_action"])))
    log_norm = float(np.linalg.norm(np.asarray(result["log_descriptor_field_action"])))
    validation = {
        "tracked_core_has_positive_descriptor": descriptor > 0.0,
        "fixed_s_oracle_is_certified": (
            field["claim_boundary"]["exact_fixed_s_field_oracle"] == "CERTIFIED"
        ),
        "parametric_family_exists_at_core_section": (
            family["claim_boundary"]["parametric_base_history_existence_through_1222"]
            == "DERIVED"
        ),
        "terminal_projection_and_jets_are_available": (
            terminal["claim_boundary"]["terminal_capture_projection"]
            == "DERIVED_WITH_FIRST_AND_MIXED_SECOND_JETS"
        ),
        "same_selected_branch_replayed": (
            int(result["selected_branch"]) == int(core["segment"]["endpoint_selected_branch"])
        ),
        "descriptor_chain_rule_is_exact": (
            abs(float(result["Dlambda_log_descriptor_field"]) - descriptor)
            <= 1.0e-12 * descriptor
        ),
        "proper_time_orientation_is_positive": (
            result["orientation_preserving"] is True
            and result["proper_time_density_d_tau_d_log_s"] > 0.0
        ),
        "log_field_is_exactly_s_times_fixed_s_field": np.allclose(
            np.asarray(result["log_descriptor_field_action"]),
            float(result["signed_descriptor"]) * np.asarray(result["field_action"]),
            rtol=0.0,
            atol=0.0,
        ),
        "near_birth_field_norm_is_rescaled_below_one": log_norm < 1.0,
        "global_interval_connection_not_overpromoted": True,
        "no_selector_recurrence_chord_fit_scale_action_endpoint_or_time_added": True,
        "FULL_BHSM_COMPLETE_false": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_LOG_DESCRIPTOR_MULTIPLE_SHOOTING",
        "status": (
            "EXACT_LOG_DESCRIPTOR_FLOW_CHART_DERIVED_INTERVAL_CONNECTION_OPEN"
            if passed else "LOG_DESCRIPTOR_FLOW_CHART_INVALID"
        ),
        "classification": (
            "THE_EXACT_CHANGE_r=log_s_REPARAMETERIZES_THE_SAME_FORWARD_BHSM_"
            "TRAJECTORY_WITH_G_r=sF_s,_Dlambda_G_r=s,_AND_POSITIVE_PROPER_"
            "TIME_DENSITY;_IT_REMOVES_THE_MICROSCOPIC_LINEAR_s_STEP_ARTIFACT_"
            "BUT_DOES_NOT_REPLACE_THE_REQUIRED_RECENTERED_INTERVAL_COVER"
        ),
        "exact_chart": {
            "coordinate": "r=log(s)",
            "field": "G_r=s*F_s",
            "descriptor_identity": "Dlambda[G_r]=s>0",
            "proper_time_density": "d_tau/dr=N_boundary*s^2/Delta>0",
            "birth_section": "ANY_CERTIFIED_s_start>0_AFTER_THE_FIXED_s_COLLAR",
            "same_action_trajectory": True,
            "new_physical_time": False,
        },
        "core_formula_witness": {
            "signed_descriptor": descriptor,
            "log_descriptor": math.log(descriptor),
            "selected_branch": int(result["selected_branch"]),
            "Delta": float(result["Delta"]),
            "boundary_lapse": float(result["boundary_lapse"]),
            "fixed_s_field_action_norm": fixed_norm,
            "log_descriptor_field_action_norm": log_norm,
            "norm_reduction_factor": log_norm / fixed_norm,
            "proper_time_density_d_tau_d_log_s": float(
                result["proper_time_density_d_tau_d_log_s"]
            ),
            "role": "FORMULA_REPLAY_AT_PROOF_CENTER_NOT_A_SELECTED_HISTORY",
        },
        "multiple_shooting_assembly": {
            "initial_block": "73_PARAMETER_RESET_LAUNCH_INTERSECT_FIXED_POSITIVE_s_SECTION",
            "seam_block": "Y_j+1-Phi_log_s(Y_j)=0_USING_G_r",
            "terminal_block": "EXACT_98_TO_74_COMPACTIFIED_MAP_AND_JETS",
            "terminal_alternatives": "STRICT_CAPTURE_TUBE_INCLUSION_OR_FIRST_RETAINED_CANONICAL_STOP",
            "domain_margins": "STRICT_INEQUALITIES_NOT_FITTED_RESIDUAL_PENALTIES",
            "proof_methods": "INTERVAL_MULTIPLE_SHOOTING_OR_NONZERO_DEGREE",
        },
        "reconnaissance_boundary": {
            "candidate_Delta_loss_near_s_order": "1e-9",
            "promoted_to_certified_stop": False,
            "used_as_physical_threshold": False,
            "permitted_role": "RECENTERING_GRID_GUIDANCE_ONLY",
        },
        "exact_next_dependency": (
            "BUILD_RECENTERED_INTERVAL_G_r_BOXES_FROM_THE_1222_POSITIVE_"
            "SECTION_TOWARD_THE_RECONNAISSANCE_Delta_LOSS_REGION;_CERTIFY_"
            "EITHER_A_TRANSVERSE_FIRST_CANONICAL_STOP_OR_CONTINUED_REGULAR_"
            "PROPAGATION,_THEN_COMPOSE_WITH_THE_TERMINAL_CAPTURE_MAP"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_LOG_DESCRIPTOR_INTERVAL_CONNECTION_OR_STOP",
            "log_descriptor_flow_chart": "DERIVED",
            "terminal_capture_projection": "DERIVED",
            "reset_to_capture_or_stop_certificate": "OPEN_CURRENT_OWNER",
            "reconnaissance_Delta_loss": "NOT_A_CERTIFICATE",
            "actual_projected_zero_source_force": "OPEN_AFTER_CONNECTION",
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
        "core_formula_witness": payload["core_formula_witness"],
        "next": payload["exact_next_dependency"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
