"""Measure the signed ordered-event squared rate on both certified chords.

Only the 130 already-retained Hermite centers are evaluated.  This creates no
state or trajectory and is diagnostic until a subspan variation enclosure is
combined with the values.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (  # noqa: E402
    exact_full_action_jet_at_state,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (  # noqa: E402
    dimensions,
)


ORDER = 12
POINTS = 96
COMPLEX_STEP = 1.0e-20
BASE = ROOT / "artifacts/intrinsic_state_selection"
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_TWO_CHORD_SIGNED_CENTER_RATE_PROFILE.json"
)
SIGN_AUTHORITY = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_TWO_CHORD_EVENT_TRANSPORT_SIGN_AUTHORITY.json"
)
NODES = BASE / "BHSM_N12_PERSISTENCE_PROPOSAL_NODES.npz"
CENTERS = {
    "chord_01": BASE / "BHSM_N12_FIRST_CHORD_HIGH_PRECISION_HERMITE_CENTER.npz",
    "chord_02": BASE / "BHSM_N12_CHORD_02_HIGH_PRECISION_HERMITE_CENTER.npz",
}


def _sha256(path: Path) -> str:
    content = path.read_bytes()
    if path.suffix.lower() == ".json":
        content = content.replace(b"\r\n", b"\n")
    return hashlib.sha256(content).hexdigest().upper()


def _directional_event(
    state: np.ndarray,
    direction_action: np.ndarray,
    weights: np.ndarray,
    qdim: int,
) -> np.ndarray:
    shifted = state.astype(complex)
    shifted += 1j * COMPLEX_STEP * (direction_action / weights)
    jet = exact_full_action_jet_at_state(
        ORDER,
        shifted[:qdim], shifted[qdim:2 * qdim], shifted[2 * qdim:],
        points=POINTS,
    )
    return np.imag(np.asarray(jet.hessian)[qdim:, qdim:]) / COMPLEX_STEP


def _chord_profile(
    path: Path, reference: np.ndarray, qdim: int,
) -> dict[str, object]:
    data = np.load(path)
    weights = np.asarray(data["action_weights"], dtype=float)
    states = np.asarray(data["action_states"], dtype=float) / weights
    flows = np.asarray(data["exact_action_vectors"], dtype=float)
    taus = np.asarray(data["taus"], dtype=float)
    rows = []
    for tau, state, flow in zip(taus, states, flows):
        jet = exact_full_action_jet_at_state(
            ORDER,
            state[:qdim], state[qdim:2 * qdim], state[2 * qdim:],
            points=POINTS,
        )
        event = np.asarray(jet.hessian, dtype=float)[qdim:, qdim:]
        values, vectors = np.linalg.eigh(event)
        selected = int(np.argmax(np.abs(vectors.T @ reference)))
        psi = vectors[:, selected]
        if float(psi @ reference) < 0.0:
            psi = -psi
        derivative = _directional_event(state, flow, weights, qdim)
        lam = float(values[selected])
        lambda_rate = float(psi @ derivative @ psi)
        u_rate = 2.0 * lam * lambda_rate
        symmetry_scale = max(float(np.linalg.norm(derivative)), np.finfo(float).tiny)
        rows.append({
            "tau": float(tau),
            "physical_selected_index": selected,
            "lambda": lam,
            "lambda_rate": lambda_rate,
            "u_rate": u_rate,
            "directional_event_symmetry_relative_residual": float(
                np.linalg.norm(derivative - derivative.T) / symmetry_scale
            ),
        })
    rates = np.asarray([row["u_rate"] for row in rows])
    lambdas = np.asarray([row["lambda"] for row in rows])
    symmetry = np.asarray([
        row["directional_event_symmetry_relative_residual"] for row in rows
    ])
    return {
        "rows": rows,
        "summary": {
            "nodes": len(rows),
            "u_rate_minimum": float(np.min(rates)),
            "u_rate_maximum": float(np.max(rates)),
            "u_rate_positive_nodes": int(np.count_nonzero(rates > 0.0)),
            "u_rate_negative_nodes": int(np.count_nonzero(rates < 0.0)),
            "lambda_minimum": float(np.min(lambdas)),
            "lambda_maximum": float(np.max(lambdas)),
            "selected_indices": sorted({
                int(row["physical_selected_index"]) for row in rows
            }),
            "maximum_directional_event_symmetry_relative_residual": float(
                np.max(symmetry)
            ),
        },
    }


def build_payload() -> dict[str, object]:
    inputs = [SIGN_AUTHORITY, NODES, *CENTERS.values()]
    if not all(path.is_file() for path in inputs):
        raise FileNotFoundError("two-chord signed-center inputs required")
    authority = json.loads(SIGN_AUTHORITY.read_text(encoding="utf-8"))
    if authority.get("validation_passed") is not True:
        raise RuntimeError("validated sign-authority audit required")
    node_data = np.load(NODES)
    reference = np.asarray(node_data["branch_reference"], dtype=float)
    qdim = dimensions(ORDER)["coordinates"]
    profiles = {
        name: _chord_profile(path, reference, qdim)
        for name, path in CENTERS.items()
    }
    summaries = {name: profile["summary"] for name, profile in profiles.items()}
    validation = {
        "all_130_existing_centers_consumed": sum(
            item["nodes"] for item in summaries.values()
        ) == 130,
        "same_selected_branch_23_on_both_chords": all(
            item["selected_indices"] == [23] for item in summaries.values()
        ),
        "physical_event_positive_at_all_centers": all(
            item["lambda_minimum"] > 0.0 for item in summaries.values()
        ),
        "directional_event_derivatives_symmetric_at_binary64_scale": all(
            item["maximum_directional_event_symmetry_relative_residual"] < 1.0e-12
            for item in summaries.values()
        ),
        "node_sign_not_promoted_to_subspan_interval_sign": True,
        "no_new_state_trajectory_solver_equation_gate_or_physics": True,
        "chord_03_not_used": True,
    }
    return {
        "artifact": "BHSM_N12_GATE7_TWO_CHORD_SIGNED_CENTER_RATE_PROFILE",
        "classification": (
            "SIGNED_ORDERED_EVENT_SQUARED_RATE_EVALUATED_ON_ALL_130_EXISTING_"
            "TWO_CHORD_CENTERS;_SUBSPAN_D5_KATO_VARIATION_REMAINS_REQUIRED"
        ),
        "identity": "u_rate=2*e_ord*<psi,D_H(Y)[V(Y)]psi>",
        "profiles": profiles,
        "summary": summaries,
        "claim_boundary": {
            "signed_center_rate": "EVALUATED",
            "128_subspan_interval_sign": "OPEN",
            "continuum_tube_sign_transfer": "OPEN",
            "terminal_chart_entry": "OPEN",
        },
        "exact_next_dependency": (
            "BOUND_THE_CANCELLATION_PRESERVING_D5_KATO_VARIATION_OF_u_rate_"
            "ON_THE_EXISTING_128_CERTIFIED_SUBSPANS"
        ),
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in inputs
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "Gate7_status_changed": False,
        "chord_03_authorized": False,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise RuntimeError("two-chord signed-center profile failed")
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "classification": payload["classification"],
        "summary": payload["summary"],
        "validation_passed": payload["validation_passed"],
        "sha256": _sha256(RESULT),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
