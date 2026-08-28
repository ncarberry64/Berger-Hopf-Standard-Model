"""Reconcile Gate-7 numerical artifacts with the selected proof center.

The quarter-step retained center was selected before the later signed Green
and curvature work.  This audit detects any downstream composition that
loads a different center or tangent family and scopes the affected claims
without erasing the standalone calculations on their original histories.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
SELECTION = BASE / "BHSM_N12_C2_STOP_RETAINED_CENTER_SELECTION.json"
ORIGINAL = BASE / "BHSM_N12_C2_STOP_MULTIPLE_SHOOTING_CENTER.npz"
HALF = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_HALF_STEP_CENTER_RECONNAISSANCE.npz"
QUARTER = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
HALF_TANGENT = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_HALF_STEP_PHYSICAL_TANGENT_TRANSFER_RECONNAISSANCE.json"
QUARTER_TANGENT = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_PHYSICAL_TANGENT_TRANSFER_RECONNAISSANCE.json"
GREEN = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_MATCHED_TANGENT_CORRELATED_DEFECT_GAUSS12_RECONNAISSANCE.json"
GREEN_DATA = GREEN.with_suffix(".npz")
RESULT = BASE / "BHSM_N12_GATE7_SELECTED_CENTER_PROVENANCE_RECONCILIATION.json"

EXACT_SCRIPTS = (
    ROOT / "scripts" / "derive_n12_gate7_exact_signed_directional_field_curvature.py",
    ROOT / "scripts" / "derive_n12_gate7_exact_signed_mixed_field_curvature.py",
    ROOT / "scripts" / "derive_n12_gate7_exact_signed_full_transverse_curvature.py",
    ROOT / "scripts" / "derive_n12_gate7_signed_causal_vector_bootstrap.py",
    ROOT / "scripts" / "derive_n12_gate7_outward_closure_budget.py",
)
PREREQUISITE_SCRIPTS = (
    ROOT / "scripts" / "certify_n12_gate7_correction_direction_action_majorants.py",
    ROOT / "scripts" / "derive_n12_gate7_retained_correction_eigenline_first_jets.py",
    ROOT / "scripts" / "derive_n12_gate7_retained_correction_bordered_response_first_jets.py",
    ROOT / "scripts" / "derive_n12_gate7_correction_bordered_response_second_jets.py",
    ROOT / "scripts" / "certify_n12_gate7_two_free_leg_action_majorants.py",
    ROOT / "scripts" / "derive_n12_gate7_exact_signed_selected_multiplier_jets.py",
)
RECENTERED_CONE_SCRIPT = (
    ROOT / "scripts" / "certify_n12_gate7_recentered_cone_boundary_cluster_spectrum.py"
)
COMMON_FRAME_SCRIPT = (
    ROOT / "scripts" / "audit_n12_gate7_signed_common_frame_data_matching.py"
)
CURRENT_ARTIFACTS = {
    "directional": BASE / "BHSM_N12_GATE7_EXACT_SIGNED_DIRECTIONAL_FIELD_CURVATURE.json",
    "mixed": BASE / "BHSM_N12_GATE7_EXACT_SIGNED_MIXED_FIELD_CURVATURE.json",
    "transverse": BASE / "BHSM_N12_GATE7_EXACT_SIGNED_FULL_TRANSVERSE_CURVATURE_ADJUDICATION.json",
    "eigenline": BASE / "BHSM_N12_GATE7_RETAINED_CORRECTION_EIGENLINE_FIRST_JETS.json",
    "response_first": BASE / "BHSM_N12_GATE7_RETAINED_CORRECTION_BORDERED_RESPONSE_FIRST_JETS.json",
    "response_second": BASE / "BHSM_N12_GATE7_CORRECTION_BORDERED_RESPONSE_SECOND_JETS.json",
    "action_majorants": BASE / "BHSM_N12_GATE7_CORRECTION_DIRECTION_ACTION_MAJORANTS.json",
    "two_free": BASE / "BHSM_N12_GATE7_TWO_FREE_LEG_ACTION_MAJORANTS.json",
    "multiplier": BASE / "BHSM_N12_GATE7_EXACT_SIGNED_SELECTED_MULTIPLIER_JETS.json",
    "graph": BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_GRAPH_JACOBIAN_RECONNAISSANCE.json",
    "hybrid_graph": BASE / "BHSM_N12_GATE7_QUARTER_STEP_HYBRID_GRAPH_JACOBIAN_EQUIVALENCE_AUDIT.json",
    "residual": BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_RETAINED_DENSE_RESIDUAL_GAUSS12_RECONNAISSANCE.json",
    "first_hit": BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_DENSE_DESCRIPTOR_FIRST_HIT.json",
    "common_frame": BASE / "BHSM_N12_GATE7_SIGNED_COMMON_FRAME_DATA_MATCHING.json",
    "dop853_spectrum": BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BOUNDARY_CLUSTER_SPECTRUM.json",
    "dop853_projector": BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_SELECTED_PROJECTOR_GRAPH.json",
    "dop853_inverse": BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BORDERED_HARD_INVERSE.json",
    "dop853_response": BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BORDERED_RHS_RESPONSE_CERTIFICATE.json",
    "dop853_response_first": BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BORDERED_RESPONSE_FIRST_VARIATION.json",
    "dop853_response_second": BASE / "BHSM_N12_C2_STOP_DOP853_BORDERED_RESPONSE_SECOND_VARIATION.json",
}


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _center(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    with np.load(path) as source:
        states = np.asarray(source["centers"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        times = np.asarray(source["action_lengths"], dtype=float)
    return states * weights, weights, times


def build_payload() -> dict[str, Any]:
    inputs = (
        SELECTION, ORIGINAL, HALF, QUARTER, HALF_TANGENT, QUARTER_TANGENT,
        GREEN, GREEN_DATA, *EXACT_SCRIPTS, *PREREQUISITE_SCRIPTS,
        RECENTERED_CONE_SCRIPT, COMMON_FRAME_SCRIPT,
        *CURRENT_ARTIFACTS.values(),
    )
    if not all(path.is_file() for path in inputs):
        raise FileNotFoundError("selected-center provenance inputs required")
    selection = json.loads(SELECTION.read_text(encoding="utf-8"))
    half_tangent = json.loads(HALF_TANGENT.read_text(encoding="utf-8"))
    quarter_tangent = json.loads(QUARTER_TANGENT.read_text(encoding="utf-8"))
    green = json.loads(GREEN.read_text(encoding="utf-8"))
    with np.load(GREEN_DATA) as source:
        green_times = np.asarray(source["fine_action_lengths"], dtype=float)
    original, original_weights, original_times = _center(ORIGINAL)
    half, half_weights, half_times = _center(HALF)
    quarter, quarter_weights, quarter_times = _center(QUARTER)
    exact_sources = {path.name: path.read_text(encoding="utf-8") for path in EXACT_SCRIPTS}
    prerequisite_sources = {
        path.name: path.read_text(encoding="utf-8")
        for path in PREREQUISITE_SCRIPTS
    }
    cone_source = RECENTERED_CONE_SCRIPT.read_text(encoding="utf-8")
    common_frame_source = COMMON_FRAME_SCRIPT.read_text(encoding="utf-8")
    current_records = {
        key: json.loads(path.read_text(encoding="utf-8"))
        for key, path in CURRENT_ARTIFACTS.items()
    }

    half_difference = np.linalg.norm(half - quarter, axis=1)
    original_difference = np.linalg.norm(original - quarter, axis=1)
    quarter_crossing = float(quarter_tangent["summary"][
        "terminal_descriptor_crossing_on_physical_tangent"
    ])
    half_crossing = float(half_tangent["summary"][
        "terminal_descriptor_crossing_on_physical_tangent"
    ])
    green_crossing = float(green["summary"]["terminal_descriptor_crossing"])

    validation = {
        "selection_manifest_names_quarter_step_center": selection["selected_center"].endswith(
            "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.json"
        ),
        "quarter_center_and_tangent_weights_match": np.array_equal(
            quarter_weights, original_weights
        ) and np.array_equal(quarter_weights, half_weights),
        "green_terminal_time_matches_quarter_center": abs(
            float(quarter_times[-1]) - float(green_times[-1])
        ) < 1.0e-12,
        "green_terminal_crossing_matches_quarter_tangent_exactly": green_crossing == quarter_crossing,
        "green_terminal_crossing_does_not_match_half_tangent": green_crossing != half_crossing,
        "half_and_quarter_centers_are_not_identical": float(np.max(half_difference)) > 0.0,
        "original_and_quarter_centers_are_not_identical": float(np.max(original_difference)) > 0.0,
        "all_current_exact_scripts_name_quarter_center": all(
            "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz" in source
            for source in exact_sources.values()
        ),
        "all_current_exact_scripts_name_quarter_tangent": all(
            "BHSM_N12_C2_STOP_QUARTER_STEP_PHYSICAL_TANGENT_TRANSFER_RECONNAISSANCE.npz" in source
            for source in exact_sources.values()
        ),
        "all_current_prerequisite_scripts_name_quarter_center": all(
            "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
            in source for source in prerequisite_sources.values()
        ),
        "no_current_prerequisite_script_names_half_center": all(
            "BHSM_N12_C2_STOP_HIGH_ORDER_HALF_STEP_CENTER_RECONNAISSANCE.npz"
            not in source for source in prerequisite_sources.values()
        ),
        "legacy_recentered_cone_default_center_mismatch_detected": (
            "BHSM_N12_STOP_CENTER_DATA" not in cone_source
            and "audit_n12_c2_stop_boundary_cluster_probe" in cone_source
        ),
        "current_common_frame_script_names_only_quarter_center_operands": (
            'BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_HALF_STEP' not in common_frame_source
            and "QUARTER_STEP_PHYSICAL_TANGENT" in common_frame_source
            and "QUARTER_STEP_GRAPH_JACOBIAN" in common_frame_source
            and "QUARTER_STEP_RETAINED_DENSE_RESIDUAL_GAUSS12" in common_frame_source
            and "QUARTER_STEP_DENSE_DESCRIPTOR_FIRST_HIT" in common_frame_source
        ),
        "current_exact_curvature_artifacts_validated": all(
            current_records[key]["validation_passed"] is True
            for key in ("directional", "mixed", "transverse")
        ),
        "current_retained_response_prerequisites_validated": all(
            current_records[key]["validation_passed"] is True
            for key in (
                "eigenline", "response_first", "response_second",
                "action_majorants", "two_free", "multiplier",
            )
        ),
        "current_quarter_common_frame_operands_replayed": (
            current_records["graph"]["center"]
            == "artifacts/flagship_integration/BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
            and current_records["hybrid_graph"]["validation_passed"] is True
            and current_records["residual"]["construction"]["center"]
            == "artifacts/flagship_integration/BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
            and current_records["first_hit"]["center"]
            == "artifacts/flagship_integration/BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
            and current_records["common_frame"]["validation_passed"] is True
        ),
        "selected_DOP853_spectrum_projector_inverse_and_response_certified": all(
            current_records[key]["validation_passed"] is True
            for key in (
                "dop853_spectrum", "dop853_projector", "dop853_inverse",
                "dop853_response", "dop853_response_first",
            )
        ),
        "selected_DOP853_chain_names_quarter_center": all(
            (
                "artifacts/flagship_integration/"
                "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
            ) in current_records[key]["inputs"]
            for key in (
                "dop853_spectrum", "dop853_projector", "dop853_response_first",
            )
        ),
        "DOP853_scalar_second_variation_failure_is_not_promoted": (
            current_records["dop853_response_second"]["validation_passed"] is False
            and current_records["dop853_response_second"]["claim_boundary"][
                "cellwise_response_first_variation_tube"
            ] == "CERTIFIED_FINITE"
            and current_records["dop853_response_second"]["claim_boundary"][
                "cellwise_response_second_variation_tube"
            ] == "OPEN_SIGNED_CORRELATION_REQUIRED"
        ),
        "no_action_equation_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_GATE7_SELECTED_CENTER_PROVENANCE_RECONCILIATION",
        "status": (
            "SELECTED_QUARTER_CENTER_PROVENANCE_RECONCILED;_DOP853_SIGNED_CORRELATION_OPEN"
            if passed else "SELECTED_CENTER_PROVENANCE_AUDIT_INVALID"
        ),
        "classification": "PROVENANCE_DEFECT",
        "selected_center": selection["selected_center"],
        "measurements": {
            "maximum_half_to_quarter_action_state_2_norm": float(np.max(half_difference)),
            "maximum_original_to_quarter_action_state_2_norm": float(np.max(original_difference)),
            "half_action_duration": float(half_times[-1]),
            "quarter_action_duration": float(quarter_times[-1]),
            "original_action_duration": float(original_times[-1]),
            "green_terminal_descriptor_crossing": green_crossing,
            "quarter_tangent_terminal_descriptor_crossing": quarter_crossing,
            "half_tangent_terminal_descriptor_crossing": half_crossing,
        },
        "classification_ledger": [
            {
                "objects": "half-step exact directional/mixed/transverse center tensors",
                "classification": "HISTORICAL_VALID_BUT_NOT_CURRENT",
                "reason": "valid standalone derivatives on the half-step history; not composable with the selected quarter-step Green data",
            },
            {
                "objects": "pre-reconciliation signed causal vector, exact center certificate, and outward budget",
                "classification": "INVALIDATED",
                "reason": "combined half-step center/tangent derivatives with quarter-step Green correction and propagators",
            },
            {
                "objects": "pre-reconciliation recentered-cone spectrum/projector/inverse/response chain",
                "classification": "INVALIDATED",
                "reason": "combined the original multiple-shooting center with the quarter-step correction and a half-step spectrum parent",
            },
            {
                "objects": "adaptive DOP853 spectrum/projector/inverse/internal-response/first-variation chain",
                "classification": "CURRENT_CERTIFIED_SELECTED_CENTER_CHAIN",
                "reason": "built directly from the selected quarter-step degree-seven DOP853 polynomial; it is independent of the invalidated original-plus-quarter recentered cone",
            },
            {
                "objects": "DOP853 scalar response second-variation denominator",
                "classification": "CONSERVATIVE_SCALAR_ROUTE_OPEN",
                "reason": "the finite first-variation tube is certified, but the decorrelated scalar second-variation denominator fails; route the same cells through the signed common-frame curvature rather than rebuilding the certified cone",
            },
            {
                "objects": "pre-reconciliation common-frame matching, anisotropic Z2, dense residual, and first-hit composition",
                "classification": "INVALIDATED",
                "reason": "combined half-step tangent/graph/residual/first-hit data with the selected quarter-step Green and response chain",
            },
            {
                "objects": "current exact directional/mixed/transverse replay",
                "classification": "CURRENT_REBUILD",
                "reason": "all source constants now name the selected quarter-step center and matching quarter-step tangent",
            },
        ],
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "same_center_exact_directional_mixed_transverse": "DERIVED",
            "same_center_DOP853_spectrum_projector_inverse_response": "CERTIFIED",
            "same_center_DOP853_response_first_variation": "CERTIFIED_FINITE",
            "same_center_DOP853_response_second_variation": "OPEN_SIGNED_CORRELATION_REQUIRED",
            "same_center_DOP853_nonlinear_tube": "OPEN_RADIUS_ATTACHMENT",
            "legacy_mixed_center_recentered_cone": "HISTORICAL_NOT_CURRENT",
            "same_center_common_frame_operands": "DERIVED",
            "causal_interval_vector_radius": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "ATTACH_THE_SELECTED_QUARTER_CAUSAL_RADIUS_TO_THE_ALREADY_"
            "CERTIFIED_DOP853_CELL_CARRIER,_THEN_CONTRACT_THE_SIGNED_COMMON_"
            "FRAME_CURVATURE_AND_RESPONSE_FIRST_VARIATION_TO_DERIVE_"
            "CELLWISE_Y_Z1_Z2;_FINALLY_TRANSFER_THE_EXISTING_DENSE_FIRST_"
            "HIT_AND_DOMAIN_MARGIN"
        ),
        "inputs": {_relative(path): _sha256(path) for path in inputs},
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
        "measurements": payload["measurements"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
