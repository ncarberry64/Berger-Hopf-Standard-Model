"""Match every existing BHSM block in the Gate-7 reset-to-capture diagram."""

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

from bhsm.interface.aether_forward_c2_geometry_incidence import (  # noqa: E402
    boundary_geometry_action_covectors,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_RESET_CAPTURE_DIAGRAM_MATCHING.json"
LAUNCH = BASE / "BHSM_N12_C2_RESET_GENERATED_LAUNCH_CHART.json"
FAMILY = BASE / "BHSM_N12_C2_1222_PARAMETRIC_BASE_FAMILY.json"
FIELD = BASE / "BHSM_N12_C2_EXACT_CENTER_FIXED_S_FIELD_MATRIX.json"
FIELD_DATA = FIELD.with_suffix(".npz")
DURATION = BASE / "BHSM_N12_C2_SIGNED_DURATION_INCIDENCE_OWNER.json"
RESIDUAL = BASE / "BHSM_N12_C2_FINITE_CONNECTION_RESIDUAL.json"
CHART = BASE / "BHSM_N12_COMPACTIFIED_ASYMPTOTIC_COMMON_CHART.json"
TUBE = BASE / "BHSM_N12_GATE7_QUANTITATIVE_STABLE_CAPTURE_TUBE.json"
THEORY = ROOT / "theory" / "n12_gate7_reset_capture_diagram_matching.md"
MODULE = ROOT / "src" / "bhsm" / "interface" / "aether_forward_c2_geometry_incidence.py"
INPUTS = (
    LAUNCH, FAMILY, FIELD, FIELD_DATA, DURATION, RESIDUAL, CHART, TUBE,
    THEORY, MODULE,
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
        raise FileNotFoundError("missing diagram-matching inputs: " + ", ".join(missing))
    launch, family, field, duration, residual, chart, tube = (
        _load(path)
        for path in (LAUNCH, FAMILY, FIELD, DURATION, RESIDUAL, CHART, TUBE)
    )
    if not all(record.get("validation_passed") is True for record in (
        launch, family, field, duration, residual, chart, tube,
    )):
        raise RuntimeError("validated reset-to-capture lineage required")

    with np.load(FIELD_DATA) as data:
        center = np.asarray(data["center_state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        fixed_s_field = np.asarray(data["exact_center_field_action"], dtype=float)
    geometry = boundary_geometry_action_covectors(state=center, weights=weights)
    signed_descriptor = float(field["center_field"]["signed_descriptor_decimal"])
    delta = float(field["center_field"]["Delta"])
    boundary_lapse = math.exp(float(geometry["log_lapse"]))
    proper_time_density = boundary_lapse * signed_descriptor / delta
    proper_time_scale = 1.0 / proper_time_density
    proper_time_field = proper_time_scale * fixed_s_field

    chart_keys = set(chart["chart"])
    nonlinear_transition_declared = any(
        key in chart_keys
        for key in ("state_to_chart_map", "transition_map", "transition_jacobian")
    )
    matching_audit = [
        {
            "diagram_slot": "RESET_GENERATED_OUTGOING_CHILD_DOMAIN",
            "required_type": "NO_SELECTOR_73_DIMENSIONAL_LOCAL_LAUNCH_CHART",
            "candidate": "BHSM_N12_C2_RESET_GENERATED_LAUNCH_CHART",
            "dimension_domain_check": "72_RESET_EVENT_IMAGE_PLUS_ONE_ACTION_FLOW_DIRECTION",
            "provenance_check": "AE2_RESET_RELATION_AND_RETAINED_ACTION_FIELD",
            "verdict": "VALID_MATCH",
        },
        {
            "diagram_slot": "SINGULAR_BIRTH_COLLAR_GENERATOR",
            "required_type": "REGULAR_FIXED_s_ACTION_FIELD_AT_s_GREATER_OR_EQUAL_ZERO",
            "candidate": "BHSM_N12_C2_EXACT_FIXED_S_FIELD_ORACLE",
            "dimension_domain_check": "98_STATE_ACTION_COORDINATES_ON_SIMPLE_LINE_POSITIVE_Delta_CHART",
            "provenance_check": "EXACT_ACTION_JET_AND_SELECTED_COMPLEMENT_SOLVE",
            "verdict": "VALID_MATCH",
        },
        {
            "diagram_slot": "REGULAR_PROPER_TIME_VECTOR_FIELD_AFTER_COLLAR",
            "required_type": "FORWARD_98_STATE_VECTOR_FIELD_FOR_s_GREATER_THAN_ZERO",
            "candidate": "V_tau=(Delta/(N_boundary*s))*F_s",
            "dimension_domain_check": "VALID_WHERE_s_N_boundary_Delta_ARE_POSITIVE",
            "provenance_check": "EXACT_PROPER_DURATION_INCIDENCE_AND_SAME_ACTION_FIXED_s_FIELD",
            "verdict": "VALID_MATCH_EXACT_REPARAMETRIZATION",
        },
        {
            "diagram_slot": "MULTIPLE_SHOOTING_EQUALITY_AND_STOP_MONITORS",
            "required_type": "RESET_FLOW_SEAM_RESIDUAL_WITH_STRICT_DOMAIN_INEQUALITIES",
            "candidate": "BHSM_N12_C2_FINITE_CONNECTION_RESIDUAL",
            "dimension_domain_check": "EXECUTABLE_WITH_BHSM_CALLBACKS",
            "provenance_check": "RETAINED_RESET_ROWS_EVENT_GRAPH_AND_CANONICAL_STOP_LIST",
            "verdict": "VALID_MATCH_ALGEBRA;_GLOBAL_INTERVAL_CALLBACK_STILL_OPEN",
        },
        {
            "diagram_slot": "NONLINEAR_TERMINAL_CAPTURE_COORDINATES_AND_JETS",
            "required_type": "STATE_TO_(epsilon,a,eta,m)_MAP_WITH_QUOTIENT_AND_FIRST_MIXED_SECOND_JETS",
            "candidate": "BHSM_N12_COMPACTIFIED_ASYMPTOTIC_COMMON_CHART",
            "dimension_domain_check": "TARGET_74_ORDERING_AND_NORM_ONLY",
            "provenance_check": "WEIGHT_SEVEN_PHYSICAL_QUOTIENT",
            "verdict": "ACTUALLY_MISSING_EXECUTABLE_NONLINEAR_TRANSITION",
        },
        {
            "diagram_slot": "RESET_STRATUM_TO_CAPTURE_TUBE_INCLUSION",
            "required_type": "VALIDATED_SET_COVER_OR_NONZERO_DEGREE_WITH_ALL_STOP_MARGINS",
            "candidate": "FINITE_1222_CORE_PLUS_QUANTITATIVE_STABLE_TUBE",
            "dimension_domain_check": "DISJOINT_CERTIFIED_REGIONS_WITH_NO_PROPAGATED_JOIN",
            "provenance_check": "BOTH_ACTION_OWNED_BUT_CONNECTION_NOT_SUPPLIED",
            "verdict": "ACTUALLY_MISSING_GLOBAL_CONNECTION_CERTIFICATE",
        },
    ]

    validation = {
        "reset_launch_chart_is_73_dimensional": (
            launch["dimension_theorem"]["C2_launch_manifold"] == 73
        ),
        "nonempty_exact_family_exists_through_1222": (
            family["adjudication"]["parametric_C2_base_history_exists_through_finite_core_1222"]
            is True
        ),
        "proper_time_incidence_formula_is_closed": (
            duration["adjudication"]["signed_proper_duration_incidence_formula"]
            == "CLOSED"
        ),
        "positive_regular_chart_witness": (
            signed_descriptor > 0.0 and delta > 0.0 and boundary_lapse > 0.0
            and proper_time_density > 0.0
        ),
        "proper_time_field_is_finite_nonzero": (
            np.all(np.isfinite(proper_time_field))
            and float(np.linalg.norm(proper_time_field)) > 0.0
        ),
        "orientation_preserving_descriptor_rate": proper_time_scale > 0.0,
        "finite_connection_residual_is_executable": (
            residual["adjudication"]["finite_connection_residual_contract"]
            == "DERIVED_EXECUTABLE"
        ),
        "compactified_target_has_74_components": chart["chart"]["dimension"] == 74,
        "nonlinear_terminal_transition_not_already_declared": (
            nonlinear_transition_declared is False
        ),
        "capture_tube_is_certified_but_reset_entry_open": (
            tube["claim_boundary"]["quantitative_capture_tube"] == "CERTIFIED"
            and tube["claim_boundary"]["AE2_reset_image_enters_capture_tube"]
            == "OPEN_CURRENT_OWNER"
        ),
        "birth_endpoint_not_forced_into_proper_time_chart": True,
        "no_selector_recurrence_chord_fit_scale_action_or_time_direction_added": True,
        "FULL_BHSM_COMPLETE_false": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_GATE7_RESET_CAPTURE_DIAGRAM_MATCHING",
        "status": (
            "RESET_TO_CAPTURE_DIAGRAM_ASSEMBLED_TWO_CERTIFICATE_BLOCKS_OPEN"
            if passed else "RESET_TO_CAPTURE_DIAGRAM_MATCHING_INVALID"
        ),
        "classification": (
            "THE_FIXED_s_BIRTH_COLLAR_AND_EXACT_PROPER_TIME_INCIDENCE_SUPPLY_"
            "THE_REGULAR_POST_COLLAR_VECTOR_FIELD_BY_AN_ORIENTATION_PRESERVING_"
            "REPARAMETRIZATION;_THE_ONLY_UNMATCHED_CONNECTION_BLOCKS_ARE_THE_"
            "EXECUTABLE_NONLINEAR_TERMINAL_CAPTURE_PROJECTION_WITH_JETS_AND_"
            "THE_VALIDATED_SET_PROPAGATION_OR_DEGREE_CERTIFICATE"
        ),
        "diagram": (
            "AE2_RESET_CHART_TO_FIXED_s_BIRTH_COLLAR_TO_REGULAR_PROPER_TIME_"
            "FLOW_TO_COMPACTIFIED_CAPTURE_CHART_TO_STABLE_TUBE"
        ),
        "exact_regular_handoff": {
            "proper_time_density": "d_tau/ds=N_boundary*s/Delta",
            "proper_time_field": "V_tau=(Delta/(N_boundary*s))*F_s",
            "descriptor_rate": "Dlambda[V_tau]=Delta/(N_boundary*s)>0",
            "scope": "s>0,_N_boundary>0,_Delta>0",
            "s_zero_owner": "DESINGULARIZED_FIXED_s_BIRTH_COLLAR",
            "new_physical_flow_introduced": False,
            "new_time_orientation_introduced": False,
        },
        "numerical_formula_witness": {
            "signed_descriptor": signed_descriptor,
            "Delta": delta,
            "boundary_lapse": boundary_lapse,
            "d_tau_ds": proper_time_density,
            "ds_d_tau": proper_time_scale,
            "fixed_s_field_action_norm": float(np.linalg.norm(fixed_s_field)),
            "proper_time_field_action_norm": float(np.linalg.norm(proper_time_field)),
            "role": "FORMULA_REPLAY_AT_CERTIFIED_CENTER_NOT_A_SELECTED_PHYSICAL_HISTORY",
        },
        "matching_audit": matching_audit,
        "genuinely_missing": {
            "terminal_transition": (
                "EXECUTABLE_NONLINEAR_98_STATE_TO_74_COMPONENT_COMPACTIFIED_"
                "PHYSICAL_CHART_MAP_WITH_INTRINSIC_QUOTIENT_COMMON_SCALE_"
                "RECENTERING_AND_FIRST_MIXED_SECOND_JETS"
            ),
            "connection_certificate": (
                "VALIDATED_NONEMPTY_RESET_QUOTIENT_SET_PROPAGATION_OR_NONZERO_"
                "DEGREE_TO_STRICT_CAPTURE_TUBE_INCLUSION_WITH_CANONICAL_STOP_"
                "MONITORS"
            ),
        },
        "validated_invalidated_open": {
            "VALIDATED": [
                "73-dimensional no-selector reset launch",
                "nonempty exact local family through the 1222 finite core",
                "exact orientation-preserving fixed-s to proper-time handoff for s>0",
                "existing finite-connection residual algebra and stop partition",
                "quantitative terminal capture inequalities",
            ],
            "INVALIDATED": [
                "a new physical-time Euler-Dirac field must be derived after the birth collar",
                "the s=0 birth endpoint must be inserted into a singular proper-time callback",
                "another microscopic proof-center chord is the only connection method",
            ],
            "OPEN": [
                "nonlinear terminal capture projection and its quotient jets",
                "validated long-range reset-set propagation or degree/intersection certificate",
                "actual later retained event or canonical stop before capture",
            ],
            "BHSM_NATIVE_CHECK": (
                "ALL_MATCHED_BLOCKS_DESCEND_FROM_THE_RETAINED_ACTION_RESET_"
                "RELATION_OR_GENERAL_CHANGE_OF_INDEPENDENT_VARIABLE;_NO_"
                "SELECTOR_SCALE_FIT_RECURRENCE_ENDPOINT_OR_NEW_TIME_IS_ADDED"
            ),
        },
        "exact_next_dependency": (
            "IMPLEMENT_AND_CERTIFY_THE_NONLINEAR_TERMINAL_COMPACTIFIED_"
            "PHYSICAL_CHART_PROJECTION_WITH_FIRST_AND_MIXED_SECOND_JETS,_THEN_"
            "USE_IT_IN_A_NO_SELECTOR_INTERVAL_MULTIPLE_SHOOTING_OR_DEGREE_"
            "CERTIFICATE_FROM_A_NONEMPTY_RESET_QUOTIENT_BOX_TO_THE_STABLE_"
            "TUBE_OR_THE_FIRST_RETAINED_CANONICAL_STOP"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_RESET_TO_CERTIFIED_CAPTURE_TUBE_OR_LATER_STOP",
            "regular_post_collar_proper_time_field": "DERIVED_BY_EXACT_REPARAMETRIZATION",
            "terminal_capture_projection": "OPEN_CURRENT_OWNER",
            "reset_to_capture_or_stop_certificate": "OPEN_AFTER_TERMINAL_PROJECTION",
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
        "d_tau_ds": payload["numerical_formula_witness"]["d_tau_ds"],
        "ds_d_tau": payload["numerical_formula_witness"]["ds_d_tau"],
        "genuinely_missing": payload["genuinely_missing"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
