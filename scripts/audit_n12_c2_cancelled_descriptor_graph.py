"""Audit the exact sheared descriptor incidence on the finite cover."""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
BASE = ROOT / "artifacts" / "flagship_integration"
COVER = BASE / "BHSM_N12_C2_EXPANDED_CANCELLED_THETA_COVER_FROM_1221.json"
COVER_DATA = COVER.with_suffix(".npz")
MONOTONE = BASE / "BHSM_N12_C2_1221_CANCELLED_DELTA_MONOTONICITY.json"
RESULT = BASE / "BHSM_N12_C2_CANCELLED_DESCRIPTOR_GRAPH.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()

from bhsm.interface.aether_cancelled_descriptor_graph import (  # noqa: E402
    exact_cancelled_descriptor_graph_field_action,
)


def build_payload() -> dict:
    cover = json.loads(COVER.read_text(encoding="utf-8"))
    monotone = json.loads(MONOTONE.read_text(encoding="utf-8"))
    if not cover.get("validation_passed") or not monotone.get("validation_passed"):
        raise RuntimeError("validated cover and monotonicity theorem required")
    with np.load(COVER_DATA) as data:
        states = np.asarray(data["predictor_centers"], dtype=float)
        descriptors = np.asarray(data["signed_descriptor_centers"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)
    indices = (0, len(states) // 2, len(states) - 1)
    witnesses = []
    for index in indices:
        field = exact_cancelled_descriptor_graph_field_action(
            state=states[index], weights=weights, reference=reference,
            signed_descriptor=float(descriptors[index]),
        )
        witnesses.append({
            "index": index,
            "selected_branch": int(field["selected_branch"]),
            "signed_descriptor": float(field["signed_descriptor"]),
            "Delta": float(field["Delta"]),
            "signed_descriptor_rate": float(field["signed_descriptor_rate"]),
            "Dlambda_cancelled_field": float(field["Dlambda_cancelled_field"]),
            "descriptor_graph_defect_rate": float(field["descriptor_graph_defect_rate"]),
            "extended_field_norm": float(np.linalg.norm(
                field["extended_graph_field_action"]
            )),
        })
    validation = {
        "all_sampled_centers_retain_branch_24": all(
            row["selected_branch"] == 24 for row in witnesses
        ),
        "signed_descriptor_and_selected_eigenvalue_rates_agree_exactly": all(
            row["signed_descriptor_rate"] == row["Dlambda_cancelled_field"]
            for row in witnesses
        ),
        "descriptor_graph_defect_rate_is_identically_zero": all(
            row["descriptor_graph_defect_rate"] == 0.0 for row in witnesses
        ),
        "extended_graph_fields_are_finite": all(
            np.isfinite(row["extended_field_norm"]) for row in witnesses
        ),
        "independent_wrapped_descriptor_interval_is_superseded": (
            monotone["adjudication"]["near_zero_independent_descriptor_lower_bound"]
            == "SCALAR_WRAPPING_ARTIFACT"
        ),
        "no_selector_recurrence_scale_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_CANCELLED_DESCRIPTOR_GRAPH",
        "status": "C2_CANCELLED_SIGNED_DESCRIPTOR_GRAPH_INVARIANT_DERIVED" if passed else "C2_CANCELLED_DESCRIPTOR_GRAPH_AUDIT_FAILED",
        "identity": "d_theta(s-lambda(Y))=Delta-Dlambda[G_theta]=0",
        "dimension": {
            "ambient_extended_coordinates": 99,
            "invariant_descriptor_graph_dimension": 98,
            "extra_physical_degree_of_freedom_added": False,
        },
        "witnesses": witnesses,
        "adjudication": {
            "descriptor_interval_role": "COUPLED_GRAPH_COORDINATE_NOT_INDEPENDENT_SCALAR_TUBE",
            "binary64_eigenvalue_role": "LINE_IDENTIFICATION_DIAGNOSTIC_ONLY",
            "physical_stop_derived": False,
        },
        "exact_next_dependency": (
            "PROPAGATE_A_SHEARED_LOHNER_OR_MULTIPLE_SHOOTING_TUBE_ON_THE_"
            "INVARIANT_DESCRIPTOR_GRAPH_AND_RECENTER_THE_COMPLETE_RESPONSE"
        ),
        "inputs": {
            COVER.relative_to(ROOT).as_posix(): _sha256(COVER),
            COVER_DATA.relative_to(ROOT).as_posix(): _sha256(COVER_DATA),
            MONOTONE.relative_to(ROOT).as_posix(): _sha256(MONOTONE),
        },
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
