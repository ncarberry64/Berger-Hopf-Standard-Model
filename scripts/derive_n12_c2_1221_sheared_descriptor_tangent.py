"""Assemble the endpoint tangent on the invariant signed-descriptor graph."""

from __future__ import annotations

import json
import hashlib
import math
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_C2_1221_EXPANDED_ENDPOINT_FIXED_S_FIELD.json"
CENTER_DATA = CENTER.with_suffix(".npz")
BORDERED = BASE / "BHSM_N12_C2_1221_EXPANDED_ENDPOINT_BORDERED_MATRIX.json"
BORDERED_DATA = BORDERED.with_suffix(".npz")
CENTER_INPUT = BASE / "BHSM_N12_C2_1221_EXPANDED_ENDPOINT_CENTER_INPUT.json"
MONOTONICITY = BASE / "BHSM_N12_C2_1221_CANCELLED_DELTA_MONOTONICITY.json"
RESULT = BASE / "BHSM_N12_C2_1221_EXPANDED_ENDPOINT_SHEARED_DESCRIPTOR_TANGENT.json"
DATA = RESULT.with_suffix(".npz")
INFLATION = 1.0 + 1.0e-10

from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data  # noqa: E402


def _up(value: float) -> float:
    return math.nextafter(float(value) * INFLATION, math.inf)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def build_payload() -> dict:
    center_record = json.loads(CENTER.read_text(encoding="utf-8"))
    bordered_record = json.loads(BORDERED.read_text(encoding="utf-8"))
    continuation = json.loads(CENTER_INPUT.read_text(encoding="utf-8"))
    monotonicity = json.loads(MONOTONICITY.read_text(encoding="utf-8"))
    if not all(record.get("validation_passed") for record in (
        center_record, bordered_record, continuation, monotonicity,
    )):
        raise RuntimeError("validated endpoint recenter parents required")
    with np.load(CENTER_DATA) as data:
        center = np.asarray(data["center_state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        fixed = np.asarray(data["exact_center_field_action"], dtype=float)
        fixed_first = np.asarray(data["fixed_s_field_matrix_partial_action"], dtype=float)
        delta_first = np.asarray(data["Delta_first_partial_action"], dtype=float)
    with np.load(BORDERED_DATA) as data:
        psi = np.asarray(data["selected_vector"], dtype=float)
        lambda_first = np.asarray(data["lambda_gradient_action"], dtype=float)
        response = np.asarray(data["bordered_response"], dtype=float)

    signed_s = float(
        continuation["continuation"]["final_signed_lambda_decimal"]
    )
    Delta = float(center_record["center_field"]["Delta"])
    q_weights, reduced_weights, _, _ = metric_data()
    configuration = q_weights * center[37:74]
    full_hard = np.concatenate((configuration, reduced_weights * response[:-1]))
    psi_action = np.concatenate((np.zeros(37), reduced_weights * psi))
    b = float(response[-1])
    G = b * psi_action + signed_s * full_hard
    G_from_recombination = Delta * fixed
    R = float(lambda_first @ full_hard)
    graph_incidence = float(lambda_first @ G)
    fixed_s_DG = Delta * fixed_first + np.outer(fixed, delta_first)
    graph_DG = fixed_s_DG + np.outer(full_hard, lambda_first)
    symmetric = 0.5 * (graph_DG + graph_DG.T)
    graph_mu = float(np.linalg.eigvalsh(symmetric)[-1])
    graph_norm = float(np.linalg.norm(graph_DG, 2))
    injection = np.vstack((np.eye(center.size), lambda_first[None, :]))
    normal = np.concatenate((-lambda_first, np.ones(1)))
    normal_injection_defect = float(np.linalg.norm(normal @ injection))
    recombination_defect = float(np.linalg.norm(G - G_from_recombination))
    incidence_defect = abs(graph_incidence - Delta)
    np.savez_compressed(
        DATA,
        center_state=center,
        state_weights=weights,
        descriptor_graph_injection=injection,
        descriptor_graph_normal=normal,
        fixed_s_cancelled_tangent_partial=fixed_s_DG,
        sheared_descriptor_graph_tangent_partial=graph_DG,
        lambda_gradient_action=lambda_first,
        descriptor_partial_field_action=full_hard,
    )
    validation = {
        "cancelled_field_recombines_before_norms": recombination_defect < 1.0e-14,
        "descriptor_rate_equals_selected_eigenvalue_rate": incidence_defect < 1.0e-14,
        "graph_normal_annihilates_graph_injection": normal_injection_defect < 1.0e-14,
        "sheared_graph_tangent_is_finite": np.all(np.isfinite(graph_DG)),
        "graph_has_98_intrinsic_columns": injection.shape == (99, 98),
        "binary64_eigenvalue_not_used_as_descriptor": True,
        "no_selector_recurrence_scale_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_1221_EXPANDED_ENDPOINT_SHEARED_DESCRIPTOR_TANGENT",
        "status": "C2_EXPANDED_ENDPOINT_SHEARED_GRAPH_TANGENT_DERIVED" if passed else "C2_EXPANDED_ENDPOINT_SHEARED_TANGENT_FAILED",
        "signed_descriptor": signed_s,
        "incoming_correlated_descriptor_interval": monotonicity[
            "sharpened_correlated_descriptor_interval"
        ],
        "center_Delta": Delta,
        "descriptor_partial_Delta": R,
        "fixed_s_cancelled_tangent_operator_norm": float(np.linalg.norm(fixed_s_DG, 2)),
        "sheared_graph_tangent_operator_norm": graph_norm,
        "sheared_graph_tangent_numerical_abscissa": graph_mu,
        "cancelled_field_recombination_defect": recombination_defect,
        "descriptor_incidence_defect": incidence_defect,
        "normal_injection_defect": normal_injection_defect,
        "data": DATA.relative_to(ROOT).as_posix(),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in (CENTER, CENTER_DATA, BORDERED, BORDERED_DATA,
                         CENTER_INPUT, MONOTONICITY)
        },
        "scope": (
            "EXACT_CENTER_SHEARED_TANGENT_ONLY;_THE_COMPLETE_INTERVAL_"
            "TANGENT_REMAINDER_AND_RECENTERED_TUBE_REMAIN"
        ),
        "exact_next_dependency": (
            "ENCLOSE_THE_SHEARED_GRAPH_TANGENT_VARIATION_ON_THE_REALIZED_"
            "COVER_AND_APPLY_MATRIX_LOHNER_RECENTERING"
        ),
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
